"use client"

import React, { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { User, Mail, Shield, Link, Plus } from 'lucide-react'
import { AccountLinkingData } from '@/lib/google-oauth'

interface AccountLinkingDialogProps {
  isOpen: boolean
  onClose: () => void
  linkingData: AccountLinkingData
  onLinkAccount: (action: 'link' | 'create_separate') => Promise<void>
  isLoading?: boolean
}

export function AccountLinkingDialog({
  isOpen,
  onClose,
  linkingData,
  onLinkAccount,
  isLoading = false
}: AccountLinkingDialogProps) {
  const [selectedAction, setSelectedAction] = useState<'link' | 'create_separate' | null>(null)

  const handleLink = async () => {
    if (selectedAction) {
      await onLinkAccount(selectedAction)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Account Linking Required
          </DialogTitle>
          <DialogDescription>
            {linkingData.message}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Existing Account */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <User className="h-4 w-4" />
                Existing Account
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-500" />
                <span className="font-medium">{linkingData.existing_user.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-500" />
                <span>{linkingData.existing_user.full_name}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">
                  {linkingData.existing_user.provider === 'password' ? 'Email/Password' : 'Google OAuth'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Google Account */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <img src="/google-icon.svg" alt="Google" className="h-4 w-4" />
                Google Account
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-500" />
                <span className="font-medium">{linkingData.google_data.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-500" />
                <span>{linkingData.google_data.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">Google OAuth</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Action Selection */}
          <div className="space-y-4">
            <h3 className="font-medium">Choose an option:</h3>
            
            <div className="space-y-3">
              {/* Link Accounts Option */}
              <Card 
                className={`cursor-pointer transition-colors ${
                  selectedAction === 'link' 
                    ? 'ring-2 ring-blue-500 bg-blue-50' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedAction('link')}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="action"
                      value="link"
                      checked={selectedAction === 'link'}
                      onChange={() => setSelectedAction('link')}
                      className="h-4 w-4"
                    />
                    <Link className="h-5 w-5 text-blue-500" />
                    <div>
                      <h4 className="font-medium">Link Google Account</h4>
                      <p className="text-sm text-gray-600">
                        Connect your Google account to your existing account. You'll be able to sign in with either method.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Create Separate Account Option */}
              <Card 
                className={`cursor-pointer transition-colors ${
                  selectedAction === 'create_separate' 
                    ? 'ring-2 ring-green-500 bg-green-50' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedAction('create_separate')}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="action"
                      value="create_separate"
                      checked={selectedAction === 'create_separate'}
                      onChange={() => setSelectedAction('create_separate')}
                      className="h-4 w-4"
                    />
                    <Plus className="h-5 w-5 text-green-500" />
                    <div>
                      <h4 className="font-medium">Create Separate Account</h4>
                      <p className="text-sm text-gray-600">
                        Create a new account with your Google credentials. Your existing account will remain separate.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button 
              onClick={handleLink} 
              disabled={!selectedAction || isLoading}
              className="min-w-[120px]"
            >
              {isLoading ? 'Processing...' : 'Continue'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
