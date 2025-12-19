/**
 * 地址簿相关 API 调用
 */
import { apiClient } from './client'

export interface Address {
  id: number
  user_id: number
  address_type: 'shipping' | 'billing'
  is_default: boolean
  first_name?: string
  last_name?: string
  company?: string
  phone_country_code?: string
  phone_number?: string
  country_code: string
  province?: string
  province_code?: string
  city?: string
  district?: string
  address_line1: string
  address_line2?: string
  postal_code?: string
  tax_region?: string
  shipping_zone?: string
  is_shippable: boolean
  deleted_at?: number
  createtime?: number
  updatetime?: number
}

export interface AddressListResponse {
  addresses: Address[]
  total: number
}

export interface CreateAddressRequest {
  address_type?: 'shipping' | 'billing'
  first_name?: string
  last_name?: string
  company?: string
  phone_country_code?: string
  phone_number?: string
  country_code: string
  province?: string
  province_code?: string
  city?: string
  district?: string
  address_line1: string
  address_line2?: string
  postal_code?: string
  tax_region?: string
  shipping_zone?: string
  is_shippable?: boolean
  is_default?: boolean
}

export interface UpdateAddressRequest {
  address_type?: 'shipping' | 'billing'
  first_name?: string
  last_name?: string
  company?: string
  phone_country_code?: string
  phone_number?: string
  country_code?: string
  province?: string
  province_code?: string
  city?: string
  district?: string
  address_line1?: string
  address_line2?: string
  postal_code?: string
  tax_region?: string
  shipping_zone?: string
  is_shippable?: boolean
  is_default?: boolean
}

/**
 * 获取地址列表
 */
export async function getAddresses(addressType?: 'shipping' | 'billing'): Promise<AddressListResponse> {
  const url = addressType ? `/addresses?address_type=${addressType}` : '/addresses'
  return apiClient.get<AddressListResponse>(url)
}

/**
 * 获取单个地址
 */
export async function getAddress(addressId: number): Promise<Address> {
  return apiClient.get<Address>(`/addresses/${addressId}`)
}

/**
 * 创建地址
 */
export async function createAddress(data: CreateAddressRequest): Promise<Address> {
  return apiClient.post<Address>('/addresses', data)
}

/**
 * 更新地址
 */
export async function updateAddress(addressId: number, data: UpdateAddressRequest): Promise<Address> {
  return apiClient.patch<Address>(`/addresses/${addressId}`, data)
}

/**
 * 设置默认地址
 */
export async function setDefaultAddress(addressId: number): Promise<Address> {
  return apiClient.post<Address>(`/addresses/${addressId}/set-default`, {})
}

/**
 * 删除地址（软删除）
 */
export async function deleteAddress(addressId: number): Promise<void> {
  return apiClient.delete(`/addresses/${addressId}`)
}
