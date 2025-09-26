"use client"

import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { 
  Home, 
  FileText, 
  Users,
  Play,
  BookOpen,
  Bell,
  Settings,
  MessageSquare
} from "lucide-react"

interface RoleBasedSidebarProps {
  currentPath?: string
}

export default function RoleBasedSidebar({ currentPath = "/dashboard" }: RoleBasedSidebarProps) {
  const { user } = useAuth()
  
  // Determine user role and get appropriate navigation
  const isProfessor = user?.role === 'professor' || user?.role === 'admin'
  const isStudent = user?.role === 'student'
  
  // Professor navigation items
  const professorNavItems = [
    { href: "/professor/dashboard", icon: Home, label: "Dashboard" },
    { href: "/professor/cohorts", icon: Users, label: "Cohorts" },
    { href: "/professor/simulation-builder", icon: FileText, label: "Simulation Builder" },
    { href: "/professor/test-simulations", icon: MessageSquare, label: "Test Simulations" },
    { href: "/professor/notifications", icon: Bell, label: "Notifications" },
  ]
  
  // Student navigation items
  const studentNavItems = [
    { href: "/student/dashboard", icon: Home, label: "Dashboard" },
    { href: "/student/simulations", icon: Play, label: "Simulations" },
    { href: "/student/my-cohorts", icon: BookOpen, label: "My Cohorts" },
    { href: "/student/notifications", icon: Bell, label: "Notifications" },
    { href: "/student/chat", icon: MessageSquare, label: "Chat" },
  ]
  
  // Get navigation items based on role
  const navItems = isProfessor ? professorNavItems : studentNavItems
  
  return (
    <div className="w-20 bg-black flex flex-col items-center py-6 fixed left-0 top-0 h-full z-50">
      {/* Logo */}
      <div className="mb-8">
        <img src="/n-aiblelogo.png" alt="Logo" className="w-18 h-10" />
      </div>

      {/* Navigation Icons */}
      <nav className="flex flex-col space-y-4">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPath === item.href
          
          return (
            <Link 
              key={item.href}
              href={item.href} 
              className={`p-3 rounded-lg transition-colors group relative ${
                isActive 
                  ? "bg-gray-700" 
                  : "hover:bg-gray-800"
              }`}
              title={item.label}
            >
              <Icon className="h-6 w-6 text-white" />
              
              {/* Tooltip */}
              <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                {item.label}
              </div>
            </Link>
          )
        })}
      </nav>
      
      {/* User Role Indicator */}
      <div className="mt-auto mb-4">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
          isProfessor 
            ? "bg-blue-600 text-white" 
            : isStudent 
            ? "bg-green-600 text-white" 
            : "bg-gray-600 text-white"
        }`}>
          {isProfessor ? "P" : isStudent ? "S" : "U"}
        </div>
      </div>
    </div>
  )
}
