import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DevAudit Dashboard',
  description: 'Local development environment audit dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
