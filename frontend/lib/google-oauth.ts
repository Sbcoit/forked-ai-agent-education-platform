// Google OAuth utility functions
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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

      // Wait for the window to close or receive message
      return new Promise((resolve, reject) => {
        const checkClosed = setInterval(() => {
          if (this.authWindow?.closed) {
            clearInterval(checkClosed)
            reject(new Error('OAuth window was closed'))
          }
        }, 1000)

        // Listen for messages from the popup
        const messageHandler = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return

          if (event.data.type === 'GOOGLE_OAUTH_SUCCESS') {
            clearInterval(checkClosed)
            window.removeEventListener('message', messageHandler)
            this.authWindow?.close()
            resolve(event.data.data)
          } else if (event.data.type === 'GOOGLE_OAUTH_ERROR') {
            clearInterval(checkClosed)
            window.removeEventListener('message', messageHandler)
            this.authWindow?.close()
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

  async linkAccount(action: 'link' | 'create_separate', existingUserId: number, googleData: OAuthUserData): Promise<any> {
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
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to link account')
      }

      return await response.json()
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
    const response = await fetch(`${API_BASE_URL}/auth/google/callback?code=${code}&state=${state}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'OAuth callback failed')
    }

    return await response.json()
  } catch (error) {
    console.error('Error handling OAuth callback:', error)
    throw error
  }
}
