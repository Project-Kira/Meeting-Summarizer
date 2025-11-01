import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Project Keera - 30 Days, 30 AI Solutions',
  description: 'A team challenge to build 30 AI solutions in 30 days, exploring how AI can transform multiple industries.',
  keywords: 'AI, artificial intelligence, innovation, technology, social media, education, healthcare, real estate',
} 

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}