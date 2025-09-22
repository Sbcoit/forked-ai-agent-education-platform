"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import RoleChooser from "@/components/RoleChooser"

interface RoleSelectionData {
  requires_role_selection: boolean
  state: string
  user_info: {
    google_id: string
    email: string
    name: string
    picture?: string
  }
}

export default function RoleSelectionPage() {
  const router = useRouter()
  const [roleData, setRoleData] = useState<RoleSelectionData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedRole, setSelectedRole] = useState<"student" | "professor" | null>(null)

  useEffect(() => {
    const handleRoleSelection = () => {
      try {
        const urlParams = new URLSearchParams(window.location.search)
        const dataParam = urlParams.get('data')

        if (dataParam) {
          const data = JSON.parse(decodeURIComponent(dataParam))
          console.log('Role selection page: Received data:', data)
          setRoleData(data)
        } else {
          console.error('Role selection page: No data parameter found')
          setError('No role selection data found')
        }
      } catch (error) {
        console.error('Role selection page: Error parsing data:', error)
        setError('Invalid role selection data')
      }
    }

    handleRoleSelection()
  }, [])

  const handleRoleSelection = async (role: 'student' | 'professor') => {
    if (!roleData) return

    setLoading(true)
    setError(null)

    try {
      console.log('Role selection: Selecting role:', role)
      
      // Call the backend to complete the OAuth with the selected role
      const response = await fetch('http://localhost:8000/auth/google/select-role', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          role: role,
          state: roleData.state,
          user_info: roleData.user_info
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to select role')
      }

      const result = await response.json()
      console.log('Role selection: Success:', result)

      // Set the cookie in the main window context
      if (result.access_token) {
        document.cookie = `access_token=${result.access_token}; path=/; domain=localhost; max-age=1800; secure=false; samesite=lax`
        console.log('Role selection: Set access_token cookie')
      }

      // Store user data in sessionStorage for immediate access
      if (result.user) {
        sessionStorage.setItem('user', JSON.stringify(result.user))
        console.log('Role selection: Stored user in sessionStorage')
      }

      // Redirect to dashboard
      console.log('Role selection: Redirecting based on role:', role)
      if (role === 'professor') {
        console.log('Role selection: Redirecting to professor dashboard')
        // Use window.location.href to force a full page reload
        window.location.href = '/professor/dashboard'
      } else if (role === 'student') {
        console.log('Role selection: Redirecting to student dashboard')
        window.location.href = '/student/dashboard'
      } else {
        console.log('Role selection: Redirecting to generic dashboard')
        window.location.href = '/dashboard'
      }
    } catch (error) {
      console.error('Role selection: Error:', error)
      setError(error instanceof Error ? error.message : 'Failed to select role')
    } finally {
      setLoading(false)
    }
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-400 mb-4">Error</h1>
          <p className="text-white mb-4">{error}</p>
          <button 
            onClick={() => router.push('/')} 
            className="bg-white text-black px-4 py-2 rounded hover:bg-gray-100 transition-colors"
          >
            Go to Login
          </button>
        </div>
      </div>
    )
  }

  if (!roleData) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white">Loading role selection...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Choose Your Role</h1>
          <p className="text-gray-400">Welcome, {roleData?.user_info?.name || 'User'}! Please select your role to continue.</p>
        </div>

        <RoleChooser
          selectedRole={selectedRole}
          onRoleSelect={setSelectedRole}
          onContinue={() => selectedRole && handleRoleSelection(selectedRole)}
          isLoading={loading}
          showContinueButton={true}
          variant="detailed"
        />

        {error && (
          <div className="mt-6 bg-red-900/20 border border-red-500/50 rounded-md p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-red-400 text-sm font-medium">{error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
