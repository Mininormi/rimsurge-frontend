// components/HeroSection.tsx
import HeroVideo from './HeroVideo'
import Image from 'next/image'

export default function HeroSection() {
  return (
    <section className="relative h-[520px] md:h-[680px] w-full overflow-hidden flex items-center">
      {/* 背景视频 */}
      <HeroVideo />

      {/* 文案层 */}
      <div className="absolute left-0 right-0 top-[30%] mx-auto max-w-6xl px-4 select-none">
        <div className="space-y-4">
          {/* 主标题 */}
          <h1
            className="
              text-white 
              font-black 
              tracking-tight 
              leading-[1.08]
              text-4xl md:text-6xl
              drop-shadow-[0_4px_18px_rgba(0,0,0,0.55)]
            "
          >
            Built for Drivers.
            <br />
            <span className="text-white/90">Priced for Real Life.</span>
          </h1>

          {/* 加拿大标语 Badge */}
          <div
            className="
              inline-flex items-center gap-2
              rounded-full
              bg-white/92
              px-4 py-1.5
              text-[13px] md:text-sm
              font-semibold
              text-slate-900
              shadow-[0_8px_26px_rgba(15,23,42,0.35)]
            "
          >
            <Image
              src="https://cdn-icons-png.freepik.com/256/12363/12363960.png"
              alt="Canada Flag"
              width={18}
              height={18}
              className="rounded-sm"
            />

            <span>A New Canadian Way to Upgrade — Same Quality, Smarter Costs.</span>
          </div>
        </div>
      </div>
    </section>
  )
}
