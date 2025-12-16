// \components\HeaderRightNav.tsx

'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth/context'

export function HeaderRightNav({ textColor }: { textColor: string }) {
  const { isAuthenticated, user } = useAuth()
  // TODO: 后续可以从购物车 Context 或 API 获取实际购物车数量
  const cartCount = 0

  return (
    <div className="flex items-center gap-4 text-xs font-semibold tracking-[0.12em]">
      <nav className={`hidden md:flex gap-8 text-xs font-semibold tracking-[0.16em] ${textColor}`}>
        <Link href="/gallery" className="hover:opacity-80">
          GALLERY
        </Link>
        <Link href="/about" className="hover:opacity-80">
          ABOUT
        </Link>
        <Link href="/support" className="hover:opacity-80">
          SUPPORT
        </Link>
      </nav>

      <div className="hidden h-4 w-px bg-slate-400/40 md:block" />

      <div className={`hidden items-center gap-4 md:flex ${textColor}`}>
        {isAuthenticated ? (
          <>
            <Link href="/cart" className="hover:opacity-80">
              CART ({cartCount})
            </Link>
            <Link href="/profile" className="hover:opacity-80">
              个人中心
            </Link>
          </>
        ) : (
          <Link href="/login" className="hover:opacity-80">
            LOG IN
          </Link>
        )}
      </div>
    </div>
  )
}
