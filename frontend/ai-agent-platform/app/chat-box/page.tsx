"use client"

import React, { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { 
  Send, 
  Users, 
  Target, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  HelpCircle,
  Play,
  RefreshCw
} from "lucide-react"

// Types for the new simulation system - aligned with backend
interface SimulationData {
  user_progress_id: number
  scenario: {
    id: number
    title: string
    description: string
    challenge: string
    industry?: string
    learning_objectives: string[]
    student_role?: string
  }
  current_scene: {
    id: number
    scenario_id: number
    title: string
    description: string
    user_goal?: string
    scene_order: number
    estimated_duration?: number
    image_url?: string
    image_prompt?: string
    created_at: string
    updated_at: string
    personas?: Array<{
      id: number
      name: string
      role: string
      background: string
      correlation: string
      primary_goals: string[]
      personality_traits: Record<string, number>
    }>
  }
  simulation_status: string
}

interface Message {
  id: number
  sender: string
  text: string
  timestamp: Date
  type: 'user' | 'ai_persona' | 'system' | 'hint'
  persona_id?: number
}

interface UserProgress {
  completion_percentage: number
  total_attempts: number
  hints_used: number
  scenes_completed: number[]
}

// Timeline component showing progress through scenes
const TimelineProgress = ({ 
  currentScene, 
  totalScenes, 
  completedScenes 
}: { 
  currentScene: number
  totalScenes: number
  completedScenes: number[]
}) => {
  const progress = (completedScenes.length / totalScenes) * 100

  return (
    <div className="bg-white border rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-sm">Timeline Progress</h3>
        <span className="text-xs text-gray-500">
          Scene {currentScene} of {totalScenes}
        </span>
      </div>
      <Progress value={progress} className="mb-2" />
      <div className="flex justify-between text-xs text-gray-500">
        <span>{completedScenes.length} completed</span>
        <span>{Math.round(progress)}%</span>
      </div>
    </div>
  )
}

// Goal panel showing current objective
const GoalPanel = ({ 
  goal, 
  attempts, 
  maxAttempts, 
  hintsUsed 
}: { 
  goal: string
  attempts: number
  maxAttempts: number
  hintsUsed: number
}) => {
  const attemptsRemaining = maxAttempts - attempts
  const isNearLimit = attemptsRemaining <= 2

  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Target className="w-4 h-4 text-blue-500" />
            Current Goal
          </CardTitle>
          <div className="flex gap-2">
            <Badge variant={isNearLimit ? "destructive" : "secondary"}>
              {attemptsRemaining} attempts left
            </Badge>
            {hintsUsed > 0 && (
              <Badge variant="outline">
                {hintsUsed} hints used
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-700">{goal}</p>
      </CardContent>
    </Card>
  )
}

// Persona indicator showing who's speaking
const PersonaIndicator = ({ 
  personas, 
  currentPersona 
}: { 
  personas: Array<{ 
    id: number
    name: string
    role: string
    background?: string
    correlation?: string
    primary_goals?: string[]
    personality_traits?: Record<string, number>
  }>
  currentPersona?: number
}) => {
  return (
    <div className="bg-white border rounded-lg p-3 mb-4">
      <div className="flex items-center gap-2 mb-2">
        <Users className="w-4 h-4 text-purple-500" />
        <span className="font-semibold text-sm">Active Personas</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {personas.map((persona) => (
          <Badge 
            key={persona.id}
            variant={currentPersona === persona.id ? "default" : "secondary"}
            className="text-xs"
          >
            {persona.name} ({persona.role})
          </Badge>
        ))}
      </div>
    </div>
  )
}

// Typing indicator
const TypingIndicator = ({ personaName }: { personaName: string }) => (
  <div className="flex items-start gap-3 mb-4">
    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
      <span className="text-xs font-semibold">{personaName[0]}</span>
    </div>
    <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    </div>
  </div>
)

// PDF Metrics Panel
const PDFMetricsPanel = ({ scenarioId }: { scenarioId: number }) => {
  const [pdfMetrics, setPdfMetrics] = useState<any>(null)
  
  useEffect(() => {
    const pdfResults = localStorage.getItem("pdfParsingResults")
    if (pdfResults) {
      try {
        const parsed = JSON.parse(pdfResults)
        if (parsed.scenario_id === scenarioId) {
          setPdfMetrics(parsed)
        }
      } catch (e) {
        console.error("Failed to parse PDF metrics:", e)
      }
    }
  }, [scenarioId])
  
  if (!pdfMetrics) return null
  
  return (
    <Card className="mb-4 border-green-200 bg-green-50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-green-500" />
          PDF Analysis Complete
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span>Key Figures:</span>
            <Badge variant="secondary">{pdfMetrics.key_figures?.length || 0}</Badge>
          </div>
          <div className="flex justify-between">
            <span>Scenes Generated:</span>
            <Badge variant="secondary">{pdfMetrics.scenes?.length || 0}</Badge>
          </div>
          <div className="flex justify-between">
            <span>Learning Outcomes:</span>
            <Badge variant="secondary">{pdfMetrics.learning_outcomes?.length || 0}</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function SequentialSimulationChat() {
  // Core simulation state
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [typingPersona, setTypingPersona] = useState("")
  
  // Progress tracking
  const [userProgress, setUserProgress] = useState<UserProgress>({
    completion_percentage: 0,
    total_attempts: 0,
    hints_used: 0,
    scenes_completed: []
  })
  
  // UI state
  const [showHint, setShowHint] = useState(false)
  const [lastHint, setLastHint] = useState("")
  const [scenarioId, setScenarioId] = useState<number | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Load scenario from localStorage or use hardcoded ID
  useEffect(() => {
    // Try to get scenario from localStorage first
    const storedScenario = localStorage.getItem("chatboxScenario")
    if (storedScenario) {
      try {
        const parsed = JSON.parse(storedScenario)
        if (parsed.scenario_id) {
          setScenarioId(parsed.scenario_id)
          console.log("Loaded scenario from localStorage:", parsed.scenario_id)
        }
      } catch (e) {
        console.error("Failed to parse stored scenario:", e)
      }
    }
    
    // Also check for PDF parsing results
    const pdfResults = localStorage.getItem("pdfParsingResults")
    if (pdfResults && !scenarioId) {
      try {
        const parsed = JSON.parse(pdfResults)
        if (parsed.scenario_id) {
          setScenarioId(parsed.scenario_id)
          console.log("Loaded scenario from PDF parsing results:", parsed.scenario_id)
        }
      } catch (e) {
        console.error("Failed to parse PDF results:", e)
      }
    }
    
    // Fallback to hardcoded scenario ID for testing
    if (!scenarioId) {
      setScenarioId(1)
      console.log("Using fallback scenario ID: 1")
    }
  }, [])

  // Start simulation
  const startSimulation = async () => {
    if (!scenarioId) {
      alert("No scenario selected. Please create a scenario first.")
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch("http://localhost:8000/api/simulation/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: scenarioId,
          user_id: 1 // Hardcoded for now - should come from auth
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: SimulationData = await response.json()
      setSimulationData(data)
      
      // Add welcome message with orchestrator instructions
      setMessages([{
        id: Date.now(),
        sender: "System",
        text: `Welcome to "${data.scenario.title}"!\n\n${data.scenario.description}\n\n**Your Role:** ${data.scenario.student_role}\n\n**Instructions:**\n- Type **"begin"** when ready to start the simulation\n- Type **"help"** for available commands\n- Use @mentions to speak with specific agents`,
        timestamp: new Date(),
        type: 'system'
      }])

    } catch (error) {
      console.error("Failed to start simulation:", error)
      alert("Failed to start simulation. Please ensure the backend is running.")
    } finally {
      setIsLoading(false)
    }
  }

  // Send message to AI persona
  const sendMessage = async () => {
    if (!simulationData || !input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      sender: "You",
      text: input.trim(),
      timestamp: new Date(),
      type: 'user'
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setIsTyping(true)

    // Handle special commands locally for better UX
    const command = userMessage.text.toLowerCase().trim()
    if (command === "begin") {
      setTypingPersona("Orchestrator")
    } else if (command === "help") {
      setTypingPersona("System")
    } else {
      setTypingPersona("AI Agent")
    }

    try {
      // Send chat message using the new linear-chat endpoint
      const chatResponse = await fetch("http://localhost:8000/api/simulation/linear-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: simulationData.scenario.id,
          user_id: 1, // Hardcoded for now - should come from auth
          scene_id: simulationData.current_scene.id,
          message: userMessage.text
        })
      })

      if (!chatResponse.ok) {
        throw new Error(`Chat failed: ${chatResponse.status}`)
      }

      const chatData = await chatResponse.json()
      setTypingPersona("Orchestrator")
      
      // Simulate typing delay
      setTimeout(async () => {
        setIsTyping(false)
        
        // Add AI response from orchestrator
        const aiMessage: Message = {
          id: Date.now() + 1,
          sender: "Orchestrator",
          text: chatData.message,
          timestamp: new Date(),
          type: 'ai_persona'
        }
        setMessages(prev => [...prev, aiMessage])

        // Check if scene progression happened (orchestrator handles this internally)
        if (chatData.scene_completed) {
          // Scene completed, update UI
          const completedScenes = [...userProgress.scenes_completed, simulationData.current_scene.id]
          setUserProgress(prev => ({
            ...prev,
            scenes_completed: completedScenes,
            completion_percentage: (completedScenes.length / 5) * 100
          }))
          
          if (chatData.next_scene_id) {
            // Update current scene if orchestrator provided next scene
            // This would need scene data from backend
          }
        }
        
      }, 1500) // 1.5 second typing delay

    } catch (error) {
      console.error("Failed to send message:", error)
      setIsTyping(false)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: "System",
        text: "Sorry, I couldn't process your message. Please try again.",
        timestamp: new Date(),
        type: 'system'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Note: Goal validation and scene progression are now handled by the ChatOrchestrator
  // The orchestrator manages scene transitions internally and returns appropriate responses

  // Request hint
  const requestHint = () => {
    if (lastHint) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: "Hint",
        text: `💡 ${lastHint}`,
        timestamp: new Date(),
        type: 'hint'
      }])
      setShowHint(false)
    }
  }

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Integration Status Banner */}
        <Card className="mb-4 border-blue-200 bg-blue-50">
          <CardContent className="p-3">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-blue-500" />
              <span className="font-medium">Linear Flow Integration Active</span>
              <Badge variant="outline">v2.0</Badge>
              <span className="text-xs text-gray-600 ml-auto">
                Using ChatOrchestrator + PDF Metrics
              </span>
            </div>
          </CardContent>
        </Card>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          
          {/* Left Sidebar - Progress & Goal */}
          <div className="lg:col-span-1">
            {/* Show PDF metrics if available */}
            {scenarioId && <PDFMetricsPanel scenarioId={scenarioId} />}
            
            {simulationData && (
              <>
                <TimelineProgress
                  currentScene={simulationData.current_scene.scene_order}
                  totalScenes={5} // This should come from scenario data
                  completedScenes={userProgress.scenes_completed}
                />
                
                <GoalPanel
                  goal={simulationData.current_scene.user_goal || "Complete the scene objectives"}
                  attempts={userProgress.total_attempts}
                  maxAttempts={5} // This should come from scene data
                  hintsUsed={userProgress.hints_used}
                />
                
                <PersonaIndicator
                  personas={simulationData.current_scene.personas || []}
                />

                {showHint && (
                  <Card className="mb-4 border-yellow-200 bg-yellow-50">
                    <CardContent className="p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <HelpCircle className="w-4 h-4 text-yellow-600" />
                          <span className="text-sm font-medium">Hint Available</span>
                        </div>
                        <Button size="sm" variant="outline" onClick={requestHint}>
                          Show Hint
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[80vh] flex flex-col">
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">
                    {simulationData ? simulationData.scenario.title : "Sequential Simulation"}
                  </CardTitle>
                  {!simulationData && (
                    <div className="flex items-center gap-2">
                      <Button onClick={startSimulation} disabled={isLoading || !scenarioId}>
                        <Play className="w-4 h-4 mr-2" />
                        {isLoading ? "Starting..." : "Start Simulation"}
                      </Button>
                      {scenarioId && (
                        <Badge variant="secondary" className="text-xs">
                          Scenario #{scenarioId}
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
              </CardHeader>

              {/* Messages Area */}
              <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : message.type === 'system'
                        ? 'bg-gray-100 text-gray-800 border'
                        : message.type === 'hint'
                        ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                        : 'bg-white text-gray-800 border'
                    }`}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold opacity-75">
                          {message.sender}
                        </span>
                        {message.type === 'ai_persona' && (
                          <Badge variant="secondary" className="text-xs">
                            AI
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm whitespace-pre-wrap">
                        {message.text}
                      </div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <TypingIndicator personaName={typingPersona} />
                )}

                <div ref={messagesEndRef} />
              </CardContent>

              {/* Input Area */}
              {simulationData && (
                <div className="border-t p-4">
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message, @mention agents, or try 'help'..."
                        disabled={isLoading || isTyping}
                        className="flex-1"
                      />
                      <Button
                        onClick={sendMessage}
                        disabled={isLoading || isTyping || !input.trim()}
                      >
                        {isLoading ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                    
                    {/* Quick command buttons */}
                    <div className="flex gap-2 text-xs">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setInput("begin")}
                        disabled={isLoading || isTyping}
                      >
                        Begin
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setInput("help")}
                        disabled={isLoading || isTyping}
                      >
                        Help
                      </Button>
                      {simulationData.current_scene.personas && simulationData.current_scene.personas.length > 0 && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            const firstPersona = simulationData.current_scene.personas![0]
                            const mentionId = firstPersona.name.toLowerCase().replace(/\s+/g, '_')
                            setInput(`@${mentionId} `)
                          }}
                          disabled={isLoading || isTyping}
                        >
                          @{simulationData.current_scene.personas[0].name.split(' ')[0]}
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
} 