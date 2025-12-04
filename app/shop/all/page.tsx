// app/shop/all/page.tsx
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'All Wheels | Rimsurge',
}

type WheelCard = {
  id: string
  brand: string
  name: string
  originalPrice: string
  salePrice: string
  colours: string[]
  winterApproved?: boolean
}

const mockWheels: WheelCard[] = [
  {
    id: '1',
    brand: 'RAYS',
    name: 'TE37 Saga S-Plus',
    originalPrice: '$3,299',
    salePrice: '$2,899',
    colours: ['bg-slate-900', 'bg-zinc-200', 'bg-amber-700'],
    winterApproved: false,
  },
  {
    id: '2',
    brand: 'WedsSport',
    name: 'SA-25R Flow Form',
    originalPrice: '$2,499',
    salePrice: '$2,149',
    colours: ['bg-slate-900', 'bg-sky-900'],
    winterApproved: true,
  },
  {
    id: '3',
    brand: 'Enkei',
    name: 'NT03RR Track Spec',
    originalPrice: '$2,099',
    salePrice: '$1,799',
    colours: ['bg-slate-900'],
  },
  {
    id: '4',
    brand: 'Work',
    name: 'Emotion ZR10',
    originalPrice: '$2,899',
    salePrice: '$2,499',
    colours: ['bg-slate-900', 'bg-neutral-800', 'bg-slate-500'],
    winterApproved: true,
  },
  {
    id: '5',
    brand: 'Advan',
    name: 'GT Premium Version',
    originalPrice: '$3,599',
    salePrice: '$3,199',
    colours: ['bg-slate-900', 'bg-slate-500'],
  },
  {
    id: '6',
    brand: 'OZ Racing',
    name: 'Superturismo LM',
    originalPrice: '$2,399',
    salePrice: '$2,049',
    colours: ['bg-slate-900', 'bg-zinc-200'],
    winterApproved: true,
  },
]

