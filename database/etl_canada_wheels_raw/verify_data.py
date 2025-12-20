#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 ETL 导入的数据
"""
import pymysql
import sqlite3
from pathlib import Path


def verify_data(mysql_config: dict, sqlite_db_path: str):
    """
    验证数据导入是否正确
    
    Args:
        mysql_config: MySQL 配置
        sqlite_db_path: SQLite 数据库路径
    """
    print("=" * 60)
    print("数据验证")
    print("=" * 60)
    
    # 连接 MySQL
    mysql_conn = pymysql.connect(**mysql_config)
    mysql_cursor = mysql_conn.cursor()
    
    # 连接 SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # 验证年份
        print("\n1. 验证年份数据:")
        sqlite_cursor.execute("SELECT COUNT(*) FROM years")
        sqlite_count = sqlite_cursor.fetchone()[0]
        mysql_cursor.execute("SELECT COUNT(*) FROM mini_vehicle_year")
        mysql_count = mysql_cursor.fetchone()[0]
        print(f"   SQLite: {sqlite_count} 条")
        print(f"   MySQL:  {mysql_count} 条")
        if sqlite_count == mysql_count:
            print(f"   ✓ 通过")
        else:
            print(f"   ✗ 失败: 数量不匹配")
        
        # 验证品牌（year-scoped，不去重）
        print("\n2. 验证品牌数据:")
        sqlite_cursor.execute("SELECT COUNT(*) FROM makes")
        sqlite_count = sqlite_cursor.fetchone()[0]
        mysql_cursor.execute("SELECT COUNT(*) FROM mini_vehicle_make")
        mysql_count = mysql_cursor.fetchone()[0]
        print(f"   SQLite: {sqlite_count} 条")
        print(f"   MySQL:  {mysql_count} 条")
        if sqlite_count == mysql_count:
            print(f"   ✓ 通过")
        else:
            print(f"   ✗ 失败: 数量不匹配")
        
        # 验证型号（year-scoped，不去重）
        print("\n3. 验证型号数据:")
        sqlite_cursor.execute("SELECT COUNT(*) FROM models")
        sqlite_count = sqlite_cursor.fetchone()[0]
        mysql_cursor.execute("SELECT COUNT(*) FROM mini_vehicle_model")
        mysql_count = mysql_cursor.fetchone()[0]
        print(f"   SQLite: {sqlite_count} 条")
        print(f"   MySQL:  {mysql_count} 条")
        if sqlite_count == mysql_count:
            print(f"   ✓ 通过")
        else:
            print(f"   ✗ 失败: 数量不匹配")
        
        # 验证车辆详情（关键：必须等于 159112）
        print("\n4. 验证车辆详情数据（关键）:")
        sqlite_cursor.execute("SELECT COUNT(*) FROM vehicle_details")
        sqlite_count = sqlite_cursor.fetchone()[0]
        mysql_cursor.execute("SELECT COUNT(*) FROM mini_vehicle_detail")
        mysql_count = mysql_cursor.fetchone()[0]
        print(f"   SQLite: {sqlite_count} 条")
        print(f"   MySQL:  {mysql_count} 条")
        if sqlite_count == mysql_count == 159112:
            print(f"   ✓ 通过: 数量正确 ({mysql_count} 条)")
        else:
            print(f"   ✗ 失败: 数量不匹配或不是 159112")
            print(f"      期望: 159112")
            print(f"      实际: MySQL={mysql_count}, SQLite={sqlite_count}")
        
        # 验证 ID 保留
        print("\n5. 验证 ID 保留:")
        # 检查年份 ID
        sqlite_cursor.execute("SELECT id FROM years ORDER BY id LIMIT 5")
        sqlite_ids = [row[0] for row in sqlite_cursor.fetchall()]
        mysql_cursor.execute("SELECT id FROM mini_vehicle_year ORDER BY id LIMIT 5")
        mysql_ids = [row[0] for row in mysql_cursor.fetchall()]
        print(f"   年份 ID 示例 (SQLite): {sqlite_ids}")
        print(f"   年份 ID 示例 (MySQL):  {mysql_ids}")
        if sqlite_ids == mysql_ids:
            print(f"   ✓ 年份 ID 保留正确")
        else:
            print(f"   ✗ 年份 ID 保留失败")
        
        # 检查车辆详情 vehicle_id
        sqlite_cursor.execute("SELECT vehicle_id FROM vehicle_details ORDER BY vehicle_id LIMIT 5")
        sqlite_vehicle_ids = [row[0] for row in sqlite_cursor.fetchall()]
        mysql_cursor.execute("SELECT vehicle_id FROM mini_vehicle_detail ORDER BY vehicle_id LIMIT 5")
        mysql_vehicle_ids = [row[0] for row in mysql_cursor.fetchall()]
        print(f"   车辆 ID 示例 (SQLite): {sqlite_vehicle_ids}")
        print(f"   车辆 ID 示例 (MySQL):  {mysql_vehicle_ids}")
        if sqlite_vehicle_ids == mysql_vehicle_ids:
            print(f"   ✓ 车辆 ID 保留正确")
        else:
            print(f"   ✗ 车辆 ID 保留失败")
        
        print("\n" + "=" * 60)
        print("验证完成")
        print("=" * 60)
        
    finally:
        mysql_conn.close()
        sqlite_conn.close()


if __name__ == "__main__":
    import sys
    import os
    from pathlib import Path
    
    # MySQL 配置 - 从环境变量读取，如果没有则使用默认值
    mysql_config = {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', '3306')),
        'user': os.getenv('DATABASE_USER', 'mininormi'),
        'password': os.getenv('DATABASE_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD', 'a123123')),
        'database': os.getenv('DATABASE_NAME', os.getenv('MYSQL_DATABASE', 'rimsurge')),
        'charset': 'utf8mb4'
    }
    
    # SQLite 数据库路径 - 使用脚本所在目录计算项目根目录
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent  # database/etl_canada_wheels_raw -> database -> project_root
    sqlite_db_path = str(project_root / "canada_wheels.db")
    
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
    
    verify_data(mysql_config, sqlite_db_path)


