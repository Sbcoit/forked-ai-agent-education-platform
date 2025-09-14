// Google OAuth utility functions
function getApiBaseUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL
  if (!apiUrl) {
    // Check if we're in production
    if (process.env.NODE_ENV === 'production') {
      throw new Error('NEXT_PUBLIC_API_URL environment variable is required in production')
    }
    // Only allow localhost fallback in development
    return 'http://localhost:8000'
  }
  return apiUrl
}

const API_BASE_URL = getApiBaseUrl()

// Configuration constants
const OAUTH_TIMEOUT_MS = 60000 // 1 minute timeout for better UX

export interface GoogleOAuthResponse {
  auth_url: string
  state: string
}

export interface AccountLinkingData {
  action: 'link_required'
  message: string
  existing_user: {
    id: number
    email: string
    full_name: string
    provider: string
  }
  google_data: {
    email: string
    name: string
    picture?: string
  }
  state: string
}

export interface OAuthUserData {
  google_id: string
  email: string
  full_name: string
  avatar_url?: string
}

export class GoogleOAuth {
  private static instance: GoogleOAuth
  private authWindow: Window | null = null
  private state: string | null = null

  static getInstance(): GoogleOAuth {
    if (!GoogleOAuth.instance) {
      GoogleOAuth.instance = new GoogleOAuth()
    }
    return GoogleOAuth.instance
  }

  async initiateLogin(): Promise<GoogleOAuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/google/login`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to initiate Google OAuth')
      }

      const data = await response.json()
      this.state = data.state
      return data
    } catch (error) {
      console.error('Error initiating Google OAuth:', error)
      throw error
    }
  }

  async openAuthWindow(): Promise<AccountLinkingData | any> {
    try {
      const { auth_url } = await this.initiateLogin()
      
      // Open popup window
      this.authWindow = window.open(
        auth_url,
        'google-oauth',
        'width=500,height=600,scrollbars=yes,resizable=yes'
      )

      if (!this.authWindow) {
        throw new Error('Failed to open OAuth window. Please allow popups.')
      }

      // Wait for messages from the popup
      return new Promise((resolve, reject) => {
        // Set a timeout to prevent hanging
        const timeout = setTimeout(() => {
          window.removeEventListener('message', messageHandler)
          try {
            this.authWindow?.close()
          } catch (e) {
            // Ignore COOP errors when closing window
            console.log('Window close blocked by COOP policy')
          }
          reject(new Error('OAuth timeout - please try again'))
        }, OAUTH_TIMEOUT_MS)

        // Listen for messages from the popup
        const messageHandler = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return

          if (event.data.type === 'GOOGLE_OAUTH_SUCCESS') {
            clearTimeout(timeout)
            window.removeEventListener('message', messageHandler)
            try {
              this.authWindow?.close()
            } catch (e) {
              // Ignore COOP errors when closing window
              console.log('Window close blocked by COOP policy')
            }
            resolve(event.data.data)
          } else if (event.data.type === 'GOOGLE_OAUTH_ERROR') {
            clearTimeout(timeout)
            window.removeEventListener('message', messageHandler)
            try {
              this.authWindow?.close()
            } catch (e) {
              // Ignore COOP errors when closing window
              console.log('Window close blocked by COOP policy')
            }
            reject(new Error(event.data.error))
          }
        }

        window.addEventListener('message', messageHandler)
      })
    } catch (error) {
      console.error('Error in Google OAuth flow:', error)
      throw error
    }
  }

  async linkAccount(action: 'link' | 'create_separate', existingUserId: number, googleData: OAuthUserData, state: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/google/link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          existing_user_id: existingUserId,
          google_data: googleData,
          state,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        console.error('Link account error response:', errorData)
        
        // Handle different error formats
        let errorMessage = 'Failed to link account'
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // Pydantic validation errors
            errorMessage = errorData.detail.map((err: any) => err.msg || err.message || err).join(', ')
          } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail
          } else {
            errorMessage = JSON.stringify(errorData.detail)
          }
        }
        
        throw new Error(errorMessage)
      }

      const data = await response.json()
      
      // Store the access token if present (for successful account linking)
      if (data.access_token) {
        localStorage.setItem('auth_token', data.access_token)
        // Token stored successfully - no need to log sensitive information
      }
      
      return data
    } catch (error) {
      console.error('Error linking account:', error)
      throw error
    }
  }

  // Alternative method using redirect instead of popup
  async redirectToGoogle(): Promise<void> {
    try {
      const { auth_url } = await this.initiateLogin()
      window.location.href = auth_url
    } catch (error) {
      console.error('Error redirecting to Google:', error)
      throw error
    }
  }
}

// Helper function to handle OAuth callback (for redirect method)
export async function handleOAuthCallback(): Promise<AccountLinkingData | any> {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  const error = urlParams.get('error')

  if (error) {
    throw new Error(`OAuth error: ${error}`)
  }

  if (!code || !state) {
    throw new Error('Missing authorization code or state')
  }

  try {
    // Build URL with properly encoded parameters
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

    const data = await response.json()
    
    // Store the access token if present (for successful login)
    if (data.access_token) {
      localStorage.setItem('auth_token', data.access_token)
      // Token stored successfully - no need to log sensitive information
    }
    
    return data
  } catch (error) {
    console.error('Error handling OAuth callback:', error)
    throw error
  }
}
