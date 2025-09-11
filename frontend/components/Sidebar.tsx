"use client"

import Link from "next/link"
import { 
  Home, 
  Monitor, 
  MessageSquare
} from "lucide-react"

interface SidebarProps {
  currentPath?: string
}

export default function Sidebar({ currentPath = "/dashboard" }: SidebarProps) {
  return (
    <div className="w-20 bg-black flex flex-col items-center py-6 fixed left-0 top-0 h-full z-50">
      {/* Logo */}
      <div className="mb-8">
        <img src="/n-aiblelogo.png" alt="Logo" className="w-18 h-10" />
      </div>

      {/* Navigation Icons */}
      <nav className="flex flex-col space-y-4">
        <Link 
          href="/dashboard" 
          className={`p-3 rounded-lg transition-colors ${
            currentPath === "/dashboard" 
              ? "bg-gray-700" 
              : "hover:bg-gray-800"
          }`}
        >
          <Home className="h-6 w-6 text-white" />
        </Link>
        <Link 
          href="/simulation-builder" 
          className={`p-3 rounded-lg transition-colors ${
            currentPath === "/simulation-builder" 
              ? "bg-gray-700" 
              : "hover:bg-gray-800"
          }`}
        >
          <Monitor className="h-6 w-6 text-white" />
        </Link>
        <Link 
          href="/chat-box" 
          className={`p-3 rounded-lg transition-colors ${
            currentPath === "/chat-box" 
              ? "bg-gray-700" 
              : "hover:bg-gray-800"
          }`}
        >
          <MessageSquare className="h-6 w-6 text-white" />
        </Link>
      </nav>

    </div>
  )
}
