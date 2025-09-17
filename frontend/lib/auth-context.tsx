"use client"

import React, { createContext, useContext, ReactNode, useEffect } from 'react'
import { apiClient, User, LoginCredentials, RegisterData } from './api'
import { GoogleOAuth, AccountLinkingData } from './google-oauth'

// Define proper types for Google OAuth responses
export interface GoogleOAuthSuccessData {
  user: User
  access_token?: string
  message?: string
}

export interface AuthError {
  error: string
  message?: string
}

export type GoogleOAuthResult = AccountLinkingData | GoogleOAuthSuccessData

// Configuration constants
export const INACTIVITY_THRESHOLD_MS = 10 * 60 * 1000 // 10 minutes in milliseconds

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (data: RegisterData) => Promise<void>
  loginWithGoogle: () => Promise<GoogleOAuthResult>
  linkGoogleAccount: (action: 'link' | 'create_separate', existingUserId: number, googleData: AccountLinkingData['google_data'], state: string) => Promise<void>
  clearCache: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)

  // Track user activity for inactivity-based logout
  const updateLastActivity = React.useCallback(async () => {
    const timestamp = Date.now().toString()
    
    // Store in sessionStorage for per-tab scope (more secure than localStorage)
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('last_activity', timestamp)
    }
    
    // Also send heartbeat to server for secure activity tracking
    try {
      await apiClient.apiRequest('/users/activity', {
        method: 'POST',
        body: JSON.stringify({ timestamp: parseInt(timestamp) })
      }, true) // Silent auth error to avoid disrupting UX
    } catch (error) {
      // Fallback to client-side tracking if server call fails
      console.debug('Server activity tracking failed, using client-side fallback')
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.log('Activity timestamp updated:', new Date(parseInt(timestamp)).toLocaleTimeString())
    }
  }, [])

  const checkInactivity = React.useCallback(() => {
    const lastActivity = sessionStorage.getItem('last_activity')
    if (process.env.NODE_ENV === 'development') {
      console.log('Checking inactivity, last activity timestamp:', lastActivity)
    }
    
    if (!lastActivity) {
      // No activity timestamp means this is a fresh session, set current time and don't logout
      if (process.env.NODE_ENV === 'development') {
        console.log('Fresh session detected, setting activity timestamp')
      }
      updateLastActivity()
      return false
    }
    
    const timeSinceActivity = Date.now() - parseInt(lastActivity)
    const inactivityThreshold = INACTIVITY_THRESHOLD_MS
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`Time since last activity: ${Math.round(timeSinceActivity / 1000)} seconds (${Math.round(timeSinceActivity / 60000)} minutes)`)
    }
    
    if (timeSinceActivity > inactivityThreshold) {
      if (process.env.NODE_ENV === 'development') {
        console.log(`User inactive for ${Math.round(timeSinceActivity / 60000)} minutes, logging out...`)
      }
      apiClient.logout()
      setUser(null)
      return true
    }
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`User active within last ${Math.round(timeSinceActivity / 60000)} minutes, staying logged in`)
    }
    return false
  }, [updateLastActivity])

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check for inactivity first
        if (checkInactivity()) {
          setIsLoading(false)
          return
        }

        // Skip cache version check to avoid clearing auth token on page refresh
        // Cache will be managed by TTL and selective invalidation instead
        
        // Check if we have a token (now includes localStorage fallback)
        if (process.env.NODE_ENV === 'development') {
          console.log('Checking authentication status...')
        }
        if (apiClient.isAuthenticated()) {
          if (process.env.NODE_ENV === 'development') {
            console.log('Token found, fetching current user...')
          }
          const currentUser = await apiClient.getCurrentUser()
          if (currentUser) {
            if (process.env.NODE_ENV === 'development') {
              console.log('User authenticated successfully:', currentUser.email)
            }
            setUser(currentUser)
            updateLastActivity() // Update activity on successful login
          } else {
            if (process.env.NODE_ENV === 'development') {
              console.log('Token invalid, clearing...')
            }
            // Token is invalid, clear it
            apiClient.logout()
          }
        } else {
          if (process.env.NODE_ENV === 'development') {
            console.log('No token found')
          }
        }
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          console.log('Auth initialization failed:', error)
        }
        // Clear invalid token
        apiClient.logout()
      } finally {
        setIsLoading(false)
      }
    }
    
    initializeAuth()
  }, [checkInactivity])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await apiClient.login({ email, password })
      setUser(response.user)
      updateLastActivity() // Update activity on successful login
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await apiClient.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      sessionStorage.removeItem('last_activity') // Clear activity tracking on logout
    }
  }

  const register = async (data: RegisterData) => {
    setIsLoading(true)
    try {
      const response = await apiClient.register(data)
      setUser(response.user)
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const loginWithGoogle = async (): Promise<GoogleOAuthResult> => {
    setIsLoading(true)
    try {
      const googleOAuth = GoogleOAuth.getInstance()
      const result = await googleOAuth.openAuthWindow()
      
      if ('action' in result && result.action === 'link_required') {
        // Return the linking data instead of throwing an error
        return result as AccountLinkingData
      } else if ('user' in result) {
        // Direct login success
        const successResult = result as GoogleOAuthSuccessData
        setUser(successResult.user)
        updateLastActivity() // Update activity on successful Google login
        return successResult
      } else {
        // Fallback for unexpected result structure
        throw new Error('Unexpected OAuth result structure')
      }
    } catch (error) {
      console.error('Google login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const linkGoogleAccount = async (action: 'link' | 'create_separate', existingUserId: number, googleData: AccountLinkingData['google_data'], state: string) => {
    setIsLoading(true)
    try {
      const googleOAuth = GoogleOAuth.getInstance()
      const result = await googleOAuth.linkAccount(action, existingUserId, googleData, state)
      setUser(result.user)
      updateLastActivity() // Update activity on successful account linking
    } catch (error) {
      console.error('Account linking failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const clearCache = () => {
    console.log('Manually clearing all cache...')
    apiClient.clearAllCache()
    setUser(null)
    sessionStorage.removeItem('last_activity') // Clear activity tracking on manual cache clear
  }

  const isAuthenticated = !!user

  // Add activity tracking on user interactions
  useEffect(() => {
    if (!user) return

    let lastActivityTime = 0
    const THROTTLE_MS = 1000 // Throttle activity updates to once per second

    const handleUserActivity = () => {
      const now = Date.now()
      if (now - lastActivityTime > THROTTLE_MS) {
        updateLastActivity()
        lastActivityTime = now
      }
    }

    // Use fewer, more focused events with passive listeners for better performance
    const events = ['pointerdown', 'touchstart', 'keydown']
    
    events.forEach(event => {
      document.addEventListener(event, handleUserActivity, { passive: true })
    })

    // Periodic inactivity check every minute
    const inactivityCheckInterval = setInterval(() => {
      if (checkInactivity()) {
        setUser(null)
      }
    }, 60000) // Check every minute

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleUserActivity)
      })
      clearInterval(inactivityCheckInterval)
    }
  }, [user, updateLastActivity, checkInactivity])

  return (
    <AuthContext.Provider value={{ 
      user, 
      isLoading, 
      isAuthenticated, 
      login, 
      logout, 
      register, 
      loginWithGoogle, 
      linkGoogleAccount,
      clearCache
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 