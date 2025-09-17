"use client"

import { useEffect } from 'react'

export default function GoogleCallbackPage() {
  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the URL parameters
        const urlParams = new URLSearchParams(window.location.search)
        const code = urlParams.get('code')
        const state = urlParams.get('state')
        const error = urlParams.get('error')

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
        const response = await fetch(`${API_BASE_URL}/auth/google/callback?${params.toString()}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'OAuth callback failed')
        }

        const result = await response.json()

        // Store the access token if present (for successful login)
        if (result.access_token) {
          localStorage.setItem('auth_token', result.access_token)
          // Only log in development environment, never log the actual token
          if (process.env.NODE_ENV === 'development') {
            console.log('Google OAuth token stored successfully in callback page')
          }
        }

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

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-white">Completing Google login...</p>
      </div>
    </div>
  )
}
