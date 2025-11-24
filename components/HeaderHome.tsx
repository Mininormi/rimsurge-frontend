// components/HeaderHome.tsx
'use client'

import Link from 'next/link'
import { useState, useEffect, useRef } from 'react'

type MegaItemId = 'by-vehicle' | 'aftermarket' | 'oem'

const megaItems: {
  id: MegaItemId
  title: string
  subtitle: string
  highlightTitle: string
  highlightDesc: string
}[] = [
  {
    id: 'by-vehicle',
    title: 'By Vehicle',
    subtitle: 'Search wheels by exact fitment',
    highlightTitle: 'By Vehicle Search',
    highlightDesc:
      'Enter your vehicle details and only see wheels that clear your brakes, hub and fenders. No more guessing offsets or test-fitting.',
  },
  {
    id: 'aftermarket',
    title: 'Aftermarket Wheels',
    subtitle: 'Performance & aesthetic focused',
    highlightTitle: 'Aftermarket Wheels',
    highlightDesc:
      'Lightweight forged and flow-formed wheels curated for street and track use, with proper fitment for Canadian roads.',
  },
  {
    id: 'oem',
    title: 'OEM Wheels',
    subtitle: 'Original factory wheels',
    highlightTitle: 'OEM Replacement',
    highlightDesc:
      'Factory-spec replacement wheels for lease returns, winter setups or fixing curb damage without upsetting your dealer.',
  },
]

export default function HeaderHome() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [pinned, setPinned] = useState(false) // 是否“锁定”展开
  const [activeItemId, setActiveItemId] = useState<MegaItemId>('by-vehicle')

  const dropdownRef = useRef<HTMLDivElement | null>(null)
  const closeTimeoutRef = useRef<number | null>(null)

  // 滚动：控制透明 / 白底
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const clearCloseTimeout = () => {
    if (closeTimeoutRef.current !== null) {
      window.clearTimeout(closeTimeoutRef.current)
      closeTimeoutRef.current = null
    }
  }

  // 点击外部：关闭并取消锁定
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (!dropdownRef.current) return
      if (!dropdownRef.current.contains(e.target as Node)) {
        clearCloseTimeout()
        setMenuOpen(false)
        setPinned(false)
      }
    }

    if (menuOpen || pinned) {
      document.addEventListener('mousedown', handleClickOutside)
    } else {
      document.removeEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      clearCloseTimeout()
    }
  }, [menuOpen, pinned])

  const textColor = scrolled ? 'text-slate-900' : 'text-white'
  const buttonBase = 'rounded-full px-4 py-1.5 text-xs font-semibold transition-all duration-300'
  const buttonColor = scrolled ? 'bg-slate-900 text-white' : 'bg-white/90 text-slate-900'

  // 点击按钮：锁定 / 取消锁定
  const handleToggleClick = () => {
    if (pinned) {
      // 已锁定 → 关闭并解锁
      setPinned(false)
      setMenuOpen(false)
    } else {
      // 未锁定 → 打开并锁定
      setPinned(true)
      setMenuOpen(true)
    }
  }

  // 悬停进入：如果没锁定，就临时打开，并取消任何关闭定时器
  const handleMouseEnter = () => {
    clearCloseTimeout()
    if (!pinned) setMenuOpen(true)
  }

  // 悬停离开：如果没锁定，不是立刻关，而是延迟 200ms 关
  const handleMouseLeave = () => {
    if (pinned) return
    clearCloseTimeout()
    closeTimeoutRef.current = window.setTimeout(() => {
      setMenuOpen(false)
      closeTimeoutRef.current = null
    }, 200)
  }

  const activeItem = megaItems.find((item) => item.id === activeItemId) ?? megaItems[0]

  return (
    <header
      className={`
        fixed top-0 left-0 w-full z-50
        transition-colors duration-150
        ${
          scrolled
            ? 'bg-white/95 backdrop-blur border-b border-gray-200 shadow-md'
            : 'bg-transparent border-b border-transparent shadow-none'
        }
      `}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 transition-all duration-300">
        {/* 左侧：Logo + SHOP WHEELS mega menu */}
        <div className="flex items-center gap-18">
          <Link href="/" className="flex items-baseline gap-2">
            <span
              className={`text-xl font-black tracking-tight ${
                scrolled ? 'text-slate-900' : 'text-white'
              }`}
            >
              Rimsurge
            </span>
          </Link>

          <div
            className="relative"
            ref={dropdownRef}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          >
            <button
              type="button"
              onClick={handleToggleClick}
              className={`${buttonBase} ${buttonColor} flex items-center gap-2`}
            >
              <span>SHOP WHEELS</span>
              <span
                className={`text-[10px] transition-transform ${
                  menuOpen ? 'rotate-180' : 'rotate-0'
                }`}
              >
                ▼
              </span>
            </button>

            {menuOpen && (
              <div
                className="
                            absolute left-0 mt-3
                            w-[560px]
                            rounded-3xl
                            border border-white/10
                            bg-slate-900/80
                            text-slate-50
                            backdrop-blur-2xl
                            shadow-[0_24px_80px_rgba(15,23,42,0.65)]
                            p-6
                            flex gap-6
                            animate-[menuFadeIn_0.18s_ease-out]
                            "
              >
                {/* 左侧列表 */}
                <div className="w-1/2 flex flex-col gap-2 text-sm">
                  {megaItems.map((item) => {
                    const isActive = item.id === activeItemId
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onMouseEnter={() => setActiveItemId(item.id)}
                        onFocus={() => setActiveItemId(item.id)}
                        className={`
                          w-full text-left rounded-xl px-3 py-2
                          transition-colors
                          ${isActive ? 'bg-white/10 text-white' : 'text-slate-100 hover:bg-white/5'}
                        `}
                      >
                        <div className="text-sm font-semibold">{item.title}</div>
                        <div className="text-xs text-slate-300">{item.subtitle}</div>
                      </button>
                    )
                  })}

                  {/* 分隔线和“View all wheels”之类的 CTA 以后可以加 */}
                </div>

                {/* 右侧高亮卡片 */}
                <div className="w-1/2 rounded-2xl bg-white text-slate-900 shadow-sm p-5 flex flex-col justify-center">
                  <div className="flex items-center justify-center h-20 mb-3">
                    {/* 占位图标：以后可以换成轮毂图、icon 等 */}
                    <div className="h-10 w-10 rounded-full border border-slate-200 flex items-center justify-center">
                      <span className="text-xs text-slate-400">RS</span>
                    </div>
                  </div>

                  <div className="text-base font-semibold mb-1">{activeItem.highlightTitle}</div>
                  <div className="text-xs text-slate-600 leading-relaxed">
                    {activeItem.highlightDesc}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 右侧：导航 + 分割线 + 登录/购物车/结账 */}
        <div className="flex items-center gap-8 text-xs font-semibold tracking-[0.12em]">
          <nav
            className={`
              hidden md:flex
              gap-8 text-xs font-semibold tracking-[0.16em]
              ${textColor}
            `}
          >
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

          <div className="hidden md:block h-4 w-px bg-slate-400/40" />

          <div className={`hidden md:flex items-center gap-4 ${textColor}`}>
            <Link href="/login" className="hover:opacity-80">
              LOG IN
            </Link>
            <Link href="/cart" className="hover:opacity-80">
              CART (0)
            </Link>
            <Link href="/checkout" className="hover:opacity-80">
              CHECKOUT
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}
