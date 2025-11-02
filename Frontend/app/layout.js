import './globals.css'

export const metadata = {
  title: 'Meeting Summarizer',
  description: 'AI-powered meeting transcription and summarization',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
