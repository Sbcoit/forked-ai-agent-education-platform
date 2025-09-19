"use client"

import { useState, useEffect } from "react"
import { debugLog } from "@/lib/debug"
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
  X,
  ChevronDown,
  Check,
  Play,
  Trash2,
  Edit
} from "lucide-react"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/lib/auth-context"
import { apiClient, Agent, Scenario } from "@/lib/api"

export default function Dashboard() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  // Real data from API
  const [simulations, setSimulations] = useState<any[]>([])
  const [cohorts, setCohorts] = useState<any[]>([])
  const [simulationsLoading, setSimulationsLoading] = useState(true)
  const [cohortsLoading, setCohortsLoading] = useState(true)
  const [simulationsError, setSimulationsError] = useState<string | null>(null)
  const [cohortsError, setCohortsError] = useState<string | null>(null)
  
  const [activeFilter, setActiveFilter] = useState("All")
  const [showWhatsNew, setShowWhatsNew] = useState(true)
  const [editingStatus, setEditingStatus] = useState<number | null>(null)
  const [statusUpdating, setStatusUpdating] = useState<number | null>(null)
  
  // State for deletion
  const [deletingScenario, setDeletingScenario] = useState<number | null>(null)
  
  // Request deduplication - prevent multiple simultaneous API calls
  const [pendingRequests, setPendingRequests] = useState<Set<string>>(new Set())

  // Close status editor when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (editingStatus !== null) {
        const target = event.target as HTMLElement
        if (!target.closest('.status-editor')) {
          setEditingStatus(null)
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [editingStatus])

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch simulations
        setSimulationsLoading(true)
        setSimulationsError(null)
        const simulationsData = await apiClient.getSimulations()
        setSimulations(simulationsData)
      } catch (error) {
        console.error('Failed to fetch simulations:', error)
        // Check if it's an authentication error
        if (error instanceof Error && error.message.includes('Authentication failed')) {
          // Logout and redirect to login
          logout()
          router.push('/')
          return
        }
        setSimulationsError('Failed to load simulations')
        // Fallback to empty array
        setSimulations([])
      } finally {
        setSimulationsLoading(false)
      }

      try {
        // Fetch cohorts (placeholder - no API endpoint yet)
        setCohortsLoading(true)
        setCohortsError(null)
        // TODO: Replace with real API call when endpoint is available
        // const cohortsData = await apiClient.getCohorts()
        setCohorts([])
      } catch (error) {
        console.error('Failed to fetch cohorts:', error)
        setCohortsError('Failed to load cohorts')
        setCohorts([])
      } finally {
        setCohortsLoading(false)
      }
    }

    if (user && !authLoading) {
      fetchData()
    }
  }, [user, authLoading])

  // Refresh function
  const refreshData = async () => {
    try {
      setSimulationsLoading(true)
      setCohortsLoading(true)
      setSimulationsError(null)
      setCohortsError(null)
      
      const simulationsData = await apiClient.getSimulations()
      setSimulations(simulationsData)
      
      // TODO: Replace with real API call when endpoint is available
      setCohorts([])
    } catch (error) {
      console.error('Failed to refresh data:', error)
      // Check if it's an authentication error
      if (error instanceof Error && error.message.includes('Authentication failed')) {
        // Logout and redirect to login
        logout()
        router.push('/')
        return
      }
      setSimulationsError('Failed to refresh data')
      setCohortsError('Failed to refresh data')
    } finally {
      setSimulationsLoading(false)
      setCohortsLoading(false)
    }
  }

  // Update simulation status
  const updateSimulationStatus = async (simulationId: number, newStatus: string) => {
    try {
      setStatusUpdating(simulationId)
      debugLog(`Updating scenario ${simulationId} to status: ${newStatus}`)
      
      await apiClient.updateScenarioStatus(simulationId, newStatus)
      
      // Update local state
      setSimulations(prev => prev.map(sim => 
        sim.id === simulationId 
          ? { 
              ...sim, 
              status: newStatus === 'active' ? 'Active' : 'Draft',
              statusColor: newStatus === 'active' ? 'bg-green-100 text-green-800' : 
                          'bg-yellow-100 text-yellow-800',
              is_draft: newStatus === 'draft' // Update is_draft field
            }
          : sim
      ))
      
      // If simulation was published (draft -> active), refresh cohorts data
      // This ensures any cohorts with this simulation will show the updated status
      if (newStatus === 'active') {
        debugLog('Simulation published, refreshing cohorts data...')
        try {
          const cohortsData = await apiClient.getCohorts()
          setCohorts(cohortsData)
          
          // Notify cohorts page to refresh simulation data
          localStorage.setItem('simulationStatusChanged', JSON.stringify({
            simulationId,
            newStatus,
            timestamp: Date.now()
          }))
        } catch (error) {
          console.warn('Failed to refresh cohorts data:', error)
        }
      }
      
      setEditingStatus(null)
      debugLog(`Successfully updated scenario ${simulationId} to ${newStatus}`)
    } catch (error) {
      console.error('Failed to update status:', error)
      debugLog(`Error updating scenario ${simulationId}:`, error)
      
      // If scenario not found, refresh the data to get current state
      if (error instanceof Error && error.message.includes('Scenario not found')) {
        debugLog('Scenario not found, refreshing data...')
        await refreshData()
        alert('Scenario not found. Data has been refreshed.')
      } else {
        alert('Failed to update simulation status. Please try again.')
      }
    } finally {
      setStatusUpdating(null)
    }
  }

  // Play simulation - navigate to chat-box with scenario data
  const playSimulation = (simulation: any) => {
    // Check if simulation is draft
    if (simulation.is_draft || simulation.status === 'Draft') {
      alert('Cannot play draft simulations. Please publish the simulation first.')
      return
    }
    
    // Store scenario data for chat-box
    const chatboxData = {
      scenario_id: simulation.id,
      title: simulation.title
    }
    
    localStorage.setItem("chatboxScenario", JSON.stringify(chatboxData))
    
    // Navigate to chat-box
    router.push("/chat-box")
  }

  // Delete draft simulation
  const deleteDraftSimulation = async (simulationId: number) => {
    if (!confirm('Are you sure you want to delete this draft simulation? This action cannot be undone.')) {
      return
    }
    
    try {
      setDeletingScenario(simulationId)
      await apiClient.deleteDraftScenario(simulationId)
      
      // Remove from local state
      setSimulations(prev => prev.filter(sim => sim.id !== simulationId))
      
    } catch (error) {
      console.error('Failed to delete simulation:', error)
      alert('Failed to delete simulation. Please try again.')
    } finally {
      setDeletingScenario(null)
    }
  }

  // Edit draft simulation - navigate to simulation builder with draft ID
  const editDraftSimulation = async (simulation: any) => {
    const requestKey = `edit-${simulation.id}`
    
    // Prevent duplicate requests
    if (pendingRequests.has(requestKey)) {
      debugLog(`Request already pending for ${requestKey}`)
      return
    }
    
    try {
      setPendingRequests(prev => new Set(prev).add(requestKey))
      
      debugLog("=== EDIT DRAFT SIMULATION DEBUG ===")
      debugLog("Navigating to edit draft simulation:", simulation.id)
      debugLog("Simulation is_draft:", simulation.is_draft)
      console.log("Simulation published_version_id:", simulation.published_version_id)
      console.log("Simulation status:", simulation.status)
      console.log("Simulation full object:", simulation)
      console.log("All simulations:", simulations.map(s => ({ 
        id: s.id, 
        unique_id: s.unique_id,
        is_draft: s.is_draft, 
        published_version_id: s.published_version_id,
        draft_of_id: s.draft_of_id,
        status: s.status
      })))
      
      // If this is a published simulation, we need to find its draft
      if (!simulation.is_draft) {
        console.log("Looking for draft of published scenario:", simulation.id)
        console.log("Published scenario details:", { id: simulation.id, is_draft: simulation.is_draft, published_version_id: simulation.published_version_id })
        
        // Find the draft scenario that has this published scenario as its published_version_id
        const draftSimulation = simulations.find(s => s.published_version_id === simulation.id && s.is_draft)
        if (draftSimulation) {
          console.log("Found draft scenario:", draftSimulation.id)
          router.push(`/simulation-builder?edit=${draftSimulation.id}`)
          return
        } else {
          console.log("No draft found for published scenario:", simulation.id)
          console.log("Available simulations:", simulations.map(s => ({ id: s.id, is_draft: s.is_draft, published_version_id: s.published_version_id })))
          alert("No draft found for this published simulation")
          return
        }
      }
      
      // Navigate directly with the draft ID as a URL parameter
      router.push(`/simulation-builder?edit=${simulation.id}`)
      
    } catch (error) {
      console.error('Failed to navigate to draft editing:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      alert(`Failed to open draft for editing: ${errorMessage}`)
    } finally {
      setPendingRequests(prev => {
        const newSet = new Set(prev)
        newSet.delete(requestKey)
        return newSet
      })
    }
  }

  // Calculate stats from actual data
  const activeCohorts = cohorts.filter(cohort => cohort.status === "Active").length
  const activeSimulations = simulations.filter(sim => sim.status === "Active").length
  
  // Debug: Log simulations data
  debugLog('All simulations:', simulations.map(s => ({ 
    id: s.id, 
    unique_id: s.unique_id,
    is_draft: s.is_draft, 
    published_version_id: s.published_version_id,
    draft_of_id: s.draft_of_id,
    status: s.status
  })))
  
  // Handle redirect when user is not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/")
    }
  }, [user?.id, authLoading, router]) // More specific dependency
  
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
        <div className="p-6 pb-40">
          {/* Stats Section */}
          <div className="mb-12">
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <span>{activeCohorts} cohorts active</span>
              <span>{activeSimulations} simulations active</span>
            </div>
          </div>

          {/* What's New Notification */}
          {showWhatsNew && (
            <div className="mb-16">
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
          <div className="mt-16">
            <div className="flex items-center justify-between mb-8">
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
            
            {/* Loading State */}
            {simulationsLoading && (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600"></div>
                </div>
                <p className="text-gray-500 text-base">Loading simulations...</p>
              </div>
            )}

            {/* Error State */}
            {simulationsError && !simulationsLoading && (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <X className="h-8 w-8 text-red-500" />
                </div>
                <p className="text-red-500 text-base mb-2">Failed to load simulations</p>
                <p className="text-gray-400 text-sm mb-4">{simulationsError}</p>
                <Button onClick={refreshData} variant="outline" size="sm">
                  Try Again
                </Button>
              </div>
            )}

            {/* Simulations Grid */}
            {!simulationsLoading && !simulationsError && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-8">
                {simulations
                  .filter(sim => activeFilter === "All" || sim.status === activeFilter)
                  .map((simulation) => (
                  <Card key={simulation.id} className="bg-white border border-gray-200 hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-4 px-4 sm:px-6 pt-4 sm:pt-6">
                      {/* Header Container - Title and Status */}
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                        <CardTitle className="text-base sm:text-lg font-semibold text-gray-900 leading-tight cursor-pointer hover:text-blue-600 transition-colors flex-1 min-w-0"
                          onClick={() => playSimulation(simulation)}
                        >
                          <span className="block truncate">{simulation.title}</span>
                          {simulation.unique_id && (
                            <span className="text-xs text-gray-500 font-mono mt-1 block">ID: {simulation.unique_id}</span>
                          )}
                        </CardTitle>
                        <div className="relative status-editor flex-shrink-0">
                          {editingStatus === simulation.id ? (
                            <div className="flex items-center space-x-2">
                              <select
                                value={simulation.status === 'Active' ? 'active' : 'draft'}
                                onChange={(e) => updateSimulationStatus(simulation.id, e.target.value)}
                                className="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                                disabled={statusUpdating === simulation.id}
                              >
                                <option value="draft">Draft</option>
                                <option value="active">Active</option>
                              </select>
                              {statusUpdating === simulation.id && (
                                <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                              )}
                            </div>
                          ) : (
                            <div className="flex items-center space-x-2">
                              <Badge 
                                className={`text-xs ${simulation.statusColor} cursor-pointer hover:opacity-80`}
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setEditingStatus(simulation.id)
                                }}
                              >
                                {simulation.status}
                              </Badge>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setEditingStatus(simulation.id)
                                }}
                                className="text-gray-400 hover:text-gray-600 transition-colors"
                              >
                                <ChevronDown className="h-3 w-3" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0 px-4 sm:px-6 pb-4 sm:pb-6">
                      {/* Content Container - Metadata and Actions */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-sm text-gray-600">
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-2 flex-shrink-0" />
                            <span>{simulation.date}</span>
                          </div>
                          <div className="flex items-center">
                            <Users className="h-4 w-4 mr-2 flex-shrink-0" />
                            <span>{simulation.students} students</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-end sm:justify-start gap-2 flex-wrap">
                          <Button
                            onClick={(e) => {
                              e.stopPropagation()
                              playSimulation(simulation)
                            }}
                            disabled={simulation.is_draft || simulation.status === 'Draft'}
                            className={`text-sm px-3 sm:px-4 py-2 h-8 flex-shrink-0 ${
                              (simulation.is_draft || simulation.status === 'Draft')
                                ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-700 text-white'
                            }`}
                          >
                            <Play className="h-4 w-4 mr-1 flex-shrink-0" />
                            <span className="hidden sm:inline">{(simulation.is_draft || simulation.status === 'Draft') ? 'Draft' : 'Play'}</span>
                            <span className="sm:hidden">{(simulation.is_draft || simulation.status === 'Draft') ? 'Draft' : 'Play'}</span>
                          </Button>
                          
                          {/* Edit and Delete buttons for draft simulations */}
                          {(simulation.is_draft || simulation.status === 'Draft') && (
                            <>
                              <Button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  debugLog('Edit button clicked for simulation:', simulation)
                                  editDraftSimulation(simulation)
                                }}
                                variant="outline"
                                size="sm"
                                className="h-8 px-3 flex-shrink-0"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteDraftSimulation(simulation.id)
                                }}
                                disabled={deletingScenario === simulation.id}
                                variant="destructive"
                                size="sm"
                                className="h-8 px-3 flex-shrink-0"
                              >
                                {deletingScenario === simulation.id ? (
                                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                ) : (
                                  <Trash2 className="h-4 w-4" />
                                )}
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                {/* Show message if no simulations match filter */}
                {simulations.filter(sim => activeFilter === "All" || sim.status === activeFilter).length === 0 && (
                  <div className="text-center py-8 col-span-full">
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
            )}
          </div>
        </div>
      </div>
    </div>
  )
}