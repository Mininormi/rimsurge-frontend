#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL 主程序：原样迁移 canada_wheels.db 数据到 MySQL（不去重）
"""
import sys
from pathlib import Path
from extract import CanadaWheelsRawExtractor
from load import MySQLRawLoader


def main():
    """主函数"""
    import os
    
    # 配置 - 使用脚本所在目录计算项目根目录
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent  # database/etl_canada_wheels_raw -> database -> project_root
    sqlite_db_path = str(project_root / "canada_wheels.db")
    
    # MySQL 配置 - 从环境变量读取，如果没有则使用默认值
    mysql_config = {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', '3306')),
        'user': os.getenv('DATABASE_USER', 'mininormi'),
        'password': os.getenv('DATABASE_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD', 'a123123')),
        'database': os.getenv('DATABASE_NAME', os.getenv('MYSQL_DATABASE', 'rimsurge'))
    }
    
    # 从命令行参数读取配置（可选）
    if len(sys.argv) > 1:
        sqlite_db_path = sys.argv[1]
    if len(sys.argv) > 2:
        mysql_config['host'] = sys.argv[2]
    if len(sys.argv) > 3:
        mysql_config['port'] = int(sys.argv[3])
    if len(sys.argv) > 4:
        mysql_config['user'] = sys.argv[4]
    if len(sys.argv) > 5:
        mysql_config['password'] = sys.argv[5]
    if len(sys.argv) > 6:
        mysql_config['database'] = sys.argv[6]
    
    print("=" * 60)
    print("Canada Wheels 原样数据迁移 ETL")
    print("=" * 60)
    print(f"源数据库: {sqlite_db_path}")
    print(f"目标数据库: {mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")
    print("=" * 60)
    
    # 提取数据
    print("\n[步骤 1] 提取数据...")
    extractor = CanadaWheelsRawExtractor(sqlite_db_path)
    
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
        
        if len(vehicle_details_data) != 159112:
            print(f"\n⚠ 警告: 车辆详情数据不是 159112 条，实际为 {len(vehicle_details_data)} 条")
        
        # 加载数据
        print("\n[步骤 2] 加载数据到 MySQL...")
        loader = MySQLRawLoader(**mysql_config)
        
        try:
            loader.connect()
            
            # 清空表（按顺序，先清空依赖表）
            print("\n清空目标表...")
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



