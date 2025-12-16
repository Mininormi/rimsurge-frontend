// app/(app)/profile/page.tsx

'use client'

import { useAuth } from '@/lib/auth/context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="text-slate-600">加载中...</div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return null
  }

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="bg-slate-50 min-h-screen">
      <section className="mx-auto max-w-2xl px-4 py-12 md:py-16">
        {/* 页面标题 */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
            个人中心
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Manage your account settings
          </p>
        </div>

        {/* 用户信息卡片 */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
          <div className="space-y-6">
            {/* 用户基本信息 */}
            <div>
              <h2 className="text-lg font-semibold text-slate-900 mb-4">基本信息</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-slate-100">
                  <span className="text-sm font-medium text-slate-600">用户名</span>
                  <span className="text-sm text-slate-900">{user.username}</span>
                </div>
                {user.nickname && (
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-sm font-medium text-slate-600">昵称</span>
                    <span className="text-sm text-slate-900">{user.nickname}</span>
                  </div>
                )}
                {user.email && (
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-sm font-medium text-slate-600">邮箱</span>
                    <span className="text-sm text-slate-900">{user.email}</span>
                  </div>
                )}
                {user.mobile && (
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-sm font-medium text-slate-600">手机号</span>
                    <span className="text-sm text-slate-900">{user.mobile}</span>
                  </div>
                )}
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="pt-4 border-t border-slate-200">
              <button
                onClick={handleLogout}
                className="w-full rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-slate-900/30 transition hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2"
              >
                登出
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
