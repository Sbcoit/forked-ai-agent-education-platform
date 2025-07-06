"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, Play, Pause, Square, Bot, Clock, CheckCircle, BarChart3, AlertCircle } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { apiClient, type Scenario, type Agent, type Task, type SimulationMessage } from "@/lib/api"

interface Simulation {
  simulation_id: number
  scenario: {
    id: number
    title: string
    description: string
    industry: string
    challenge: string
  }
  status: string // Allow any status string from the API
  results?: any
  message?: string
  messages?: SimulationMessage[]
  created_at?: string
  updated_at?: string
}

interface SimulationStep {
  id: number
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  agent: string
  message: string
}

export default function SimulationRunner() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null)
  const [simulation, setSimulation] = useState<Simulation | null>(null)
  const [simulationStatus, setSimulationStatus] = useState<"idle" | "running" | "paused" | "completed" | "failed">("idle")
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [simulationSteps, setSimulationSteps] = useState<SimulationStep[]>([])

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user && !loading) {
      router.push('/login')
    }
  }, [user, router, loading])

  // Fetch scenarios on component mount
  useEffect(() => {
    const fetchScenarios = async () => {
      if (!isAuthenticated) return
      
      try {
        const data = await apiClient.getScenarios()
        setScenarios(data)
      } catch (err) {
        console.error('Error fetching scenarios:', err)
        setError('Failed to load scenarios')
      } finally {
        setLoading(false)
      }
    }

    if (isAuthenticated) {
      fetchScenarios()
    }
  }, [isAuthenticated])

  const startSimulation = async (scenario: Scenario) => {
    if (!isAuthenticated) return
    
    try {
      setSelectedScenario(scenario)
      setSimulationStatus("running")
      setProgress(0)
      setCurrentStep(0)
      setError(null)

      // Initialize simulation steps based on scenario learning objectives
      const steps: SimulationStep[] = scenario.learning_objectives.map((objective, index) => ({
        id: index + 1,
        name: objective,
        status: index === 0 ? 'running' : 'pending',
        agent: `Agent ${index + 1}`,
        message: `Processing: ${objective}`,
      }))
      setSimulationSteps(steps)

      // Create simulation via API
      const simulationData = await apiClient.startSimulation(scenario.id)
      setSimulation(simulationData)
      
      // Start polling for simulation status
      pollSimulationStatus(simulationData.simulation_id)
    } catch (err) {
      console.error('Error starting simulation:', err)
      setError('Failed to start simulation')
      setSimulationStatus("failed")
    }
  }

  const pollSimulationStatus = async (simulationId: number) => {
    if (!isAuthenticated) return
    
    const pollInterval = setInterval(async () => {
      try {
        const data = await apiClient.getSimulationHistory(simulationId)
        setSimulation(data as Simulation)
        
        // Update progress based on simulation status
        if (data.status === 'completed') {
          setProgress(100)
          setSimulationStatus("completed")
          clearInterval(pollInterval)
          
          // Update all steps to completed
          setSimulationSteps(prev => prev.map(step => ({
            ...step,
            status: 'completed',
            message: 'Task completed successfully'
          })))
        } else if (data.status === 'failed') {
          setSimulationStatus("failed")
          clearInterval(pollInterval)
          setError('Simulation failed')
        } else if (data.status === 'running') {
          // Simulate progress
          setProgress(prev => Math.min(prev + 10, 90))
        }
      } catch (err) {
        console.error('Error polling simulation status:', err)
        clearInterval(pollInterval)
        setError('Failed to get simulation status')
      }
    }, 2000)
  }

  const pauseSimulation = async () => {
    if (!simulation || !isAuthenticated) return
    
    try {
      // Note: This would require backend support for pausing simulations
      setSimulationStatus("paused")
    } catch (err) {
      console.error('Error pausing simulation:', err)
    }
  }

  const stopSimulation = async () => {
    if (!simulation || !isAuthenticated) return
    
    try {
      // Note: This would require backend support for stopping simulations
      setSimulationStatus("idle")
      setProgress(0)
      setCurrentStep(0)
      setSelectedScenario(null)
      setSimulation(null)
      setSimulationSteps([])
    } catch (err) {
      console.error('Error stopping simulation:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading scenarios...</p>
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
              <Play className="h-6 w-6 text-yellow-500" />
              <span className="text-xl font-bold">Simulation Runner</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {simulationStatus === "running" && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={pauseSimulation}
                  className="border-yellow-500/30 text-yellow-500 bg-transparent"
                >
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={stopSimulation}
                  className="border-red-500/30 text-red-400 bg-transparent"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Run Agent Simulations</h1>
            <p className="text-gray-400">Test your AI agents in realistic scenarios and analyze their performance</p>
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

          {simulationStatus === "idle" ? (
            // Scenario Selection
            <div className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Select a Scenario</CardTitle>
                  <CardDescription>Choose a scenario to run with your AI agents</CardDescription>
                </CardHeader>
                <CardContent>
                  {scenarios.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No scenarios available</p>
                      <p className="text-sm mb-4">Create a scenario first to run simulations</p>
                      <Button asChild className="bg-yellow-500 text-black hover:bg-yellow-400">
                        <Link href="/scenario-builder">Create Scenario</Link>
                      </Button>
                    </div>
                  ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {scenarios.map((scenario) => (
                        <Card
                          key={scenario.id}
                          className="bg-gray-900/50 border-gray-700 hover:border-yellow-500/50 transition-colors cursor-pointer"
                        >
                          <CardHeader>
                            <CardTitle className="text-lg">{scenario.title}</CardTitle>
                            <CardDescription className="text-gray-400">{scenario.description}</CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="flex justify-between text-sm">
                              <div className="flex items-center space-x-1">
                                <Bot className="h-4 w-4 text-blue-400" />
                                <span>{scenario.agents.length} agents</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <CheckCircle className="h-4 w-4 text-green-400" />
                                <span>{scenario.tasks.length} tasks</span>
                              </div>
                            </div>
                            <div className="flex justify-between text-sm text-gray-400">
                              <div className="flex items-center space-x-1">
                                <Clock className="h-4 w-4" />
                                <span>Est. {scenario.tasks.length * 2}-{scenario.tasks.length * 3} min</span>
                              </div>
                              <span>Created: {new Date(scenario.created_at).toLocaleDateString()}</span>
                            </div>
                            <Button
                              onClick={() => startSimulation(scenario)}
                              className="w-full bg-yellow-500 text-black hover:bg-yellow-400"
                            >
                              <Play className="h-4 w-4 mr-2" />
                              Run Simulation
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            // Simulation Running
            <div className="space-y-6">
              {/* Simulation Header */}
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center">
                        <div
                          className={`w-3 h-3 rounded-full mr-3 ${
                            simulationStatus === "running"
                              ? "bg-green-400 animate-pulse"
                              : simulationStatus === "paused"
                                ? "bg-yellow-500"
                                : simulationStatus === "completed"
                                  ? "bg-blue-400"
                                  : simulationStatus === "failed"
                                    ? "bg-red-400"
                                    : "bg-gray-400"
                          }`}
                        />
                        {selectedScenario?.title}
                      </CardTitle>
                      <CardDescription>{selectedScenario?.description}</CardDescription>
                    </div>
                    <Badge
                      variant={
                        simulationStatus === "running"
                          ? "default"
                          : simulationStatus === "paused"
                            ? "secondary"
                            : simulationStatus === "completed"
                              ? "outline"
                              : simulationStatus === "failed"
                                ? "destructive"
                                : "secondary"
                      }
                      className={
                        simulationStatus === "running"
                          ? "bg-green-500/20 text-green-400"
                          : simulationStatus === "paused"
                            ? "bg-yellow-500/20 text-yellow-500"
                            : simulationStatus === "completed"
                              ? "bg-blue-500/20 text-blue-400"
                              : simulationStatus === "failed"
                                ? "bg-red-500/20 text-red-400"
                                : ""
                      }
                    >
                      {simulationStatus.charAt(0).toUpperCase() + simulationStatus.slice(1)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <span>Progress</span>
                      <span>{progress}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                    <div className="flex justify-between text-sm text-gray-400">
                      <span>Est. time: {selectedScenario?.tasks.length || 0 * 2}-{selectedScenario?.tasks.length || 0 * 3} min</span>
                      <span>Step {currentStep + 1} of {simulationSteps.length}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid lg:grid-cols-2 gap-6">
                {/* Live Activity */}
                <Card className="bg-black border-blue-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Bot className="h-5 w-5 mr-2 text-blue-400" />
                      Live Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {simulationSteps.map((step) => (
                        <div
                          key={step.id}
                          className={`p-3 rounded-lg border ${
                            step.status === "completed"
                              ? "border-green-500/30 bg-green-500/10"
                              : step.status === "running"
                                ? "border-yellow-500/30 bg-yellow-500/10"
                                : step.status === "failed"
                                  ? "border-red-500/30 bg-red-500/10"
                                  : "border-gray-700 bg-gray-900/50"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {step.status === "completed" && <CheckCircle className="h-4 w-4 text-green-400" />}
                              {step.status === "running" && (
                                <div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
                              )}
                              {step.status === "failed" && <AlertCircle className="h-4 w-4 text-red-400" />}
                              {step.status === "pending" && (
                                <div className="w-4 h-4 border border-gray-600 rounded-full" />
                              )}
                              <span className="font-medium">{step.name}</span>
                            </div>
                            <Badge variant="outline" className="border-blue-400/30 text-blue-400 text-xs">
                              {step.agent}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-400">{step.message}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Simulation Results */}
                <Card className="bg-black border-purple-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <BarChart3 className="h-5 w-5 mr-2 text-purple-400" />
                      Simulation Results
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {simulation?.results ? (
                      <div className="space-y-4">
                        <div className="p-3 rounded-lg bg-gray-900/50">
                          <h4 className="font-medium mb-2">Performance Metrics</h4>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-400">Success Rate:</span>
                              <span className="ml-2 text-green-400">
                                {simulation.results.success_rate || 'N/A'}%
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-400">Avg Response Time:</span>
                              <span className="ml-2 text-blue-400">
                                {simulation.results.avg_response_time || 'N/A'}s
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        {simulation.results.agent_performance && (
                          <div className="space-y-2">
                            <h4 className="font-medium">Agent Performance</h4>
                            {Object.entries(simulation.results.agent_performance).map(([agent, metrics]: [string, any]) => (
                              <div key={agent} className="p-2 bg-gray-900/50 rounded">
                                <div className="flex justify-between text-sm">
                                  <span>{agent}</span>
                                  <span className="text-green-400">{metrics.accuracy || 'N/A'}%</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-400">
                        <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Results will appear here</p>
                        <p className="text-sm">during simulation execution</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {simulationStatus === "completed" && (
                <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30">
                  <CardHeader>
                    <CardTitle className="flex items-center text-blue-400">
                      <CheckCircle className="h-6 w-6 mr-2" />
                      Simulation Completed Successfully
                    </CardTitle>
                    <CardDescription>Your agents have completed all tasks in the scenario</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex space-x-4">
                      <Button className="bg-blue-500 text-white hover:bg-blue-400">
                        View Detailed Results
                      </Button>
                      <Button variant="outline" className="border-blue-400/30 text-blue-400 bg-transparent">
                        Export Report
                      </Button>
                      <Button variant="ghost" onClick={stopSimulation} className="text-gray-400">
                        Run Another Simulation
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {simulationStatus === "failed" && (
                <Card className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border-red-500/30">
                  <CardHeader>
                    <CardTitle className="flex items-center text-red-400">
                      <AlertCircle className="h-6 w-6 mr-2" />
                      Simulation Failed
                    </CardTitle>
                    <CardDescription>There was an error during simulation execution</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex space-x-4">
                      <Button variant="outline" className="border-red-400/30 text-red-400 bg-transparent">
                        View Error Details
                      </Button>
                      <Button variant="ghost" onClick={stopSimulation} className="text-gray-400">
                        Try Again
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
