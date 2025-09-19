"use client"

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"

export default function GoogleCallbackPage() {
  const [step, setStep] = useState<'callback' | 'role_selection' | 'complete'>('callback')
  const [selectedRole, setSelectedRole] = useState<'student' | 'professor' | null>(null)
  const [oauthState, setOauthState] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasProcessed, setHasProcessed] = useState(false)
  
  useEffect(() => {
    const handleCallback = async () => {
      // Prevent multiple executions
      if (hasProcessed) {
        console.log('Callback already processed, skipping...')
        return
      }
      setHasProcessed(true)
      try {
        // Get the URL parameters
        const urlParams = new URLSearchParams(window.location.search)
        const code = urlParams.get('code')
        const state = urlParams.get('state')
        const error = urlParams.get('error')
        
        console.log('🔍 OAuth Callback - Code:', code ? 'Present' : 'Missing')
        console.log('🔍 OAuth Callback - State:', state ? 'Present' : 'Missing')
        console.log('🔍 OAuth Callback - Error:', error || 'None')

        if (error) {
          // Send error to parent window
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ERROR',
              error: `OAuth error: ${error}`
            }, window.location.origin)
          }
          window.close()
          return
        }

        if (!code || !state) {
          // Send error to parent window
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ERROR',
              error: 'Missing authorization code or state'
            }, window.location.origin)
          }
          window.close()
          return
        }

        // Validate state parameter (should be alphanumeric and reasonable length)
        if (!state || !/^[a-zA-Z0-9_-]{10,100}$/.test(state)) {
          throw new Error('Invalid OAuth state parameter')
        }

        // Call the backend callback endpoint with properly encoded parameters
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const params = new URLSearchParams({
          code: code,
          state: state
        })
        const callbackUrl = `${API_BASE_URL}/auth/google/callback?${params.toString()}`
        console.log('🚀 Calling backend callback:', callbackUrl)
        
        const response = await fetch(callbackUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        })
        
        console.log('📡 Backend response status:', response.status)

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'OAuth callback failed')
        }

        const result = await response.json()

        // Check if role selection is needed
        if (result.requires_role_selection) {
          setOauthState(state)
          setStep('role_selection')
          return
        }

        // Token is now handled server-side via HttpOnly cookies
        // No client-side token storage for security

        // Send success data to parent window
        if (window.opener) {
          window.opener.postMessage({
            type: 'GOOGLE_OAUTH_SUCCESS',
            data: result
          }, window.location.origin)
        }

        // Close the popup window
        window.close()

      } catch (error) {
        console.error('OAuth callback error:', error)
        
        // Send error to parent window
        if (window.opener) {
          window.opener.postMessage({
            type: 'GOOGLE_OAUTH_ERROR',
            error: error instanceof Error ? error.message : 'OAuth callback failed'
          }, window.location.origin)
        }
        
        window.close()
      }
    }

    handleCallback()
  }, [])

  const handleRoleSelect = async (role: 'student' | 'professor') => {
    if (!oauthState) return
    
    setIsLoading(true)
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/auth/google/select-role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          role,
          state: oauthState
        })
      })

      if (!response.ok) {
        throw new Error('Failed to select role')
      }

      const result = await response.json()

      // Send success data to parent window
      if (window.opener) {
        window.opener.postMessage({
          type: 'GOOGLE_OAUTH_SUCCESS',
          data: result
        }, window.location.origin)
      }

      // Close the popup window
      window.close()
    } catch (error) {
      console.error('Role selection error:', error)
      if (window.opener) {
        window.opener.postMessage({
          type: 'GOOGLE_OAUTH_ERROR',
          error: error instanceof Error ? error.message : 'Role selection failed'
        }, window.location.origin)
      }
      window.close()
    } finally {
      setIsLoading(false)
    }
  }

  // Role selection UI
  if (step === 'role_selection') {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 mb-6">
              <img src="/n-aiblelogo.png" alt="Logo" className="w-24 h-12" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Choose Your Role</h1>
            <p className="text-gray-400">How will you be using the platform?</p>
          </div>

          {/* Role Selection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Student Card */}
            <div 
              className={`cursor-pointer p-6 rounded-lg border-2 transition-all duration-200 ${
                selectedRole === "student" 
                  ? "border-blue-500 bg-blue-900/20" 
                  : "border-gray-600 bg-gray-900/20 hover:border-gray-500"
              }`}
              onClick={() => setSelectedRole("student")}
            >
              <div className="text-center">
                <div className="mx-auto mb-4 p-4 rounded-full bg-blue-600/20">
                  <svg className="h-10 w-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Student</h3>
                <p className="text-gray-400 text-sm">Join cohorts and participate in simulations</p>
              </div>
            </div>

            {/* Professor Card */}
            <div 
              className={`cursor-pointer p-6 rounded-lg border-2 transition-all duration-200 ${
                selectedRole === "professor" 
                  ? "border-purple-500 bg-purple-900/20" 
                  : "border-gray-600 bg-gray-900/20 hover:border-gray-500"
              }`}
              onClick={() => setSelectedRole("professor")}
            >
              <div className="text-center">
                <div className="mx-auto mb-4 p-4 rounded-full bg-purple-600/20">
                  <svg className="h-10 w-10 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Professor</h3>
                <p className="text-gray-400 text-sm">Create cohorts and manage student learning</p>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <div className="text-center">
            <Button
              onClick={() => selectedRole && handleRoleSelect(selectedRole)}
              disabled={!selectedRole || isLoading}
              className={`px-8 py-3 text-lg font-medium transition-all duration-200 ${
                selectedRole === "student"
                  ? "bg-blue-600 hover:bg-blue-700 text-white"
                  : selectedRole === "professor"
                  ? "bg-purple-600 hover:bg-purple-700 text-white"
                  : "bg-gray-600 text-gray-400 cursor-not-allowed"
              }`}
            >
              {isLoading ? "Processing..." : `Continue as ${selectedRole === "student" ? "Student" : selectedRole === "professor" ? "Professor" : "..."}`}
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Loading state for callback processing
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-white">Completing Google login...</p>
      </div>
    </div>
  )
}
