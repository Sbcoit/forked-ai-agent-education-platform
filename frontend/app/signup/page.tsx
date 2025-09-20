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
  
  // Debug logging
  console.log("🔍 Current step:", step)
  
  // Handle redirect after successful registration
  useEffect(() => {
    if (user && !loading) {
      // User just registered, redirect based on role
      console.log("🔄 User authenticated, redirecting based on role:", user.role)
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
  const [loading, setLoading] = useState(false)
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
    setStep(2)
    console.log("📝 Form data after role selection:", { ...formData, role })
    console.log("🔄 Step changed to:", 2)
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
      
      // Redirect is now handled by useEffect when user state changes
      console.log("🎯 Registration successful, redirect will be handled by useEffect")
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

  // This duplicate step 2 was removed - step 2 should show registration form
  if (false) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
        <div className="w-full max-w-4xl">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 mb-6">
              <img src="/n-aiblelogo.png" alt="Logo" className="w-30 h-16" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Choose Your Role</h1>
            <p className="text-gray-400">How will you be using the platform?</p>
          </div>

          {/* Role Selection Cards */}
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
                  <svg className="h-12 w-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Student</h3>
                <p className="text-gray-400 mb-4">Join cohorts and participate in simulations</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-white">Access assigned simulations</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-white">Track progress and achievements</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-white">Join professor-led cohorts</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Professor Card */}
            <div 
              className={`cursor-pointer p-6 rounded-lg border-2 transition-all duration-200 ${
                selectedRole === "professor" 
                  ? "border-purple-500 bg-purple-900/20" 
                  : "border-gray-600 bg-gray-900/20 hover:border-gray-500"
              }`}
              onClick={() => setSelectedRole("professor")}
            >
              <div className="text-center">
                <div className="mx-auto mb-4 p-4 rounded-full bg-purple-600/20">
                  <svg className="h-12 w-12 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Professor</h3>
                <p className="text-gray-400 mb-4">Create cohorts and manage student learning</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-white">Build custom simulations</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-white">Create and manage cohorts</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-white">Track student progress</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="flex justify-center gap-2 mb-6">
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
          </div>

          {/* Continue Button */}
          <div className="text-center">
            <Button
              onClick={() => selectedRole && handleRoleSelect(selectedRole)}
              disabled={!selectedRole}
              className={`px-8 py-3 text-lg font-medium transition-all duration-200 ${
                selectedRole === "student"
                  ? "bg-blue-600 hover:bg-blue-700 text-white"
                  : selectedRole === "professor"
                  ? "bg-purple-600 hover:bg-purple-700 text-white"
                  : "bg-gray-600 text-gray-400 cursor-not-allowed"
              }`}
            >
              Continue as {selectedRole === "student" ? "Student" : selectedRole === "professor" ? "Professor" : "..."}
            </Button>
          </div>

          {/* Back Button */}
          <div className="text-center mt-4">
            <button
              onClick={() => setStep(1)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← Back
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Step 1: Role Selection
  if (step === 1) {
    console.log("🎯 Rendering Step 1 - Role Selection")
    return (
      <>
        <RoleChooser
          selectedRole={selectedRole}
          onRoleSelect={handleRoleSelect}
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