#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL 主程序：原样迁移 canada_wheels.db 数据到 MySQL（不去重）

支持年份过滤：
  python main.py                    # 全量迁移（TRUNCATE 全表）
  python main.py --years 2025,2026  # 只迁移指定年份（先删除这些年份，再导入）
"""
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from extract import CanadaWheelsRawExtractor
from load import MySQLRawLoader


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Canada Wheels 原样数据迁移 ETL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                                    # 全量迁移
  python main.py --years 2025,2026                  # 只迁移 2025 和 2026
  python main.py --years 2025,2026 --db path/to/db # 指定数据库路径
        """
    )
    parser.add_argument(
        '--db', '--database',
        type=str,
        help='SQLite 数据库路径（默认：项目根目录/canada_wheels.db）'
    )
    parser.add_argument(
        '--years', '-y',
        type=str,
        help='年份列表，逗号分隔（如：2025,2026）。如果指定，只迁移这些年份的数据（增量模式）'
    )
    parser.add_argument(
        '--host',
        type=str,
        help='MySQL 主机（默认：从环境变量 DATABASE_HOST 读取，或 localhost）'
    )
    parser.add_argument(
        '--port',
        type=int,
        help='MySQL 端口（默认：从环境变量 DATABASE_PORT 读取，或 3306）'
    )
    parser.add_argument(
        '--user',
        type=str,
        help='MySQL 用户名（默认：从环境变量 DATABASE_USER 读取，或 mininormi）'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='MySQL 密码（默认：从环境变量 DATABASE_PASSWORD 读取，或 a123123）'
    )
    parser.add_argument(
        '--database-name',
        type=str,
        dest='database',
        help='MySQL 数据库名（默认：从环境变量 DATABASE_NAME 读取，或 rimsurge）'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    import os
    
    args = parse_args()
    
    # 配置 - 使用脚本所在目录计算项目根目录
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent  # database/etl_canada_wheels_raw -> database -> project_root
    
    # SQLite 数据库路径
    if args.db:
        sqlite_db_path = args.db
    else:
        sqlite_db_path = str(project_root / "canada_wheels.db")
    
    # MySQL 配置 - 从环境变量读取，如果没有则使用默认值
    mysql_config = {
        'host': args.host or os.getenv('DATABASE_HOST', 'localhost'),
        'port': args.port or int(os.getenv('DATABASE_PORT', '3306')),
        'user': args.user or os.getenv('DATABASE_USER', 'mininormi'),
        'password': args.password or os.getenv('DATABASE_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD', 'a123123')),
        'database': args.database or os.getenv('DATABASE_NAME', os.getenv('MYSQL_DATABASE', 'rimsurge'))
    }
    
    # 解析年份列表
    filter_years: Optional[List[int]] = None
    if args.years:
        try:
            filter_years = [int(y.strip()) for y in args.years.split(',')]
            print(f"[INFO] 年份过滤模式: 只迁移年份 {filter_years}")
        except ValueError as e:
            print(f"[ERROR] 年份格式错误: {args.years}，应为逗号分隔的整数（如：2025,2026）")
            sys.exit(1)
    
    print("=" * 60)
    print("Canada Wheels 原样数据迁移 ETL")
    print("=" * 60)
    print(f"源数据库: {sqlite_db_path}")
    print(f"目标数据库: {mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")
    if filter_years:
        print(f"迁移模式: 增量模式（只迁移年份 {filter_years}）")
    else:
        print(f"迁移模式: 全量模式（TRUNCATE 全表后导入）")
    print("=" * 60)
    
    # 提取数据
    print("\n[步骤 1] 提取数据...")
    extractor = CanadaWheelsRawExtractor(sqlite_db_path, filter_years=filter_years)
    
    try:
        years_data = extractor.extract_years()
        makes_data = extractor.extract_makes()
        models_data = extractor.extract_models()
        vehicle_details_data = extractor.extract_vehicle_details()
        
        print(f"\n提取完成:")
        print(f"  年份: {len(years_data)} 条")
        print(f"  品牌: {len(makes_data)} 条")
        print(f"  型号: {len(models_data)} 条")
        print(f"  车辆详情: {len(vehicle_details_data)} 条")
        
        if not filter_years and len(vehicle_details_data) != 159112:
            print(f"\n⚠ 警告: 车辆详情数据不是 159112 条，实际为 {len(vehicle_details_data)} 条")
        
        if len(years_data) == 0:
            print(f"\n⚠ 警告: 没有提取到任何年份数据")
            if filter_years:
                print(f"  请检查 SQLite 数据库中是否存在年份 {filter_years}")
            sys.exit(1)
        
        # 加载数据
        print("\n[步骤 2] 加载数据到 MySQL...")
        loader = MySQLRawLoader(**mysql_config)
        
        try:
            loader.connect()
            
            if filter_years:
                # 增量模式：先删除指定年份的数据
                # 从提取的 years_data 中获取 year_id（注意：这里的 id 就是 year_id）
                year_ids = [row['id'] for row in years_data]
                print(f"\n[增量模式] 删除年份数据 (year_ids: {year_ids})...")
                loader.delete_years(year_ids)
            else:
                # 全量模式：TRUNCATE 全表
                print("\n[全量模式] 清空目标表...")
                loader.truncate_table("mini_vehicle_detail")
                loader.truncate_table("mini_vehicle_model")
                loader.truncate_table("mini_vehicle_make")
                loader.truncate_table("mini_vehicle_year")
            
            # 导入数据（按顺序，先导入被依赖表）
            print("\n导入数据...")
            loader.load_years(years_data)
            loader.load_makes(makes_data)
            loader.load_models(models_data)
            loader.load_vehicle_details(vehicle_details_data)
            
            print("\n" + "=" * 60)
            print("[完成] 所有数据导入完成！")
            print("=" * 60)
            if filter_years:
                print(f"\n已迁移年份: {filter_years}")
                print(f"请验证这些年份的数据是否正确")
            else:
                print(f"\n请运行 verify_data.py 验证数据:")
                print(f"  python verify_data.py")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n[错误] 加载数据失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            loader.close()
            
    except Exception as e:
        print(f"\n[错误] 提取数据失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        extractor.close()


if __name__ == "__main__":
    main()



