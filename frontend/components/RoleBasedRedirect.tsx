"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

interface RoleBasedRedirectProps {
  children: React.ReactNode
}

export default function RoleBasedRedirect({ children }: RoleBasedRedirectProps) {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && user) {
      // If user is authenticated, redirect based on role
      const currentPath = window.location.pathname
      
      // Don't redirect if already on a role-specific path
      if (currentPath.startsWith('/professor/') || currentPath.startsWith('/student/')) {
        return
      }
      
      // Don't redirect from auth pages, landing page, or other non-dashboard pages
      const skipRedirectPaths = ['/login', '/signup', '/auth', '/']
      if (skipRedirectPaths.some(path => currentPath === path || currentPath.startsWith(path))) {
        return
      }
      
      // Redirect based on role
      if (user.role === 'professor' || user.role === 'admin') {
        router.push('/professor/dashboard')
      } else if (user.role === 'student') {
        router.push('/student/dashboard')
      }
    }
  }, [user, isLoading, router])

  // Show loading while determining redirect
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-black">Loading...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
