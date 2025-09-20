"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

export interface RoleChooserProps {
  selectedRole: "student" | "professor" | null
  onRoleSelect: (role: "student" | "professor") => void
  onContinue?: () => void
  isLoading?: boolean
  showContinueButton?: boolean
  variant?: "detailed" | "simple"
  className?: string
}

export default function RoleChooser({
  selectedRole,
  onRoleSelect,
  onContinue,
  isLoading = false,
  showContinueButton = false,
  variant = "detailed",
  className = ""
}: RoleChooserProps) {
  const isDetailed = variant === "detailed"
  const maxWidth = isDetailed ? "max-w-4xl" : "max-w-2xl"
  const iconSize = isDetailed ? "h-12 w-12" : "h-10 w-10"
  const titleSize = isDetailed ? "text-xl" : "text-lg"

  return (
    <div className={`min-h-screen bg-black text-white flex items-center justify-center p-4 ${className}`}>
      <div className={`w-full ${maxWidth}`}>
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-6">
            <img 
              src="/n-aiblelogo.png" 
              alt="Logo" 
              className={isDetailed ? "w-30 h-16" : "w-24 h-12"} 
            />
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
            onClick={() => onRoleSelect("student")}
          >
            <div className="text-center">
              <div className="mx-auto mb-4 p-4 rounded-full bg-blue-600/20">
                <svg className={`${iconSize} text-blue-400`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                </svg>
              </div>
              <h3 className={`${titleSize} font-bold text-white mb-2`}>Student</h3>
              <p className={`text-gray-400 ${isDetailed ? "mb-4" : "text-sm"}`}>
                Join cohorts and participate in simulations
              </p>
              
              {isDetailed && (
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-white">Access assigned simulations</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-white">Track your progress</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-white">Receive notifications</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Professor Card */}
          <div 
            className={`cursor-pointer p-6 rounded-lg border-2 transition-all duration-200 ${
              selectedRole === "professor" 
                ? "border-purple-500 bg-purple-900/20" 
                : "border-gray-600 bg-gray-900/20 hover:border-gray-500"
            }`}
            onClick={() => onRoleSelect("professor")}
          >
            <div className="text-center">
              <div className="mx-auto mb-4 p-4 rounded-full bg-purple-600/20">
                <svg className={`${iconSize} text-purple-400`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className={`${titleSize} font-bold text-white mb-2`}>Professor</h3>
              <p className={`text-gray-400 ${isDetailed ? "mb-4" : "text-sm"}`}>
                Create cohorts and design simulations
              </p>
              
              {isDetailed && (
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-white">Build custom simulations</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-white">Manage student cohorts</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-white">Track learning analytics</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Continue Button */}
        {showContinueButton && (
          <div className="text-center">
            <Button
              onClick={onContinue}
              disabled={!selectedRole || isLoading}
              className="w-full max-w-md bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium py-3 px-8 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Processing..." : `Continue as ${selectedRole === "student" ? "Student" : selectedRole === "professor" ? "Professor" : "..."}`}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
