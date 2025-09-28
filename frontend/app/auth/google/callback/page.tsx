"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function GoogleCallbackPage() {
  const router = useRouter()
  
  useEffect(() => {
    const handleCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search)
        const token = urlParams.get('token')
        const userData = urlParams.get('user')

        console.log('Frontend callback: Received token and user data')

        if (token && userData) {
          // Set the cookie in the main window context
          const isProduction = process.env.NODE_ENV === 'production'
          const domain = isProduction ? '.railway.app' : 'localhost'
          const secure = isProduction ? 'secure' : ''
          document.cookie = `access_token=${token}; path=/; domain=${domain}; max-age=1800; ${secure}; samesite=lax`
          console.log('Frontend callback: Set access_token cookie')

          // Parse user data
          const responseData = JSON.parse(decodeURIComponent(userData))
          console.log('Frontend callback: Response data:', responseData)
          
          // Extract user from response data
          const user = responseData.user
          console.log('Frontend callback: User data:', user)

          // Store user data in sessionStorage for immediate access
          sessionStorage.setItem('user', JSON.stringify(user))
          console.log('Frontend callback: Stored user in sessionStorage')

          // Force a page reload to ensure auth context picks up the user
          console.log('Frontend callback: User role:', user.role)
          if (user.role === 'professor' || user.role === 'admin') {
            console.log('Frontend callback: Redirecting to professor dashboard')
            // Use window.location.href to force a full page reload
            window.location.href = '/professor/dashboard'
          } else if (user.role === 'student') {
            console.log('Frontend callback: Redirecting to student dashboard')
            window.location.href = '/student/dashboard'
          } else {
            console.log('Frontend callback: Unknown role, redirecting to generic dashboard')
            window.location.href = '/dashboard'
          }
        } else {
          console.error('Frontend callback: Missing token or user data')
          router.push('/')
        }
      } catch (error) {
        console.error('Frontend callback: Error handling callback:', error)
        router.push('/')
      }
    }

    handleCallback()
  }, [router])
  
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-white">Processing authentication...</p>
      </div>
    </div>
  )
}