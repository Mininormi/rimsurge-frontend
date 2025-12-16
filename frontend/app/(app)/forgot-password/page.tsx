// app/(app)/forgot-password/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { sendVerificationCode, resetPassword } from '@/lib/api/auth'
import { useAuth } from '@/lib/auth/context'

type Step = 'email' | 'reset' | 'success'

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSendingCode, setIsSendingCode] = useState(false)
  const [isResetting, setIsResetting] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const router = useRouter()
  const { isAuthenticated, isLoading: authLoading } = useAuth()

  // 如果已登录，重定向到首页
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace('/')
    }
  }, [isAuthenticated, authLoading, router])

  // 倒计时效果
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  // 加载中时显示加载状态，避免闪烁
  if (authLoading) {
    return (
      <div className="bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="text-slate-600">加载中...</div>
      </div>
    )
  }

  // 如果已登录，不渲染页面（等待重定向）
  if (isAuthenticated) {
    return null
  }

  /**
   * 发送验证码
   */
  const handleSendCode = async () => {
    if (!email.trim()) {
      setErrors({ email: '请先输入邮箱地址' })
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setErrors({ email: '请输入有效的邮箱地址' })
      return
    }

    setIsSendingCode(true)
    setErrors({})

    try {
      const response = await sendVerificationCode(email.trim(), 'reset')
      // 使用后端返回的冷却时间，如果没有则使用默认60秒
      setCountdown(response.rate_limit_seconds || 60)
      // 发送成功，进入下一步
      setStep('reset')
    } catch (err: any) {
      // 显示后端返回的错误信息（反枚举保护：统一消息）
      const errorMessage = err.detail || '如果该邮箱可用，你将收到邮件/验证码'
      setErrors({ email: errorMessage })
      // 如果是限流错误，设置倒计时
      if (err.status === 429) {
        setCountdown(60)
      }
    } finally {
      setIsSendingCode(false)
    }
  }

  /**
   * 重置密码
   */
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()

    // 验证表单
    const newErrors: Record<string, string> = {}
    if (!code.trim()) {
      newErrors.code = '请输入验证码'
    } else if (!/^\d{6}$/.test(code.trim())) {
      newErrors.code = '验证码必须是6位数字'
    }

    if (!newPassword) {
      newErrors.newPassword = '请输入新密码'
    } else if (newPassword.length < 6) {
      newErrors.newPassword = '密码长度至少6位'
    }

    if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setIsResetting(true)
    setErrors({})

    try {
      await resetPassword({
        email: email.trim(),
        code: code.trim(),
        new_password: newPassword,
      })
      // 重置成功，进入成功页面
      setStep('success')
    } catch (err: any) {
      // 显示错误信息
      const errorMessage = err.detail || '重置密码失败，请稍后再试'
      if (errorMessage.includes('验证码')) {
        setErrors({ code: errorMessage })
      } else {
        setErrors({ submit: errorMessage })
      }
    } finally {
      setIsResetting(false)
    }
  }

  /**
   * 返回第一步（重新输入邮箱）
   */
  const handleBackToEmail = () => {
    setStep('email')
    setCode('')
    setNewPassword('')
    setConfirmPassword('')
    setErrors({})
    setCountdown(0)
  }

  return (
    <div className="bg-slate-50 min-h-screen">
      <section className="mx-auto max-w-md px-4 py-12 md:py-16">
        {/* 页面标题 */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
            {step === 'success' ? '密码重置成功' : '忘记密码'}
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            {step === 'success'
              ? '请使用新密码登录'
              : '通过邮箱验证码重置您的密码'}
          </p>
        </div>

        {/* Step 1: 输入邮箱并发送验证码 */}
        {step === 'email' && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
            <form onSubmit={(e) => { e.preventDefault(); handleSendCode(); }} className="space-y-5">
              {errors.email && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
                  {errors.email}
                </div>
              )}

              <div>
                <label htmlFor="email" className="mb-1.5 block text-sm font-semibold text-slate-900">
                  邮箱地址 *
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (errors.email) setErrors({ ...errors, email: '' })
                  }}
                  required
                  className={`w-full rounded-lg border ${
                    errors.email ? 'border-red-300' : 'border-slate-300'
                  } bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-colors focus:border-slate-900 focus:ring-2 focus:ring-slate-900/20`}
                  placeholder="your.email@example.com"
                />
              </div>

              <button
                type="submit"
                disabled={isSendingCode || countdown > 0}
                className="w-full rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-slate-900/30 transition hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSendingCode
                  ? '发送中...'
                  : countdown > 0
                  ? `发送验证码 (${countdown}秒)`
                  : '发送验证码'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link href="/login" className="text-sm font-semibold text-slate-900 hover:text-slate-700">
                返回登录
              </Link>
            </div>
          </div>
        )}

        {/* Step 2: 输入验证码和新密码 */}
        {step === 'reset' && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
            <form onSubmit={handleResetPassword} className="space-y-5">
              {errors.submit && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
                  {errors.submit}
                </div>
              )}

              {/* 邮箱显示（只读） */}
              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-900">
                  邮箱地址
                </label>
                <div className="w-full rounded-lg border border-slate-300 bg-slate-50 px-4 py-2.5 text-sm text-slate-600">
                  {email}
                </div>
                <button
                  type="button"
                  onClick={handleBackToEmail}
                  className="mt-2 text-xs text-slate-600 hover:text-slate-900 underline"
                >
                  修改邮箱
                </button>
              </div>

              {/* 验证码输入 */}
              <div>
                <label htmlFor="code" className="mb-1.5 block text-sm font-semibold text-slate-900">
                  验证码 *
                </label>
                <input
                  id="code"
                  type="text"
                  value={code}
                  onChange={(e) => {
                    setCode(e.target.value.replace(/\D/g, '').slice(0, 6))
                    if (errors.code) setErrors({ ...errors, code: '' })
                  }}
                  required
                  maxLength={6}
                  className={`w-full rounded-lg border ${
                    errors.code ? 'border-red-300' : 'border-slate-300'
                  } bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-colors focus:border-slate-900 focus:ring-2 focus:ring-slate-900/20`}
                  placeholder="6位验证码"
                />
                {errors.code && (
                  <p className="mt-1 text-xs text-red-600">{errors.code}</p>
                )}
              </div>

              {/* 新密码输入 */}
              <div>
                <label htmlFor="newPassword" className="mb-1.5 block text-sm font-semibold text-slate-900">
                  新密码 *
                </label>
                <div className="relative">
                  <input
                    id="newPassword"
                    type={showPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value)
                      if (errors.newPassword) setErrors({ ...errors, newPassword: '' })
                    }}
                    required
                    className={`w-full rounded-lg border ${
                      errors.newPassword ? 'border-red-300' : 'border-slate-300'
                    } bg-white px-4 py-2.5 pr-10 text-sm text-slate-900 shadow-sm outline-none transition-colors focus:border-slate-900 focus:ring-2 focus:ring-slate-900/20`}
                    placeholder="至少6位"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                        />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                    )}
                  </button>
                </div>
                {errors.newPassword && (
                  <p className="mt-1 text-xs text-red-600">{errors.newPassword}</p>
                )}
                <p className="mt-1 text-xs text-slate-500">至少6位字符</p>
              </div>

              {/* 确认密码输入 */}
              <div>
                <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-semibold text-slate-900">
                  确认密码 *
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value)
                      if (errors.confirmPassword) setErrors({ ...errors, confirmPassword: '' })
                    }}
                    required
                    className={`w-full rounded-lg border ${
                      errors.confirmPassword ? 'border-red-300' : 'border-slate-300'
                    } bg-white px-4 py-2.5 pr-10 text-sm text-slate-900 shadow-sm outline-none transition-colors focus:border-slate-900 focus:ring-2 focus:ring-slate-900/20`}
                    placeholder="再次输入密码"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {showConfirmPassword ? (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                        />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="mt-1 text-xs text-red-600">{errors.confirmPassword}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={isResetting}
                className="w-full rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-slate-900/30 transition hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isResetting ? '重置中...' : '重置密码'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={handleBackToEmail}
                className="text-sm font-semibold text-slate-900 hover:text-slate-700"
              >
                返回上一步
              </button>
            </div>
          </div>
        )}

        {/* Step 3: 成功提示 */}
        {step === 'success' && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
            <div className="text-center space-y-6">
              <div className="mx-auto w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-slate-900 mb-2">密码重置成功</h2>
                <p className="text-sm text-slate-600">
                  您的密码已成功重置，请使用新密码登录
                </p>
              </div>

              <Link
                href="/login"
                className="inline-block w-full rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-slate-900/30 transition hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2"
              >
                前往登录
              </Link>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
