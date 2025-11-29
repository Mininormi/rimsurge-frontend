// app/admin/layout.tsx
import type { ReactNode } from 'react'

// 全局样式放在“非 client”的 layout 里
import '@refinedev/antd/dist/reset.css'
import 'antd/dist/reset.css'

import { AdminApp } from './AdminApp'

export default function AdminLayout({ children }) {
  return <AdminApp>{children}</AdminApp>
}
