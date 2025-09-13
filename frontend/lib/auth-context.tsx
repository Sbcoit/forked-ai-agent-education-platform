"use client"

import React, { createContext, useContext, ReactNode, useEffect } from 'react'
import { apiClient, User, LoginCredentials, RegisterData } from './api'
import { GoogleOAuth, AccountLinkingData } from './google-oauth'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (data: RegisterData) => Promise<void>
  loginWithGoogle: () => Promise<AccountLinkingData | any>
  linkGoogleAccount: (action: 'link' | 'create_separate', existingUserId: number, googleData: any, state: string) => Promise<void>
  clearCache: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)

  // Track user activity for inactivity-based logout
  const updateLastActivity = React.useCallback(() => {
    const timestamp = Date.now().toString()
    localStorage.setItem('last_activity', timestamp)
    console.log('Activity timestamp updated:', new Date(parseInt(timestamp)).toLocaleTimeString())
  }, [])

  const checkInactivity = React.useCallback(() => {
    const lastActivity = localStorage.getItem('last_activity')
    console.log('Checking inactivity, last activity timestamp:', lastActivity)
    
    if (!lastActivity) {
      // No activity timestamp means this is a fresh session, set current time and don't logout
      console.log('Fresh session detected, setting activity timestamp')
      updateLastActivity()
      return false
    }
    
    const timeSinceActivity = Date.now() - parseInt(lastActivity)
    const inactivityThreshold = 10 * 60 * 1000 // 10 minutes in milliseconds
    
    console.log(`Time since last activity: ${Math.round(timeSinceActivity / 1000)} seconds (${Math.round(timeSinceActivity / 60000)} minutes)`)
    
    if (timeSinceActivity > inactivityThreshold) {
      console.log(`User inactive for ${Math.round(timeSinceActivity / 60000)} minutes, logging out...`)
      apiClient.logout()
      setUser(null)
      return true
    }
    
    console.log(`User active within last ${Math.round(timeSinceActivity / 60000)} minutes, staying logged in`)
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
        
        // Check if we have a token
        console.log('Checking authentication status...')
        if (apiClient.isAuthenticated()) {
          console.log('Token found, fetching current user...')
          const currentUser = await apiClient.getCurrentUser()
          if (currentUser) {
            console.log('User authenticated successfully:', currentUser.email)
            setUser(currentUser)
            updateLastActivity() // Update activity on successful login
          } else {
            console.log('Token invalid, clearing...')
            // Token is invalid, clear it
            apiClient.logout()
          }
        } else {
          console.log('No token found')
        }
      } catch (error) {
        console.log('Auth initialization failed:', error)
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
      localStorage.removeItem('last_activity') // Clear activity tracking on logout
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

  const loginWithGoogle = async () => {
    setIsLoading(true)
    try {
      const googleOAuth = GoogleOAuth.getInstance()
      const result = await googleOAuth.openAuthWindow()
      
      if (result.action === 'link_required') {
        // Return the linking data instead of throwing an error
        return result
      } else {
        // Direct login success
        setUser(result.user)
        updateLastActivity() // Update activity on successful Google login
        return result
      }
    } catch (error) {
      console.error('Google login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const linkGoogleAccount = async (action: 'link' | 'create_separate', existingUserId: number, googleData: any, state: string) => {
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
    localStorage.removeItem('last_activity') // Clear activity tracking on manual cache clear
  }

  const isAuthenticated = !!user

  // Add activity tracking on user interactions
  useEffect(() => {
    if (!user) return

    const handleUserActivity = () => {
      updateLastActivity()
    }

    // Track various user activities
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    events.forEach(event => {
      document.addEventListener(event, handleUserActivity, true)
    })

    // Periodic inactivity check every minute
    const inactivityCheckInterval = setInterval(() => {
      if (checkInactivity()) {
        setUser(null)
      }
    }, 60000) // Check every minute

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleUserActivity, true)
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