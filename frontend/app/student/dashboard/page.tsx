"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Target,
  Star,
  Bell,
  Users,
  Shield,
  Trophy,
  Clock,
  BookOpen,
  TrendingUp,
  Crown,
  Play,
  Eye,
  MessageCircle,
  UserPlus,
  Calendar,
  ArrowRight,
  CheckCircle,
  Zap
} from "lucide-react"
import RoleBasedSidebar from "@/components/RoleBasedSidebar"
import { useAuth } from "@/lib/auth-context"

export default function StudentDashboard() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  // Mock data - in real app, this would come from API
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: "Invitation to Business Strategy Fall 2024",
      message: "Dr. Sarah Wilson has invited you to join their cohort. Experience Harvard Business School case simulations with AI-powered scenarios.",
      time: "2 hours ago",
      isNew: true,
      type: "invitation"
    }
  ])
  
  const [achievements] = useState([
    {
      id: 1,
      title: "Strategic Thinker",
      description: "Scored 90+ on 3 strategy simulations",
      icon: Target,
      earnedDate: "Dec 10",
      color: "bg-yellow-100 text-yellow-800"
    },
    {
      id: 2,
      title: "Speed Runner",
      description: "Complete a simulation in under 30 minutes",
      icon: Zap,
      earnedDate: "Dec 8",
      color: "bg-yellow-100 text-yellow-800"
    },
    {
      id: 3,
      title: "Top Performer",
      description: "Rank #1 in any simulation",
      icon: Trophy,
      earnedDate: "Dec 10",
      color: "bg-yellow-100 text-yellow-800"
    },
    {
      id: 4,
      title: "Consistent Player",
      description: "Complete 10 simulations",
      icon: TrendingUp,
      progress: "7/10",
      color: "bg-yellow-100 text-yellow-800"
    }
  ])
  
  const [activeCohorts] = useState([
    {
      id: 1,
      title: "Financial Management 401",
      instructor: "Dr. Michael Chen",
      description: "Master corporate finance through realistic AI-powered business simulations and case studies.",
      progress: "3/4 completed",
      progressPercentage: 75,
      currentRank: "#2",
      bestRank: "#1",
      avgScore: "88%",
      xpEarned: "1250",
      joinedDate: "Nov 28",
      nextSimulation: "Investment Portfolio Challenge",
      simulations: [
        {
          id: 1,
          title: "Investment Portfolio Challenge",
          status: "Started Dec 8",
          progress: "Scene 1 of 4",
          progressPercentage: 25,
          ranking: "Rank #2/18"
        },
        {
          id: 2,
          title: "Risk Assessment Simulation",
          status: "Started Dec 12",
          progress: "Scene 2 of 5",
          progressPercentage: 40,
          ranking: "Rank #3/15"
        }
      ]
    }
  ])
  
  const [recentSimulations] = useState([
    {
      id: 1,
      title: "Tesla Strategic Analysis",
      course: "Business Strategy Fall 2024",
      completedDate: "Dec 10",
      duration: "45 min",
      score: "95%",
      grade: "A",
      rank: "Rank #1/24",
      action: "View Results"
    },
    {
      id: 2,
      title: "Netflix Market Entry",
      course: "Financial Management 401",
      completedDate: "Dec 8",
      duration: "35 min",
      score: "87%",
      grade: "B+",
      rank: "Rank #3/18",
      action: "View Results"
    }
  ])

  // Handle redirect when user is not authenticated or not a student
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/")
    } else if (!authLoading && user && user.role !== 'student' && user.role !== 'admin') {
      // Redirect professors to their dashboard
      router.push("/professor/dashboard")
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

  const handleAcceptInvitation = () => {
    // Handle invitation acceptance
    console.log("Accepting invitation...")
  }

  const handleDeclineInvitation = () => {
    // Handle invitation decline
    console.log("Declining invitation...")
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Fixed Sidebar */}
      <RoleBasedSidebar currentPath="/student/dashboard" />

      {/* Main Content with left margin for sidebar */}
      <div className="ml-20 bg-white">
        {/* Main Content Area */}
        <div className="p-6">
          {/* Welcome Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Target className="h-6 w-6 text-gray-600" />
                <div>
                  <h1 className="text-2xl font-bold text-black">Welcome back, {user?.full_name || 'Student'}!</h1>
                  <p className="text-gray-600">Ready to tackle some challenging business simulations?</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="flex items-center space-x-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    <span className="font-semibold text-gray-900">Level 7 Strategist</span>
                  </div>
                  <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '83%' }}></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">1,250 / 1,500 XP</p>
                </div>
                
                {/* User Menu with Logout */}
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-gray-700">
                      {user?.full_name?.charAt(0) || 'S'}
                    </span>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleLogout}
                    className="border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    Logout
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="mb-8">
            <div className="flex items-center space-x-2 mb-4">
              <Bell className="h-5 w-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-black">Notifications</h2>
              <Badge className="bg-red-100 text-red-800 text-xs">1 New</Badge>
            </div>
            
            {notifications.map((notification) => (
              <Card key={notification.id} className="bg-white border border-gray-200 mb-4">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900">{notification.title}</h3>
                        {notification.isNew && (
                          <Badge className="bg-blue-100 text-blue-800 text-xs">New</Badge>
                        )}
                      </div>
                      <p className="text-gray-600 text-sm mb-3">{notification.message}</p>
                      <p className="text-xs text-gray-500">{notification.time}</p>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button 
                        size="sm"
                        className="bg-black text-white hover:bg-gray-800"
                        onClick={handleAcceptInvitation}
                      >
                        Join Cohort
                      </Button>
                      <Button 
                        size="sm"
                        variant="outline"
                        className="border-gray-300 text-gray-700 hover:bg-gray-50"
                        onClick={handleDeclineInvitation}
                      >
                        Decline
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <Users className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Active Cohorts</p>
                    <p className="text-2xl font-bold text-gray-900">1</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                    <Shield className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Avg. Score</p>
                    <p className="text-2xl font-bold text-gray-900">91%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                    <Target className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Completed</p>
                    <p className="text-2xl font-bold text-gray-900">2</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
                    <Trophy className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Best Rank</p>
                    <p className="text-2xl font-bold text-gray-900">#1</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Achievements */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-black">Recent Achievements</h2>
              <Link href="#" className="text-sm text-gray-600 hover:text-black flex items-center">
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {achievements.map((achievement) => {
                const Icon = achievement.icon
                return (
                  <Card key={achievement.id} className="bg-yellow-50 border border-yellow-200">
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                          <Icon className="h-5 w-5 text-yellow-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 text-sm">{achievement.title}</h3>
                          <p className="text-xs text-gray-600 mt-1">{achievement.description}</p>
                          {achievement.progress ? (
                            <p className="text-xs text-gray-500 mt-2">Progress: {achievement.progress}</p>
                          ) : (
                            <p className="text-xs text-gray-500 mt-2">Earned {achievement.earnedDate}</p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>

          {/* Active Cohorts */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-black">Active Cohorts</h2>
              <Link href="/student/cohorts" className="text-sm text-gray-600 hover:text-black flex items-center">
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
            
            <div className="space-y-6">
              {activeCohorts.map((cohort) => (
                <Card key={cohort.id} className="bg-white border border-gray-200">
                  <CardHeader className="pb-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg font-bold text-black">{cohort.title}</CardTitle>
                        <p className="text-sm text-gray-600 mt-1">Instructor: {cohort.instructor}</p>
                        <p className="text-sm text-gray-600 mt-2">{cohort.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-100 text-green-800 text-xs">Active</Badge>
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Trophy className="h-4 w-4" />
                          <span>Rank {cohort.currentRank}/18</span>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Simulation Progress</span>
                        <span>{cohort.progress}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${cohort.progressPercentage}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Performance Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Trophy className="h-4 w-4 text-gray-600" />
                          <span className="text-lg font-bold text-gray-900">{cohort.currentRank}</span>
                        </div>
                        <p className="text-xs text-gray-600">Current Rank</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Crown className="h-4 w-4 text-gray-600" />
                          <span className="text-lg font-bold text-gray-900">{cohort.bestRank}</span>
                        </div>
                        <p className="text-xs text-gray-600">Best Rank</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Shield className="h-4 w-4 text-gray-600" />
                          <span className="text-lg font-bold text-gray-900">{cohort.avgScore}</span>
                        </div>
                        <p className="text-xs text-gray-600">Avg. Score</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Star className="h-4 w-4 text-gray-600" />
                          <span className="text-lg font-bold text-gray-900">{cohort.xpEarned}</span>
                        </div>
                        <p className="text-xs text-gray-600">XP Earned</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Calendar className="h-4 w-4 text-gray-600" />
                          <span className="text-lg font-bold text-gray-900">{cohort.joinedDate}</span>
                        </div>
                        <p className="text-xs text-gray-600">Joined</p>
                      </div>
                    </div>
                    
                    {/* Next Simulation */}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">Next Simulation</p>
                        <p className="text-sm text-gray-600">{cohort.nextSimulation}</p>
                      </div>
                      <Button size="sm" className="bg-black text-white hover:bg-gray-800">
                        <BookOpen className="h-4 w-4 mr-2" />
                        Start Now
                      </Button>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Trophy className="h-4 w-4 mr-2" />
                        Leaderboard
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <BookOpen className="h-4 w-4 mr-2" />
                        Simulations
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Discussion
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <UserPlus className="h-4 w-4 mr-2" />
                        Classmates
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Simulations */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-black">Recent Simulations</h2>
              <Link href="/student/simulations" className="text-sm text-gray-600 hover:text-black flex items-center">
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
            
            <div className="space-y-4">
              {recentSimulations.map((simulation) => (
                <Card key={simulation.id} className="bg-white border border-gray-200 rounded-lg shadow-sm">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-bold text-gray-900 text-lg mb-2">{simulation.title}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                          <span>{simulation.course}</span>
                          <span>Completed {simulation.completedDate}</span>
                          <span>{simulation.duration}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Completed
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-sm text-gray-600 mb-2">
                          Score: {simulation.score} ({simulation.grade})
                        </div>
                        <div className="text-sm text-gray-600 mb-2">
                          Rank: {simulation.rank}
                        </div>
                        <Link href="#" className="text-sm text-blue-600 hover:text-blue-800">
                          {simulation.action}
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
