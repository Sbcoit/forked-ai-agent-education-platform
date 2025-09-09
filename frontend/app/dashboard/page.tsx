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
  Package
} from "lucide-react"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/lib/auth-context"
import { apiClient, Agent, Scenario } from "@/lib/api"

export default function Dashboard() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  const [agents, setAgents] = useState<Agent[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    // Commented out auth check for development
    // if (!authLoading && !user) {
    //   router.push("/")
    //   return
    // }

    // if (user) {
    //   loadDashboardData()
    // }
    
    // Load dashboard data without auth for now
    loadDashboardData()
  }, [user, authLoading, router])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Commented out API calls for development - just show empty state
      // const [userAgents, allScenarios] = await Promise.all([
      //   apiClient.getUserAgents(user!.id),
      //   apiClient.getScenarios()
      // ])
      
      // setAgents(userAgents.slice(0, 3)) // Show only recent 3 agents
      // setScenarios(allScenarios.slice(0, 3)) // Show only recent 3 scenarios
      
      // Set empty arrays for now
      setAgents([])
      setScenarios([])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  // Commented out loading check for development
  // if (authLoading || loading) {
  //   return (
  //     <div className="min-h-screen bg-white flex items-center justify-center">
  //       <div className="text-center">
  //         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
  //         <p className="text-black">Loading your dashboard...</p>
  //       </div>
  //     </div>
  //   )
  // }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={loadDashboardData} className="bg-black text-white hover:bg-gray-800">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  // Commented out user check for development
  // if (!user) return null

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
              <h1 className="text-xl font-bold text-black">Dashboard</h1>
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
          {/* Getting Started Section */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-black mb-6">Getting started</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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

              {/* Create a simulation (duplicate) */}
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
            </div>
          </div>

          {/* My Simulations Section */}
          <div>
            <h2 className="text-2xl font-bold text-black mb-6">My simulations</h2>
            
            {scenarios.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Package className="h-8 w-8 text-gray-400" />
                </div>
                <p className="text-gray-500 text-base mb-2">No simulations yet</p>
                <p className="text-gray-400 text-sm mb-4">Create your first simulation to get started</p>
                <Link href="/simulation-builder">
                  <Button className="bg-black text-white hover:bg-gray-800 text-sm">
                    Create Simulation
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {scenarios.map((scenario) => (
                  <Card key={scenario.id} className="bg-white border-gray-200 hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{scenario.title}</CardTitle>
                      <p className="text-sm text-gray-600">{scenario.description}</p>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="border-gray-300 text-gray-600">
                          {scenario.difficulty}
                        </Badge>
                        <Button size="sm" variant="ghost" className="text-black hover:text-gray-600">
                          View
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