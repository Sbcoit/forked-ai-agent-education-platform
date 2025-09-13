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

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Clear all cached data on page refresh/load
        console.log('Clearing all cache on page refresh...')
        apiClient.clearAllCache()
        
        // Check if we have a token (this will be null after clearing)
        if (apiClient.isAuthenticated()) {
          const currentUser = await apiClient.getCurrentUser()
          if (currentUser) {
            setUser(currentUser)
          } else {
            // Token is invalid, clear it
            apiClient.logout()
          }
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
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await apiClient.login({ email, password })
      setUser(response.user)
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
  }

  const isAuthenticated = !!user

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