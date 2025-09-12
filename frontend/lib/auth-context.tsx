"use client"

import React, { createContext, useContext, ReactNode, useEffect } from 'react'
import { apiClient, User, LoginCredentials, RegisterData } from './api'
import { GoogleOAuth, AccountLinkingData } from './google-oauth'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (data: RegisterData) => Promise<void>
  loginWithGoogle: () => Promise<void>
  linkGoogleAccount: (action: 'link' | 'create_separate', existingUserId: number, googleData: any) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if we have a token
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
        // Handle account linking - this will be handled by the component
        throw new Error('ACCOUNT_LINKING_REQUIRED')
      } else {
        // Direct login success
        setUser(result.user)
      }
    } catch (error) {
      console.error('Google login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const linkGoogleAccount = async (action: 'link' | 'create_separate', existingUserId: number, googleData: any) => {
    setIsLoading(true)
    try {
      const googleOAuth = GoogleOAuth.getInstance()
      const result = await googleOAuth.linkAccount(action, existingUserId, googleData)
      setUser(result.user)
    } catch (error) {
      console.error('Account linking failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
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
      linkGoogleAccount 
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