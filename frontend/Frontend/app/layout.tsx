import './globals.css';
import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'RajOS — Your Personal AI Operating System',
  description:
    'An intelligent workspace that remembers, reasons, and acts. AI agents, long-term memory, RAG knowledge intelligence, and multi-LLM integration in one operating system.',
  keywords: [
    'AI Operating System',
    'AI Agents',
    'RAG',
    'Long-term Memory',
    'LLM',
    'RajOS',
  ],
  themeColor: '#0a0c12',
  openGraph: {
    title: 'RajOS — Your Personal AI Operating System',
    description:
      'An intelligent workspace that remembers, reasons, and acts.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'RajOS — Your Personal AI Operating System',
    description: 'An intelligent workspace that remembers, reasons, and acts.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrains.variable} font-sans antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
