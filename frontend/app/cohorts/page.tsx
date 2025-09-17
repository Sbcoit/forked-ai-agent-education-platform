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
  Plus,
  Calendar,
  Users,
  BookOpen,
  LogOut,
  X,
  ChevronDown
} from "lucide-react"
import Sidebar from "@/components/Sidebar"
import { useAuth } from "@/lib/auth-context"

export default function Cohorts() {
  const router = useRouter()
  const { user, logout, isLoading: authLoading } = useAuth()
  
  // Mock cohort data matching the image exactly
  const [cohorts] = useState([
    {
      id: "CH-A7B3K9X2",
      title: "Business Strategy Fall 2024",
      status: "Active",
      statusColor: "bg-green-100 text-green-800",
      description: "Advanced strategic planning and competitive analysis for senior business students.",
      students: 24,
      simulations: 3,
      date: "Dec 1"
    },
    {
      id: "CH-M4N8P1Q5",
      title: "Financial Management 401",
      status: "Active",
      statusColor: "bg-green-100 text-green-800",
      description: "Corporate finance, investment analysis, and risk management simulations.",
      students: 18,
      simulations: 2,
      date: "Nov 28"
    },
    {
      id: "CH-R9S2T6W1",
      title: "Marketing Analytics Lab",
      status: "Draft",
      statusColor: "bg-yellow-100 text-yellow-800",
      description: "Data-driven marketing decision making with real client case studies.",
      students: 0,
      simulations: 0,
      date: "Dec 8"
    },
    {
      id: "CH-E5F7H3J9",
      title: "Operations Management Spring 2024",
      status: "Archived",
      statusColor: "bg-gray-100 text-gray-800",
      description: "Supply chain optimization and process improvement simulations.",
      students: 32,
      simulations: 4,
      date: "Oct 15"
    }
  ])
  
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
    tags: [] as string[]
  })
  const [showTagDropdown, setShowTagDropdown] = useState(false)
  
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

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleAddTag = (tag: string) => {
    if (!formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }))
    }
    setShowTagDropdown(false)
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleCreateCohort = () => {
    // Here you would typically send the data to your API
    console.log("Creating cohort:", formData)
    
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
      tags: []
    })
    setShowCreateModal(false)
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
      tags: []
    })
  }

  // Filter cohorts based on active filter and search term
  const filteredCohorts = cohorts.filter(cohort => {
    const matchesSearch = cohort.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cohort.description.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (activeFilter === "All") {
      return matchesSearch
    } else if (activeFilter === "Active") {
      return cohort.status === "Active" && matchesSearch
    } else if (activeFilter === "Draft") {
      return cohort.status === "Draft" && matchesSearch
    } else if (activeFilter === "Archived") {
      return cohort.status === "Archived" && matchesSearch
    }
    return matchesSearch
  })

  // Count cohorts by status
  const cohortCounts = {
    "All": cohorts.length,
    "Active": cohorts.filter(c => c.status === "Active").length,
    "Draft": cohorts.filter(c => c.status === "Draft").length,
    "Archived": cohorts.filter(c => c.status === "Archived").length
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Fixed Sidebar */}
      <Sidebar currentPath="/cohorts" />

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
          <div className="flex-1 overflow-y-auto p-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 hover:scrollbar-thumb-gray-400">
            <div className="space-y-4">
              {filteredCohorts.map((cohort) => (
                <Link key={cohort.id} href={`/cohorts/${cohort.id}`}>
                  <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-semibold text-gray-900 leading-tight">
                        {cohort.title}
                      </h3>
                      <Badge className={`ml-2 text-xs ${cohort.statusColor}`}>
                        {cohort.status}
                      </Badge>
                    </div>
                    
                    <p className="text-xs text-gray-600 mb-3 leading-relaxed">
                      {cohort.description}
                    </p>
                    
                    {/* Stats */}
                    <div className="flex items-center space-x-4 text-xs text-gray-600 mb-2">
                      <div className="flex items-center">
                        <Users className="h-3 w-3 mr-1" />
                        {cohort.students}
                      </div>
                      <div className="flex items-center">
                        <BookOpen className="h-3 w-3 mr-1" />
                        {cohort.simulations}
                      </div>
                    </div>
                    
                    {/* Date */}
                    <div className="flex items-center text-xs text-gray-600 mb-2">
                      <Calendar className="h-3 w-3 mr-1" />
                      {cohort.date}
                    </div>
                    
                    {/* ID */}
                    <div className="text-xs text-gray-500">
                      ID: {cohort.id}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content Area - Empty State - Fixed Position */}
        <div className="flex-1 bg-white flex items-center justify-center p-8 h-full">
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-8 max-w-xl w-full flex flex-col justify-center">
            <div className="text-center">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="h-10 w-10 text-gray-400" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Select a Cohort</h2>
              <p className="text-gray-600 mb-6">
                Choose a cohort from the sidebar to view its details, manage students, and assign simulations.
              </p>
              
              <div className="space-y-3 text-left mb-6">
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <Users className="h-4 w-4 text-blue-600" />
                  </div>
                  Manage student enrollment and invitations
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                    <BookOpen className="h-4 w-4 text-purple-600" />
                  </div>
                  Assign and track simulation progress
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                    <Calendar className="h-4 w-4 text-green-600" />
                  </div>
                  Monitor cohort analytics and performance
                </div>
              </div>
              
              <Button 
                onClick={() => setShowCreateModal(true)}
                className="w-full bg-black text-white hover:bg-gray-800"
              >
                Create Your First Cohort
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Create Cohort Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Create New Cohort</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cohort Name *
                    </label>
                    <input
                      type="text"
                      value={formData.cohortName}
                      onChange={(e) => handleInputChange("cohortName", e.target.value)}
                      placeholder="e.g., Business Strategy Fall 2024"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleInputChange("description", e.target.value)}
                      placeholder="Brief description of the cohort and its objectives..."
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {/* Course Details */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Course Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Course Code
                    </label>
                    <input
                      type="text"
                      value={formData.courseCode}
                      onChange={(e) => handleInputChange("courseCode", e.target.value)}
                      placeholder="e.g., BUS-401"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Semester
                    </label>
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => setShowSemesterDropdown(!showSemesterDropdown)}
                        className="w-full px-3 py-2 pr-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent bg-white cursor-pointer hover:border-gray-400 transition-colors text-left flex items-center justify-between"
                      >
                        <span className={formData.semester ? "text-gray-900" : "text-gray-500"}>
                          {formData.semester || "Select semester"}
                        </span>
                        <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${showSemesterDropdown ? 'rotate-180' : ''}`} />
                      </button>
                      
                      {showSemesterDropdown && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-32 overflow-y-auto">
                          <button
                            type="button"
                            onClick={() => {
                              handleInputChange("semester", "")
                              setShowSemesterDropdown(false)
                            }}
                            className="w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm text-gray-500"
                          >
                            Not selected
                          </button>
                          {["Fall", "Spring", "Summer", "Winter"].map((semester) => (
                            <button
                              key={semester}
                              type="button"
                              onClick={() => {
                                handleInputChange("semester", semester)
                                setShowSemesterDropdown(false)
                              }}
                              className="w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm"
                            >
                              {semester}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Year
                    </label>
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => setShowYearDropdown(!showYearDropdown)}
                        className="w-full px-3 py-2 pr-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent bg-white cursor-pointer hover:border-gray-400 transition-colors text-left flex items-center justify-between"
                      >
                        <span className={formData.year ? "text-gray-900" : "text-gray-500"}>
                          {formData.year || "Select year"}
                        </span>
                        <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${showYearDropdown ? 'rotate-180' : ''}`} />
                      </button>
                      
                      {showYearDropdown && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-32 overflow-y-auto">
                          <button
                            type="button"
                            onClick={() => {
                              handleInputChange("year", "")
                              setShowYearDropdown(false)
                            }}
                            className="w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm text-gray-500"
                          >
                            Not selected
                          </button>
                          {(() => {
                            const currentYear = new Date().getFullYear()
                            const years = []
                            for (let i = 0; i <= 5; i++) {
                              years.push((currentYear + i).toString())
                            }
                            return years
                          })().map((year) => (
                            <button
                              key={year}
                              type="button"
                              onClick={() => {
                                handleInputChange("year", year)
                                setShowYearDropdown(false)
                              }}
                              className="w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm"
                            >
                              {year}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Advanced Settings */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Advanced Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Maximum Students
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="1000"
                      step="1"
                      maxLength={4}
                      value={formData.maxStudents}
                      onChange={(e) => {
                        const value = e.target.value.trim()
                        
                        // Allow empty string
                        if (value === '') {
                          handleInputChange("maxStudents", value)
                          return
                        }
                        
                        // Parse and validate the number
                        const numValue = parseInt(value, 10)
                        
                        // Check for valid number, no leading zeros (unless exactly "0"), and within range
                        if (!isNaN(numValue) && 
                            (value === "0" || !value.startsWith("0")) && 
                            numValue >= 1 && 
                            numValue <= 1000) {
                          handleInputChange("maxStudents", value)
                        }
                      }}
                      placeholder="Enter maximum number of students (1-1000)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent"
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Auto-approve student requests</p>
                      <p className="text-xs text-gray-500">Students can join immediately without approval</p>
                    </div>
                    <button
                      onClick={() => handleInputChange("autoApprove", !formData.autoApprove)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        formData.autoApprove ? 'bg-gray-800' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          formData.autoApprove ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Allow self-enrollment</p>
                      <p className="text-xs text-gray-500">Students can find and join this cohort</p>
                    </div>
                    <button
                      onClick={() => handleInputChange("allowSelfEnrollment", !formData.allowSelfEnrollment)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        formData.allowSelfEnrollment ? 'bg-gray-800' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          formData.allowSelfEnrollment ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>

              {/* Tags */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Tags</h3>
                <div className="relative mb-3">
                  <button
                    type="button"
                    onClick={() => setShowTagDropdown(!showTagDropdown)}
                    className="w-full px-3 py-2 pr-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-200 focus:border-transparent bg-white cursor-pointer hover:border-gray-400 transition-colors text-left flex items-center justify-between"
                  >
                    <span className="text-gray-500">Add a tag...</span>
                    <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${showTagDropdown ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {showTagDropdown && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-32 overflow-y-auto">
                      {["Active", "Draft"].map((tag) => (
                        <button
                          key={tag}
                          type="button"
                          onClick={() => handleAddTag(tag)}
                          disabled={formData.tags.includes(tag)}
                          className={`w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm ${
                            formData.tags.includes(tag) ? 'text-gray-400 cursor-not-allowed' : 'text-gray-700'
                          }`}
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className={`px-3 py-1 ${
                          tag === "Active" 
                            ? "bg-green-100 text-green-800" 
                            : tag === "Draft" 
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {tag}
                        <button
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-2 text-gray-500 hover:text-gray-700"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
              <Button
                variant="outline"
                onClick={handleCloseModal}
                className="px-6"
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateCohort}
                className="bg-gray-800 text-white hover:bg-gray-700 px-6"
              >
                Create Cohort
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
