"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, FileText, Upload, Bot, Plus, X, Wand2, Save, Play, AlertCircle, CheckCircle } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { apiClient, Agent } from "@/lib/api"

export default function ScenarioBuilder() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  
  const [scenarioTitle, setScenarioTitle] = useState("")
  const [scenarioDescription, setScenarioDescription] = useState("")
  const [scenarioIndustry, setScenarioIndustry] = useState("")
  const [scenarioChallenge, setScenarioChallenge] = useState("")
  const [learningObjectives, setLearningObjectives] = useState<string[]>([])
  const [newObjective, setNewObjective] = useState("")
  
  // Task management state
  const [scenarioTasks, setScenarioTasks] = useState<Array<{
    id: string;
    title: string;
    description: string;
    expected_output: string;
    assigned_agent_role?: string;
    execution_order: number;
    depends_on_tasks: string[];
    category?: string;
    tools: string[];
  }>>([])
  const [taskTitle, setTaskTitle] = useState("")
  const [taskDescription, setTaskDescription] = useState("")
  const [taskExpectedOutput, setTaskExpectedOutput] = useState("")
  const [taskAgentRole, setTaskAgentRole] = useState("")
  const [taskCategory, setTaskCategory] = useState("")
  const [taskTools, setTaskTools] = useState<string[]>([])
  const [taskDependencies, setTaskDependencies] = useState<string[]>([])
  
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([])
  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([])
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const industries = [
    "Technology", "Finance", "Healthcare", "Education", "Manufacturing", 
    "Retail", "E-commerce", "Real Estate", "Marketing", "Consulting"
  ]

  const taskCategories = [
    "analysis", "research", "planning", "execution", "communication",
    "data_processing", "content_creation", "decision_making", "monitoring"
  ]

  const agentRoles = [
    "marketing", "finance", "product", "operations", "sales", 
    "customer_service", "hr", "legal", "technical", "strategy"
  ]

  const availableTools = [
    "web_search", "calculator", "email", "database_query", "file_reader",
    "api_caller", "data_analysis", "report_generator", "social_media"
  ]

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user && !loading) {
      router.push('/login')
    }
  }, [user, router, loading])

  // Fetch available agents
  useEffect(() => {
    const fetchAgents = async () => {
      if (!isAuthenticated) return
      
      try {
        const agents = await apiClient.getAgents()
        setAvailableAgents(agents)
      } catch (err) {
        console.error('Error fetching agents:', err)
        setError('Failed to load agents')
      } finally {
        setLoading(false)
      }
    }

    if (isAuthenticated) {
      fetchAgents()
    }
  }, [isAuthenticated])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === "application/pdf") {
      setUploadedFile(file)
      // Simulate AI analysis
      setTimeout(() => {
        setAiSuggestions([
          {
            type: "scenario",
            title: "E-commerce Customer Journey Optimization",
            description: "Based on your PDF, this scenario focuses on improving customer experience across the purchase funnel.",
            industry: "E-commerce",
            challenge: "Optimizing customer conversion rates and reducing cart abandonment",
            objectives: [
              "Analyze customer behavior patterns",
              "Identify conversion bottlenecks",
              "Implement targeted improvements",
              "Measure impact on key metrics"
            ]
          },
          {
            type: "agents",
            suggestions: availableAgents.slice(0, 3).map(agent => ({
              ...agent,
              relevance: Math.floor(Math.random() * 20) + 80
            }))
          }
        ])
      }, 2000)
    }
  }

  const addAgent = (agent: Agent) => {
    if (!selectedAgents.find((a) => a.id === agent.id)) {
      setSelectedAgents([...selectedAgents, agent])
    }
  }

  const removeAgent = (agentId: number) => {
    setSelectedAgents(selectedAgents.filter((a) => a.id !== agentId))
  }

  const addLearningObjective = () => {
    if (newObjective.trim() && !learningObjectives.includes(newObjective.trim())) {
      setLearningObjectives([...learningObjectives, newObjective.trim()])
      setNewObjective("")
    }
  }

  const removeLearningObjective = (index: number) => {
    setLearningObjectives(learningObjectives.filter((_, i) => i !== index))
  }

  // Task management functions
  const addTask = () => {
    if (!taskTitle.trim() || !taskDescription.trim() || !taskExpectedOutput.trim()) {
      setError('Please fill in all required task fields')
      return
    }

    const newTask = {
      id: Date.now().toString(),
      title: taskTitle.trim(),
      description: taskDescription.trim(),
      expected_output: taskExpectedOutput.trim(),
      assigned_agent_role: taskAgentRole || undefined,
      execution_order: scenarioTasks.length + 1,
      depends_on_tasks: taskDependencies,
      category: taskCategory || undefined,
      tools: taskTools
    }

    setScenarioTasks([...scenarioTasks, newTask])
    
    // Clear task form
    setTaskTitle("")
    setTaskDescription("")
    setTaskExpectedOutput("")
    setTaskAgentRole("")
    setTaskCategory("")
    setTaskTools([])
    setTaskDependencies([])
    setError(null)
  }

  const removeTask = (taskId: string) => {
    setScenarioTasks(scenarioTasks.filter(task => task.id !== taskId))
    // Remove this task from dependencies of other tasks
    setScenarioTasks(prevTasks => 
      prevTasks.map(task => ({
        ...task,
        depends_on_tasks: task.depends_on_tasks.filter(depId => depId !== taskId)
      }))
    )
  }

  const toggleTaskTool = (toolId: string) => {
    setTaskTools(prev => 
      prev.includes(toolId) 
        ? prev.filter(id => id !== toolId)
        : [...prev, toolId]
    )
  }

  const toggleTaskDependency = (taskId: string) => {
    setTaskDependencies(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    )
  }

  const applySuggestion = (suggestion: any) => {
    if (suggestion.type === "scenario") {
      setScenarioTitle(suggestion.title)
      setScenarioDescription(suggestion.description)
      setScenarioIndustry(suggestion.industry)
      setScenarioChallenge(suggestion.challenge)
      setLearningObjectives(suggestion.objectives)
    }
  }

  const saveScenario = async () => {
    if (!isAuthenticated) return
    
    if (!scenarioTitle.trim() || !scenarioDescription.trim() || !scenarioIndustry.trim() || !scenarioChallenge.trim()) {
      setError('Please fill in all required fields')
      return
    }

    if (learningObjectives.length === 0) {
      setError('Please add at least one learning objective')
      return
    }

    if (scenarioTasks.length === 0) {
      setError('Please add at least one task to the scenario')
      return
    }

    try {
      setSaving(true)
      setError(null)

      const scenarioData = {
        title: scenarioTitle.trim(),
        description: scenarioDescription.trim(),
        industry: scenarioIndustry,
        challenge: scenarioChallenge.trim(),
        learning_objectives: learningObjectives,
        source_type: uploadedFile ? 'pdf' as const : 'manual' as const,
        pdf_content: uploadedFile ? 'PDF content would be processed here' : undefined,
        is_public: false,
        is_template: false,
        allow_remixes: true,
      }

      const newScenario = await apiClient.createScenario(scenarioData)
      setSuccess('Scenario created successfully!')
      
      // Reset form
      setTimeout(() => {
        setScenarioTitle("")
        setScenarioDescription("")
        setScenarioIndustry("")
        setScenarioChallenge("")
        setLearningObjectives([])
        setSelectedAgents([])
        setUploadedFile(null)
        setAiSuggestions([])
        setSuccess(null)
      }, 2000)
      
    } catch (err) {
      console.error('Error creating scenario:', err)
      setError('Failed to create scenario. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const testScenario = async () => {
    if (!scenarioTitle.trim()) {
      setError('Please enter a scenario title first')
      return
    }
    
    // For now, just navigate to simulation page
    router.push('/simulation')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading scenario builder...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-yellow-500/20 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div className="flex items-center space-x-2">
              <FileText className="h-6 w-6 text-yellow-500" />
              <span className="text-xl font-bold">Scenario Builder</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={testScenario}
              className="border-yellow-500/30 text-yellow-500 bg-transparent"
            >
              <Play className="h-4 w-4 mr-2" />
              Test Scenario
            </Button>
            <Button 
              size="sm" 
              onClick={saveScenario}
              disabled={saving}
              className="bg-yellow-500 text-black hover:bg-yellow-400"
            >
              {saving ? (
                <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin mr-2" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {saving ? 'Saving...' : 'Save Scenario'}
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Create Test Scenario</h1>
            <p className="text-gray-400">Design scenarios to test your AI agents in realistic environments</p>
          </div>

          {error && (
            <Card className="mb-6 bg-red-500/10 border-red-500/30">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2 text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  <p>{error}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {success && (
            <Card className="mb-6 bg-green-500/10 border-green-500/30">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2 text-green-400">
                  <CheckCircle className="h-5 w-5" />
                  <p>{success}</p>
                </div>
              </CardContent>
            </Card>
          )}

          <Tabs defaultValue="source" className="space-y-6">
            <TabsList className="grid w-full grid-cols-5 bg-gray-900">
              <TabsTrigger value="source" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Scenario Source
              </TabsTrigger>
              <TabsTrigger value="details" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Scenario Details
              </TabsTrigger>
              <TabsTrigger value="tasks" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Define Tasks
              </TabsTrigger>
              <TabsTrigger value="agents" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Suggested Agents
              </TabsTrigger>
              <TabsTrigger value="review" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Review & Save
              </TabsTrigger>
            </TabsList>

            <TabsContent value="source" className="space-y-6">
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Manual Creation */}
                <Card className="bg-black border-yellow-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="h-5 w-5 mr-2 text-yellow-500" />
                      Create Manually
                    </CardTitle>
                    <CardDescription>Build your scenario from scratch with full control</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="scenario-title">Scenario Title</Label>
                      <Input
                        id="scenario-title"
                        placeholder="e.g., Customer Onboarding Flow"
                        value={scenarioTitle}
                        onChange={(e) => setScenarioTitle(e.target.value)}
                        className="bg-gray-900 border-gray-700 focus:border-yellow-500"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="scenario-description">Description</Label>
                      <Textarea
                        id="scenario-description"
                        placeholder="Describe what this scenario tests..."
                        value={scenarioDescription}
                        onChange={(e) => setScenarioDescription(e.target.value)}
                        className="bg-gray-900 border-gray-700 focus:border-yellow-500 min-h-[120px]"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* PDF Upload */}
                <Card className="bg-black border-blue-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Upload className="h-5 w-5 mr-2 text-blue-400" />
                      Upload Business Case
                    </CardTitle>
                    <CardDescription>Let AI analyze your PDF and suggest optimal scenarios</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-blue-400/50 transition-colors">
                      <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <p className="text-gray-400 mb-4">Drop your PDF here or click to browse</p>
                      <input type="file" accept=".pdf" onChange={handleFileUpload} className="hidden" id="pdf-upload" />
                      <Button variant="outline" className="border-blue-400/30 text-blue-400 bg-transparent" asChild>
                        <label htmlFor="pdf-upload" className="cursor-pointer">
                          Choose File
                        </label>
                      </Button>
                    </div>

                    {uploadedFile && (
                      <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-blue-400">File Uploaded</span>
                          <Wand2 className="h-4 w-4 text-blue-400 animate-spin" />
                        </div>
                        <p className="text-sm text-gray-400">{uploadedFile.name}</p>
                        <p className="text-sm text-blue-400 mt-2">AI is analyzing your document...</p>
                      </div>
                    )}

                    {aiSuggestions.length > 0 && (
                      <div className="space-y-4">
                        <h4 className="font-medium text-blue-400">AI Suggestions</h4>
                        {aiSuggestions.map((suggestion, index) => (
                          <div key={index} className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            {suggestion.type === "scenario" && (
                              <div>
                                <h5 className="font-medium mb-2">{suggestion.title}</h5>
                                <p className="text-sm text-gray-400 mb-3">{suggestion.description}</p>
                                <Button 
                                  size="sm" 
                                  onClick={() => applySuggestion(suggestion)}
                                  className="bg-blue-500 text-white hover:bg-blue-400"
                                >
                                  Use This Scenario
                                </Button>
                              </div>
                            )}
                            {suggestion.type === "agents" && (
                              <div>
                                <h5 className="font-medium mb-2">Recommended Agents</h5>
                                <div className="space-y-2">
                                  {suggestion.suggestions.map((agent: any) => (
                                    <div
                                      key={agent.id}
                                      className="flex items-center justify-between p-2 bg-gray-900/50 rounded"
                                    >
                                      <span className="text-sm">{agent.name}</span>
                                      <div className="flex items-center space-x-2">
                                        <Badge variant="outline" className="border-blue-400/30 text-blue-400 text-xs">
                                          {agent.relevance}% match
                                        </Badge>
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          onClick={() => addAgent(agent)}
                                        >
                                          <Plus className="h-3 w-3" />
                                        </Button>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="details" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Scenario Details</CardTitle>
                  <CardDescription>Define the business context and learning objectives</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="industry">Industry</Label>
                      <Select value={scenarioIndustry} onValueChange={setScenarioIndustry}>
                        <SelectTrigger className="bg-gray-900 border-gray-700 focus:border-yellow-500">
                          <SelectValue placeholder="Select industry" />
                        </SelectTrigger>
                        <SelectContent className="bg-gray-900 border-gray-700">
                          {industries.map((industry) => (
                            <SelectItem key={industry} value={industry}>
                              {industry}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="challenge">Business Challenge</Label>
                      <Input
                        id="challenge"
                        placeholder="e.g., Reduce customer churn by 20%"
                        value={scenarioChallenge}
                        onChange={(e) => setScenarioChallenge(e.target.value)}
                        className="bg-gray-900 border-gray-700 focus:border-yellow-500"
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label>Learning Objectives</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          placeholder="Add learning objective..."
                          value={newObjective}
                          onChange={(e) => setNewObjective(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && addLearningObjective()}
                          className="bg-gray-900 border-gray-700 focus:border-yellow-500 w-64"
                        />
                        <Button 
                          size="sm" 
                          onClick={addLearningObjective}
                          className="bg-yellow-500 text-black hover:bg-yellow-400"
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {learningObjectives.length > 0 && (
                      <div className="space-y-2">
                        {learningObjectives.map((objective, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                            <span>{objective}</span>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeLearningObjective(index)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tasks" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Scenario Tasks</CardTitle>
                  <CardDescription>
                    Define the tasks that agents will collaborate on to complete this scenario
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Current Tasks */}
                  {scenarioTasks.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="font-medium text-yellow-500">Current Tasks ({scenarioTasks.length})</h4>
                      <div className="space-y-3">
                        {scenarioTasks.map((task, index) => (
                          <div key={task.id} className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center space-x-2">
                                <Badge variant="outline" className="border-yellow-400/30 text-yellow-400">
                                  #{index + 1}
                                </Badge>
                                <h5 className="font-medium">{task.title}</h5>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeTask(task.id)}
                                className="text-red-400 hover:text-red-300"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                            <p className="text-sm text-gray-400 mb-2">{task.description}</p>
                            <div className="flex flex-wrap gap-2 mb-2">
                              {task.assigned_agent_role && (
                                <Badge variant="outline" className="border-blue-400/30 text-blue-400">
                                  Role: {task.assigned_agent_role}
                                </Badge>
                              )}
                              {task.category && (
                                <Badge variant="outline" className="border-purple-400/30 text-purple-400">
                                  {task.category}
                                </Badge>
                              )}
                              {task.tools.map((tool) => (
                                <Badge key={tool} variant="outline" className="border-green-400/30 text-green-400">
                                  {tool}
                                </Badge>
                              ))}
                            </div>
                            <p className="text-xs text-gray-500">Expected: {task.expected_output}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Add New Task */}
                  <div className="border-t border-gray-700 pt-6">
                    <h4 className="font-medium text-yellow-500 mb-4">Add New Task</h4>
                    <div className="space-y-4">
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="task-title">Task Title *</Label>
                          <Input
                            id="task-title"
                            placeholder="e.g., Market Analysis"
                            value={taskTitle}
                            onChange={(e) => setTaskTitle(e.target.value)}
                            className="bg-gray-900 border-gray-700 focus:border-yellow-500"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="task-category">Category</Label>
                          <Select value={taskCategory} onValueChange={setTaskCategory}>
                            <SelectTrigger className="bg-gray-900 border-gray-700 focus:border-yellow-500">
                              <SelectValue placeholder="Select category" />
                            </SelectTrigger>
                            <SelectContent className="bg-gray-900 border-gray-700">
                              {taskCategories.map((category) => (
                                <SelectItem key={category} value={category}>
                                  {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="task-description">Task Description *</Label>
                        <Textarea
                          id="task-description"
                          placeholder="Describe what this task involves..."
                          value={taskDescription}
                          onChange={(e) => setTaskDescription(e.target.value)}
                          className="bg-gray-900 border-gray-700 focus:border-yellow-500 min-h-[100px]"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="task-expected">Expected Output *</Label>
                        <Textarea
                          id="task-expected"
                          placeholder="What should this task produce?"
                          value={taskExpectedOutput}
                          onChange={(e) => setTaskExpectedOutput(e.target.value)}
                          className="bg-gray-900 border-gray-700 focus:border-yellow-500 min-h-[80px]"
                        />
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Assigned Agent Role (Optional)</Label>
                          <Select value={taskAgentRole} onValueChange={setTaskAgentRole}>
                            <SelectTrigger className="bg-gray-900 border-gray-700 focus:border-yellow-500">
                              <SelectValue placeholder="Any agent can handle" />
                            </SelectTrigger>
                            <SelectContent className="bg-gray-900 border-gray-700">
                              {agentRoles.map((role) => (
                                <SelectItem key={role} value={role}>
                                  {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Task Dependencies</Label>
                          <div className="text-sm text-gray-400 mb-2">
                            Select tasks that must be completed before this one:
                          </div>
                          {scenarioTasks.length > 0 ? (
                            <div className="space-y-2 max-h-32 overflow-y-auto">
                              {scenarioTasks.map((task) => (
                                <div key={task.id} className="flex items-center space-x-2">
                                  <input
                                    type="checkbox"
                                    id={`dep-${task.id}`}
                                    checked={taskDependencies.includes(task.id)}
                                    onChange={() => toggleTaskDependency(task.id)}
                                    className="rounded border-gray-600 bg-gray-800"
                                  />
                                  <label htmlFor={`dep-${task.id}`} className="text-sm text-gray-300">
                                    {task.title}
                                  </label>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-500">No tasks created yet</p>
                          )}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Required Tools</Label>
                        <div className="grid grid-cols-3 gap-2">
                          {availableTools.map((tool) => (
                            <div
                              key={tool}
                              className={`p-2 rounded border cursor-pointer text-sm transition-colors ${
                                taskTools.includes(tool)
                                  ? "border-yellow-500 bg-yellow-500/10 text-yellow-400"
                                  : "border-gray-700 hover:border-gray-600 text-gray-300"
                              }`}
                              onClick={() => toggleTaskTool(tool)}
                            >
                              {tool.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </div>
                          ))}
                        </div>
                      </div>

                      <Button 
                        onClick={addTask}
                        className="bg-yellow-500 text-black hover:bg-yellow-400"
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Add Task
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="agents" className="space-y-6">
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Available Agents */}
                <Card className="bg-black border-yellow-500/20">
                  <CardHeader>
                    <CardTitle>Available Agents</CardTitle>
                    <CardDescription>Select agents to participate in your scenario</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {availableAgents.map((agent) => (
                        <div
                          key={agent.id}
                          className="flex items-center justify-between p-3 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <Bot className="h-6 w-6 text-blue-400" />
                            <div>
                              <h4 className="font-medium">{agent.name}</h4>
                              <p className="text-sm text-gray-400">{agent.role}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="border-gray-600 text-gray-400 text-xs">
                              {agent.category}
                            </Badge>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => addAgent(agent)}
                              disabled={selectedAgents.some((a) => a.id === agent.id)}
                              className="border-yellow-500/30 text-yellow-500 hover:bg-yellow-500 hover:text-black disabled:opacity-50"
                            >
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Selected Agents */}
                <Card className="bg-black border-green-500/20">
                  <CardHeader>
                    <CardTitle>Selected Agents ({selectedAgents.length})</CardTitle>
                    <CardDescription>Agents that will participate in your scenario</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {selectedAgents.length === 0 ? (
                      <div className="text-center py-8 text-gray-400">
                        <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No agents selected yet</p>
                        <p className="text-sm">Choose agents from the left panel</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {selectedAgents.map((agent) => (
                          <div
                            key={agent.id}
                            className="flex items-center justify-between p-3 rounded-lg bg-green-500/10 border border-green-500/20"
                          >
                            <div className="flex items-center space-x-3">
                              <Bot className="h-6 w-6 text-green-400" />
                              <div>
                                <h4 className="font-medium">{agent.name}</h4>
                                <p className="text-sm text-gray-400">{agent.role}</p>
                              </div>
                            </div>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeAgent(agent.id)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="review" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Scenario Review</CardTitle>
                  <CardDescription>Review your scenario configuration before saving</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Scenario Title</h4>
                        <p>{scenarioTitle || "Untitled Scenario"}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Description</h4>
                        <p className="text-sm text-gray-400">{scenarioDescription || "No description provided"}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Industry</h4>
                        <p className="text-sm text-gray-400">{scenarioIndustry || "Not specified"}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Business Challenge</h4>
                        <p className="text-sm text-gray-400">{scenarioChallenge || "Not specified"}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Learning Objectives ({learningObjectives.length})</h4>
                        <div className="space-y-2">
                          {learningObjectives.map((objective, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                              <span className="text-sm">{objective}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Selected Agents ({selectedAgents.length})</h4>
                        <div className="space-y-2">
                          {selectedAgents.map((agent) => (
                            <div key={agent.id} className="flex items-center space-x-2">
                              <Bot className="h-4 w-4 text-blue-400" />
                              <span className="text-sm">{agent.name}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-end space-x-4 pt-6 border-t border-gray-700">
                    <Button 
                      variant="outline" 
                      onClick={testScenario}
                      className="border-yellow-500/30 text-yellow-500 bg-transparent"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Test Scenario
                    </Button>
                    <Button 
                      onClick={saveScenario}
                      disabled={saving}
                      className="bg-yellow-500 text-black hover:bg-yellow-400"
                    >
                      {saving ? (
                        <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin mr-2" />
                      ) : (
                        <Save className="h-4 w-4 mr-2" />
                      )}
                      {saving ? 'Saving...' : 'Save Scenario'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
