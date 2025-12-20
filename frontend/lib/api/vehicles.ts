/**
 * 车辆数据 API（基于 raw 表结构）
 * 游客可访问，无需鉴权
 */
import { apiClient } from './client'

export interface Year {
  id: number
  year: number
}

export interface Make {
  id: number
  name: string
}

export interface Model {
  id: number
  make_id: number
  name: string
}

export interface Vehicle {
  vehicle_id: string
  vehicle_name: string | null
}

export interface FitmentOEM {
  bolt_pattern: string | null
  hub_bore: string | null
  offset_oem: string | null
  offset_min: string | null
  offset_max: string | null
  wheel_size: string | null
  rim_diameter: string | null
  rim_width: string | null
  tire_size: string | null
}

export interface Fitment {
  vehicle_id: string
  vehicle_name: string | null
  year_id: number
  make_id: number
  model_id: number
  oem_front: FitmentOEM | null
  oem_rear: FitmentOEM | null
  is_staggered: boolean
  available_sizes: Array<{ diameter: number | null; label: string }>
}

/**
 * 获取年份列表
 */
export async function getYears(): Promise<Year[]> {
  return apiClient.get<Year[]>('/vehicles/years')
}

/**
 * 获取品牌列表
 */
export async function getMakes(year?: number): Promise<Make[]> {
  const url = year ? `/vehicles/makes?year=${year}` : '/vehicles/makes'
  return apiClient.get<Make[]>(url)
}

/**
 * 获取型号列表
 */
export async function getModels(makeId: number, year?: number): Promise<Model[]> {
  const url = year
    ? `/vehicles/models?make_id=${makeId}&year=${year}`
    : `/vehicles/models?make_id=${makeId}`
  return apiClient.get<Model[]>(url)
}

/**
 * 获取车辆列表
 */
export async function getVehicles(
  year?: number,
  makeId?: number,
  modelId?: number
): Promise<Vehicle[]> {
  const params = new URLSearchParams()
  if (year) params.append('year', year.toString())
  if (makeId) params.append('make_id', makeId.toString())
  if (modelId) params.append('model_id', modelId.toString())
  
  const queryString = params.toString()
  return apiClient.get<Vehicle[]>(`/vehicles/vehicles${queryString ? `?${queryString}` : ''}`)
}

/**
 * 获取车辆适配参数
 */
export async function getFitment(vehicleId: string): Promise<Fitment> {
  return apiClient.get<Fitment>(`/vehicles/fitment?vehicle_id=${vehicleId}`)
}


