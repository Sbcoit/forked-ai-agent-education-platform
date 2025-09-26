"use client"

import { useState, useRef, KeyboardEvent } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { X, Mail } from "lucide-react"
import { apiClient } from "@/lib/api"

interface InviteStudentsModalProps {
  isOpen: boolean
  onClose: () => void
  cohortId: number
  cohortTitle: string
  onSuccess?: () => void
}

interface EmailPill {
  id: string
  email: string
}

export default function InviteStudentsModal({
  isOpen,
  onClose,
  cohortId,
  cohortTitle,
  onSuccess
}: InviteStudentsModalProps) {
  const [emailPills, setEmailPills] = useState<EmailPill[]>([])
  const [emailInput, setEmailInput] = useState("")
  const [personalMessage, setPersonalMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const addEmailPill = (email: string) => {
    const trimmedEmail = email.trim().toLowerCase()
    
    if (!trimmedEmail) return
    
    if (!validateEmail(trimmedEmail)) {
      setError("Please enter a valid email address")
      return
    }
    
    if (emailPills.some(pill => pill.email === trimmedEmail)) {
      setError("This email has already been added")
      return
    }
    
    const newPill: EmailPill = {
      id: Date.now().toString(),
      email: trimmedEmail
    }
    
    setEmailPills([...emailPills, newPill])
    setEmailInput("")
    setError(null)
  }

  const removeEmailPill = (id: string) => {
    setEmailPills(emailPills.filter(pill => pill.id !== id))
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault()
      addEmailPill(emailInput)
    } else if (e.key === "Backspace" && emailInput === "" && emailPills.length > 0) {
      // Remove last pill if input is empty and backspace is pressed
      const lastPill = emailPills[emailPills.length - 1]
      removeEmailPill(lastPill.id)
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault()
    const pastedText = e.clipboardData.getData("text")
    const emails = pastedText.split(/[,\n\s]+/).filter(email => email.trim())
    
    emails.forEach(email => {
      if (email.trim()) {
        addEmailPill(email.trim())
      }
    })
  }

  const handleSendInvites = async () => {
    if (emailPills.length === 0) {
      setError("Please add at least one email address")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const invitations = emailPills.map(pill => ({
        email: pill.email,
        message: personalMessage.trim() || undefined
      }))

      await apiClient.inviteStudentsToCohort(cohortId, invitations)
      
      // Reset form
      setEmailPills([])
      setEmailInput("")
      setPersonalMessage("")
      
      onSuccess?.()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send invitations")
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    if (!isLoading) {
      setEmailPills([])
      setEmailInput("")
      setPersonalMessage("")
      setError(null)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            Invite Students to {cohortTitle}
          </h2>
          <button
            onClick={handleClose}
            disabled={isLoading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <p className="text-sm text-gray-600">
            Send email invitations to students to join this cohort.
          </p>

          {/* Email Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Email Addresses
            </label>
            <div className="min-h-[40px] border border-gray-300 rounded-md p-2 flex flex-wrap gap-2 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
              {/* Email Pills */}
              {emailPills.map((pill) => (
                <div
                  key={pill.id}
                  className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-sm"
                >
                  <Mail className="h-3 w-3" />
                  <span>{pill.email}</span>
                  <button
                    onClick={() => removeEmailPill(pill.id)}
                    disabled={isLoading}
                    className="text-blue-600 hover:text-blue-800 disabled:opacity-50"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
              
              {/* Input */}
              <input
                ref={inputRef}
                type="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                onKeyDown={handleKeyDown}
                onPaste={handlePaste}
                placeholder={emailPills.length === 0 ? "Enter email addresses separated by commas or new lines..." : ""}
                disabled={isLoading}
                className="flex-1 min-w-[200px] border-none outline-none text-sm placeholder-gray-400 disabled:opacity-50"
              />
            </div>
            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}
          </div>

          {/* Personal Message */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Personal Message (Optional)
            </label>
            <Textarea
              value={personalMessage}
              onChange={(e) => setPersonalMessage(e.target.value)}
              placeholder="Add a personal message to your invitation..."
              disabled={isLoading}
              rows={3}
              className="resize-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSendInvites}
            disabled={isLoading || emailPills.length === 0}
            className="bg-gray-800 text-white hover:bg-gray-700"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Sending...
              </>
            ) : (
              <>
                <Mail className="h-4 w-4 mr-2" />
                Send Invites
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
