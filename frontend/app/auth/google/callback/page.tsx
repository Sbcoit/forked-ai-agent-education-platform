"use client"

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import RoleChooser from "@/components/RoleChooser"

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
      <RoleChooser
        selectedRole={selectedRole}
        onRoleSelect={setSelectedRole}
        onContinue={() => selectedRole && handleRoleSelect(selectedRole)}
        isLoading={isLoading}
        showContinueButton={true}
        variant="simple"
      />
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
