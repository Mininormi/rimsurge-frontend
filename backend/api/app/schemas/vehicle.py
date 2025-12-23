"""
车辆相关的 Pydantic 模式（基于 raw 表结构）
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class YearResponse(BaseModel):
    """年份响应"""
    id: int
    year: int


class MakeResponse(BaseModel):
    """品牌响应"""
    id: int
    name: str  # make_name


class ModelResponse(BaseModel):
    """型号响应"""
    id: int
    make_id: int
    name: str  # model_name


class VehicleResponse(BaseModel):
    """车辆响应（vehicle_detail）"""
    vehicle_id: str
    vehicle_name: Optional[str] = None


class FitmentOEM(BaseModel):
    """OEM 适配参数"""
    bolt_pattern: Optional[str] = None
    hub_bore: Optional[str] = None
    offset_oem: Optional[str] = None
    offset_min: Optional[str] = None
    offset_max: Optional[str] = None
    wheel_size: Optional[str] = None
    rim_diameter: Optional[str] = None
    rim_width: Optional[str] = None
    tire_size: Optional[str] = None


class FitmentResponse(BaseModel):
    """Fitment 响应"""
    model_config = {"protected_namespaces": ()}  # 允许使用 model_id 字段
    
    vehicle_id: str
    vehicle_name: Optional[str] = None
    year_id: int
    make_id: int
    model_id: int
    oem_front: Optional[FitmentOEM] = None
    oem_rear: Optional[FitmentOEM] = None
    is_staggered: bool = False
    available_sizes: List[dict] = Field(default_factory=list, description="可用尺寸列表：[{diameter: 17, label: '17\" (-3)'}, ...]")



