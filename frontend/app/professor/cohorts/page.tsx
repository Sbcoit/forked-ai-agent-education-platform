"use client"

import { useState, useEffect } from "react"
import { debugLog } from "@/lib/debug"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Search,
  Filter,
  Plus,
  Calendar,
  Users,
  BookOpen,
  LogOut,
  X,
  ChevronDown,
  Trash2,
  ArrowLeft,
  Copy,
  Settings,
  CheckCircle,
  Clock,
  MoreVertical
} from "lucide-react"
import RoleBasedSidebar from "@/components/RoleBasedSidebar"
import { useAuth } from "@/lib/auth-context"
import { apiClient } from "@/lib/api"
import InviteStudentsModal from "@/components/InviteStudentsModal"

export default function Cohorts() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  // State for cohorts data
  const [cohorts, setCohorts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [activeFilter, setActiveFilter] = useState("All")
  const [searchTerm, setSearchTerm] = useState("")
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showSemesterDropdown, setShowSemesterDropdown] = useState(false)
  const [showYearDropdown, setShowYearDropdown] = useState(false)
  const [showStatusDropdown, setShowStatusDropdown] = useState(false)
  
  // Form state for create cohort modal
  const [formData, setFormData] = useState({
    cohortName: "",
    description: "",
    courseCode: "",
    semester: "",
    year: "",
    maxStudents: "",
    autoApprove: true,
    allowSelfEnrollment: false,
    isActive: true, // Add status field
    tags: [] as string[] // Array for tags
  })
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [cohortToDelete, setCohortToDelete] = useState<any>(null)
  const [showTagDropdown, setShowTagDropdown] = useState(false)
  
  // State for inline cohort details
  const [selectedCohort, setSelectedCohort] = useState<any>(null)
  const [cohortDetails, setCohortDetails] = useState<any>(null)
  const [cohortStudents, setCohortStudents] = useState<any[]>([])
  const [cohortSimulations, setCohortSimulations] = useState<any[]>([])
  const [loadingDetails, setLoadingDetails] = useState(false)
  const [activeTab, setActiveTab] = useState('students')
  const [studentSearchTerm, setStudentSearchTerm] = useState('')
  const [studentFilter, setStudentFilter] = useState('all')
  
  // Simulation assignment state
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [availableScenarios, setAvailableScenarios] = useState<any[]>([])
  const [selectedScenario, setSelectedScenario] = useState<any>(null)
  const [dueDate, setDueDate] = useState("")
  const [isRequired, setIsRequired] = useState(true)
  const [assigning, setAssigning] = useState(false)
  const [deletingSimulation, setDeletingSimulation] = useState<number | null>(null)
  
  // Invite students modal state
  const [showInviteModal, setShowInviteModal] = useState(false)
  
  // Fetch available scenarios for assignment
  const fetchAvailableScenarios = async () => {
    try {
      const scenarios = await apiClient.getScenarios()
      setAvailableScenarios(scenarios)
    } catch (error) {
      console.error('Failed to fetch scenarios:', error)
    }
  }

  // Handle simulation assignment
  const handleAssignSimulation = async () => {
    if (!selectedScenario || !selectedCohort) return
    
    try {
      setAssigning(true)
      
      // Create the assignment data
      const assignmentData = {
        simulation_id: selectedScenario.id,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        is_required: isRequired
      }
      
      // Call the API to assign simulation to cohort
      await apiClient.assignSimulationToCohort(selectedCohort.id, assignmentData)
      
      // Refresh simulations data
      const updatedSimulations = await apiClient.getCohortSimulations(selectedCohort.unique_id)
      setCohortSimulations(updatedSimulations)
      
      // Close modal and reset form
      setShowAssignModal(false)
      setSelectedScenario(null)
      setDueDate("")
      setIsRequired(true)
      
    } catch (error) {
      console.error('Failed to assign simulation:', error)
      alert('Failed to assign simulation. Please try again.')
    } finally {
      setAssigning(false)
    }
  }

  // Handle simulation deletion
  const handleDeleteSimulation = async (simulationAssignmentId: number) => {
    if (!selectedCohort) return
    
    try {
      setDeletingSimulation(simulationAssignmentId)
      
      // Call the API to remove simulation from cohort
      await apiClient.removeSimulationFromCohort(selectedCohort.id, simulationAssignmentId)
      
      // Refresh simulations data
      const updatedSimulations = await apiClient.getCohortSimulations(selectedCohort.unique_id)
      setCohortSimulations(updatedSimulations)
      
    } catch (error) {
      console.error('Failed to delete simulation:', error)
      alert('Failed to delete simulation. Please try again.')
    } finally {
      setDeletingSimulation(null)
    }
  }

  // Fetch cohort details when a cohort is selected
  const fetchCohortDetails = async (cohortId: number | string) => {
    try {
      setLoadingDetails(true)
      // Find the cohort in the list to get its unique_id
      const cohort = cohorts.find(c => c.id === cohortId || c.unique_id === cohortId)
      if (!cohort) {
        throw new Error('Cohort not found')
      }
      
      const details = await apiClient.getCohort(cohort.unique_id)
      setCohortDetails(details)
      
      // Fetch students and simulations
      const [students, simulations] = await Promise.all([
        apiClient.getCohortStudents(cohort.unique_id).catch(() => []),
        apiClient.getCohortSimulations(cohort.unique_id).catch(() => [])
      ])
      
      setCohortStudents(students)
      setCohortSimulations(simulations)
    } catch (error) {
      console.error('Failed to fetch cohort details:', error)
    } finally {
      setLoadingDetails(false)
    }
  }

  // Fetch cohorts data on component mount
  useEffect(() => {
    const fetchCohorts = async () => {
      try {
        setLoading(true)
        setError(null)
        const cohortsData = await apiClient.getCohorts()
        setCohorts(cohortsData)
      } catch (err) {
        console.error('Error fetching cohorts:', err)
        setError(err instanceof Error ? err.message : 'Failed to load cohorts')
      } finally {
        setLoading(false)
      }
    }
    
    fetchCohorts()
  }, [])

  // Listen for simulation status changes from dashboard
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'simulationStatusChanged' && e.newValue) {
        try {
          const changeData = JSON.parse(e.newValue)
          debugLog('Simulation status changed, refreshing cohorts data:', changeData)
          
          // Refresh cohorts data to get updated simulation statuses
          const refreshCohorts = async () => {
            try {
              const cohortsData = await apiClient.getCohorts()
              setCohorts(cohortsData)
              
              // If we have a selected cohort, refresh its simulation data too
              if (selectedCohort) {
                const updatedSimulations = await apiClient.getCohortSimulations(selectedCohort.unique_id)
                setCohortSimulations(updatedSimulations)
              }
            } catch (error) {
              console.warn('Failed to refresh cohorts data after simulation status change:', error)
            }
          }
          
          refreshCohorts()
          
          // Clear the notification
          localStorage.removeItem('simulationStatusChanged')
        } catch (error) {
          console.error('Failed to parse simulation status change notification:', error)
        }
      }
    }
    
    window.addEventListener('storage', handleStorageChange)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [selectedCohort])

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

  // Show loading while fetching cohorts
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-black">Loading cohorts...</p>
        </div>
      </div>
    )
  }

  // Show error if failed to load cohorts
  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSelectTag = (tag: string) => {
      setFormData(prev => ({
        ...prev,
      tags: [tag] // Only allow one tag at a time
      }))
    setShowTagDropdown(false)
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleCohortClick = async (cohort: any) => {
    try {
      setLoadingDetails(true)
      setSelectedCohort(cohort)
      
      // Fetch detailed cohort data
      const [details, students, simulations] = await Promise.all([
        apiClient.getCohort(cohort.unique_id || cohort.id),
        apiClient.getCohortStudents(cohort.unique_id || cohort.id).catch(() => []),
        apiClient.getCohortSimulations(cohort.unique_id || cohort.id).catch(() => [])
      ])
      
      setCohortDetails(details)
      setCohortStudents(students)
      setCohortSimulations(simulations)
    } catch (err) {
      console.error('Error fetching cohort details:', err)
      setError('Failed to load cohort details')
    } finally {
      setLoadingDetails(false)
    }
  }

  const handleBackToList = () => {
    setSelectedCohort(null)
    setCohortDetails(null)
    setCohortStudents([])
    setCohortSimulations([])
  }

  const handleCreateCohort = async () => {
    // Validate required fields before making API call
    if (!formData.cohortName.trim()) {
      setError('Cohort name is required')
      return
    }
    
    try {
      setLoading(true)
      setError(null) // Clear any previous errors
      
      // Transform form data to match backend schema
      const cohortData = {
        title: formData.cohortName,
        description: formData.description || null,
        course_code: formData.courseCode || null,
        semester: formData.semester || null,
        year: formData.year ? parseInt(formData.year) : null,
        max_students: formData.maxStudents ? parseInt(formData.maxStudents) : null,
        auto_approve: formData.autoApprove,
        allow_self_enrollment: formData.allowSelfEnrollment,
        is_active: formData.isActive
      }
      
      const newCohort = await apiClient.createCohort(cohortData)
      
      // Add the new cohort with proper counts (they start at 0)
      const cohortWithCounts = {
        ...newCohort,
        student_count: 0,
        simulation_count: 0
      }
      
      setCohorts(prev => [...prev, cohortWithCounts])
      
      // Reset form and close modal
      setFormData({
        cohortName: "",
        description: "",
        courseCode: "",
        semester: "",
        year: "",
        maxStudents: "",
        autoApprove: true,
        allowSelfEnrollment: false,
        isActive: true,
        tags: []
      })
      setShowCreateModal(false)
    } catch (err) {
      console.error('Error creating cohort:', err)
      setError(err instanceof Error ? err.message : 'Failed to create cohort')
    } finally {
      setLoading(false)
    }
  }

  const handleCloseModal = () => {
    setShowCreateModal(false)
    setShowSemesterDropdown(false)
    setShowYearDropdown(false)
    setShowTagDropdown(false)
    setShowStatusDropdown(false)
    // Reset form when closing
    setFormData({
      cohortName: "",
      description: "",
      courseCode: "",
      semester: "",
      year: "",
      maxStudents: "",
      autoApprove: true,
      allowSelfEnrollment: false,
      isActive: true,
      tags: []
    })
  }

  const handleDeleteCohort = async () => {
    if (!cohortToDelete) return
    
    try {
      setLoading(true)
      setError(null)
      await apiClient.deleteCohort(cohortToDelete.unique_id || cohortToDelete.id.toString())
      setCohorts(prev => prev.filter(cohort => cohort.id !== cohortToDelete.id))
      setShowDeleteModal(false)
      setCohortToDelete(null)
    } catch (err) {
      console.error('Error deleting cohort:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete cohort')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteClick = (cohort: any, e: React.MouseEvent) => {
    e.preventDefault() // Prevent Link navigation
    e.stopPropagation() // Stop event bubbling
    setCohortToDelete(cohort)
    setShowDeleteModal(true)
  }

  // Filter cohorts based on active filter and search term
  const filteredCohorts = cohorts.filter(cohort => {
    const matchesSearch = cohort.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (cohort.description && cohort.description.toLowerCase().includes(searchTerm.toLowerCase()))
    
    if (activeFilter === "All") {
      return matchesSearch
    } else if (activeFilter === "Active") {
      return cohort.is_active && matchesSearch
    } else if (activeFilter === "Draft") {
      return !cohort.is_active && matchesSearch
    } else if (activeFilter === "Archived") {
      return !cohort.is_active && matchesSearch
    }
    return matchesSearch
  })

  // Count cohorts by status
  const cohortCounts = {
    "All": cohorts.length,
    "Active": cohorts.filter(c => c.is_active).length,
    "Draft": cohorts.filter(c => !c.is_active).length,
    "Archived": cohorts.filter(c => !c.is_active).length
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Fixed Sidebar */}
      <RoleBasedSidebar currentPath="/professor/cohorts" />

      {/* Main Content with left margin for sidebar */}
      <div className="ml-20 flex h-screen">
        {/* Middle Sidebar - Cohort Management */}
        <div className="w-96 bg-white border-r border-gray-200 flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold text-black">Cohorts</h1>
              <Button 
                onClick={() => setShowCreateModal(true)}
                className="bg-black text-white hover:bg-gray-800 text-sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create
              </Button>
            </div>
            
            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search cohorts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
              />
            </div>
            
            {/* Filter Dropdown */}
            <div className="relative">
              <Button 
                variant="outline" 
                onClick={() => setShowStatusDropdown(!showStatusDropdown)}
                className="w-full bg-gray-50 border-gray-200 hover:bg-gray-100 justify-start"
              >
                <Filter className="h-4 w-4 mr-2" />
                {activeFilter} ({cohortCounts[activeFilter as keyof typeof cohortCounts]})
                <ChevronDown className={`h-4 w-4 ml-auto transition-transform ${showStatusDropdown ? 'rotate-180' : ''}`} />
              </Button>
              
              {showStatusDropdown && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                  {Object.entries(cohortCounts).map(([filter, count]) => (
                    <button
                      key={filter}
                      onClick={() => {
                        setActiveFilter(filter)
                        setShowStatusDropdown(false)
                      }}
                      className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${
                        activeFilter === filter
                          ? "bg-gray-100 text-black font-medium"
                          : "text-gray-700"
                      }`}
                    >
                      {filter} ({count})
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Cohort Listings */}
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 hover:scrollbar-thumb-gray-400">
            <div className="space-y-3">
              {filteredCohorts.map((cohort) => (
                <div 
                  key={cohort.id} 
                  onClick={() => handleCohortClick(cohort)}
                  className={`bg-white border rounded-lg p-5 hover:shadow-lg transition-all duration-200 cursor-pointer ${
                    selectedCohort?.id === cohort.id 
                      ? 'border-gray-400 bg-gray-50 shadow-md' 
                      : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 leading-tight hover:text-gray-700 mb-1">
                        {cohort.title}
                      </h3>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={`text-xs px-2 py-1 rounded-full transition-colors duration-200 ${
                        cohort.is_active 
                          ? 'bg-green-100 text-green-700 hover:bg-black hover:text-white' 
                          : 'bg-gray-100 text-gray-600 hover:bg-black hover:text-white'
                      }`}>
                        {cohort.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteClick(cohort, e)
                        }}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                        title="Delete cohort"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    </div>
                    
                  <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                    {cohort.description || 'No description provided'}
                    </p>
                    
                  {/* Stats and Date Row */}
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-1.5" />
                        <span className="font-medium">{cohort.student_count || 0}</span>
                      </div>
                      <div className="flex items-center">
                        <BookOpen className="h-4 w-4 mr-1.5" />
                        <span className="font-medium">{cohort.simulation_count || 0}</span>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1.5" />
                      <span>{new Date(cohort.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                    </div>
                    </div>
                    
                    {/* ID */}
                  <div className="text-xs text-gray-500 font-mono hover:bg-black hover:text-white px-2 py-1 rounded transition-colors duration-200 cursor-pointer">
                    ID: {cohort.unique_id || cohort.id}
                    </div>
                  </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content Area - Cohort Details or Empty State */}
        <div className="flex-1 bg-white h-full">
          {selectedCohort && cohortDetails ? (
            <div className="h-full overflow-y-auto p-8">
              {/* Back Button */}
              <div className="mb-6">
                <button
                  onClick={handleBackToList}
                  className="inline-flex items-center text-sm text-gray-600 hover:text-black transition-colors"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Cohorts
                </button>
              </div>

              {/* Cohort Header */}
              <div className="mb-8">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-black mb-2">{cohortDetails.title}</h2>
                    <p className="text-gray-600 mb-4">{cohortDetails.description || 'No description provided'}</p>
                    
                    <div className="flex items-center space-x-4">
                      <Badge className="bg-gray-100 text-gray-700 text-xs px-2 py-1 hover:bg-black hover:text-white transition-colors duration-200 cursor-pointer">
                        ID: {cohortDetails.unique_id || cohortDetails.id}
                      </Badge>
                      <Badge className={`text-xs px-2 py-1 transition-colors duration-200 ${
                        cohortDetails.is_active 
                          ? 'bg-green-100 text-green-700 hover:bg-black hover:text-white' 
                          : 'bg-gray-100 text-gray-600 hover:bg-black hover:text-white'
                      }`}>
                        {cohortDetails.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <span className="text-sm text-gray-600">
                        Created {new Date(cohortDetails.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-3">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        const inviteLink = `${window.location.origin}/cohorts/${cohortDetails.unique_id || cohortDetails.id}/join`;
                        navigator.clipboard.writeText(inviteLink);
                      }}
                      className="border-gray-300 text-gray-700 hover:bg-gray-50"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy Invite Link
                    </Button>
                    <Button 
                      size="sm"
                      className="bg-black text-white hover:bg-gray-800"
                      onClick={() => setShowInviteModal(true)}
                    >
                      <Users className="h-4 w-4 mr-2" />
                      Invite Students
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="text-gray-600 hover:text-black"
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Metrics Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Total Students */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center h-full">
                    {/* Left Section - Icon */}
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                      <Users className="h-6 w-6 text-blue-600" />
                    </div>
                    {/* Right Section - Text Stack */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-600 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">Total Students</div>
                      <div className="text-2xl font-bold text-gray-900 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">{cohortStudents?.length || 0}</div>
                    </div>
                  </div>
                </div>

                {/* Active Students */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center h-full">
                    {/* Left Section - Icon */}
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                    {/* Right Section - Text Stack */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-600 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">Active Students</div>
                      <div className="text-2xl font-bold text-gray-900 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">
                        {cohortStudents?.filter(student => student.status === 'approved').length || 0}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Simulations */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center h-full">
                    {/* Left Section - Icon */}
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                      <BookOpen className="h-6 w-6 text-purple-600" />
                    </div>
                    {/* Right Section - Text Stack */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-600 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">Simulations</div>
                      <div className="text-2xl font-bold text-gray-900 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">{cohortSimulations?.length || 0}</div>
                    </div>
                  </div>
                </div>

                {/* Avg. Completion */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center h-full">
                    {/* Left Section - Icon */}
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                      <Clock className="h-6 w-6 text-orange-600" />
                    </div>
                    {/* Right Section - Text Stack */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-600 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">Avg. Completion</div>
                      <div className="text-2xl font-bold text-gray-900 truncate hover:whitespace-normal hover:overflow-visible transition-all duration-200">
                        {cohortStudents?.length > 0 
                          ? Math.round((cohortStudents.filter(student => student.status === 'approved').length / cohortStudents.length) * 100) 
                          : 0}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tabs Navigation */}
              <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                  {[
                    { id: 'students', label: 'Students' },
                    { id: 'simulations', label: 'Simulations' },
                    { id: 'analytics', label: 'Analytics' },
                    { id: 'settings', label: 'Settings' }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        activeTab === tab.id
                          ? 'border-black text-black'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>

              {/* Tab Content */}
              {activeTab === 'students' && (
                <div>
                  {/* Search and Filter */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="relative flex-1 max-w-md">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search students..."
                        value={studentSearchTerm}
                        onChange={(e) => setStudentSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:border-transparent"
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <Filter className="h-4 w-4 text-gray-400" />
                      <select
                        value={studentFilter}
                        onChange={(e) => setStudentFilter(e.target.value)}
                        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-black focus:border-transparent"
                      >
                        <option value="all">All Students</option>
                        <option value="active">Active</option>
                        <option value="pending">Pending</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </div>
                  </div>

                  {/* Student List */}
                  <div className="space-y-3">
                    {cohortStudents?.filter(student => {
                      const matchesSearch = student.student_name.toLowerCase().includes(studentSearchTerm.toLowerCase()) ||
                                           student.student_email.toLowerCase().includes(studentSearchTerm.toLowerCase())
                      
                      if (studentFilter === 'all') return matchesSearch
                      if (studentFilter === 'active') return student.status === 'approved' && matchesSearch
                      if (studentFilter === 'pending') return student.status === 'pending' && matchesSearch
                      if (studentFilter === 'inactive') return student.status === 'inactive' && matchesSearch
                      return matchesSearch
                    }).map((student, index) => (
                      <div key={student.id} className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
                        <div className="flex items-center space-x-4">
                          {/* Avatar */}
                          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-600">
                              {student.student_name.split(' ').map((n: string) => n[0]).join('').toUpperCase()}
                            </span>
                          </div>
                          
                          {/* Student Info */}
                          <div>
                            <h4 className="font-medium text-gray-900">{student.student_name}</h4>
                            <p className="text-sm text-gray-500">{student.student_email}</p>
                            <div className="flex items-center space-x-4 mt-1">
                              <span className="text-xs text-gray-500">
                                Completed: {Math.floor(Math.random() * 5)} | Pending: {Math.floor(Math.random() * 3)}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          {/* Status Badge */}
                          <Badge className={`text-xs px-2 py-1 ${
                            student.status === 'approved' 
                              ? 'bg-green-100 text-green-700' 
                              : student.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {student.status === 'approved' ? 'Active' : student.status === 'pending' ? 'Pending' : 'Inactive'}
                          </Badge>
                          
                          {/* Joined Date */}
                          <span className="text-xs text-gray-500">
                            Joined {new Date(student.enrollment_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                          </span>
                          
                          {/* Options */}
                          <button className="p-1 text-gray-400 hover:text-gray-600">
                            <MoreVertical className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                    
                    {cohortStudents?.length === 0 && (
                      <div className="text-center py-8">
                        <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">No students enrolled in this cohort yet.</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'simulations' && (
                <div>
                  {/* Header */}
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-black">Assigned Simulations</h3>
                    <Button 
                      onClick={() => {
                        fetchAvailableScenarios()
                        setShowAssignModal(true)
                      }}
                      className="bg-black text-white hover:bg-gray-800 text-sm"
                    >
                      <BookOpen className="h-4 w-4 mr-2" />
                      Assign Simulation
                    </Button>
                  </div>

                  {/* Simulations List */}
                  <div className="space-y-4">
                    {cohortSimulations.length === 0 ? (
                      <div className="text-center py-8">
                        <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500 mb-4">No simulations assigned yet</p>
                        <Button 
                          onClick={() => {
                            fetchAvailableScenarios()
                            setShowAssignModal(true)
                          }}
                          className="bg-black text-white hover:bg-gray-800"
                        >
                          <BookOpen className="h-4 w-4 mr-2" />
                          Assign First Simulation
                        </Button>
                      </div>
                    ) : (
                      cohortSimulations.map((simulation) => {
                        
                        // Calculate completion data (mock data for now - would come from API)
                        const totalStudents = cohortStudents.filter(s => s.status === 'approved').length
                        const completedStudents = Math.floor(Math.random() * totalStudents) // Mock completion
                        const completionPercentage = totalStudents > 0 ? (completedStudents / totalStudents) * 100 : 0
                        
                        return (
                          <div key={simulation.id} className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                  <h4 className="font-bold text-gray-900 text-lg">
                                    {simulation.simulation?.title || `Simulation ${simulation.simulation_id}`}
                                  </h4>
                                  <button
                                    onClick={() => handleDeleteSimulation(simulation.id)}
                                    disabled={deletingSimulation === simulation.id}
                                    className="text-red-500 hover:text-red-700 disabled:opacity-50"
                                  >
                                    {deletingSimulation === simulation.id ? (
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-500"></div>
                                    ) : (
                                      <X className="h-4 w-4" />
                                    )}
                                  </button>
                                </div>
                                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                                  <span>
                                    Assigned {new Date(simulation.assigned_at).toLocaleDateString('en-US', { 
                                      month: 'short', 
                                      day: 'numeric' 
                                    })}
                                  </span>
                                  {simulation.due_date && (
                                    <span>
                                      Due {new Date(simulation.due_date).toLocaleDateString('en-US', { 
                                        month: 'short', 
                                        day: 'numeric' 
                                      })}
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-center space-x-2">
                                  {simulation.simulation?.is_draft ? (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                      Draft
                                    </span>
                                  ) : (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                      Active
                                    </span>
                                  )}
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    simulation.is_required 
                                      ? 'bg-red-100 text-red-800' 
                                      : 'bg-blue-100 text-blue-800'
                                  }`}>
                                    {simulation.is_required ? 'Required' : 'Optional'}
                                  </span>
                                </div>
                              </div>
                              
                              <div className="text-right">
                                <div className="text-sm text-gray-600 mb-2">
                                  {completedStudents}/{totalStudents} completed
                                </div>
                                <div className="w-32 bg-gray-200 rounded-full h-2">
                                  <div 
                                    className="bg-gray-800 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${completionPercentage}%` }}
                                  ></div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })
                    )}
                    </div>
                  </div>
              )}

              {activeTab === 'analytics' && (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Analytics tab content coming soon.</p>
                </div>
              )}

              {activeTab === 'settings' && (
                <div className="text-center py-8">
                  <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Settings tab content coming soon.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No cohort selected</h3>
                <p className="text-gray-500">Select a cohort from the list to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Cohort Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Create New Cohort</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cohort Name
                  </label>
                  <input
                    type="text"
                    value={formData.cohortName}
                    onChange={(e) => setFormData({...formData, cohortName: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., Business Strategy Fall 2024"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                    placeholder="Brief description of the cohort..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Course Code
                    </label>
                    <input
                      type="text"
                      value={formData.courseCode}
                      onChange={(e) => setFormData({...formData, courseCode: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., BUS 101"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Students
                    </label>
                    <input
                      type="number"
                      value={formData.maxStudents}
                      onChange={(e) => setFormData({...formData, maxStudents: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="30"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Semester
                    </label>
                    <select
                      value={formData.semester}
                      onChange={(e) => setFormData({...formData, semester: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select Semester</option>
                      <option value="Fall">Fall</option>
                      <option value="Spring">Spring</option>
                      <option value="Summer">Summer</option>
                      <option value="Winter">Winter</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Year
                    </label>
                    <select
                      value={formData.year}
                      onChange={(e) => setFormData({...formData, year: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select Year</option>
                      {Array.from({ length: 10 }, (_, i) => {
                        const year = new Date().getFullYear() + i;
                        return (
                          <option key={year} value={year.toString()}>
                            {year}
                          </option>
                        );
                      })}
                    </select>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="autoApprove"
                      checked={formData.autoApprove}
                      onChange={(e) => setFormData({...formData, autoApprove: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="autoApprove" className="ml-2 text-sm text-gray-700">
                      Auto-approve student enrollments
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="allowSelfEnrollment"
                      checked={formData.allowSelfEnrollment}
                      onChange={(e) => setFormData({...formData, allowSelfEnrollment: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="allowSelfEnrollment" className="ml-2 text-sm text-gray-700">
                      Allow self-enrollment
                    </label>
                  </div>
                </div>

                {/* Status Pills */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, isActive: true})}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                        formData.isActive
                          ? 'bg-green-100 text-green-800 border-2 border-green-300'
                          : 'bg-gray-100 text-gray-600 border-2 border-gray-200 hover:bg-gray-200'
                      }`}
                    >
                      Active
                    </button>
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, isActive: false})}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                        !formData.isActive
                          ? 'bg-yellow-100 text-yellow-800 border-2 border-yellow-300'
                          : 'bg-gray-100 text-gray-600 border-2 border-gray-200 hover:bg-gray-200'
                      }`}
                    >
                      Draft
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
                <Button
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateCohort}
                  className="bg-black text-white hover:bg-gray-800"
                >
                  Create Cohort
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
              <div className="p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Delete Cohort</h2>
                <p className="text-gray-600 mb-6">
                  Are you sure you want to delete "{cohortToDelete?.title}"? This action cannot be undone.
                </p>
                <div className="flex justify-end space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleDeleteCohort}
                    className="bg-red-600 text-white hover:bg-red-700"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Assign Simulation Modal */}
        {showAssignModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Assign Simulation</h2>
                <button
                  onClick={() => setShowAssignModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select Simulation
                  </label>
                  <select
                    value={selectedScenario?.id || ""}
                    onChange={(e) => {
                      const scenario = availableScenarios.find(s => s.id === e.target.value)
                      setSelectedScenario(scenario)
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Choose a simulation...</option>
                    {availableScenarios.map((scenario) => (
                      <option key={scenario.id} value={scenario.id}>
                        {scenario.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Due Date (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="isRequired"
                    checked={isRequired}
                    onChange={(e) => setIsRequired(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="isRequired" className="ml-2 text-sm text-gray-700">
                    Required assignment
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
                <Button
                  variant="outline"
                  onClick={() => setShowAssignModal(false)}
                  disabled={assigning}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAssignSimulation}
                  disabled={!selectedScenario || assigning}
                  className="bg-black text-white hover:bg-gray-800"
                >
                  {assigning ? "Assigning..." : "Assign Simulation"}
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Invite Students Modal */}
        {selectedCohort && (
          <InviteStudentsModal
            isOpen={showInviteModal}
            onClose={() => setShowInviteModal(false)}
            cohortId={selectedCohort.id}
            cohortTitle={selectedCohort.title}
            onSuccess={() => {
              // Refresh cohort details to show updated student count
              if (selectedCohort) {
                fetchCohortDetails(selectedCohort.id)
              }
            }}
          />
        )}
      </div>
  )
}
