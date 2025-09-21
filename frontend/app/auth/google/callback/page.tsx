"use client"

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import RoleChooser from "@/components/RoleChooser"
import { AccountLinkingDialog } from "@/components/AccountLinkingDialog"
import { AccountLinkingData } from "@/lib/google-oauth"

export default function GoogleCallbackPage() {
  const [step, setStep] = useState<'callback' | 'role_selection' | 'complete'>('callback')
  const [selectedRole, setSelectedRole] = useState<'student' | 'professor' | null>(null)
  const [oauthState, setOauthState] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasProcessed, setHasProcessed] = useState(false)
  const [showRoleSelection, setShowRoleSelection] = useState(false)
  const [showAccountLinking, setShowAccountLinking] = useState(false)
  const [accountLinkingData, setAccountLinkingData] = useState<AccountLinkingData | null>(null)
  
  // Debug logging
  console.log('🔍 GoogleCallbackPage - Current step:', step)
  console.log('🔍 GoogleCallbackPage - Selected role:', selectedRole)
  console.log('🔍 GoogleCallbackPage - OAuth state:', oauthState)
  console.log('🔍 GoogleCallbackPage - Has processed:', hasProcessed)
  console.log('🔍 GoogleCallbackPage - Is loading:', isLoading)
  console.log('🔍 GoogleCallbackPage - Show role selection:', showRoleSelection)
  
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
        const requiresRoleSelection = urlParams.get('requires_role_selection')
        const success = urlParams.get('success')
        const userData = urlParams.get('user_data')
        const linkRequired = urlParams.get('link_required')
        const linkData = urlParams.get('link_data')
        
        console.log('🔍 OAuth Callback - Code:', code ? 'Present' : 'Missing')
        console.log('🔍 OAuth Callback - State:', state ? 'Present' : 'Missing')
        console.log('🔍 OAuth Callback - Error:', error || 'None')
        console.log('🔍 OAuth Callback - Requires Role Selection:', requiresRoleSelection || 'None')
        console.log('🔍 OAuth Callback - Success:', success || 'None')
        console.log('🔍 OAuth Callback - User Data:', userData ? 'Present' : 'None')
        console.log('🔍 OAuth Callback - Link Required:', linkRequired || 'None')
        console.log('🔍 OAuth Callback - Link Data:', linkData ? 'Present' : 'None')

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

        // Check if this is a success redirect with user data
        if (success === 'true' && userData) {
          try {
            console.log('🎯 Success redirect with user data detected')
            const decodedUserData = decodeURIComponent(userData)
            const parsedUserData = JSON.parse(decodedUserData)
            console.log('✅ Parsed user data:', parsedUserData)
            
            // Send success data to parent window
            if (window.opener) {
              window.opener.postMessage({
                type: 'GOOGLE_OAUTH_SUCCESS',
                data: parsedUserData
              }, window.location.origin)
            }
            
            // Close the popup window
            window.close()
            return
          } catch (error) {
            console.error('❌ Failed to parse user data:', error)
            // Fall through to error handling
          }
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

        // Check if account linking is required from URL parameter
        if (linkRequired === 'true' && linkData) {
          try {
            console.log('🎯 Account linking required from URL parameter')
            const decodedLinkData = decodeURIComponent(linkData)
            const parsedLinkData = JSON.parse(decodedLinkData)
            console.log('✅ Parsed link data:', parsedLinkData)
            
            // Set account linking data and show dialog
            setAccountLinkingData(parsedLinkData)
            setShowAccountLinking(true)
            
            // Send account linking data to parent window
            if (window.opener) {
              window.opener.postMessage({
                type: 'GOOGLE_OAUTH_ACCOUNT_LINKING_REQUIRED',
                data: parsedLinkData
              }, window.location.origin)
            }
            
            // Don't close the popup - let the user handle account linking
            return
          } catch (error) {
            console.error('❌ Failed to parse link data:', error)
            // Fall through to error handling
          }
        }

        // Check if role selection is required from URL parameter
        if (requiresRoleSelection === 'true') {
          console.log('🎯 Role selection required from URL parameter')
          setOauthState(state)
          setStep('role_selection')
          setShowRoleSelection(true)
          
          // Notify parent window that role selection is required
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ROLE_SELECTION_REQUIRED',
              data: { requires_role_selection: true, state: state }
            }, window.location.origin)
          }
          
          // Don't close the popup - let the user select a role
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
        console.log('🔍 OAuth callback result:', result)

        // Check if role selection is needed
        if (result.requires_role_selection) {
          console.log('🎯 Role selection required, setting step to role_selection')
          console.log('🔍 Setting oauthState to:', state)
          setOauthState(state)
          setStep('role_selection')
          setShowRoleSelection(true)
          console.log('🔍 Step set to role_selection, should render RoleChooser now')
          
          // Notify parent window that role selection is required
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ROLE_SELECTION_REQUIRED',
              data: result
            }, window.location.origin)
          }
          
          // Force a re-render by using setTimeout
          setTimeout(() => {
            console.log('🔍 Forcing re-render after role selection setup')
            setStep('role_selection')
            setShowRoleSelection(true)
          }, 100)
          
          
          // Don't close the popup - let the user select a role
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
    console.log('🎯 Role selected:', role)
    console.log('🔍 OAuth state:', oauthState)
    
    if (!oauthState) {
      console.error('❌ No OAuth state available')
      return
    }
    
    setIsLoading(true)
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const requestBody = {
        role,
        state: oauthState
      }
      
      console.log('🚀 Sending role selection request:', requestBody)
      
      const response = await fetch(`${API_BASE_URL}/auth/google/select-role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      })

      console.log('📡 Role selection response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json()
        console.error('❌ Role selection failed:', errorData)
        throw new Error(errorData.detail || 'Failed to select role')
      }

      const result = await response.json()
      console.log('✅ Role selection successful:', result)

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
      console.error('❌ Role selection error:', error)
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

  // Account linking dialog
  if (showAccountLinking && accountLinkingData) {
    return (
      <AccountLinkingDialog
        isOpen={showAccountLinking}
        onClose={() => {
          setShowAccountLinking(false)
          window.close()
        }}
        linkingData={accountLinkingData}
        onLinkAccount={async (action) => {
          try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            const response = await fetch(`${API_BASE_URL}/auth/google/link`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              credentials: 'include',
              body: JSON.stringify({
                action,
                existing_user_id: accountLinkingData.existing_user.id,
                google_data: accountLinkingData.google_data,
                state: accountLinkingData.state
              })
            })

            if (!response.ok) {
              const errorData = await response.json()
              throw new Error(errorData.detail || 'Account linking failed')
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
            console.error('❌ Account linking error:', error)
            if (window.opener) {
              window.opener.postMessage({
                type: 'GOOGLE_OAUTH_ERROR',
                error: error instanceof Error ? error.message : 'Account linking failed'
              }, window.location.origin)
            }
            window.close()
          }
        }}
        isLoading={isLoading}
      />
    )
  }

  // Role selection UI
  if (step === 'role_selection' || showRoleSelection) {
    console.log('🎯 Rendering RoleChooser component')
    console.log('🔍 Current step:', step)
    console.log('🔍 Show role selection:', showRoleSelection)
    console.log('🔍 Selected role:', selectedRole)
    console.log('🔍 OAuth state:', oauthState)
    
    
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-semibold text-white mb-4">Choose Your Role</h1>
            <p className="text-gray-400 mb-6">How will you be using the platform?</p>
          </div>
          
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
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.083 12.083 0 01.665-6.479L12 14z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Student</h3>
                <p className="text-gray-400 text-sm">Learn through simulations and assignments</p>
              </div>
            </div>
            
            {/* Professor Card */}
            <div 
              className={`cursor-pointer p-6 rounded-lg border-2 transition-all duration-200 ${
                selectedRole === "professor" 
                  ? "border-green-500 bg-green-900/20" 
                  : "border-gray-600 bg-gray-900/20 hover:border-gray-500"
              }`}
              onClick={() => setSelectedRole("professor")}
            >
              <div className="text-center">
                <div className="mx-auto mb-4 p-4 rounded-full bg-green-600/20">
                  <svg className="h-10 w-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Professor</h3>
                <p className="text-gray-400 text-sm">Create and manage simulations for students</p>
              </div>
            </div>
          </div>
          
          {/* Continue Button */}
          {selectedRole && (
            <div className="text-center">
              <button
                onClick={() => handleRoleSelect(selectedRole)}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
              >
                {isLoading ? 'Processing...' : 'Continue'}
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Loading state for callback processing
  console.log('🔍 Rendering loading state, current step:', step)
  console.log('🔍 Show role selection:', showRoleSelection)
  
  
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-white">Completing Google login...</p>
        <p className="text-gray-400 text-sm mt-2">Step: {step}</p>
        <p className="text-gray-400 text-sm mt-1">Show role selection: {showRoleSelection ? 'true' : 'false'}</p>
        <p className="text-gray-400 text-sm mt-1">OAuth state: {oauthState ? 'present' : 'missing'}</p>
      </div>
    </div>
  )
}
