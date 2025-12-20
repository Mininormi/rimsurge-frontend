#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将原样数据导入到 MySQL（不去重，保留源库 ID）
"""
import pymysql
from typing import Dict, List, Any
from datetime import datetime


class MySQLRawLoader:
    """MySQL 原样数据加载器（不去重）"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """
        初始化加载器
        
        Args:
            host: MySQL 主机
            port: MySQL 端口
            user: MySQL 用户名
            password: MySQL 密码
            database: 数据库名
        """
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'autocommit': False
        }
        self.conn = None
    
    def connect(self):
        """连接数据库"""
        self.conn = pymysql.connect(**self.config)
        print(f"[OK] 已连接到 MySQL: {self.config['host']}:{self.config['port']}/{self.config['database']}")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("[OK] 已关闭 MySQL 连接")
    
    def truncate_table(self, table_name: str):
        """清空表（TRUNCATE）"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            self.conn.commit()
            print(f"[OK] 已清空表: {table_name}")
        except Exception as e:
            print(f"[ERROR] 清空表失败 {table_name}: {e}")
            self.conn.rollback()
            raise
    
    def load_years(self, years_data: List[Dict[str, Any]]) -> int:
        """
        加载年份数据（原样，保留源库 ID）
        
        Args:
            years_data: 年份数据列表
        
        Returns:
            int: 插入的行数
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        now = int(datetime.now().timestamp())
        
        # 批量插入
        sql = """
            INSERT INTO mini_vehicle_year (id, year, createtime, updatetime)
            VALUES (%s, %s, %s, %s)
        """
        
        values = [
            (row['id'], row['year'], now, now)
            for row in years_data
        ]
        
        cursor.executemany(sql, values)
        self.conn.commit()
        
        count = cursor.rowcount
        print(f"[OK] 年份数据加载完成: {count} 条")
        return count
    
    def load_makes(self, makes_data: List[Dict[str, Any]]) -> int:
        """
        加载品牌数据（原样，保留源库 ID）
        
        Args:
            makes_data: 品牌数据列表
        
        Returns:
            int: 插入的行数
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        now = int(datetime.now().timestamp())
        
        # 批量插入
        sql = """
            INSERT INTO mini_vehicle_make (year_id, make_id, make_name, createtime, updatetime)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        values = [
            (row['year_id'], row['make_id'], row['make_name'], now, now)
            for row in makes_data
        ]
        
        cursor.executemany(sql, values)
        self.conn.commit()
        
        count = cursor.rowcount
        print(f"[OK] 品牌数据加载完成: {count} 条")
        return count
    
    def load_models(self, models_data: List[Dict[str, Any]]) -> int:
        """
        加载型号数据（原样，保留源库 ID）
        
        Args:
            models_data: 型号数据列表
        
        Returns:
            int: 插入的行数
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        now = int(datetime.now().timestamp())
        
        # 批量插入
        sql = """
            INSERT INTO mini_vehicle_model (year_id, make_id, model_id, model_name, createtime, updatetime)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        values = [
            (row['year_id'], row['make_id'], row['model_id'], row['model_name'], now, now)
            for row in models_data
        ]
        
        cursor.executemany(sql, values)
        self.conn.commit()
        
        count = cursor.rowcount
        print(f"[OK] 型号数据加载完成: {count} 条")
        return count
    
    def load_vehicle_details(self, vehicle_details_data: List[Dict[str, Any]], batch_size: int = 5000) -> int:
        """
        加载车辆详情数据（原样，不去重，159112 行）
        
        Args:
            vehicle_details_data: 车辆详情数据列表
            batch_size: 批量插入大小
        
        Returns:
            int: 插入的行数
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        now = int(datetime.now().timestamp())
        
        sql = """
            INSERT INTO mini_vehicle_detail (
                vehicle_id, year_id, make_id, model_id, vehicle_name,
                bolt_pattern_front, bolt_pattern_rear,
                hub_bore_front, hub_bore_rear,
                min_offset_front, min_offset_rear,
                max_offset_front, max_offset_rear,
                oem_offset_front, oem_offset_rear,
                rim_diameter_front, rim_diameter_rear,
                rim_width_front, rim_width_rear,
                wheel_size_front, wheel_size_rear,
                tire_size_front, tire_size_rear,
                createtime, updatetime
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        
        total_count = 0
        
        # 分批插入
        for i in range(0, len(vehicle_details_data), batch_size):
            batch = vehicle_details_data[i:i + batch_size]
            values = [
                (
                    row['vehicle_id'],
                    row['year_id'],
                    row['make_id'],
                    row['model_id'],
                    row.get('vehicle_name'),
                    row.get('bolt_pattern_front'),
                    row.get('bolt_pattern_rear'),
                    row.get('hub_bore_front'),
                    row.get('hub_bore_rear'),
                    row.get('min_offset_front'),
                    row.get('min_offset_rear'),
                    row.get('max_offset_front'),
                    row.get('max_offset_rear'),
                    row.get('oem_offset_front'),
                    row.get('oem_offset_rear'),
                    row.get('rim_diameter_front'),
                    row.get('rim_diameter_rear'),
                    row.get('rim_width_front'),
                    row.get('rim_width_rear'),
                    row.get('wheel_size_front'),
                    row.get('wheel_size_rear'),
                    row.get('tire_size_front'),
                    row.get('tire_size_rear'),
                    now,
                    now
                )
                for row in batch
            ]
            
            cursor.executemany(sql, values)
            self.conn.commit()
            
            batch_count = cursor.rowcount
            total_count += batch_count
            print(f"[OK] 车辆详情数据批量加载: {len(batch)} 条 (累计: {total_count}/{len(vehicle_details_data)})")
        
        print(f"[OK] 车辆详情数据加载完成: {total_count} 条")
        return total_count


if __name__ == "__main__":
    # 测试加载
    import sys
    import os
    from pathlib import Path
    from extract import CanadaWheelsRawExtractor
    
    # MySQL 配置 - 从环境变量读取，如果没有则使用默认值
    mysql_config = {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', '3306')),
        'user': os.getenv('DATABASE_USER', 'mininormi'),
        'password': os.getenv('DATABASE_PASSWORD', os.getenv('MYSQL_ROOT_PASSWORD', 'a123123')),
        'database': os.getenv('DATABASE_NAME', os.getenv('MYSQL_DATABASE', 'rimsurge'))
    }
    
    # 使用脚本所在目录计算项目根目录
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent  # database/etl_canada_wheels_raw -> database -> project_root
    db_path = str(project_root / "canada_wheels.db")
    
    # 从命令行参数读取配置（可选）
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
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
    extractor = CanadaWheelsRawExtractor(db_path)
    
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
        
        # 加载数据
        loader = MySQLRawLoader(**mysql_config)
        try:
            loader.connect()
            
            # 清空表（按顺序）
            print("\n开始清空表...")
            loader.truncate_table("mini_vehicle_detail")
            loader.truncate_table("mini_vehicle_model")
            loader.truncate_table("mini_vehicle_make")
            loader.truncate_table("mini_vehicle_year")
            
            # 导入数据（按顺序）
            print("\n开始导入数据...")
            loader.load_years(years_data)
            loader.load_makes(makes_data)
            loader.load_models(models_data)
            loader.load_vehicle_details(vehicle_details_data)
            
            print("\n[完成] 所有数据导入完成！")
        finally:
            loader.close()
    finally:
        extractor.close()


