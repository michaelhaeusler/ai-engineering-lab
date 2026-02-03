import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "InsuranceLens - AI-powered German Health Insurance Assistant",
  description: "Understand your German health insurance policy with AI-powered analysis and expert guidance",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gradient-to-br from-gray-50 via-gray-50 to-stone-100`}
      >
        <div className="min-h-screen">
          <header className="bg-white/80 backdrop-blur-xl shadow-sm border-b sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-5">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <span className="text-white font-bold text-lg">IL</span>
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900 tracking-tight">
                      InsuranceLens
                    </h1>
                    <p className="text-xs text-gray-500 hidden sm:block">
                      KI-gestützte Policenanalyse
                    </p>
                  </div>
                </div>
                <div className="hidden md:block">
                  <span className="text-sm text-gray-600 bg-gray-100 px-4 py-2 rounded-full">
                    🇩🇪 Deutsche Krankenversicherungen
                  </span>
                </div>
              </div>
            </div>
          </header>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {children}
          </main>
          <footer className="bg-white/50 backdrop-blur-sm border-t mt-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="text-center text-sm text-gray-500">
                <p>© 2025 InsuranceLens. Entwickelt mit ❤️ für transparente Versicherungen.</p>
                <p className="mt-2 text-xs">Ihre Daten werden privat und sicher verarbeitet.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
