// app/api/brands/[id]/route.ts
import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'

// 注意：Next 16 这里的 params 是 Promise
type ParamsPromise = { params: Promise<{ id: string }> }

function parseId(idStr: string) {
  const id = Number(idStr)
  if (!Number.isInteger(id)) return null
  return id
}

// GET /api/brands/:id  —— 编辑页加载
export async function GET(_req: NextRequest, { params }: ParamsPromise) {
  const { id: idStr } = await params
  const id = parseId(idStr)

  if (id === null) {
    return new Response(JSON.stringify({ message: 'Invalid id' }), {
      status: 400,
    })
  }

  const brand = await prisma.brand.findUnique({ where: { id } })

  if (!brand) {
    return new Response(JSON.stringify({ message: 'Not found' }), {
      status: 404,
    })
  }

  return Response.json(brand)
}

// PATCH /api/brands/:id  —— 保存编辑
export async function PATCH(req: NextRequest, { params }: ParamsPromise) {
  const { id: idStr } = await params
  const id = parseId(idStr)

  if (id === null) {
    return new Response(JSON.stringify({ message: 'Invalid id' }), {
      status: 400,
    })
  }

  const body = await req.json()

  const data: { name?: string; slug?: string } = {}
  if (body.name !== undefined) data.name = String(body.name).trim()
  if (body.slug !== undefined) data.slug = String(body.slug).trim()

  const brand = await prisma.brand.update({
    where: { id },
    data,
  })

  return Response.json(brand)
}

// DELETE /api/brands/:id  —— 列表删除
export async function DELETE(_req: NextRequest, { params }: ParamsPromise) {
  const { id: idStr } = await params
  const id = parseId(idStr)

  if (id === null) {
    return new Response(JSON.stringify({ message: 'Invalid id' }), {
      status: 400,
    })
  }

  await prisma.brand.delete({ where: { id } })

  return new Response(null, { status: 204 })
}
