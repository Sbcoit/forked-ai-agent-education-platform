"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Bell,
  CheckCircle,
  XCircle,
  Mail,
  Calendar,
  Users,
  BookOpen,
  Trophy,
  Star,
  ArrowRight,
  Filter,
  Search,
  Clock,
  UserPlus,
  MessageCircle,
  UserCheck,
  UserX
} from "lucide-react"
import RoleBasedSidebar from "@/components/RoleBasedSidebar"
import { useAuth } from "@/lib/auth-context"
import { apiClient } from "@/lib/api"

export default function ProfessorNotifications() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  const [searchTerm, setSearchTerm] = useState("")
  const [typeFilter, setTypeFilter] = useState("All Types")
  const [statusFilter, setStatusFilter] = useState("All Status")
  
  // Real data from API
  const [realNotifications, setRealNotifications] = useState<any[]>([])
  const [loadingNotifications, setLoadingNotifications] = useState(true)

  // Fetch notifications
  useEffect(() => {
    const fetchNotifications = async () => {
      if (!user) return
      
      try {
        setLoadingNotifications(true)
        
        // Fetch professor notifications
        const notificationsResponse = await apiClient.getProfessorNotifications().catch(() => ({ notifications: [] }))
        
        setRealNotifications(notificationsResponse.notifications || [])
      } catch (error) {
        console.error('Error fetching notifications:', error)
      } finally {
        setLoadingNotifications(false)
      }
    }

    fetchNotifications()
  }, [user])

  // Handle redirect when user is not authenticated or not a professor
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/")
    } else if (!authLoading && user && user.role !== 'professor' && user.role !== 'admin') {
      // Redirect students to their dashboard
      router.push("/student/dashboard")
    }
  }, [user, authLoading, router])

  // Show loading while auth is being checked
  if (authLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-black">Loading...</p>
        </div>
      </div>
    )
  }

  // If no user, show redirecting message
  if (!user) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-black">Redirecting...</p>
        </div>
      </div>
    )
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  // Helper function to mark notification as read
  const markNotificationAsRead = async (notificationId: number) => {
    try {
      await apiClient.markProfessorNotificationRead(notificationId)
      // Update local state
      setRealNotifications(prev => prev.map(notif => 
        notif.id === notificationId ? { ...notif, is_read: true } : notif
      ))
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  // Convert real notifications to display format
  const formattedRealNotifications = realNotifications.map(notification => ({
    id: `notif-${notification.id}`,
    type: notification.type,
    title: notification.title,
    message: notification.message,
    time: new Date(notification.created_at).toLocaleDateString(),
    isRead: notification.is_read,
    isNew: !notification.is_read,
    status: notification.data?.status || "active",
    notificationId: notification.id,
    data: notification.data,
    actions: getActionsForNotification(notification)
  }))

  // Helper function to get actions for different notification types
  function getActionsForNotification(notification: any): string[] {
    switch (notification.type) {
      case 'invitation_accepted':
        return ['View Cohort', 'Send Welcome Message']
      case 'invitation_declined':
        return ['View Cohort', 'Send Follow-up']
      case 'assignment_submitted':
        return ['Grade Assignment', 'View Submission']
      case 'student_question':
        return ['Reply', 'View Question']
      default:
        return ['View Details']
    }
  }

  // Mock notification data for demo
  const mockNotifications = [
    {
      id: 1,
      type: "invitation_accepted",
      title: "Student Joined Cohort",
      message: "John Smith has accepted your invitation to join Business Strategy Fall 2024.",
      time: "2 hours ago",
      isRead: false,
      isNew: true,
      status: "accepted",
      cohortId: 1,
      cohortTitle: "Business Strategy Fall 2024",
      studentName: "John Smith",
      studentEmail: "john.smith@university.edu",
      actions: ["View Cohort", "Send Welcome Message"]
    },
    {
      id: 2,
      type: "invitation_declined",
      title: "Invitation Declined",
      message: "Sarah Johnson has declined your invitation to join Financial Management 401.",
      time: "1 day ago",
      isRead: true,
      isNew: false,
      status: "declined",
      cohortId: 2,
      cohortTitle: "Financial Management 401",
      studentName: "Sarah Johnson",
      studentEmail: "sarah.johnson@university.edu",
      actions: ["View Cohort", "Send Follow-up"]
    },
    {
      id: 3,
      type: "assignment_submitted",
      title: "Assignment Submitted",
      message: "Michael Brown has submitted Tesla Strategic Analysis in Business Strategy Fall 2024.",
      time: "3 days ago",
      isRead: true,
      isNew: false,
      status: "submitted",
      cohortId: 1,
      cohortTitle: "Business Strategy Fall 2024",
      studentName: "Michael Brown",
      assignmentTitle: "Tesla Strategic Analysis",
      submittedAt: "Dec 12, 2024 at 11:30 PM",
      actions: ["Grade Assignment", "View Submission"]
    }
  ]

  // Combine real notifications with mock notifications for demo
  const allNotifications = [...formattedRealNotifications, ...mockNotifications]

  // Handle action clicks
  const handleActionClick = async (action: string, notification: any) => {
    // Mark notification as read if it's a real notification
    if (typeof notification.notificationId === 'number' && !notification.isRead) {
      await markNotificationAsRead(notification.notificationId)
    }

    switch (action) {
      case 'View Cohort':
        if (notification.cohortId || notification.data?.cohort_id) {
          const cohortId = notification.cohortId || notification.data.cohort_id
          router.push(`/professor/cohorts/${cohortId}`)
        }
        break
      case 'Send Welcome Message':
        console.log('Sending welcome message to:', notification.studentName || notification.data?.student_name)
        break
      case 'Send Follow-up':
        console.log('Sending follow-up to:', notification.studentName || notification.data?.student_name)
        break
      case 'Grade Assignment':
        console.log('Grading assignment:', notification.assignmentTitle)
        break
      case 'View Submission':
        console.log('Viewing submission for:', notification.assignmentTitle)
        break
      default:
        console.log('Action:', action, 'for notification:', notification.id)
    }
  }

  const handleMarkAsRead = async (notificationId: number | string) => {
    if (typeof notificationId === 'string' && notificationId.startsWith('notif-')) {
      const realId = parseInt(notificationId.replace('notif-', ''))
      await markNotificationAsRead(realId)
    } else {
      console.log('Marking mock notification as read:', notificationId)
    }
  }

  // Filter notifications based on search and filters
  const filteredNotifications = allNotifications.filter(notification => {
    const matchesSearch = notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notification.message.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesType = typeFilter === "All Types" || 
                       notification.type === typeFilter.toLowerCase() ||
                       (typeFilter === "invitation_accepted" && notification.type === "invitation_accepted") ||
                       (typeFilter === "invitation_declined" && notification.type === "invitation_declined") ||
                       (typeFilter === "assignment_submitted" && notification.type === "assignment_submitted")
    
    const matchesStatus = statusFilter === "All Status" || 
                         notification.status === statusFilter.toLowerCase() ||
                         (statusFilter === "Unread" && !notification.isRead) ||
                         (statusFilter === "Read" && notification.isRead)
    
    return matchesSearch && matchesType && matchesStatus
  })

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "invitation_accepted":
        return <UserCheck className="h-6 w-6 text-green-600" />
      case "invitation_declined":
        return <UserX className="h-6 w-6 text-red-600" />
      case "assignment_submitted":
        return <BookOpen className="h-6 w-6 text-blue-600" />
      case "student_question":
        return <MessageCircle className="h-6 w-6 text-orange-600" />
      default:
        return <Bell className="h-6 w-6 text-gray-600" />
    }
  }

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "invitation_accepted":
        return <Badge className="bg-green-100 text-green-800 text-xs">Invitation</Badge>
      case "invitation_declined":
        return <Badge className="bg-red-100 text-red-800 text-xs">Invitation</Badge>
      case "assignment_submitted":
        return <Badge className="bg-blue-100 text-blue-800 text-xs">Assignment</Badge>
      case "student_question":
        return <Badge className="bg-orange-100 text-orange-800 text-xs">Question</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 text-xs">General</Badge>
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "accepted":
        return <Badge className="bg-green-100 text-green-800 text-xs">Accepted</Badge>
      case "declined":
        return <Badge className="bg-red-100 text-red-800 text-xs">Declined</Badge>
      case "submitted":
        return <Badge className="bg-blue-100 text-blue-800 text-xs">Submitted</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 text-xs">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-white flex">
      <RoleBasedSidebar user={user} />
      
      <div className="flex-1 ml-64">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-black mb-2">Notifications</h1>
              <p className="text-gray-600">
                Stay updated on student responses and cohort activities
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline"
                onClick={() => router.push('/professor/dashboard')}
                className="border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                <ArrowRight className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <Button 
                onClick={handleLogout}
                variant="outline"
                className="border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Logout
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                  <Bell className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Notifications</p>
                  <p className="text-2xl font-bold text-gray-900">{allNotifications.length}</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                  <UserCheck className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Invitations Accepted</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {allNotifications.filter(n => n.type === 'invitation_accepted').length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                  <UserX className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Invitations Declined</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {allNotifications.filter(n => n.type === 'invitation_declined').length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
                  <MessageCircle className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Unread</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {allNotifications.filter(n => !n.isRead).length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4 mb-6">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search notifications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
              />
            </div>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
            >
              <option value="All Types">All Types</option>
              <option value="invitation_accepted">Invitations Accepted</option>
              <option value="invitation_declined">Invitations Declined</option>
              <option value="assignment_submitted">Assignments</option>
              <option value="student_question">Questions</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
            >
              <option value="All Status">All Status</option>
              <option value="Unread">Unread</option>
              <option value="Read">Read</option>
            </select>
          </div>

          {/* Notifications List */}
          <Card className="bg-white border border-gray-200">
            <CardHeader>
              <CardTitle className="text-xl text-gray-900">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingNotifications ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading notifications...</p>
                </div>
              ) : filteredNotifications.length === 0 ? (
                <div className="text-center py-8">
                  <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No notifications found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredNotifications.map((notification) => (
                    <Card 
                      key={notification.id} 
                      className={`border ${
                        notification.isNew 
                          ? "border-blue-300 bg-blue-50" 
                          : notification.isRead 
                          ? "border-gray-200 bg-white" 
                          : "border-gray-300 bg-gray-50"
                      }`}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start space-x-4">
                          <div className="flex-shrink-0">
                            {getTypeIcon(notification.type)}
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-3">
                                <h3 className="font-semibold text-gray-900">{notification.title}</h3>
                                {getTypeBadge(notification.type)}
                                {getStatusBadge(notification.status)}
                                {notification.isNew && (
                                  <Badge className="bg-blue-100 text-blue-800 text-xs">New</Badge>
                                )}
                                {!notification.isRead && (
                                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                                )}
                              </div>
                              <p className="text-xs text-gray-500">{notification.time}</p>
                            </div>
                            
                            <p className="text-gray-600 mb-3">{notification.message}</p>
                            
                            {/* Notification-specific details */}
                            {(notification.type === "invitation_accepted" || notification.type === "invitation_declined") && (
                              <div className={`border rounded-lg p-3 mb-3 ${
                                notification.type === "invitation_accepted" 
                                  ? "bg-green-50 border-green-200" 
                                  : "bg-red-50 border-red-200"
                              }`}>
                                <div className="flex items-center justify-between">
                                  <div>
                                    <p className={`text-sm font-medium ${
                                      notification.type === "invitation_accepted" 
                                        ? "text-green-900" 
                                        : "text-red-900"
                                    }`}>
                                      {notification.cohortTitle || notification.data?.cohort_title}
                                    </p>
                                    <p className={`text-xs ${
                                      notification.type === "invitation_accepted" 
                                        ? "text-green-700" 
                                        : "text-red-700"
                                    }`}>
                                      Student: {notification.studentName || notification.data?.student_name}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {notification.type === "assignment_submitted" && (
                              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <p className="text-sm font-medium text-blue-900">{notification.assignmentTitle}</p>
                                    <p className="text-xs text-blue-700">Student: {notification.studentName}</p>
                                    <p className="text-xs text-blue-700">Submitted: {notification.submittedAt}</p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {/* Action Buttons */}
                            <div className="flex items-center space-x-3">
                              {notification.actions.map((action, index) => {
                                const isPrimary = action === "View Cohort" || action === "Grade Assignment"
                                return (
                                  <Button
                                    key={index}
                                    size="sm"
                                    variant={isPrimary ? "default" : "outline"}
                                    className={
                                      isPrimary 
                                        ? "bg-black text-white hover:bg-gray-800" 
                                        : "border-gray-300 text-gray-700 hover:bg-gray-50"
                                    }
                                    onClick={() => handleActionClick(action, notification)}
                                  >
                                    {action}
                                  </Button>
                                )
                              })}
                              
                              {!notification.isRead && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handleMarkAsRead(notification.id)}
                                  className="text-gray-500 hover:text-gray-700"
                                >
                                  Mark as Read
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