export default function AllWheelsPage() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-10 md:px-6 md:py-12">
      <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
            All Wheels
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900 md:text-3xl">
            Browse every wheel we carry
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            Filter by size, finish, brand and technology. All pricing in CAD with duties included
            for Canadian delivery.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 text-xs text-slate-500">
          <span className="rounded-full border border-slate-200 px-3 py-1">
            Fitment review included
          </span>
          <span className="rounded-full border border-slate-200 px-3 py-1">
            Winter-approved options tagged
          </span>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[260px,minmax(0,1fr)]">
        {/* 左侧筛选栏 */}
        <aside className="space-y-4">
          {/* Size */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Size</span>
              <span className="text-xs font-normal text-slate-500">Select one</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="flex flex-wrap gap-2">
                {['17"', '18"', '19"', '20"', '21"'].map((size) => (
                  <button
                    key={size}
                    type="button"
                    className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-900 hover:bg-slate-100"
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          </details>

          {/* Colour */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Colour</span>
              <span className="text-xs font-normal text-slate-500">One finish</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="flex flex-wrap gap-2">
                {['Gloss Black', 'Matte Black', 'Gunmetal', 'Bronze', 'Silver'].map((label) => (
                  <button
                    key={label}
                    type="button"
                    className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-700 hover:border-slate-900 hover:bg-slate-100"
                  >
                    <span className="h-4 w-4 rounded-full border border-slate-300 bg-slate-900" />
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </details>

          {/* Brand */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Brand</span>
              <span className="text-xs font-normal text-slate-500">Pick one</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="space-y-2 text-sm text-slate-700">
                {['RAYS', 'WedsSport', 'Enkei', 'Work', 'Advan', 'OZ Racing'].map((brand) => (
                  <label key={brand} className="flex cursor-pointer items-center gap-2">
                    <input
                      type="radio"
                      name="brand"
                      className="h-3.5 w-3.5 border-slate-300 text-slate-900 focus:ring-slate-900"
                    />
                    <span>{brand}</span>
                  </label>
                ))}
              </div>
            </div>
          </details>

          {/* Technology */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Technology</span>
              <span className="text-xs font-normal text-slate-500">Construction</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="space-y-2 text-sm text-slate-700">
                {['Cast', 'Flow Formed', 'Forged 1-piece', 'Forged 2-piece'].map((tech) => (
                  <label key={tech} className="flex cursor-pointer items-center gap-2">
                    <input
                      type="radio"
                      name="technology"
                      className="h-3.5 w-3.5 border-slate-300 text-slate-900 focus:ring-slate-900"
                    />
                    <span>{tech}</span>
                  </label>
                ))}
              </div>
            </div>
          </details>

          {/* Offset 范围 */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Offset (ET)</span>
              <span className="text-xs font-normal text-slate-500">Min – Max</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="Min"
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-800 outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
                />
                <input
                  type="number"
                  placeholder="Max"
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-800 outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
                />
              </div>
              <p className="mt-2 text-[11px] text-slate-500">Example: 30 – 55</p>
            </div>
          </details>

          {/* Width */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Width</span>
              <span className="text-xs font-normal text-slate-500">One width</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="flex flex-wrap gap-2">
                {['7.5"', '8"', '8.5"', '9"', '9.5"', '10"'].map((w) => (
                  <button
                    key={w}
                    type="button"
                    className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-900 hover:bg-slate-100"
                  >
                    {w}
                  </button>
                ))}
              </div>
            </div>
          </details>

          {/* Winter Approved */}
          <details className="rounded-2xl border border-slate-200 bg-white" open>
            <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-semibold text-slate-900">
              <span>Winter Approved</span>
            </summary>
            <div className="border-t border-slate-200 px-4 py-3">
              <div className="space-y-2 text-sm text-slate-700">
                <label className="flex cursor-pointer items-center gap-2">
                  <input
                    type="radio"
                    name="winter"
                    defaultChecked
                    className="h-3.5 w-3.5 border-slate-300 text-slate-900 focus:ring-slate-900"
                  />
                  <span>All wheels</span>
                </label>
                <label className="flex cursor-pointer items-center gap-2">
                  <input
                    type="radio"
                    name="winter"
                    className="h-3.5 w-3.5 border-slate-300 text-slate-900 focus:ring-slate-900"
                  />
                  <span>Winter approved only</span>
                </label>
              </div>
            </div>
          </details>
        </aside>

        {/* 右侧内容区 */}
        <div className="space-y-6">
          {/* 选中车型卡片（图1风格） */}
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
            <div className="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-sm text-white">
                🚗
              </span>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  OEM Info
                </p>
                <p className="text-sm font-semibold text-slate-900">
                  2015 Porsche Cayman Base – 20&quot; option
                </p>
              </div>
            </div>

            <div className="overflow-x-auto px-5 py-4">
              <table className="min-w-full text-left text-xs text-slate-700">
                <thead className="border-b border-slate-200 text-[11px] uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="py-2 pr-4">OEM Wheels</th>
                    <th className="py-2 pr-4">Bolt Pattern</th>
                    <th className="py-2 pr-4">OEM Offset</th>
                    <th className="py-2 pr-4">Wheel Size</th>
                    <th className="py-2 pr-4">Hubbore</th>
                    <th className="py-2 pr-4">Tire Size</th>
                    <th className="py-2 pr-4">Load Index</th>
                    <th className="py-2 pr-4">Speed Rating</th>
                    <th className="py-2 pr-4">PSI</th>
                    <th className="py-2 pr-4">TPMS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-[11px]">
                  <tr>
                    <td className="py-2 pr-4 font-medium text-slate-900">Front</td>
                    <td className="py-2 pr-4">5x130</td>
                    <td className="py-2 pr-4">57 mm</td>
                    <td className="py-2 pr-4">20x8</td>
                    <td className="py-2 pr-4">71.5</td>
                    <td className="py-2 pr-4">235/35R20</td>
                    <td className="py-2 pr-4">88</td>
                    <td className="py-2 pr-4">Y</td>
                    <td className="py-2 pr-4">30</td>
                    <td className="py-2 pr-4">Direct</td>
                  </tr>
                  <tr>
                    <td className="py-2 pr-4 font-medium text-slate-900">Rear</td>
                    <td className="py-2 pr-4">5x130</td>
                    <td className="py-2 pr-4">45 mm</td>
                    <td className="py-2 pr-4">20x9.5</td>
                    <td className="py-2 pr-4">71.5</td>
                    <td className="py-2 pr-4">265/35R20</td>
                    <td className="py-2 pr-4">95</td>
                    <td className="py-2 pr-4">Y</td>
                    <td className="py-2 pr-4">30</td>
                    <td className="py-2 pr-4">Direct</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 可选尺寸（图2风格） */}
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Available Sizes
                </p>
                <p className="mt-1 text-xs text-slate-600">
                  Upsize / downsize around the OEM 20&quot; package.
                </p>
              </div>
            </div>
            <div className="px-5 py-4">
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-4 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-900"
                >
                  17&quot; (-3)
                </button>
                <button
                  type="button"
                  className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-4 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-900"
                >
                  19&quot; (-1)
                </button>
                <button
                  type="button"
                  className="inline-flex items-center justify-center rounded-full bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white shadow-md shadow-slate-900/30"
                >
                  20&quot; (OEM)
                </button>
                <button
                  type="button"
                  className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-slate-50 px-4 py-1.5 text-xs font-medium text-slate-700 hover:border-slate-900"
                >
                  All
                </button>
              </div>
            </div>
          </div>

          {/* All Wheels 列表 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-900">
                All Wheels ·{' '}
                <span className="font-normal text-slate-500">
                  Showing {mockWheels.length} of 120+
                </span>
              </p>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span>Sort by</span>
                <select className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700">
                  <option>Recommended</option>
                  <option>Price: low to high</option>
                  <option>Price: high to low</option>
                  <option>Newest</option>
                </select>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {mockWheels.map((wheel) => (
                <article
                  key={wheel.id}
                  className="flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                >
                  {/* 主图（未来替换成真实图片 & 详情链接） */}
                  <Link href="#" className="block">
                    <div className="aspect-square w-full bg-slate-100" />
                  </Link>

                  <div className="flex flex-1 flex-col gap-3 px-4 py-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                          {wheel.brand}
                        </p>
                        <h3 className="mt-1 text-sm font-semibold text-slate-900">{wheel.name}</h3>
                      </div>
                      {wheel.winterApproved && (
                        <span className="inline-flex items-center rounded-full bg-sky-50 px-2 py-0.5 text-[11px] font-medium text-sky-700">
                          Winter Approved
                        </span>
                      )}
                    </div>

                    <div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-sm font-semibold text-slate-900">
                          {wheel.salePrice} CAD
                        </span>
                        <span className="text-xs text-slate-400 line-through">
                          {wheel.originalPrice}
                        </span>
                      </div>
                      <p className="mt-1 text-[11px] text-slate-500">
                        Price per wheel · Duties included for Canada.
                      </p>
                    </div>

                    {/* 颜色方块 */}
                    <div className="mt-1 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-1.5">
                        {wheel.colours.map((cls, idx) => (
                          <span
                            key={`${wheel.id}-colour-${idx}`}
                            className={`h-4 w-4 rounded-[5px] border border-slate-200 ${cls}`}
                          />
                        ))}
                      </div>
                      <span className="text-[11px] text-slate-500">Multiple finishes</span>
                    </div>

                    {/* 底部按钮 */}
                    <div className="mt-2 flex items-center justify-between">
                      <Link
                        href="#"
                        className="text-xs font-semibold text-slate-900 underline-offset-2 hover:underline"
                      >
                        Details &amp; Preview
                      </Link>
                      <button
                        type="button"
                        className="inline-flex items-center justify-center rounded-full bg-slate-900 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-black"
                      >
                        Fitment Check
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {/* 分页 */}
            <nav className="mt-4 flex items-center justify-between border-t border-slate-200 pt-4 text-xs text-slate-600">
              <button
                type="button"
                className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1.5 hover:border-slate-900"
              >
                Previous
              </button>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-[11px] font-semibold text-white"
                >
                  1
                </button>
                <button
                  type="button"
                  className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-[11px] text-slate-700 hover:border-slate-900"
                >
                  2
                </button>
                <button
                  type="button"
                  className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-[11px] text-slate-700 hover:border-slate-900"
                >
                  3
                </button>
                <span className="px-1 text-[11px] text-slate-400">…</span>
                <button
                  type="button"
                  className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-[11px] text-slate-700 hover:border-slate-900"
                >
                  8
                </button>
              </div>
              <button
                type="button"
                className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1.5 hover:border-slate-900"
              >
                Next
              </button>
            </nav>
          </div>
        </div>
      </div>
    </section>
  )
}
