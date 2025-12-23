"""
车辆数据 API 路由（基于 raw 表结构）
游客可访问，无需鉴权（GET 请求）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, distinct
from typing import Optional, List
from app.database import get_db, get_table
from app.schemas.vehicle import (
    YearResponse,
    MakeResponse,
    ModelResponse,
    VehicleResponse,
    FitmentResponse,
    FitmentOEM,
)
import re

router = APIRouter()


@router.get("/years", response_model=List[YearResponse], summary="获取年份列表")
async def get_years(
    db: Session = Depends(get_db)
):
    """
    获取所有可用年份列表（从 mini_vehicle_year）
    """
    years_table = get_table("mini_vehicle_year")
    
    result = db.execute(
        select(years_table)
        .order_by(years_table.c.year.desc())
    )
    
    years = []
    for row in result.fetchall():
        years.append({
            "id": row.id,
            "year": row.year,
        })
    
    return years


@router.get("/makes", response_model=List[MakeResponse], summary="获取品牌列表")
async def get_makes(
    year: Optional[int] = Query(None, description="年份（可选，用于过滤）"),
    db: Session = Depends(get_db)
):
    """
    获取品牌列表
    
    如果提供了 year 参数，按源库逻辑返回该年份的 makes（从 mini_vehicle_make 直接过滤 year_id）
    """
    makes_table = get_table("mini_vehicle_make")
    years_table = get_table("mini_vehicle_year")
    
    if year:
        # 先找到 year_id
        year_result = db.execute(
            select(years_table.c.id)
            .where(years_table.c.year == year)
            .limit(1)
        )
        year_row = year_result.fetchone()
        if not year_row:
            # #region agent log
            print(f"[DEBUG] get_makes: year {year} not found in years table")
            # #endregion
            return []  # 该年份不存在
        
        year_id = year_row.id
        # #region agent log
        print(f"[DEBUG] get_makes: year {year} -> year_id {year_id}")
        # #endregion

        result = db.execute(
            select(makes_table)
            .where(makes_table.c.year_id == year_id)
            .order_by(makes_table.c.make_name.asc())
        )
    else:
        # 返回所有品牌
        result = db.execute(
            select(makes_table)
            .order_by(makes_table.c.make_name.asc())
        )
    
    makes = []
    for row in result.fetchall():
        makes.append({
            "id": row.make_id,
            "name": row.make_name,
        })
    
    # #region agent log
    print(f"[DEBUG] get_makes: year={year}, makes_count={len(makes)}, first_make={makes[0] if makes else None}")
    # #endregion
    
    return makes


@router.get("/models", response_model=List[ModelResponse], summary="获取型号列表")
async def get_models(
    make_id: int = Query(..., description="品牌ID"),
    year: Optional[int] = Query(None, description="年份（可选，用于过滤）"),
    db: Session = Depends(get_db)
):
    """
    根据品牌ID获取型号列表
    
    如果提供了 year 参数，按源库逻辑返回该年份+品牌下的 models（从 mini_vehicle_model 直接过滤 year_id+make_id）
    """
    models_table = get_table("mini_vehicle_model")
    years_table = get_table("mini_vehicle_year")

    if year:
        # 先找到 year_id
        year_result = db.execute(
            select(years_table.c.id)
            .where(years_table.c.year == year)
            .limit(1)
        )
        year_row = year_result.fetchone()
        if not year_row:
            return []  # 该年份不存在
        
        year_id = year_row.id
        result = db.execute(
            select(models_table)
            .where(
                and_(
                    models_table.c.year_id == year_id,
                    models_table.c.make_id == make_id
                )
            )
            .order_by(models_table.c.model_name.asc())
        )
    else:
        # 未提供 year 时：返回所有年份下该 make_id 的 models（可能较多）
        result = db.execute(
            select(models_table)
            .where(models_table.c.make_id == make_id)
            .order_by(models_table.c.year_id.desc(), models_table.c.model_name.asc())
        )
    
    models = []
    for row in result.fetchall():
        models.append({
            "id": row.model_id,
            "make_id": row.make_id,
            "name": row.model_name,
        })
    
    return models


@router.get("/vehicles", response_model=List[VehicleResponse], summary="获取车辆列表")
async def get_vehicles(
    year: Optional[int] = Query(None, description="年份（可选）"),
    make_id: Optional[int] = Query(None, description="品牌ID（可选）"),
    model_id: Optional[int] = Query(None, description="型号ID（可选）"),
    db: Session = Depends(get_db)
):
    """
    根据年份/品牌/型号获取车辆列表（vehicle_id 和 vehicle_name）
    
    不去重：允许同名多条，但 UI 可按 vehicle_id 唯一
    """
    detail_table = get_table("mini_vehicle_detail")
    years_table = get_table("mini_vehicle_year")
    
    conditions = []
    
    if year:
        # 先找到 year_id
        year_result = db.execute(
            select(years_table.c.id)
            .where(years_table.c.year == year)
            .limit(1)
        )
        year_row = year_result.fetchone()
        if not year_row:
            return []  # 该年份不存在
        
        year_id = year_row.id
        conditions.append(detail_table.c.year_id == year_id)
    
    if make_id:
        conditions.append(detail_table.c.make_id == make_id)
    
    if model_id:
        conditions.append(detail_table.c.model_id == model_id)
    
    if not conditions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供至少一个过滤条件（year, make_id, model_id）"
        )
    
    result = db.execute(
        select(
            detail_table.c.vehicle_id,
            detail_table.c.vehicle_name
        )
        .where(and_(*conditions))
        .order_by(detail_table.c.vehicle_name.asc(), detail_table.c.vehicle_id.asc())
    )
    
    vehicles = []
    for row in result.fetchall():
        vehicles.append({
            "vehicle_id": row.vehicle_id,
            "vehicle_name": row.vehicle_name,
        })
    
    return vehicles


@router.get("/fitment", response_model=FitmentResponse, summary="获取车辆适配参数")
async def get_fitment(
    vehicle_id: str = Query(..., description="车辆ID（vehicle_id）"),
    db: Session = Depends(get_db)
):
    """
    根据 vehicle_id 获取车辆适配参数（轮毂适配信息）
    
    直接从 mini_vehicle_detail 取一行，拼出 OEM front/rear 信息
    available_sizes：优先从 rim_diameter_front 解析 OEM 直径并生成（OEM±N + All）
    """
    detail_table = get_table("mini_vehicle_detail")
    
    result = db.execute(
        select(detail_table)
        .where(detail_table.c.vehicle_id == vehicle_id)
        .limit(1)
    )
    
    detail_row = result.fetchone()
    
    if not detail_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到车辆适配参数"
        )
    
    # 构建 OEM 信息
    oem_front = FitmentOEM(
        bolt_pattern=detail_row.bolt_pattern_front,
        hub_bore=detail_row.hub_bore_front,
        offset_oem=detail_row.oem_offset_front,
        offset_min=detail_row.min_offset_front,
        offset_max=detail_row.max_offset_front,
        wheel_size=detail_row.wheel_size_front,
        rim_diameter=detail_row.rim_diameter_front,
        rim_width=detail_row.rim_width_front,
        tire_size=detail_row.tire_size_front,
    )
    
    oem_rear = None
    is_staggered = False
    
    # 判断是否为 staggered（前后轮参数不同）
    if (detail_row.bolt_pattern_rear or detail_row.hub_bore_rear or 
        detail_row.rim_diameter_rear or detail_row.wheel_size_rear):
        is_staggered = True
        oem_rear = FitmentOEM(
            bolt_pattern=detail_row.bolt_pattern_rear,
            hub_bore=detail_row.hub_bore_rear,
            offset_oem=detail_row.oem_offset_rear,
            offset_min=detail_row.min_offset_rear,
            offset_max=detail_row.max_offset_rear,
            wheel_size=detail_row.wheel_size_rear,
            rim_diameter=detail_row.rim_diameter_rear,
            rim_width=detail_row.rim_width_rear,
            tire_size=detail_row.tire_size_rear,
        )
    
    # 解析 available_sizes（从 rim_diameter_front 提取 OEM 直径）
    available_sizes = []
    
    if detail_row.rim_diameter_front:
        # 提取直径数字（如 "18\"" -> 18）
        diameter_match = re.search(r'(\d+)', detail_row.rim_diameter_front)
        if diameter_match:
            oem_diameter = int(diameter_match.group(1))
            # 生成常见尺寸（OEM ±3，以及 OEM 本身）
            for d in range(max(15, oem_diameter - 3), min(22, oem_diameter + 4)):
                if d == oem_diameter:
                    label = f'{d}" (OEM)'
                else:
                    diff = d - oem_diameter
                    label = f'{d}" ({diff:+d})'
                available_sizes.append({"diameter": d, "label": label})
    
    # 如果没有解析到尺寸，添加一个 "All" 选项
    if not available_sizes:
        available_sizes.append({"diameter": None, "label": "All"})
    
    return FitmentResponse(
        vehicle_id=detail_row.vehicle_id,
        vehicle_name=detail_row.vehicle_name,
        year_id=detail_row.year_id,
        make_id=detail_row.make_id,
        model_id=detail_row.model_id,
        oem_front=oem_front,
        oem_rear=oem_rear,
        is_staggered=is_staggered,
        available_sizes=available_sizes,
    )



