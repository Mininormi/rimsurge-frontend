// components/HeroSection.tsx
import HeroVideo from './HeroVideo'

export default function HeroSection() {
  return (
    <section className="relative h-[520px] md:h-[680px] w-full overflow-hidden flex items-center">
      {/* 背景视频 */}
      <HeroVideo />

      {/* 文案层 */}
      <div className="relative z-10 px-6 md:px-16 text-white max-w-xl space-y-4">
        <h1 className="text-4xl font-extrabold md:text-5xl">Rimsurge · Wheels Only</h1>

        <p className="text-lg text-slate-200">
          改装轮毂 & OEM 原厂轮毂，专注加拿大市场的专业轮毂商店。
        </p>

        <div className="mt-4 flex gap-4">
          <a
            href="/aftermarket"
            className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-black hover:bg-slate-200"
          >
            改装轮毂
          </a>

          <a
            href="/oem"
            className="rounded-full border border-slate-300 px-5 py-2 text-sm font-semibold text-white hover:border-white"
          >
            OEM 原厂轮毂
          </a>
        </div>
      </div>
    </section>
  )
}
