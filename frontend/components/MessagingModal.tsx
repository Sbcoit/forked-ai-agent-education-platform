"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { 
  X, 
  Search, 
  UserPlus, 
  Paperclip, 
  Music,
  Check,
  ChevronDown
} from "lucide-react"
import { apiClient } from "@/lib/api"

interface MessagingModalProps {
  isOpen: boolean
  onClose: () => void
  currentUser: any
}

interface User {
  id: number
  full_name: string
  email: string
  role: string
}

interface Cohort {
  id: number
  title: string
  course_code: string
}

export default function MessagingModal({ isOpen, onClose, currentUser }: MessagingModalProps) {
  const [selectedCourse, setSelectedCourse] = useState<string>("")
  const [sendIndividual, setSendIndividual] = useState(false)
  const [recipients, setRecipients] = useState<User[]>([])
  const [subject, setSubject] = useState("")
  const [message, setMessage] = useState("")
  const [includeTranslation, setIncludeTranslation] = useState(false)
  const [sending, setSending] = useState(false)
  
  // Search and selection state
  const [searchTerm, setSearchTerm] = useState("")
  const [showUserDropdown, setShowUserDropdown] = useState(false)
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [availableCohorts, setAvailableCohorts] = useState<Cohort[]>([])
  const [showCohortDropdown, setShowCohortDropdown] = useState(false)

  // Fetch users and cohorts
  useEffect(() => {
    if (isOpen) {
      fetchUsers()
      fetchCohorts()
    }
  }, [isOpen])

  const fetchUsers = async () => {
    try {
      const data = await apiClient.getUsers()
      setAvailableUsers(data || [])
    } catch (error) {
      console.error('Error fetching users:', error)
      setAvailableUsers([])
    }
  }

  const fetchCohorts = async () => {
    try {
      const data = await apiClient.getMessagingCohorts()
      setAvailableCohorts(data || [])
    } catch (error) {
      console.error('Error fetching cohorts:', error)
      setAvailableCohorts([])
    }
  }

  const filteredUsers = availableUsers.filter(user =>
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const addRecipient = (user: User) => {
    if (!recipients.find(r => r.id === user.id)) {
      setRecipients([...recipients, user])
    }
    setSearchTerm("")
    setShowUserDropdown(false)
  }

  const removeRecipient = (userId: number) => {
    setRecipients(recipients.filter(r => r.id !== userId))
  }

  const handleSend = async () => {
    if (!subject.trim() || !message.trim() || recipients.length === 0) {
      return
    }

    try {
      setSending(true)
      
      // Send message to each recipient
      for (const recipient of recipients) {
        const messageData = {
          recipient_id: recipient.id,
          cohort_id: selectedCourse ? parseInt(selectedCourse) : null,
          subject: subject,
          message: message,
          message_type: 'general'
        }
        
        await apiClient.sendMessage(messageData)
      }
      
      // Reset form
      setRecipients([])
      setSubject("")
      setMessage("")
      setSelectedCourse("")
      setSendIndividual(false)
      setIncludeTranslation(false)
      
      onClose()
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setSending(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Compose Message</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Course Selection */}
          <div>
            <Label htmlFor="course" className="text-sm font-medium text-gray-700">
              Course
            </Label>
            <div className="relative mt-1">
              <select
                id="course"
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none"
              >
                <option value="">Select Course</option>
                {availableCohorts.map((cohort) => (
                  <option key={cohort.id} value={cohort.id}>
                    {cohort.course_code} - {cohort.title}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* Individual Message Option */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="individual"
              checked={sendIndividual}
              onChange={(e) => setSendIndividual(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <Label htmlFor="individual" className="text-sm text-gray-700">
              Send an individual message to each recipient
            </Label>
          </div>

          {/* Recipients */}
          <div>
            <Label htmlFor="recipients" className="text-sm font-medium text-gray-700">
              To <span className="text-red-500">*</span>
            </Label>
            <div className="relative mt-1">
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 text-gray-400" />
                <Input
                  id="recipients"
                  placeholder="Insert or Select Names"
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value)
                    setShowUserDropdown(true)
                  }}
                  onFocus={() => setShowUserDropdown(true)}
                  className="flex-1 border-0 focus:ring-0 p-0"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                >
                  <UserPlus className="h-4 w-4" />
                </Button>
              </div>
              
              {/* Selected Recipients */}
              {recipients.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {recipients.map((recipient) => (
                    <Badge
                      key={recipient.id}
                      variant="secondary"
                      className="flex items-center space-x-1"
                    >
                      <span>{recipient.full_name}</span>
                      <button
                        onClick={() => removeRecipient(recipient.id)}
                        className="ml-1 hover:text-red-500"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}

              {/* User Dropdown */}
              {showUserDropdown && searchTerm && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                  {filteredUsers.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => addRecipient(user)}
                      className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {user.role}
                      </Badge>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Subject */}
          <div>
            <Label htmlFor="subject" className="text-sm font-medium text-gray-700">
              Subject
            </Label>
            <Input
              id="subject"
              placeholder="Insert Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="mt-1"
            />
          </div>

          {/* Message */}
          <div>
            <Label htmlFor="message" className="text-sm font-medium text-gray-700">
              Message <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="message"
              placeholder="Type your message here..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={6}
              className="mt-1"
            />
          </div>

          {/* Translation Option */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIncludeTranslation(!includeTranslation)}
              className={`h-5 w-5 rounded-full border-2 flex items-center justify-center ${
                includeTranslation 
                  ? 'bg-blue-600 border-blue-600 text-white' 
                  : 'border-gray-300'
              }`}
            >
              {includeTranslation && <X className="h-3 w-3" />}
            </button>
            <Label className="text-sm text-gray-700">
              Include translated version of this message
            </Label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="flex items-center space-x-3">
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <Paperclip className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <Music className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={sending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSend}
              disabled={sending || !subject.trim() || !message.trim() || recipients.length === 0}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {sending ? 'Sending...' : 'Send'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
