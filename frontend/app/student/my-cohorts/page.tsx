"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Search,
  Filter,
  BookOpen,
  Trophy,
  Star,
  Clock,
  Users,
  TrendingUp,
  Calendar,
  ArrowRight,
  Play,
  Eye,
  MessageCircle,
  UserPlus,
  Crown,
  Shield,
  Target
} from "lucide-react"
import RoleBasedSidebar from "@/components/RoleBasedSidebar"
import { useAuth } from "@/lib/auth-context"
import { apiClient } from "@/lib/api"

export default function StudentMyCohorts() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("All Status")
  const [cohorts, setCohorts] = useState<any[]>([])
  const [loadingCohorts, setLoadingCohorts] = useState(true)
  
  // Fetch student cohorts from API
  useEffect(() => {
    const fetchCohorts = async () => {
      if (!user) return
      
      try {
        setLoadingCohorts(true)
        const response = await apiClient.getStudentCohorts()
        setCohorts(response || [])
      } catch (error) {
        console.error('Error fetching student cohorts:', error)
        setCohorts([])
      } finally {
        setLoadingCohorts(false)
      }
    }

    fetchCohorts()
  }, [user])
  
  // Transform API data to match UI expectations
  const transformedCohorts = cohorts.map(cohort => ({
    id: cohort.id,
    title: cohort.title,
    instructor: cohort.professor?.name || 'Unknown',
    description: cohort.description,
    status: cohort.is_active ? 'active' : 'inactive',
    progress: "0/0 completed", // Will be calculated from simulations
    progressPercentage: 0,
    currentRank: "#-",
    bestRank: "#-",
    avgScore: "0%",
    xpEarned: "0",
    joinedDate: new Date(cohort.enrollment_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    nextSimulation: "No simulations assigned",
    totalStudents: cohort.student_count,
    simulations: [] // Will be populated from cohort simulations
  }))
  
  // Mock data - fallback when no real data
  const mockCohorts = [
    {
      id: 1,
      title: "Financial Management 401",
      instructor: "Dr. Michael Chen",
      description: "Master corporate finance through realistic AI-powered business simulations and case studies.",
      status: "active",
      progress: "3/4 completed",
      progressPercentage: 75,
      currentRank: "#2",
      bestRank: "#1",
      avgScore: "88%",
      xpEarned: "1250",
      joinedDate: "Nov 28",
      nextSimulation: "Investment Portfolio Challenge",
      totalStudents: 18,
      simulations: [
        {
          id: 1,
          title: "Investment Portfolio Challenge",
          status: "available",
          progress: "Ready to start",
          progressPercentage: 0,
          ranking: "Not started",
          dueDate: "Dec 15",
          xpReward: "+400 XP"
        },
        {
          id: 2,
          title: "Risk Assessment Simulation",
          status: "in_progress",
          progress: "Scene 2 of 5",
          progressPercentage: 40,
          ranking: "Rank #3/15",
          dueDate: "Dec 20",
          xpReward: "+350 XP"
        },
        {
          id: 3,
          title: "Corporate Valuation",
          status: "completed",
          progress: "Completed",
          progressPercentage: 100,
          ranking: "Rank #1/18",
          completedDate: "Dec 10",
          score: "95%",
          xpEarned: "+380 XP"
        }
      ]
    },
    {
      id: 2,
      title: "Business Strategy Fall 2024",
      instructor: "Dr. Sarah Wilson",
      description: "Experience Harvard Business School case simulations with AI-powered scenarios.",
      status: "active",
      progress: "1/3 completed",
      progressPercentage: 33,
      currentRank: "#5",
      bestRank: "#1",
      avgScore: "92%",
      xpEarned: "750",
      joinedDate: "Dec 1",
      nextSimulation: "Amazon Supply Chain Optimization",
      totalStudents: 24,
      simulations: [
        {
          id: 4,
          title: "Tesla Strategic Analysis",
          status: "completed",
          progress: "Completed",
          progressPercentage: 100,
          ranking: "Rank #1/24",
          completedDate: "Dec 10",
          score: "95%",
          xpEarned: "+350 XP"
        },
        {
          id: 5,
          title: "Amazon Supply Chain Optimization",
          status: "in_progress",
          progress: "Scene 2 of 4",
          progressPercentage: 50,
          ranking: "Rank #5/22",
          dueDate: "Dec 18",
          xpReward: "+300 XP"
        }
      ]
    },
  ]; // Added semicolon here

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

  // Filter cohorts based on search and filters
  const filteredCohorts = transformedCohorts.filter(cohort => {
    const matchesSearch = cohort.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cohort.instructor.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cohort.description.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === "All Status" || 
                         cohort.status === statusFilter.toLowerCase()
    
    return matchesSearch && matchesStatus
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-100 text-green-800 text-xs">Active</Badge>
      case "completed":
        return <Badge className="bg-blue-100 text-blue-800 text-xs">Completed</Badge>
      case "archived":
        return <Badge className="bg-gray-100 text-gray-800 text-xs">Archived</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 text-xs">{status}</Badge>
    }
  }

  const getSimulationStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800 text-xs">Completed</Badge>
      case "available":
        return <Badge className="bg-red-100 text-red-800 text-xs">Available</Badge>
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800 text-xs">In Progress</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 text-xs">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Fixed Sidebar */}
      <RoleBasedSidebar currentPath="/student/my-cohorts" />

      {/* Main Content with left margin for sidebar */}
      <div className="ml-20 bg-white">
        {/* Main Content Area */}
        <div className="p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-black mb-2">My Cohorts</h1>
            <p className="text-gray-600">View your enrolled cohorts, track progress, and access simulations.</p>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center space-x-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search cohorts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
              />
            </div>
            
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
              >
                <option value="All Status">All Status</option>
                <option value="Active">Active</option>
                <option value="Completed">Completed</option>
                <option value="Archived">Archived</option>
              </select>
            </div>
          </div>

          {/* Summary Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <BookOpen className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Cohorts</p>
                    <p className="text-2xl font-bold text-gray-900">{transformedCohorts.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                    <Target className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Active Cohorts</p>
                    <p className="text-2xl font-bold text-gray-900">{transformedCohorts.filter(c => c.status === 'active').length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                    <Trophy className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Best Rank</p>
                    <p className="text-2xl font-bold text-gray-900">#1</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
                    <Star className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total XP</p>
                    <p className="text-2xl font-bold text-gray-900">2,000</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Cohorts List */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-black mb-4">Enrolled Cohorts ({filteredCohorts.length})</h2>
            
            {loadingCohorts ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
                <p className="text-gray-600">Loading cohorts...</p>
              </div>
            ) : filteredCohorts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">No cohorts found</p>
                <p className="text-sm">You haven't joined any cohorts yet.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {filteredCohorts.map((cohort) => (
                <Card key={cohort.id} className="bg-white border border-gray-200">
                  <CardHeader className="pb-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <CardTitle className="text-xl font-bold text-black">{cohort.title}</CardTitle>
                          {getStatusBadge(cohort.status)}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Instructor: {cohort.instructor}</p>
                        <p className="text-sm text-gray-600">{cohort.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Users className="h-4 w-4" />
                          <span>{cohort.totalStudents} students</span>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Overall Progress</span>
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
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
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
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-6">
                      <div>
                        <p className="text-sm font-medium text-gray-900">Next Simulation</p>
                        <p className="text-sm text-gray-600">{cohort.nextSimulation}</p>
                      </div>
                      <Button size="sm" className="bg-black text-white hover:bg-gray-800">
                        <BookOpen className="h-4 w-4 mr-2" />
                        Start Now
                      </Button>
                    </div>
                    
                    {/* Simulations */}
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-black mb-4">Simulations</h3>
                      <div className="space-y-3">
                        {cohort.simulations && cohort.simulations.length > 0 ? (
                          cohort.simulations.map((simulation: any) => (
                          <div key={simulation.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h4 className="font-medium text-gray-900">{simulation.title}</h4>
                                {getSimulationStatusBadge(simulation.status)}
                              </div>
                              <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <span>{simulation.progress}</span>
                                <span>{simulation.ranking}</span>
                                {simulation.dueDate && <span>Due: {simulation.dueDate}</span>}
                                {simulation.completedDate && <span>Completed: {simulation.completedDate}</span>}
                              </div>
                              {simulation.progressPercentage > 0 && simulation.progressPercentage < 100 && (
                                <div className="mt-2">
                                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                                    <div 
                                      className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                                      style={{ width: `${simulation.progressPercentage}%` }}
                                    ></div>
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            <div className="text-right">
                              {simulation.status === "completed" && (
                                <div className="mb-2">
                                  <p className="text-sm font-semibold text-gray-900">{simulation.score}</p>
                                  <p className="text-xs text-gray-600">{simulation.xpEarned}</p>
                                </div>
                              )}
                              {simulation.status === "available" && (
                                <p className="text-xs text-gray-600 mb-2">{simulation.xpReward}</p>
                              )}
                              {simulation.status === "in_progress" && (
                                <p className="text-xs text-gray-600 mb-2">{simulation.xpReward}</p>
                              )}
                              
                              <Button size="sm" variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50">
                                {simulation.status === "completed" && <Eye className="h-4 w-4 mr-2" />}
                                {simulation.status === "available" && <Play className="h-4 w-4 mr-2" />}
                                {simulation.status === "in_progress" && <Play className="h-4 w-4 mr-2" />}
                                {simulation.status === "completed" ? "View Results" : 
                                 simulation.status === "available" ? "Start" : "Continue"}
                              </Button>
                            </div>
                          </div>
                          ))
                        ) : (
                          <div className="text-center py-8 text-gray-500">
                            <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                            <p className="text-lg font-medium mb-2">No simulations assigned yet</p>
                            <p className="text-sm">Your instructor will assign simulations to this cohort soon.</p>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Trophy className="h-4 w-4 mr-2" />
                        Leaderboard
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <BookOpen className="h-4 w-4 mr-2" />
                        All Simulations
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
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
