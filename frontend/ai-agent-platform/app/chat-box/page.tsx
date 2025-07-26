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
  RefreshCw,
  ArrowRight,
  BookOpen,
  User
} from "lucide-react"
import { buildApiUrl } from "@/lib/api"

// Types aligned with backend database schema
interface Scenario {
  id: number
  title: string
  description: string
  challenge: string
  industry?: string
  learning_objectives: string[]
  student_role?: string
  created_at: string
  is_public: boolean
}

interface Persona {
  id: number
  name: string
  role: string
  background: string
  correlation: string
  primary_goals: string[]
  personality_traits: Record<string, number>
}

interface Scene {
  id: number
  title: string
  description: string
  user_goal?: string
  scene_order: number
  estimated_duration?: number
  image_url?: string
  personas: Persona[]
  personas_involved?: string[] // Add this to track which personas are actually involved
  timeout_turns?: number // Add this line
}

interface SimulationData {
  user_progress_id: number
  scenario: Scenario
  current_scene: Scene
  simulation_status: string
}

interface Message {
  id: number
  sender: string
  text: string
  timestamp: Date
  type: 'user' | 'ai_persona' | 'system' | 'orchestrator'
  persona_id?: number
  persona_name?: string  // Add persona name for display
  scene_completed?: boolean  // Add scene completion flag
  next_scene_id?: number  // Add next scene ID for progression
  showSubmitForGrading?: boolean // Add this for the new system message
  showViewGrading?: boolean // Add this for completion messages
  gradingInProgress?: boolean // Add this for loading bar
}

