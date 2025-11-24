'use client'

import Link from 'next/link'
import { useEffect, useRef, useState } from 'react'

export default function HeaderDefault() {
  const [isHidden, setIsHidden] = useState(false)
  const lastScrollY = useRef(0)

  useEffect(() => {
    const handleScroll = () => {
      const current = window.scrollY

      if (current > lastScrollY.current && current > 50) {
        setIsHidden(true)
      } else {
        setIsHidden(false)
      }

      lastScrollY.current = current
    }

    handleScroll()
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const headerClass = [
    'fixed top-0 left-0 right-0 z-50',
    'bg-white/95 text-slate-900 border-b border-slate-200 backdrop-blur',
    'transition-all duration-300',
    isHidden ? '-translate-y-full' : 'translate-y-0',
  ].join(' ')

  return (
    <header className={headerClass}>
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 md:h-20 md:px-8">
        <Link href="/" className="text-lg font-semibold tracking-wide">
          Rimsurge · 东街车房
        </Link>

        <nav className="hidden gap-6 text-sm font-medium md:flex">
          <Link href="/aftermarket" className="hover:opacity-70">
            Aftermarket
          </Link>
          <Link href="/oem" className="hover:opacity-70">
            OEM
          </Link>
          <Link href="/about" className="hover:opacity-70">
            About
          </Link>
        </nav>

        <button className="inline-flex items-center justify-center rounded-full border px-3 py-1 text-xs md:hidden">
          Menu
        </button>
      </div>
    </header>
  )
}
