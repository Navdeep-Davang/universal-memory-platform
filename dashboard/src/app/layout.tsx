import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { 
  LayoutDashboard, 
  Search, 
  AlertTriangle, 
  Settings, 
  Database,
  Github
} from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Universal Memory Dashboard",
  description: "Management interface for Universal Cognitive Memory Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-950 text-slate-50`}>
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col">
            <div className="p-6 border-b border-slate-800">
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                Memory Engine
              </h1>
              <p className="text-xs text-slate-500 mt-1">v1.0.0-alpha</p>
            </div>
            
            <nav className="flex-1 p-4 space-y-2">
              <Link href="/" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white group">
                <LayoutDashboard size={18} className="text-slate-500 group-hover:text-blue-400" />
                <span>Overview</span>
              </Link>
              <Link href="/query" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white group">
                <Search size={18} className="text-slate-500 group-hover:text-blue-400" />
                <span>Query Playbox</span>
              </Link>
              <Link href="/conflicts" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white group">
                <AlertTriangle size={18} className="text-slate-500 group-hover:text-amber-400" />
                <span>Conflicts</span>
              </Link>
              <Link href="/explorer" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white group">
                <Database size={18} className="text-slate-500 group-hover:text-blue-400" />
                <span>Graph Explorer</span>
              </Link>
            </nav>

            <div className="p-4 border-t border-slate-800 space-y-2">
              <Link href="/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white">
                <Settings size={18} className="text-slate-500" />
                <span>Settings</span>
              </Link>
              <a href="https://github.com" target="_blank" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors text-slate-300 hover:text-white">
                <Github size={18} className="text-slate-500" />
                <span>Documentation</span>
              </a>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto bg-slate-950 p-8">
            <div className="max-w-6xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
