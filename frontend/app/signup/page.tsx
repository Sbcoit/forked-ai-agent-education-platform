"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { useAuth } from "@/lib/auth-context"
import { AccountLinkingDialog } from "@/components/AccountLinkingDialog"
import { AccountLinkingData } from "@/lib/google-oauth"
import RoleChooser from "@/components/RoleChooser"

export default function SignupPage() {
  const router = useRouter()
  const { user, register, loginWithGoogle, linkGoogleAccount } = useAuth()
  
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  
  // Debug logging
  console.log("🔍 Current step:", step)
  
  // Handle redirect after successful Google OAuth registration
  useEffect(() => {
    // Check if we're in a popup window
    const isPopup = window.opener !== null || window.parent !== window
    
    if (isPopup) {
      console.log('Signup page: In popup context, preventing automatic redirection')
      // Don't redirect automatically when in popup - let the OAuth flow complete
      return
    }
    
    if (user && !loading) {
      // User just registered via Google OAuth, redirect based on role
      console.log("🔄 User authenticated via Google OAuth, redirecting based on role:", user.role)
      if (user.role === 'professor' || user.role === 'admin') {
        router.push('/professor/dashboard')
      } else if (user.role === 'student') {
        router.push('/student/dashboard')
      } else {
        // Fallback to generic dashboard
        router.push('/dashboard')
      }
    }
  }, [user, loading, router])
  
  const [selectedRole, setSelectedRole] = useState<"student" | "professor" | null>(null)
  const [formData, setFormData] = useState({
    email: "",
    full_name: "",
    password: "",
    role: "" as "student" | "professor" | "",
    profile_public: true,
    allow_contact: true
  })
  const [error, setError] = useState("")
  const [showLinkingDialog, setShowLinkingDialog] = useState(false)
  const [linkingData, setLinkingData] = useState<AccountLinkingData | null>(null)

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleRoleSelect = (role: "student" | "professor") => {
    console.log("🎯 Role selected:", role)
    setSelectedRole(role)
    setFormData(prev => ({ ...prev, role }))
    setError("") // Clear any existing error
    // Don't automatically move to step 2 - let user confirm with Continue button
    console.log("📝 Form data after role selection:", { ...formData, role })
  }

  const handleContinue = () => {
    if (selectedRole) {
      console.log("🔄 Moving to step 2 with role:", selectedRole)
      setStep(2)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    
    console.log("🚀 Submitting registration with data:", formData)

    // Validate password length
    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long")
      setLoading(false)
      return
    }

    try {
      // Generate username from email if not provided
      const username = formData.email.split('@')[0]
      const registerData = {
        ...formData,
        username: username
      }
      await register(registerData)
      
      // Redirect to login page after successful registration
      console.log("🎯 Registration successful, redirecting to login page")
      router.push('/')
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignup = async () => {
    setLoading(true)
    setError("")
    
    try {
      const result = await loginWithGoogle()
      
      if ('action' in result && result.action === 'link_required') {
        // Show account linking dialog
        setLinkingData(result as AccountLinkingData)
        setShowLinkingDialog(true)
      } else {
        // Direct login success
        router.push("/dashboard")
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Google signup failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleLinkAccount = async (action: 'link' | 'create_separate') => {
    if (!linkingData) return
    
    try {
      await linkGoogleAccount(action, linkingData.existing_user.id, linkingData.google_data, linkingData.state)
      setShowLinkingDialog(false)
      setLinkingData(null)
      router.push("/dashboard")
    } catch (error) {
      setError(error instanceof Error ? error.message : "Account linking failed. Please try again.")
    }
  }

  // Step 1: Role Selection
  if (step === 1) {
    console.log("🎯 Rendering Step 1 - Role Selection")
    return (
      <>
        <RoleChooser
          selectedRole={selectedRole}
          onRoleSelect={handleRoleSelect}
          onContinue={handleContinue}
          showContinueButton={true}
          variant="detailed"
        />
        
        {/* Sign In Link */}
        <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 text-center">
          <span className="text-gray-400">Already have an account? </span>
          <Link href="/" className="text-white hover:underline">
            Sign In
          </Link>
        </div>
      </>
    )
  }

  // Step 2: Registration Form
  console.log("🎯 Rendering Step 2 - Registration Form")
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4 py-8 md:py-16 lg:py-20">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-20 h-20 mb-6">
            <img src="/n-aiblelogo.png" alt="Logo" className="w-30 h-16" />
          </div>
          <h1 className="text-2xl font-semibold text-white">Create an account</h1>
        </div>

        {/* Google Signup Button */}
        <Button
          onClick={handleGoogleSignup}
          variant="outline"
          className="w-full mb-6 bg-white text-black hover:bg-gray-100 border-gray-300"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          Sign up with Google
        </Button>

        {/* OR Divider */}
        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-600"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-black text-gray-400">OR</span>
          </div>
        </div>

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="full_name" className="text-white">Full Name</Label>
            <Input
              id="full_name"
              type="text"
              placeholder="Enter your full name"
              value={formData.full_name}
              onChange={(e) => handleInputChange("full_name", e.target.value)}
              className="bg-black border-white text-white placeholder-gray-400 focus:border-white"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => handleInputChange("email", e.target.value)}
              className="bg-black border-white text-white placeholder-gray-400 focus:border-white"
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={(e) => handleInputChange("password", e.target.value)}
              className="bg-black border-white text-white placeholder-gray-400 focus:border-white"
              required
            />
          </div>

          {/* Progress Indicator */}
          <div className="flex justify-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <div className="w-2 h-2 bg-white rounded-full"></div>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-500/50 rounded-md p-3 mb-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-red-400 text-sm font-medium">{error}</p>
              </div>
            </div>
          )}

          <Button
            type="submit"
            className="w-full bg-white text-black hover:bg-gray-100"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Sign Up"}
          </Button>
        </form>

        {/* Login link */}
        <div className="text-center mt-6">
          <span className="text-gray-400">Already have an account? </span>
          <Link href="/" className="text-white hover:underline">
            Sign In
          </Link>
        </div>
      </div>

      {/* Account Linking Dialog */}
      {showLinkingDialog && linkingData && (
        <AccountLinkingDialog
          isOpen={showLinkingDialog}
          onClose={() => {
            setShowLinkingDialog(false)
            setLinkingData(null)
          }}
          linkingData={linkingData}
          onLinkAccount={handleLinkAccount}
          isLoading={loading}
        />
      )}
    </div>
  )
}