// Scenario Selection Component
const ScenarioSelector = ({ 
  onScenarioSelect 
}: { 
  onScenarioSelect: (scenarioId: number) => void 
}) => {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null)

  useEffect(() => {
    fetchScenarios()
  }, [])

  const fetchScenarios = async () => {
    try {
      const response = await fetch(buildApiUrl("/api/scenarios/"))
      if (response.ok) {
        const data = await response.json()
        // Filter scenarios that have both personas and scenes
        const validScenarios = data.filter((s: any) => 
          s.personas && s.personas.length > 0 && 
          s.scenes && s.scenes.length > 0
        )
        setScenarios(validScenarios)
        
        // Auto-select the most recent scenario
        if (validScenarios.length > 0) {
          const mostRecent = validScenarios.reduce((latest: any, current: any) => 
            new Date(current.created_at) > new Date(latest.created_at) ? current : latest
          )
          setSelectedScenario(mostRecent.id)
        }
      }
    } catch (error) {
      console.error("Failed to fetch scenarios:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="p-6 text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Loading available scenarios...</p>
        </CardContent>
      </Card>
    )
  }

  if (scenarios.length === 0) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="p-6 text-center">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">No Scenarios Available</h3>
          <p className="text-gray-600 mb-4">
            You need to create a scenario first using the Scenario Builder.
          </p>
          <Button onClick={() => window.open("/scenario-builder", "_blank")}>
            Create Scenario
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="w-5 h-5" />
            Select a Scenario to Simulate
          </CardTitle>
          <p className="text-sm text-gray-600">
            Choose from your available scenarios with AI personas and scenes
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                selectedScenario === scenario.id 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200'
              }`}
              onClick={() => setSelectedScenario(scenario.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold">{scenario.title}</h3>
                    {scenario.is_public && (
                      <Badge variant="secondary" className="text-xs">Public</Badge>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {scenario.description}
                  </p>
                  
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {scenario.student_role || "Student"}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      Multiple Personas
                    </span>
                    <span className="flex items-center gap-1">
                      <Target className="w-3 h-3" />
                      Multi-Scene
                    </span>
                  </div>
                </div>
                
                <div className="ml-4 flex flex-col items-end gap-2">
                  <Badge variant="outline" className="text-xs">
                    ID: {scenario.id}
                  </Badge>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (!window.confirm(`Delete scenario '${scenario.title}'? This cannot be undone.`)) return;
                      try {
                        const res = await fetch(buildApiUrl(`/api/scenarios/${scenario.id}`), { method: 'DELETE' });
                        if (!res.ok) throw new Error('Failed to delete');
                        setScenarios(scenarios => scenarios.filter(s => s.id !== scenario.id));
                        if (selectedScenario === scenario.id) setSelectedScenario(null);
                      } catch (err) {
                        alert('Failed to delete scenario.');
                      }
                    }}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          ))}
          
          <div className="pt-4 border-t">
            <Button 
              onClick={() => selectedScenario && onScenarioSelect(selectedScenario)}
              disabled={!selectedScenario}
              className="w-full"
              size="lg"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Simulation
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Scene Progress Component
const SceneProgress = ({ 
  currentScene, 
  totalScenes, 
  completedScenes 
}: { 
  currentScene: number
  totalScenes: number
  completedScenes: number[]
}) => {
  const progress = (completedScenes.length / totalScenes) * 100
  console.log("[DEBUG] SceneProgress - currentScene:", currentScene, "totalScenes:", totalScenes, "completedScenes:", completedScenes, "progress:", progress)

  return (
    <Card className="mb-4">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-sm">Scene Progress</h3>
          <span className="text-xs text-gray-500">
            Scene {currentScene} of {totalScenes}
          </span>
        </div>
        <Progress value={progress} className="mb-2" />
        <div className="flex justify-between text-xs text-gray-500">
          <span>{completedScenes.length} completed</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </CardContent>
    </Card>
  )
}

// Current Scene Info
const CurrentSceneInfo = ({ scene, turnCount }: { scene: Scene, turnCount: number }) => {
  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Target className="w-4 h-4 text-blue-500" />
          Current Scene
        </CardTitle>
      </CardHeader>
      <CardContent>
        <h3 className="font-semibold mb-2">{scene.title}</h3>
        
        {/* Scene Image */}
        {scene.image_url && (
          <div className="mb-3">
            <img 
              src={scene.image_url} 
              alt={scene.title}
              className="w-full h-32 object-cover rounded-lg border"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                console.log("[DEBUG] Image failed to load:", scene.image_url);
                target.style.display = 'none';
              }}
              onLoad={() => {
                console.log("[DEBUG] Image loaded successfully:", scene.image_url);
              }}
            />
          </div>
        )}
        
        <p className="text-sm text-gray-600 mb-3">{scene.description}</p>
        
        {scene.user_goal && (
          <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-3">
            <p className="text-sm font-medium text-blue-800">Your Goal:</p>
            <p className="text-sm text-blue-700">{scene.user_goal}</p>
          </div>
        )}
        
        {/* Always display timeout_turns and current turn count */}
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
          <p className="text-sm font-medium text-yellow-800">Timeout Turns:</p>
          <p className="text-sm text-yellow-700">
            {typeof scene.timeout_turns === 'number' ? `${Math.min(turnCount, scene.timeout_turns)} / ${scene.timeout_turns}` : 'Not set'}
          </p>
        </div>
        
        {/* Only use scene.personas for available personas */}
        {scene.personas && scene.personas.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-700 mb-2">Available Personas:</p>
            <div className="flex flex-wrap gap-1">
              {scene.personas.map((persona) => (
                <Badge key={persona.id} variant="secondary" className="text-xs">
                  {persona.name}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Typing Indicator
const TypingIndicator = ({ personaName }: { personaName: string }) => (
  <div className="flex justify-start mb-4">
    <div className="bg-gray-100 rounded-lg px-4 py-2 border">
      <div className="flex items-center gap-2">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <span className="text-xs text-gray-600">{personaName} is typing...</span>
      </div>
    </div>
  </div>
)

export default function LinearSimulationChat() {
  // Core simulation state
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [typingPersona, setTypingPersona] = useState("")
  // UI state
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | null>(null)
  const [completedScenes, setCompletedScenes] = useState<number[]>([])
  // 1. Add state for current turn count
  const [turnCount, setTurnCount] = useState(0);
  // Add a state to block input when scene is completed and next scene is loading
  const [inputBlocked, setInputBlocked] = useState(false);
  // Add a state for all scenes
  const [allScenes, setAllScenes] = useState<Scene[]>([]);
  // Grading/Feedback state (must be at top)
  const [gradingData, setGradingData] = useState<any>(null);
  const [showGrading, setShowGrading] = useState(false);
  // Block input after grading is shown
  useEffect(() => {
    if (gradingData && showGrading) {
      setInputBlocked(true);
    }
  }, [gradingData, showGrading]);
  // Add state for submit button
  const [canSubmitForGrading, setCanSubmitForGrading] = useState(false);
  const [hasSubmittedForGrading, setHasSubmittedForGrading] = useState(false);
  // Add state to track if grading has been shown
  const [gradingHasBeenShown, setGradingHasBeenShown] = useState(false);
  const [simulationComplete, setSimulationComplete] = useState(false);
  // Add gradingInProgress state
  const [gradingInProgress, setGradingInProgress] = useState(false);
  // Helper to add a scene to allScenes if not already present
  const addSceneIfMissing = (scene: Scene) => {
    setAllScenes(prev => {
      if (!scene || !scene.id) return prev;
      const exists = prev.some(s => s.id === scene.id);
      if (!exists) {
        return [...prev, scene];
      }
      return prev;
    });
  };
  
  // Helper to generate scene introduction text
  const generateSceneIntroduction = (scene: Scene) => {
    // Filter personas to only show involved ones
    const involvedPersonas = scene.personas_involved && scene.personas_involved.length > 0
      ? scene.personas.filter(persona => 
          scene.personas_involved!.includes(persona.name)
        )
      : scene.personas; // Fallback to all personas if personas_involved is not available
    
    return `**Scene ${scene.scene_order} — ${scene.title}**

