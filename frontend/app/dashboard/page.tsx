"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  FileText, 
  BookOpen, 
  Upload,
  LogOut,
  Package,
  Plus,
  Calendar,
  Users,
  Lightbulb,
  X
} from "lucide-react"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/lib/auth-context"
import { apiClient, Agent, Scenario } from "@/lib/api"

export default function Dashboard() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  // Mock simulation data - replace with real data from API
  const [simulations] = useState([
    {
      id: 1,
      title: "Marketing Strategy Case Study: Digital Transformation",
      status: "Active",
      statusColor: "bg-green-100 text-green-800",
      date: "Dec 8",
      students: 24
    },
    {
      id: 2,
      title: "Financial Analysis: Tech Startup Valuation",
      status: "Active",
      statusColor: "bg-green-100 text-green-800",
      date: "Dec 5",
      students: 18
    },
    {
      id: 3,
      title: "Operations Management: Supply Chain Crisis",
      status: "Draft",
      statusColor: "bg-yellow-100 text-yellow-800",
      date: "Dec 3",
      students: 0
    },
    {
      id: 4,
      title: "Strategic Planning: Market Entry Analysis",
      status: "Active",
      statusColor: "bg-green-100 text-green-800",
      date: "Nov 28",
      students: 32
    },
    {
      id: 5,
      title: "Leadership Challenge: Team Restructuring",
      status: "Active",
      statusColor: "bg-green-100 text-green-800",
      date: "Nov 25",
      students: 15
    },
    {
      id: 6,
      title: "Data Analytics: Customer Segmentation",
      status: "Draft",
      statusColor: "bg-yellow-100 text-yellow-800",
      date: "Nov 22",
      students: 28
    }
  ])

  // Mock cohort data - replace with real data from API
  const [cohorts] = useState([
    {
      id: "CH-A7B3K9X2",
      title: "Business Strategy Fall 2024",
      status: "Active",
      students: 24,
      simulations: 3
    },
    {
      id: "CH-M4N8P105",
      title: "Financial Management 401",
      status: "Active",
      students: 18,
      simulations: 2
    },
    {
      id: "CH-R9S2T6W1",
      title: "Marketing Analytics Lab",
      status: "Draft",
      students: 0,
      simulations: 0
    },
    {
      id: "CH-E5F7H3J9",
      title: "Operations Management Spring 2024",
      status: "Archived",
      students: 32,
      simulations: 4
    }
  ])
  
  const [activeFilter, setActiveFilter] = useState("All")
  const [showWhatsNew, setShowWhatsNew] = useState(true)

  // Calculate stats from actual data
  const activeCohorts = cohorts.filter(cohort => cohort.status === "Active").length
  const activeSimulations = simulations.filter(sim => sim.status === "Active").length
  
  // Handle redirect when user is not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/")
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

  // If no user, show redirecting message (navigation handled in useEffect)
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

  return (
    <div className="min-h-screen bg-white">
      {/* Fixed Sidebar */}
      <Sidebar currentPath="/dashboard" />

      {/* Main Content with left margin for sidebar */}
      <div className="ml-20 bg-white">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-black">Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome back, {user?.full_name || user?.username || 'User'}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-gray-600 hover:text-black">
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="p-6">
          {/* Stats Section */}
          <div className="mb-6">
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <span>{activeCohorts} cohorts active</span>
              <span>{activeSimulations} simulations active</span>
            </div>
          </div>

          {/* What's New Notification */}
          {showWhatsNew && (
            <div className="mb-8">
              <Card className="bg-white border-l-4 border-l-blue-500 shadow-sm">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <Lightbulb className="h-5 w-5 text-blue-500 mt-0.5" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-blue-900 mb-2">What's New</h3>
                        <p className="text-blue-900 text-sm leading-relaxed mb-3">
                          New feature: Real-time collaboration! Students can now work together on simulations with live updates and shared decision-making tools.
                        </p>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="border-blue-300 text-blue-700 hover:bg-blue-50"
                        >
                          Learn More
                        </Button>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowWhatsNew(false)}
                      className="text-gray-400 hover:text-gray-600 p-1"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Getting Started Section */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-black mb-6">Getting started</h2>
            
            <div className="bg-gray-50 rounded-lg py-6 px-4">
              <div className="flex justify-center">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl">
              {/* Create a simulation */}
              <Link href="/simulation-builder">
                <Card className="bg-gray-50 border-gray-200 hover:shadow-lg transition-shadow cursor-pointer">
                  <div className="w-full h-30 overflow-hidden rounded-t-lg">
                    <img src="/createsim.png" alt="Create simulation" className="h-full w-full object-cover" />
                  </div>
                  <CardHeader className="pb-3 pt-3">
                    <CardTitle className="text-base text-gray-800">Create a simulation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-gray-600">Upload a case study, configure parameters and publish</p>
                  </CardContent>
                </Card>
              </Link>

              {/* Set up a cohort */}
              <Card className="bg-gray-50 border-gray-200 hover:shadow-lg transition-shadow cursor-pointer">
                <div className="w-full h-30 overflow-hidden rounded-t-lg">
                  <img src="/cohort.png" alt="Set up cohort" className="h-full w-full object-cover" />
                </div>
                <CardHeader className="pb-3 pt-3">
                  <CardTitle className="text-base text-gray-800">Set up a cohort</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-gray-600">Create a group of students and give them certain simulations</p>
                </CardContent>
              </Card>

              {/* Read our documentation */}
              <Card className="bg-gray-50 border-gray-200 hover:shadow-lg transition-shadow cursor-pointer">
                <div className="w-full h-30 overflow-hidden rounded-t-lg">
                  <img src="/createsim.png" alt="Read documentation" className="h-full w-full object-cover" />
                </div>
                <CardHeader className="pb-3 pt-3">
                  <CardTitle className="text-base text-gray-800">Read our documentation</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-gray-600">Get guides, and further understand the platform</p>
                </CardContent>
              </Card>
                </div>
              </div>
            </div>
          </div>

          {/* My Simulations Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-black">My simulations</h2>
              <Link href="/simulation-builder">
                <Button className="bg-black text-white hover:bg-gray-800 text-sm">
                  <Plus className="h-4 w-4 mr-2" />
                  New Simulation
                </Button>
              </Link>
            </div>
            
            {/* Filter Bar */}
            <div className="flex space-x-2 mb-6">
              {["All", "Draft", "Active"].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setActiveFilter(filter)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    activeFilter === filter
                      ? "bg-gray-200 text-black"
                      : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
            
            {/* Simulations Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {simulations
                .filter(sim => activeFilter === "All" || sim.status === activeFilter)
                .map((simulation) => (
                  <Card key={simulation.id} className="bg-white border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-base font-semibold text-gray-900 leading-tight">
                          {simulation.title}
                        </CardTitle>
                        <Badge className={`ml-2 text-xs ${simulation.statusColor}`}>
                          {simulation.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {simulation.date}
                        </div>
                        <div className="flex items-center">
                          <Users className="h-4 w-4 mr-1" />
                          {simulation.students} students
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
            
            {/* Show message if no simulations match filter */}
            {simulations.filter(sim => activeFilter === "All" || sim.status === activeFilter).length === 0 && (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Package className="h-8 w-8 text-gray-400" />
                </div>
                <p className="text-gray-500 text-base mb-2">No {activeFilter.toLowerCase()} simulations</p>
                <p className="text-gray-400 text-sm mb-4">
                  {activeFilter === "All" 
                    ? "Create your first simulation to get started" 
                    : `No simulations with status "${activeFilter}" found`}
                </p>
                <Link href="/simulation-builder">
                  <Button className="bg-black text-white hover:bg-gray-800 text-sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Create Simulation
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}