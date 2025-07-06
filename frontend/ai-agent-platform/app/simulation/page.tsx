"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { ArrowLeft, Play, Bot, CheckCircle, Users, Settings, Zap } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { apiClient, type Scenario, type Agent } from "@/lib/api"

export default function SimulationRunner() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null)
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([])
  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([])
  const [processType, setProcessType] = useState<"sequential" | "hierarchical" | "collaborative">("sequential")
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3>(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user && !loading) {
      router.push('/login')
    }
  }, [user, router, loading])

  // Fetch scenarios and agents on component mount
  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated) return
      
      try {
        const [scenariosData, agentsData] = await Promise.all([
          apiClient.getScenarios(),
          apiClient.getAgents()
        ])
        setScenarios(scenariosData)
        setAvailableAgents(agentsData)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load scenarios and agents')
      } finally {
        setLoading(false)
      }
    }

    if (isAuthenticated) {
      fetchData()
    }
  }, [isAuthenticated])

  const selectScenario = (scenario: Scenario) => {
    setSelectedScenario(scenario)
    setCurrentStep(2)
    setError(null)
  }

  const toggleAgent = (agent: Agent) => {
    setSelectedAgents(prev => {
      const exists = prev.find(a => a.id === agent.id)
      if (exists) {
        return prev.filter(a => a.id !== agent.id)
      } else {
        return [...prev, agent]
      }
    })
  }

  const proceedToProcessSelection = () => {
    if (selectedAgents.length === 0) {
      setError('Please select at least one agent')
      return
    }
    setCurrentStep(3)
    setError(null)
  }

  const startSimulation = async () => {
    if (!selectedScenario || selectedAgents.length === 0) return
    
    try {
      // For now, use the existing API endpoint
      // In the future, this will call the dynamic simulation endpoint
      const simulationData = await apiClient.startSimulation(selectedScenario.id)
      
      // Show success message and redirect to simulation view
      alert(`🎉 Crew Assembled Successfully!\n\nScenario: ${selectedScenario.title}\nAgents: ${selectedAgents.map(a => a.name).join(', ')}\nProcess: ${processType}\n\nSimulation ID: ${simulationData.simulation_id}`)
      
      // Reset form
      setSelectedScenario(null)
      setSelectedAgents([])
      setProcessType("sequential")
      setCurrentStep(1)
      
    } catch (err) {
      console.error('Error starting simulation:', err)
      setError('Failed to start simulation')
    }
  }

  const resetWorkflow = () => {
    setSelectedScenario(null)
    setSelectedAgents([])
    setProcessType("sequential")
    setCurrentStep(1)
    setError(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading scenarios and agents...</p>
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
              <span className="text-xl font-bold">Dynamic Crew Simulation</span>
            </div>
          </div>
          {currentStep > 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={resetWorkflow}
              className="border-gray-600 text-gray-300 bg-transparent"
            >
              Start Over
            </Button>
          )}
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Run Dynamic Crew Simulation</h1>
            <p className="text-gray-400">Select scenario → Pick agents → Choose process → Auto-assemble crew</p>
          </div>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              {[
                { step: 1, title: "Select Scenario", icon: Bot },
                { step: 2, title: "Pick Agents", icon: Users },
                { step: 3, title: "Choose Process", icon: Settings }
              ].map(({ step, title, icon: Icon }, index) => (
                <div key={step} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    currentStep >= step 
                      ? "border-yellow-500 bg-yellow-500 text-black" 
                      : "border-gray-600 text-gray-400"
                  }`}>
                    {currentStep > step ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <span className={`ml-3 font-medium ${
                    currentStep >= step ? "text-yellow-500" : "text-gray-400"
                  }`}>
                    {title}
                  </span>
                  {index < 2 && (
                    <div className={`mx-4 h-0.5 w-16 ${
                      currentStep > step + 1 ? "bg-yellow-500" : "bg-gray-600"
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {error && (
            <Card className="mb-6 bg-red-500/10 border-red-500/30">
              <CardContent className="pt-6">
                <p className="text-red-400">{error}</p>
              </CardContent>
            </Card>
          )}

          {/* Step 1: Select Scenario */}
          {currentStep === 1 && (
            <Card className="bg-black border-yellow-500/20">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bot className="h-5 w-5 mr-2 text-yellow-500" />
                  Step 1: Select a Scenario
                </CardTitle>
                <CardDescription>Choose a scenario with defined tasks for your agents to collaborate on</CardDescription>
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
                  <div className="grid md:grid-cols-2 gap-6">
                    {scenarios.map((scenario) => (
                      <Card
                        key={scenario.id}
                        className="bg-gray-900/50 border-gray-700 hover:border-yellow-500/50 transition-colors cursor-pointer"
                        onClick={() => selectScenario(scenario)}
                      >
                        <CardHeader>
                          <CardTitle className="text-lg">{scenario.title}</CardTitle>
                          <CardDescription className="text-gray-400">{scenario.description}</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="flex items-center justify-between text-sm">
                            <Badge variant="outline" className="border-blue-400/30 text-blue-400">
                              {scenario.industry}
                            </Badge>
                            <span className="text-gray-400">
                              {scenario.tasks?.length || 0} tasks
                            </span>
                          </div>
                          <p className="text-sm text-gray-400">{scenario.challenge}</p>
                          <Button
                            className="w-full bg-yellow-500 text-black hover:bg-yellow-400"
                            onClick={(e) => {
                              e.stopPropagation()
                              selectScenario(scenario)
                            }}
                          >
                            Select Scenario
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Step 2: Pick Agents */}
          {currentStep === 2 && selectedScenario && (
            <div className="space-y-6">
              <Card className="bg-black border-blue-500/20">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CheckCircle className="h-5 w-5 mr-2 text-green-400" />
                    Selected Scenario: {selectedScenario.title}
                  </CardTitle>
                  <CardDescription>{selectedScenario.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-400">
                    <p><strong>Industry:</strong> {selectedScenario.industry}</p>
                    <p><strong>Challenge:</strong> {selectedScenario.challenge}</p>
                    <p><strong>Tasks:</strong> {selectedScenario.tasks?.length || 0} defined</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-5 w-5 mr-2 text-yellow-500" />
                    Step 2: Pick Agents ({selectedAgents.length} selected)
                  </CardTitle>
                  <CardDescription>Choose agents to form your crew for this scenario</CardDescription>
                </CardHeader>
                <CardContent>
                  {availableAgents.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No agents available</p>
                      <p className="text-sm mb-4">Create agents first to run simulations</p>
                      <Button asChild className="bg-yellow-500 text-black hover:bg-yellow-400">
                        <Link href="/agent-builder">Create Agent</Link>
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid md:grid-cols-2 gap-4">
                        {availableAgents.map((agent) => (
                          <div
                            key={agent.id}
                            className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                              selectedAgents.find(a => a.id === agent.id)
                                ? "border-yellow-500 bg-yellow-500/10"
                                : "border-gray-700 hover:border-gray-600"
                            }`}
                            onClick={() => toggleAgent(agent)}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <h4 className="font-medium">{agent.name}</h4>
                                <p className="text-sm text-gray-400">{agent.role}</p>
                              </div>
                              <Checkbox
                                checked={!!selectedAgents.find(a => a.id === agent.id)}
                                onChange={() => toggleAgent(agent)}
                              />
                            </div>
                            <p className="text-sm text-gray-400 mb-2">{agent.goal}</p>
                            <div className="flex flex-wrap gap-1">
                              <Badge variant="outline" className="border-purple-400/30 text-purple-400 text-xs">
                                {agent.category}
                              </Badge>
                              {agent.tools.slice(0, 2).map((tool) => (
                                <Badge key={tool} variant="outline" className="border-green-400/30 text-green-400 text-xs">
                                  {tool}
                                </Badge>
                              ))}
                              {agent.tools.length > 2 && (
                                <Badge variant="outline" className="border-gray-400/30 text-gray-400 text-xs">
                                  +{agent.tools.length - 2} more
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex justify-end pt-4">
                        <Button 
                          onClick={proceedToProcessSelection}
                          className="bg-yellow-500 text-black hover:bg-yellow-400"
                          disabled={selectedAgents.length === 0}
                        >
                          Continue with {selectedAgents.length} Agent{selectedAgents.length !== 1 ? 's' : ''}
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Step 3: Choose Process */}
          {currentStep === 3 && selectedScenario && selectedAgents.length > 0 && (
            <div className="space-y-6">
              <Card className="bg-black border-blue-500/20">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CheckCircle className="h-5 w-5 mr-2 text-green-400" />
                    Crew Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-yellow-500 mb-2">Scenario</h4>
                      <p className="font-medium">{selectedScenario.title}</p>
                      <p className="text-sm text-gray-400">{selectedScenario.industry}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-yellow-500 mb-2">Selected Agents</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgents.map((agent) => (
                          <Badge key={agent.id} variant="outline" className="border-blue-400/30 text-blue-400">
                            {agent.name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Settings className="h-5 w-5 mr-2 text-yellow-500" />
                    Step 3: Choose Process Type
                  </CardTitle>
                  <CardDescription>Select how your agents will collaborate on tasks</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="grid md:grid-cols-3 gap-4">
                      {[
                        {
                          value: "sequential",
                          title: "Sequential",
                          description: "Agents work one after another in order",
                          icon: "→"
                        },
                        {
                          value: "hierarchical",
                          title: "Hierarchical",
                          description: "Manager agent delegates tasks to team",
                          icon: "↓"
                        },
                        {
                          value: "collaborative",
                          title: "Collaborative",
                          description: "All agents work together simultaneously",
                          icon: "◆"
                        }
                      ].map((process) => (
                        <div
                          key={process.value}
                          className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                            processType === process.value
                              ? "border-yellow-500 bg-yellow-500/10"
                              : "border-gray-700 hover:border-gray-600"
                          }`}
                          onClick={() => setProcessType(process.value as any)}
                        >
                          <div className="text-center">
                            <div className="text-2xl mb-2">{process.icon}</div>
                            <h4 className="font-medium mb-1">{process.title}</h4>
                            <p className="text-sm text-gray-400">{process.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="border-t border-gray-700 pt-6">
                    <div className="flex justify-center">
                      <Button 
                        onClick={startSimulation}
                        className="bg-gradient-to-r from-yellow-500 to-orange-500 text-black hover:from-yellow-400 hover:to-orange-400 px-8 py-3 text-lg font-medium"
                      >
                        <Zap className="h-5 w-5 mr-2" />
                        Auto-Assemble Crew & Start Simulation
                      </Button>
                    </div>
                    <p className="text-center text-sm text-gray-400 mt-2">
                      This will create a dynamic crew and begin the simulation
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
