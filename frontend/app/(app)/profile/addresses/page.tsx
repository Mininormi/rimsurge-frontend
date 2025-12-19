// app/(app)/profile/addresses/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  getAddresses, 
  createAddress, 
  updateAddress, 
  deleteAddress, 
  setDefaultAddress,
  type Address,
  type CreateAddressRequest 
} from '@/lib/api/addresses'

// 常用国家代码（ISO 2位）
const COMMON_COUNTRIES = [
  { code: 'CA', name: 'Canada' },
  { code: 'US', name: 'United States' },
  { code: 'CN', name: 'China' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'AU', name: 'Australia' },
]

// 常用电话国家码
const COMMON_PHONE_CODES = [
  { code: '+1', name: 'Canada/US (+1)' },
  { code: '+86', name: 'China (+86)' },
  { code: '+44', name: 'UK (+44)' },
  { code: '+61', name: 'Australia (+61)' },
]

export default function AddressesPage() {
  const [addresses, setAddresses] = useState<Address[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingAddress, setEditingAddress] = useState<Address | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const router = useRouter()

  // 表单数据
  const [formData, setFormData] = useState<CreateAddressRequest>({
    address_type: 'shipping',
    first_name: '',
    last_name: '',
    company: '',
    phone_country_code: '+1',
    phone_number: '',
    country_code: 'CA',
    province: '',
    province_code: '',
    city: '',
    district: '',
    address_line1: '',
    address_line2: '',
    postal_code: '',
    is_default: false,
  })

  // 加载地址列表
  useEffect(() => {
    loadAddresses()
  }, [])

  const loadAddresses = async () => {
    try {
      setIsLoading(true)
      const response = await getAddresses()
      setAddresses(response.addresses)
    } catch (err: any) {
      console.error('加载地址失败:', err)
      alert(err.detail || '加载地址失败')
    } finally {
      setIsLoading(false)
    }
  }

  // 重置表单
  const resetForm = () => {
    setFormData({
      address_type: 'shipping',
      first_name: '',
      last_name: '',
      company: '',
      phone_country_code: '+1',
      phone_number: '',
      country_code: 'CA',
      province: '',
      province_code: '',
      city: '',
      district: '',
      address_line1: '',
      address_line2: '',
      postal_code: '',
      is_default: false,
    })
    setErrors({})
    setEditingAddress(null)
    setShowAddForm(false)
  }

  // 开始编辑
  const handleEdit = (address: Address) => {
    setEditingAddress(address)
    setFormData({
      address_type: address.address_type,
      first_name: address.first_name || '',
      last_name: address.last_name || '',
      company: address.company || '',
      phone_country_code: address.phone_country_code || '+1',
      phone_number: address.phone_number || '',
      country_code: address.country_code,
      province: address.province || '',
      province_code: address.province_code || '',
      city: address.city || '',
      district: address.district || '',
      address_line1: address.address_line1,
      address_line2: address.address_line2 || '',
      postal_code: address.postal_code || '',
      is_default: address.is_default,
    })
    setShowAddForm(true)
    setErrors({})
  }

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.country_code) {
      newErrors.country_code = '国家代码不能为空'
    }

    if (!formData.address_line1?.trim()) {
      newErrors.address_line1 = '地址行1不能为空'
    }

    if (!formData.first_name?.trim() && !formData.last_name?.trim()) {
      newErrors.name = '姓名至少填写一项'
    }

    if (formData.phone_country_code && !formData.phone_number?.trim()) {
      newErrors.phone_number = '电话号码不能为空'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // 提交表单（创建或更新）
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/e2a94ee8-06b0-4b36-a7b4-a3820ae00c2c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'addresses/page.tsx:151',message:'Submit form called',data:{isEditing:!!editingAddress,addressType:formData.address_type,isDefault:formData.is_default,addressesCount:addresses.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion

    try {
      // 检查该类型是否已有地址（创建时）
      if (!editingAddress) {
        const hasAddressesOfType = addresses.some(
          addr => addr.address_type === formData.address_type && !addr.deleted_at
        )
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e2a94ee8-06b0-4b36-a7b4-a3820ae00c2c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'addresses/page.tsx:158',message:'Check existing addresses',data:{hasAddressesOfType,addressType:formData.address_type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        
        // 如果没有地址，强制设为默认（后端会自动处理，但前端也要保持一致）
        if (!hasAddressesOfType) {
          formData.is_default = true
          
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/e2a94ee8-06b0-4b36-a7b4-a3820ae00c2c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'addresses/page.tsx:163',message:'Force default for first address',data:{addressType:formData.address_type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
          // #endregion
        }
      }

      if (editingAddress) {
        // 更新地址
        await updateAddress(editingAddress.id, formData)
      } else {
        // 创建地址
        await createAddress(formData)
      }
      
      await loadAddresses()
      resetForm()
    } catch (err: any) {
      console.error('保存地址失败:', err)
      alert(err.detail || '保存地址失败')
    }
  }

  // 设置默认地址
  const handleSetDefault = async (addressId: number) => {
    try {
      await setDefaultAddress(addressId)
      await loadAddresses()
    } catch (err: any) {
      console.error('设置默认地址失败:', err)
      alert(err.detail || '设置默认地址失败')
    }
  }

  // 删除地址
  const handleDelete = async (addressId: number) => {
    if (!confirm('确定要删除这个地址吗？')) {
      return
    }

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/e2a94ee8-06b0-4b36-a7b4-a3820ae00c2c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'addresses/page.tsx:187',message:'Delete address called',data:{addressId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion

    try {
      const result = await deleteAddress(addressId)
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e2a94ee8-06b0-4b36-a7b4-a3820ae00c2c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'addresses/page.tsx:193',message:'Delete address success',data:{addressId,result},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      // 204 No Content 表示成功，无需额外处理
      await loadAddresses()
    } catch (err: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e2a94ee8-06b0-4b36-a7b4-a3820ae00c2c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'addresses/page.tsx:199',message:'Delete address error',data:{addressId,error:err?.detail||err?.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      console.error('删除地址失败:', err)
      alert(err.detail || '删除地址失败')
    }
  }

  // 格式化地址显示
  const formatAddress = (address: Address): string => {
    const parts: string[] = []
    if (address.address_line1) parts.push(address.address_line1)
    if (address.address_line2) parts.push(address.address_line2)
    if (address.city) parts.push(address.city)
    if (address.province) parts.push(address.province)
    if (address.postal_code) parts.push(address.postal_code)
    if (address.country_code) {
      const country = COMMON_COUNTRIES.find(c => c.code === address.country_code)
      parts.push(country ? country.name : address.country_code)
    }
    return parts.join(', ')
  }

  // 格式化电话显示
  const formatPhone = (address: Address): string => {
    if (address.phone_country_code && address.phone_number) {
      return `${address.phone_country_code} ${address.phone_number}`
    }
    return address.phone_number || ''
  }

  // 格式化姓名显示
  const formatName = (address: Address): string => {
    const parts: string[] = []
    if (address.first_name) parts.push(address.first_name)
    if (address.last_name) parts.push(address.last_name)
    return parts.join(' ') || 'N/A'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900">地址管理</h2>
        <button
          onClick={() => {
            if (showAddForm) {
              resetForm()
            } else {
              resetForm()
              setShowAddForm(true)
            }
          }}
          className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-black transition-colors"
        >
          {showAddForm ? '取消' : '+ 添加新地址'}
        </button>
      </div>

      {/* 添加/编辑地址表单 */}
      {showAddForm && (
        <div className="border border-slate-200 rounded-lg p-6 bg-slate-50">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            {editingAddress ? '编辑地址' : '添加新地址'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 地址类型 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">地址类型 *</label>
              <select
                value={formData.address_type}
                onChange={(e) => setFormData({ ...formData, address_type: e.target.value as 'shipping' | 'billing' })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
              >
                <option value="shipping">收货地址</option>
                <option value="billing">账单地址</option>
              </select>
            </div>

            {/* 姓名 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">名</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 ${
                    errors.name ? 'border-red-300' : 'border-slate-300'
                  }`}
                  placeholder="First Name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">姓</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 ${
                    errors.name ? 'border-red-300' : 'border-slate-300'
                  }`}
                  placeholder="Last Name"
                />
              </div>
            </div>
            {errors.name && <p className="text-xs text-red-600">{errors.name}</p>}

            {/* 公司（可选） */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">公司（可选）</label>
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                placeholder="Company Name"
              />
            </div>

            {/* 电话 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">电话国家码</label>
                <select
                  value={formData.phone_country_code}
                  onChange={(e) => setFormData({ ...formData, phone_country_code: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                >
                  {COMMON_PHONE_CODES.map(code => (
                    <option key={code.code} value={code.code}>{code.name}</option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">电话号码 *</label>
                <input
                  type="tel"
                  value={formData.phone_number}
                  onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 ${
                    errors.phone_number ? 'border-red-300' : 'border-slate-300'
                  }`}
                  placeholder="Phone Number"
                />
                {errors.phone_number && <p className="text-xs text-red-600 mt-1">{errors.phone_number}</p>}
              </div>
            </div>

            {/* 国家 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">国家 *</label>
              <select
                value={formData.country_code}
                onChange={(e) => setFormData({ ...formData, country_code: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 ${
                  errors.country_code ? 'border-red-300' : 'border-slate-300'
                }`}
              >
                {COMMON_COUNTRIES.map(country => (
                  <option key={country.code} value={country.code}>{country.name}</option>
                ))}
              </select>
              {errors.country_code && <p className="text-xs text-red-600 mt-1">{errors.country_code}</p>}
            </div>

            {/* 省/州 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">省/州</label>
                <input
                  type="text"
                  value={formData.province}
                  onChange={(e) => setFormData({ ...formData, province: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                  placeholder="Province/State"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">省/州代码（可选）</label>
                <input
                  type="text"
                  value={formData.province_code}
                  onChange={(e) => setFormData({ ...formData, province_code: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                  placeholder="Province Code (e.g., ON, CA)"
                />
              </div>
            </div>

            {/* 城市和区县 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">城市</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                  placeholder="City"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">区/县（可选）</label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                  placeholder="District"
                />
              </div>
            </div>

            {/* 地址 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">地址行1 *</label>
              <input
                type="text"
                value={formData.address_line1}
                onChange={(e) => setFormData({ ...formData, address_line1: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 ${
                  errors.address_line1 ? 'border-red-300' : 'border-slate-300'
                }`}
                placeholder="Address Line 1"
              />
              {errors.address_line1 && <p className="text-xs text-red-600 mt-1">{errors.address_line1}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">地址行2（可选）</label>
              <input
                type="text"
                value={formData.address_line2}
                onChange={(e) => setFormData({ ...formData, address_line2: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                placeholder="Apartment, Suite, etc."
              />
            </div>

            {/* 邮编 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">邮编</label>
              <input
                type="text"
                value={formData.postal_code}
                onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                placeholder="Postal Code"
              />
            </div>

            {/* 设为默认地址 */}
            {(() => {
              // 检查该类型是否已有地址
              const hasAddressesOfType = addresses.some(
                addr => addr.address_type === formData.address_type && !addr.deleted_at
              )
              const isFirstAddress = !hasAddressesOfType && !editingAddress
              
              return (
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_default"
                    checked={formData.is_default || false}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                    disabled={isFirstAddress}
                    className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <label htmlFor="is_default" className={`text-sm ${isFirstAddress ? 'text-slate-400' : 'text-slate-700'}`}>
                    {isFirstAddress 
                      ? '设为默认地址（第一个地址将自动设为默认）'
                      : '设为默认地址'
                    }
                  </label>
                </div>
              )
            })()}

            {/* 提交按钮 */}
            <div className="flex gap-3">
              <button
                type="submit"
                className="px-6 py-2 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-black transition-colors"
              >
                {editingAddress ? '更新' : '保存'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 地址列表 - 按类型分组 */}
      {(() => {
        const shippingAddresses = addresses.filter(addr => addr.address_type === 'shipping')
        const billingAddresses = addresses.filter(addr => addr.address_type === 'billing')
        
        if (addresses.length === 0) {
          return (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">📍</div>
              <p className="text-slate-600 mb-4">暂无地址</p>
            </div>
          )
        }
        
        // 地址卡片组件
        const AddressCard = ({ address }: { address: Address }) => (
          <div
            key={address.id}
            className={`border rounded-lg p-6 ${
              address.is_default
                ? 'border-slate-900 bg-slate-50'
                : 'border-slate-200'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium text-slate-900">{formatName(address)}</span>
                  {formatPhone(address) && (
                    <span className="text-slate-600">{formatPhone(address)}</span>
                  )}
                  {address.is_default && (
                    <span className="px-2 py-1 text-xs font-medium bg-slate-900 text-white rounded">
                      默认
                    </span>
                  )}
                </div>
                {address.company && (
                  <p className="text-sm text-slate-600 mb-1">{address.company}</p>
                )}
                <p className="text-sm text-slate-600">{formatAddress(address)}</p>
              </div>
            </div>
            <div className="flex gap-3">
              {!address.is_default && (
                <button
                  onClick={() => handleSetDefault(address.id)}
                  className="px-4 py-2 text-sm font-medium text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  设为默认
                </button>
              )}
              <button
                onClick={() => handleEdit(address)}
                className="px-4 py-2 text-sm font-medium text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
              >
                编辑
              </button>
              <button
                onClick={() => handleDelete(address.id)}
                className="px-4 py-2 text-sm font-medium text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        )
        
        return (
          <div className="space-y-6">
            {/* 收货地址 */}
            {shippingAddresses.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">收货地址</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {shippingAddresses.map((address) => (
                    <AddressCard key={address.id} address={address} />
                  ))}
                </div>
              </div>
            )}
            
            {/* 账单地址 */}
            {billingAddresses.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">账单地址</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {billingAddresses.map((address) => (
                    <AddressCard key={address.id} address={address} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      })()}
    </div>
  )
}
