#!/usr/bin/env python3
"""
从 canada_wheels.db (SQLite) 原样提取数据（不去重）
只提取 years/makes/models/vehicle_details 四张表
"""
import sqlite3
from typing import Dict, List, Any
from pathlib import Path


class CanadaWheelsRawExtractor:
    """从 canada_wheels.db 原样提取数据（不去重）"""
    
    def __init__(self, db_path: str):
        """
        初始化提取器
        
        Args:
            db_path: canada_wheels.db 文件路径
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def extract_years(self) -> List[Dict[str, Any]]:
        """提取年份数据（原样，不去重）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, year FROM years ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]
    
    def extract_makes(self) -> List[Dict[str, Any]]:
        """提取品牌数据（原样，不去重）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT year_id, make_id, make_name FROM makes ORDER BY year_id, make_id")
        return [dict(row) for row in cursor.fetchall()]
    
    def extract_models(self) -> List[Dict[str, Any]]:
        """提取型号数据（原样，不去重）"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT year_id, make_id, model_id, model_name FROM models ORDER BY year_id, make_id, model_id"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def extract_vehicle_details(self) -> List[Dict[str, Any]]:
        """提取车辆详情数据（原样，不去重，159112 行）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                vehicle_id,
                year_id,
                make_id,
                model_id,
                vehicle_name,
                bolt_pattern_front,
                bolt_pattern_rear,
                hub_bore_front,
                hub_bore_rear,
                min_offset_front,
                min_offset_rear,
                max_offset_front,
                max_offset_rear,
                oem_offset_front,
                oem_offset_rear,
                rim_diameter_front,
                rim_diameter_rear,
                rim_width_front,
                rim_width_rear,
                wheel_size_front,
                wheel_size_rear,
                tire_size_front,
                tire_size_rear
            FROM vehicle_details
            ORDER BY vehicle_id
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, int]:
        """获取数据统计"""
        cursor = self.conn.cursor()
        stats = {}
        tables = ['years', 'makes', 'models', 'vehicle_details']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        return stats


if __name__ == "__main__":
    # 测试提取
    import sys
    
    # 使用脚本所在目录计算项目根目录
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent  # database/etl_canada_wheels_raw -> database -> project_root
    db_path = str(project_root / "canada_wheels.db")
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    extractor = CanadaWheelsRawExtractor(db_path)
    
    try:
        print("提取数据统计:")
        stats = extractor.get_statistics()
        for table, count in stats.items():
            print(f"  {table}: {count:,} 行")
        
        print("\n提取示例数据:")
        years = extractor.extract_years()
        print(f"  年份: {len(years)} 条")
        if years:
            print(f"    示例: {years[0]}")
        
        makes = extractor.extract_makes()
        print(f"  品牌: {len(makes)} 条")
        if makes:
            print(f"    示例: {makes[0]}")
        
        models = extractor.extract_models()
        print(f"  型号: {len(models)} 条")
        if models:
            print(f"    示例: {models[0]}")
        
        vehicle_details = extractor.extract_vehicle_details()
        print(f"  车辆详情: {len(vehicle_details)} 条")
        if vehicle_details:
            print(f"    示例: {vehicle_details[0]}")
    finally:
        extractor.close()



