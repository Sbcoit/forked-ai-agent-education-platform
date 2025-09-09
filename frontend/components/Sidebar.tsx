"use client"

import Link from "next/link"
import { 
  Home, 
  Monitor, 
  Users, 
  Package, 
  User
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
          href="/cohorts" 
          className={`p-3 rounded-lg transition-colors ${
            currentPath === "/cohorts" 
              ? "bg-gray-700" 
              : "hover:bg-gray-800"
          }`}
        >
          <Users className="h-6 w-6 text-white" />
        </Link>
        <Link 
          href="/resources" 
          className={`p-3 rounded-lg transition-colors ${
            currentPath === "/resources" 
              ? "bg-gray-700" 
              : "hover:bg-gray-800"
          }`}
        >
          <Package className="h-6 w-6 text-white" />
        </Link>
      </nav>

      {/* Profile Icon at bottom */}
      <div className="mt-auto">
        <Link 
          href="/profile" 
          className={`p-3 rounded-lg transition-colors ${
            currentPath === "/profile" 
              ? "bg-gray-700" 
              : "hover:bg-gray-800"
          }`}
        >
          <User className="h-6 w-6 text-white" />
        </Link>
      </div>
    </div>
  )
}