*${scene.description}*

**Objective:** ${scene.user_goal || 'Complete the interaction'}

**Active Participants:**
${involvedPersonas.map(persona => `• @${persona.name.toLowerCase().replace(/\s+/g, '_')}: ${persona.name} (${persona.role})`).join('\n')}

*You have ${scene.timeout_turns || 15} turns to achieve the objective.*`;
  };
  const messagesEndRef = useRef<HTMLDivElement>(null)
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Start simulation with selected scenario
  const startSimulation = async (scenarioId: number) => {
    setSelectedScenarioId(scenarioId)
    setIsLoading(true)
    setSimulationComplete(false)
    setCanSubmitForGrading(false) // Reset submit button state
    setHasSubmittedForGrading(false)
    
    try {
      const response = await fetch(buildApiUrl("/api/simulation/start"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: scenarioId,
          user_id: 1 // Hardcoded for now - should come from auth
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }

      const data: SimulationData = await response.json()
      setSimulationData(data)
      
      // Try to fetch all scenes for the scenario
      const scenesRes = await fetch(buildApiUrl(`/api/scenarios/${scenarioId}/full`));
      if (scenesRes.ok) {
        const scenarioDetail = await scenesRes.json();
        console.log("[DEBUG] Scenario detail response:", scenarioDetail);
        if (scenarioDetail.scenes && Array.isArray(scenarioDetail.scenes) && scenarioDetail.scenes.length > 0) {
          setAllScenes(scenarioDetail.scenes);
          console.log("[DEBUG] allScenes set to:", scenarioDetail.scenes);
        } else {
          setAllScenes([data.current_scene]);
          console.log("[DEBUG] allScenes fallback to current_scene:", [data.current_scene]);
        }
      } else {
        setAllScenes([data.current_scene]);
        console.log("[DEBUG] allScenes fallback to current_scene (fetch error):", [data.current_scene]);
      }
      
      // Add welcome message
      setMessages([{
        id: Date.now(),
        sender: "System",
        text: `🎯 **${data.scenario.title}**\n\n${data.scenario.description}\n\n**Your Role:** ${data.scenario.student_role}\n\n**Current Scene:** ${data.current_scene.title}\n\n**Instructions:**\n• Type **"begin"** to start the simulation\n• Type **"help"** for available commands\n• Use natural conversation to interact with personas`,
        timestamp: new Date(),
        type: 'system'
      }])

    } catch (error) {
      console.error("Failed to start simulation:", error)
      alert(`Failed to start simulation: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }



  // Send message to orchestrator
  const sendMessage = async () => {
    console.log("[DEBUG] sendMessage called. Input:", input);
    if (inputBlocked) return;
    if (!simulationData || !input.trim() || isLoading) return;

    // Restrict @mentions to only personas in the current scene
    const trimmedInput = input.trim();
    const mentionMatch = trimmedInput.match(/@(\w+)/);
    if (mentionMatch) {
      const mentionId = mentionMatch[1].toLowerCase();
      // Use only the personas from the current scene for validation
      const validPersonaMentions = simulationData.current_scene.personas.map(
        p => p.name.toLowerCase().replace(/\s+/g, '_')
      );
      console.log("[DEBUG] @mention validation:");
      console.log("  - Mentioned ID:", mentionId);
      console.log("  - Valid persona mentions:", validPersonaMentions);
      console.log("  - Current scene personas:", simulationData.current_scene.personas.map(p => p.name));
      if (!validPersonaMentions.includes(mentionId)) {
        console.log("[DEBUG] Invalid mention detected - blocking message");
        alert('You can only @mention personas involved in this scene.');
        return;
      }
      console.log("[DEBUG] Valid mention - allowing message");
    }

    const userMessage: Message = {
      id: Date.now(),
      sender: "You",
      text: input.trim(),
      timestamp: new Date(),
      type: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setIsTyping(true);
    setTypingPersona("ChatOrchestrator");

    // Only increment turn count for non-command messages
    if (trimmedInput !== 'begin' && trimmedInput !== 'help') {
      setTurnCount(prev => prev + 1);
      setHasSubmittedForGrading(false);
      // Hide submit button when user sends a new message
      setCanSubmitForGrading(false);
    }

    try {
      const response = await fetch(buildApiUrl("/api/simulation/linear-chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: simulationData.scenario.id,
          user_id: 1,
          scene_id: simulationData.current_scene.id,
          message: userMessage.text,
          user_progress_id: simulationData.user_progress_id
        })
      });

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status}`);
      }

      const chatData = await response.json();
      
      // Simulate typing delay for better UX
      setTimeout(() => {
        setIsTyping(false)
        
        // Add orchestrator response with persona information
        const aiMessage: Message = {
          id: Date.now() + 1,
          sender: chatData.persona_name || "ChatOrchestrator",
          text: chatData.message,
          timestamp: new Date(),
          type: chatData.persona_name && chatData.persona_name !== "ChatOrchestrator" ? 'ai_persona' : 'orchestrator',
          persona_name: chatData.persona_name,
          persona_id: chatData.persona_id,
          scene_completed: chatData.scene_completed,
          next_scene_id: chatData.next_scene_id
        }
        setMessages(prev => [...prev, aiMessage])
        
        // If this is the first "begin" response, add scene introduction as separate message
        if (trimmedInput === 'begin') {
          // Use the scene from allScenes (by ID) for correct persona filtering
          const currentScene = allScenes.find(
            s => s.id === simulationData.current_scene.id
          ) || simulationData.current_scene;
          console.log('[DEBUG] Using scene for introduction:', currentScene);
          const sceneIntro = generateSceneIntroduction(currentScene);
          const sceneMessage: Message = {
            id: Date.now() + 2,
            sender: "System",
            text: sceneIntro,
            timestamp: new Date(),
            type: 'system'
          }
          setMessages(prev => [...prev, sceneMessage])
        }
        
        // Allow submit for grading after ANY AI response is received
        console.log("[DEBUG] Setting canSubmitForGrading to true after AI response");
        setCanSubmitForGrading(true);

        // Handle scene progression if indicated
        if (typeof chatData.turn_count === 'number') {
          setTurnCount(chatData.turn_count);
        }
        // Robust last scene detection
        const isLastScene =
          allScenes.length > 0 &&
          simulationData.current_scene &&
          simulationData.current_scene.id === allScenes[allScenes.length - 1].id;
        if (chatData.scene_completed) {
          setCompletedScenes(prev => {
            // Always add the current scene if not already present
            if (!prev.includes(simulationData.current_scene.id)) {
              return [...prev, simulationData.current_scene.id];
            }
            return prev;
          });
          addSceneIfMissing(simulationData.current_scene);

          if (chatData.next_scene_id) {
            setInputBlocked(true);
            // Fetch next scene data and update simulationData
            fetch(buildApiUrl(`/api/simulation/scenes/${chatData.next_scene_id}`))
              .then(response => {
                if (response.ok) {
                  return response.json();
                }
                throw new Error('Failed to fetch next scene');
              })
              .then(nextSceneData => {
                // Use the filtered scene from allScenes if available
                const filteredNextScene = allScenes.find(s => s.id === nextSceneData.id) || nextSceneData;
                setSimulationData(prev => prev ? {
                  ...prev,
                  current_scene: filteredNextScene
                } : null);
                setTurnCount(0);
                setInputBlocked(false);
                setCanSubmitForGrading(true); // Enable submit button after scene transition
                addSceneIfMissing(filteredNextScene);
                // Add scene transition message
                const transitionMessage: Message = {
                  id: Date.now() + 2,
                  sender: "System",
                  text: generateSceneIntroduction(filteredNextScene),
                  timestamp: new Date(),
                  type: 'system'
                };
                setMessages(prev => [...prev, transitionMessage]);
              })
              .catch(error => {
                console.error("Failed to fetch next scene:", error);
                setInputBlocked(false);
                // Fallback completion message
                const completionMessage: Message = {
                  id: Date.now() + 2,
                  sender: "System",
                  text: "🎉 Scene completed! Moving to the next scene...",
                  timestamp: new Date(),
                  type: 'system'
                };
                setMessages(prev => [...prev, completionMessage]);
              });
            return;
          } else if (isLastScene && !chatData.next_scene_id) {
            // Only trigger completion if this is the last scene
            setInputBlocked(false);
            setMessages(prev => [
              ...prev,
              {
                id: Date.now() + 3,
                sender: "System",
                text: "🎉 Simulation complete! You have finished all scenes. View your grading and feedback.",
                timestamp: new Date(),
                type: 'system'
              }
            ]);
            setGradingInProgress(true);
            setSimulationComplete(true); // Set simulation complete when grading starts
            fetchGradingData().then(() => setGradingInProgress(false));
            return;
          }
          // If not last scene and no next_scene_id, fallback
          if (!chatData.next_scene_id) {
            setInputBlocked(false);
            setMessages(prev => [
              ...prev,
              {
                id: Date.now() + 4,
                sender: "System",
                text: "🎉 Scene completed! Moving to the next scene...",
                timestamp: new Date(),
                type: 'system'
              }
            ]);
          }
          return;
        }
        
      }, 1500) // 1.5 second typing delay

    } catch (error) {
      console.error("Failed to send message:", error)
      setIsTyping(false)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: "System",
        text: `❌ Error: ${error}. Please try again or restart the simulation.`,
        timestamp: new Date(),
        type: 'system'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // If no simulation is active, show scenario selection
  if (!simulationData) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-6xl mx-auto py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Linear Simulation Experience</h1>
            <p className="text-gray-600">
              Select a scenario to begin your interactive simulation with AI personas
            </p>
          </div>
          
          <ScenarioSelector onScenarioSelect={startSimulation} />
        </div>
      </div>
    )
  }

  // Main simulation interface
  // Calculate totalScenes before the JSX return
  const totalScenes = allScenes.length > 0
    ? allScenes.length
    : Math.max(simulationData?.current_scene?.scene_order || 1, 1);

  // --- FEEDBACK/GRADING INTERFACE LOGIC (finalized) ---
  // Function to fetch grading data after simulation
  const fetchGradingData = async () => {
    if (!simulationData) return;
    const res = await fetch(buildApiUrl(`/api/simulation/grade?user_progress_id=${simulationData.user_progress_id}`));
    if (res.ok) {
      const data = await res.json();
      setGradingData(data);
      setShowGrading(true);
    }
  };

  // In sendMessage, after the last scene is completed, trigger grading
  // (Insert this logic in your sendMessage or scene progression handler)
  // if (chatData.scene_completed && !chatData.next_scene_id) {
  //   fetchGradingData();
  // }

  // Grading Modal
  {showGrading && gradingData && (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl w-full overflow-y-auto max-h-[90vh]">
        <h2 className="text-2xl font-bold mb-4 text-center">Simulation Grading & Feedback</h2>
        <div className="mb-6">
          <div className="text-lg font-semibold">Overall Score: <span className="text-blue-600">{gradingData.overall_score}</span></div>
          <div className="text-gray-700 mt-2">{gradingData.overall_feedback}</div>
        </div>
        {gradingData.scenes && gradingData.scenes.map((scene: any, idx: number) => (
          <div key={scene.id} className="mb-6 border-b pb-4">
            <div className="font-semibold text-blue-700">{scene.title}</div>
            <div className="text-sm text-gray-500 mb-2">{scene.objective}</div>
            <div className="mb-2">
              <span className="font-medium">Your Responses:</span>
              <div
                style={{
                  maxHeight: '120px',
                  overflowY: 'auto',
                  background: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.375rem',
                  padding: '0.5rem',
                  marginTop: '0.5rem',
                  fontSize: '0.95rem',
                  whiteSpace: 'pre-wrap',
                  width: '100%',
                  fontFamily: 'inherit',
                  resize: 'none',
                  color: '#222'
                }}
                tabIndex={-1}
                aria-readonly="true"
              >
                {scene.user_responses && scene.user_responses.length > 0
                  ? scene.user_responses.map((msg: any) => `• ${msg.content}`).join('\n\n')
                  : <span className="text-gray-400">No responses.</span>}
              </div>
            </div>
            <div className="text-sm text-green-700 mb-1">Score: {scene.score}</div>
            <div className="text-gray-700">{scene.feedback}</div>
            {scene.teaching_notes && (
              <div className="mt-2 text-xs text-gray-500 italic">Teaching Notes: {scene.teaching_notes}</div>
            )}
          </div>
        ))}
                    <div className="flex justify-center mt-6">
              <button className="btn btn-primary" onClick={() => {
                console.log("[DEBUG] Closing grading modal");
                setShowGrading(false);
                setGradingHasBeenShown(true);
                setInputBlocked(false);
                setCanSubmitForGrading(false);
                setHasSubmittedForGrading(false);
                
                // Update the completion message to show the "View Grading" button
                setMessages(prev => {
                  console.log("[DEBUG] Current messages before update:", prev);
                  console.log("[DEBUG] Looking for completion message with text containing '🎉 Simulation complete!'");
                  const updatedMessages = prev.map(msg => {
                    console.log("[DEBUG] Checking message:", msg.text.substring(0, 50), "showViewGrading:", msg.showViewGrading, "type:", msg.type);
                    if (msg.text.includes("🎉 Simulation complete!") && msg.type === 'system') {
                      console.log("[DEBUG] FOUND COMPLETION MESSAGE! Updating showViewGrading to true");
                      const updatedMsg = { ...msg, showViewGrading: true };
                      console.log("[DEBUG] Updated message:", updatedMsg);
                      return updatedMsg;
                    }
                    return msg;
                  });
                  console.log("[DEBUG] Final updated messages:", updatedMessages);
                  return updatedMessages;
                });
              }}>Close</button>
            </div>
      </div>
    </div>
  )}

  // Handler for submit button
  const handleSubmitForGrading = async () => {
    console.log("[DEBUG] handleSubmitForGrading called");
    console.log("[DEBUG] Current state before submit:");
    console.log("  - canSubmitForGrading:", canSubmitForGrading);
    console.log("  - hasSubmittedForGrading:", hasSubmittedForGrading);
    console.log("  - inputBlocked:", inputBlocked);
    console.log("  - simulationComplete:", simulationComplete);
    setHasSubmittedForGrading(true);
    setInputBlocked(true);
    
    // Don't add submit message to chat history - it's a UI action, not a conversation message
    
    // Instead of calling /progress directly, send a special message through the normal chat flow
    // This ensures the turn counting logic is respected
    const specialMessage = "SUBMIT_FOR_GRADING";
    
    try {
      const response = await fetch(buildApiUrl("/api/simulation/linear-chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_progress_id: simulationData.user_progress_id,
          scene_id: simulationData.current_scene.id,
          message: specialMessage,
          user_id: 1,
          scenario_id: simulationData.scenario.id
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("[DEBUG] Submit for grading response:", data);
      console.log("[DEBUG] scene_completed:", data.scene_completed);
      console.log("[DEBUG] next_scene_id:", data.next_scene_id);
      
      if (data.scene_completed) {
        if (data.next_scene_id) {
          console.log("[DEBUG] Moving to next scene via chat flow");
          // Update completed scenes
          setCompletedScenes(prev => {
            const currentSceneId = simulationData.current_scene.id;
            if (!prev.includes(currentSceneId)) {
              return [...prev, currentSceneId];
            }
            return prev;
          });
          
          // Move to next scene
          // Use the filtered scene from allScenes if available
          const filteredNextScene = allScenes.find(s => s.id === data.next_scene.id) || data.next_scene;
          setSimulationData(prev => prev ? {
            ...prev,
            current_scene: filteredNextScene
          } : null);
          setTurnCount(0);
          setCanSubmitForGrading(true); // Enable submit button immediately for new scene
          setHasSubmittedForGrading(false);
          addSceneIfMissing(filteredNextScene);
          setMessages(prev => [
            ...prev,
            {
              id: Date.now() + 2,
              sender: "System",
              text: generateSceneIntroduction(filteredNextScene),
              timestamp: new Date(),
              type: 'system'
            }
          ]);
          // Confirm backend state before unblocking input
          fetch(buildApiUrl(`/api/simulation/progress/${simulationData.user_progress_id}`))
            .then(res => res.json())
            .then(progress => {
              if (progress.current_scene_id === data.next_scene.id) {
                console.log("[DEBUG] Backend state synced, enabling submit button");
                setInputBlocked(false);
                // Enable submit button after scene transition is complete
                setCanSubmitForGrading(true);
              } else {
                // Retry after a short delay if not yet synced
                setTimeout(() => {
                  setInputBlocked(false);
                  setCanSubmitForGrading(true);
                }, 300);
              }
            })
            .catch(() => {
              setTimeout(() => {
                setInputBlocked(false);
                setCanSubmitForGrading(true);
              }, 300);
            });
        } else {
          console.log("[DEBUG] Simulation complete via chat flow");
          setSimulationComplete(true);
          // Update completed scenes
          setCompletedScenes(prev => {
            const currentSceneId = simulationData.current_scene.id;
            if (!prev.includes(currentSceneId)) {
              return [...prev, currentSceneId];
            }
            return prev;
          });
          
          // Add completion message to chat
          setMessages(prev => [
            ...prev,
            {
              id: Date.now() + 3,
              sender: "System",
              text: "🎉 Simulation complete! You have finished all scenes. View your grading and feedback.",
              timestamp: new Date(),
              type: 'system',
              showViewGrading: false
            }
          ]);
          
          // Show grading modal
          setGradingInProgress(true);
          setSimulationComplete(true); // Set simulation complete when grading starts
          fetchGradingData().then(() => setGradingInProgress(false));
        }
      } else {
        console.log("[DEBUG] Scene not completed, continuing normally");
        setInputBlocked(false);
        setCanSubmitForGrading(false);
        setHasSubmittedForGrading(false);
      }
    } catch (error) {
      console.error("[ERROR] Submit for grading failed:", error);
      setInputBlocked(false);
      setCanSubmitForGrading(false);
      setHasSubmittedForGrading(false);
      alert('Failed to submit for grading.');
    }
  };

  // Helper to determine if we should show the submit button system message
  const isLastScene = simulationData && simulationData.current_scene.scene_order >= totalScenes;
  const timeoutTurns = simulationData?.current_scene?.timeout_turns ?? 15;
  const hasTurnsRemaining = turnCount < timeoutTurns;
  const shouldShowSubmitSystemMessage = canSubmitForGrading && !hasSubmittedForGrading && !inputBlocked && !simulationComplete && hasTurnsRemaining;
  
  // Debug logging for personas
  console.log("[DEBUG] Current scene personas:", simulationData?.current_scene?.personas);
  console.log("[DEBUG] Current scene order:", simulationData?.current_scene?.scene_order);
  console.log("[DEBUG] Total scenes:", totalScenes);
  console.log("[DEBUG] Is last scene:", isLastScene);
  console.log("[DEBUG] Should show submit button:", shouldShowSubmitSystemMessage);
  
  // Debug logging for submit button conditions
  console.log("[DEBUG] Submit button conditions:");
  console.log("  - canSubmitForGrading:", canSubmitForGrading);
  console.log("  - hasSubmittedForGrading:", hasSubmittedForGrading);
  console.log("  - inputBlocked:", inputBlocked);
  console.log("  - simulationComplete:", simulationComplete);
  console.log("  - isLastScene:", isLastScene);
  console.log("  - shouldShowSubmitSystemMessage:", shouldShowSubmitSystemMessage);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Sidebar - Progress & Scene Info */}
        <div className="lg:col-span-1">
          {/* In the render, use totalScenes for SceneProgress */}
          <SceneProgress
            currentScene={simulationData.current_scene.scene_order}
            totalScenes={totalScenes}
            completedScenes={completedScenes}
          />
          
          <CurrentSceneInfo scene={simulationData.current_scene} turnCount={turnCount} />
          
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <Badge variant="outline" className="text-xs mb-2">
                  Scenario #{simulationData.scenario.id}
                </Badge>
                <p className="text-xs text-gray-500">
                  Linear Flow Integration Active
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <Card className="h-[85vh] flex flex-col">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  {simulationData.scenario.title}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">
                    {simulationData.current_scene.title}
                  </Badge>
                </div>
              </div>
            </CardHeader>

            {/* Messages Area */}
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Render messages, including the new system message if needed */}
              {[...messages,
                ...(gradingInProgress ? [{
                  id: 'grading-in-progress',
                  sender: 'System',
                  text: 'Grading in progress... ',
                  type: 'system',
                  showSubmitForGrading: false,
                  showViewGrading: false,
                  gradingInProgress: true
                }] : []),
                ...(shouldShowSubmitSystemMessage ? [{
                  id: 'submit-for-grading',
                  sender: 'System',
                  text: '',
                  type: 'system',
                  showSubmitForGrading: true,
                  showViewGrading: false
                }] : [])].map((message, idx) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : message.type === 'system'
                      ? 'bg-gray-100 text-gray-800 border'
                      : message.type === 'ai_persona'
                      ? 'bg-green-50 text-gray-800 border border-green-200'
                      : message.type === 'orchestrator'
                      ? 'bg-white text-gray-800 border border-purple-200'
                      : 'bg-white text-gray-800 border'
                  }`}>
                    <div className={`flex items-center gap-2 mb-1`}>
                      <span className="text-xs font-semibold opacity-75">
                        {message.sender}
                      </span>
                      {'persona_name' in message && message.type === 'ai_persona' && (
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                          {message.persona_name || 'Persona'}
                        </Badge>
                      )}
                      {'persona_name' in message && message.type === 'orchestrator' && (
                        <Badge variant="secondary" className="text-xs">
                          AI
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm whitespace-pre-wrap">
                      {/* Simple markdown-like formatting */}
                      {message.text.split('\n').map((line, index) => {
                        // Handle bold text with **
                        const boldFormatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        return (
                          <div key={index} dangerouslySetInnerHTML={{ __html: boldFormatted }} />
                        )
                      })}
                      {message.showSubmitForGrading && (
                        <div className="flex flex-col items-center">
                          <div className="mb-2 text-sm text-gray-700">Ready to submit your response for this scene?</div>
                          <Button
                            variant="default"
                            onClick={handleSubmitForGrading}
                            disabled={inputBlocked}
                          >
                            Submit for Grading
                          </Button>
                    </div>
                      )}
                      {message.showViewGrading && (
                        <div className="flex flex-col items-center">
                          <Button
                            variant="default"
                            onClick={() => {
                              if (gradingData) {
                                setShowGrading(true);
                              } else {
                                setGradingInProgress(true);
                                fetchGradingData().then(() => setGradingInProgress(false));
                              }
                            }}
                            className="mt-2"
                          >
                            View Grading & Feedback
                          </Button>
                        </div>
                      )}
                      {message.gradingInProgress && (
                        <div className="w-full mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-2 bg-blue-400 animate-pulse w-3/4 transition-all duration-1000" style={{ width: '75%' }}></div>
                        </div>
                      )}

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
            <div className="border-t p-4">
              <div className="space-y-3">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message or command..."
                    disabled={inputBlocked || isLoading || isTyping || simulationComplete || gradingInProgress}
                    className="flex-1"
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={inputBlocked || isLoading || isTyping || !input.trim()}
                  >
                    {isLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                
                {/* Quick command buttons */}
                <div className="flex gap-2 flex-wrap">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setInput("begin")}
                    disabled={inputBlocked || isLoading || isTyping}
                  >
                    Begin
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setInput("help")}
                    disabled={inputBlocked || isLoading || isTyping}
                  >
                    Help
                  </Button>
                  {simulationData.current_scene.personas && simulationData.current_scene.personas.length > 0 && simulationData.current_scene.personas[0]?.name && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        const firstPersona = simulationData.current_scene.personas![0]
                        const mentionId = firstPersona.name.toLowerCase().replace(/\s+/g, '_')
                        setInput(`@${mentionId} `)
                      }}
                      disabled={inputBlocked || isLoading || isTyping}
                    >
                      @{simulationData.current_scene.personas[0]?.name?.split(' ')[0] || 'Persona'}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
      {/* Grading/Feedback Modal - moved inside the return block */}
      {showGrading && gradingData && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl w-full overflow-y-auto max-h-[90vh]">
            <h2 className="text-2xl font-bold mb-4 text-center">Simulation Grading & Feedback</h2>
            <div className="mb-6">
              <div className="text-lg font-semibold">Overall Score: <span className="text-blue-600">{gradingData.overall_score}</span></div>
              <div className="text-gray-700 mt-2">{gradingData.overall_feedback}</div>
            </div>
            {gradingData.scenes && gradingData.scenes.map((scene: any, idx: number) => (
              <div key={scene.id} className="mb-6 border-b pb-4">
                <div className="font-semibold text-blue-700">{scene.title}</div>
                <div className="text-sm text-gray-500 mb-2">{scene.objective}</div>
                <div className="mb-2">
                  <span className="font-medium">Your Responses:</span>
                  <div
                    style={{
                      maxHeight: '120px',
                      overflowY: 'auto',
                      background: '#f9fafb',
                      border: '1px solid #e5e7eb',
                      borderRadius: '0.375rem',
                      padding: '0.5rem',
                      marginTop: '0.5rem',
                      fontSize: '0.95rem',
                      whiteSpace: 'pre-wrap',
                      width: '100%',
                      fontFamily: 'inherit',
                      resize: 'none',
                      color: '#222'
                    }}
                    tabIndex={-1}
                    aria-readonly="true"
                  >
                    {scene.user_responses && scene.user_responses.length > 0
                      ? scene.user_responses.map((msg: any) => `• ${msg.content}`).join('\n\n')
                      : <span className="text-gray-400">No responses.</span>}
                  </div>
                </div>
                <div className="text-sm text-green-700 mb-1">Score: {scene.score}</div>
                <div className="text-gray-700">{scene.feedback}</div>
                {scene.teaching_notes && (
                  <div className="mt-2 text-xs text-gray-500 italic">Teaching Notes: {scene.teaching_notes}</div>
                )}
              </div>
            ))}
            <div className="flex justify-center mt-6">
              <button 
                className="btn btn-primary" 
                onClick={() => {
                  console.log("[DEBUG] Closing grading modal");
                  setShowGrading(false);
                  setGradingHasBeenShown(true);
                  setInputBlocked(false);
                  setCanSubmitForGrading(false);
                  setHasSubmittedForGrading(false);
                  
                  // Update the completion message to show the "View Grading" button
                  setMessages(prev => {
                    console.log("[DEBUG] Current messages before update:", prev);
                    console.log("[DEBUG] Looking for completion message with text containing '🎉 Simulation complete!'");
                    const updatedMessages = prev.map(msg => {
                      console.log("[DEBUG] Checking message:", msg.text.substring(0, 50), "showViewGrading:", msg.showViewGrading, "type:", msg.type);
                      if (msg.text.includes("🎉 Simulation complete!") && msg.type === 'system') {
                        console.log("[DEBUG] FOUND COMPLETION MESSAGE! Updating showViewGrading to true");
                        const updatedMsg = { ...msg, showViewGrading: true };
                        console.log("[DEBUG] Updated message:", updatedMsg);
                        return updatedMsg;
                      }
                      return msg;
                    });
                    console.log("[DEBUG] Final updated messages:", updatedMessages);
                    return updatedMessages;
                  });
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 