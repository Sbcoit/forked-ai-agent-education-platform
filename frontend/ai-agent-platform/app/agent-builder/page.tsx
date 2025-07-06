"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Bot, ArrowLeft, Save, Play, Share, Plus, X, Wand2 } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { apiClient } from "@/lib/api"

export default function AgentBuilder() {
  const router = useRouter()
  const { user, isLoading: authLoading } = useAuth()

  const [agentName, setAgentName] = useState("")
  const [agentRole, setAgentRole] = useState("")
  const [agentGoal, setAgentGoal] = useState("")
  const [agentBackstory, setAgentBackstory] = useState("")
  const [agentCategory, setAgentCategory] = useState("")
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [newTag, setNewTag] = useState("")
  const [isPublic, setIsPublic] = useState(false)
  const [allowRemixes, setAllowRemixes] = useState(true)
  const [verbose, setVerbose] = useState(true)
  const [allowDelegation, setAllowDelegation] = useState(false)
  const [reasoning, setReasoning] = useState(true)
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login")
    }
  }, [user, authLoading, router])

  const availableTools = [
    { id: "web_search", name: "Web Search", description: "Search the internet for information" },
    { id: "calculator", name: "Calculator", description: "Perform mathematical calculations" },
    { id: "email", name: "Email", description: "Send and receive emails" },
    { id: "database_query", name: "Database Query", description: "Query databases for information" },
    { id: "file_reader", name: "File Reader", description: "Read and analyze files" },
    { id: "api_caller", name: "API Caller", description: "Make API calls to external services" },
    { id: "data_analysis", name: "Data Analysis", description: "Analyze and process data" },
    { id: "report_generator", name: "Report Generator", description: "Generate comprehensive reports" },
    { id: "social_media", name: "Social Media", description: "Manage social media interactions" },
  ]

  const agentCategories = [
    "customer_service",
    "data_analysis", 
    "content_creation",
    "sales_marketing",
    "research",
    "automation",
    "education",
    "finance",
    "business"
  ]

  const addTag = () => {
    if (newTag && !tags.includes(newTag)) {
      setTags([...tags, newTag])
      setNewTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const toggleTool = (toolId: string) => {
    setSelectedTools((prev) => (prev.includes(toolId) ? prev.filter((id) => id !== toolId) : [...prev, toolId]))
  }

  const handleSave = async () => {
    if (!user) return

    if (!agentName || !agentRole || !agentGoal || !agentBackstory || !agentCategory) {
      setError("Please fill in all required fields")
      return
    }

    setLoading(true)
    setError("")
    setSuccess("")

    try {
      await apiClient.createAgent({
        name: agentName,
        role: agentRole,
        goal: agentGoal,
        backstory: agentBackstory,
        tools: selectedTools,
        verbose,
        allow_delegation: allowDelegation,
        reasoning,
        category: agentCategory,
        tags,
        is_public: isPublic,
        allow_remixes: allowRemixes,
        version: "1.0.0",
        version_notes: "Initial release"
      })

      setSuccess("Agent created successfully!")
      
      // Reset form or redirect
      setTimeout(() => {
        router.push("/dashboard")
      }, 2000)

    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create agent")
    } finally {
      setLoading(false)
    }
  }

  const handleTest = () => {
    // For now, just show a preview - in the future this could open a test dialog
    console.log("Testing agent with current configuration:", {
      name: agentName,
      role: agentRole,
      goal: agentGoal,
      backstory: agentBackstory,
      tools: selectedTools,
      category: agentCategory,
      tags
    })
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <Bot className="h-12 w-12 text-yellow-500 animate-spin" />
      </div>
    )
  }

  if (!user) return null

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
              <Bot className="h-6 w-6 text-yellow-500" />
              <span className="text-xl font-bold">Agent Builder</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleTest}
              className="border-yellow-500/30 text-yellow-500 bg-transparent"
            >
              <Play className="h-4 w-4 mr-2" />
              Test Agent
            </Button>
            <Button 
              size="sm" 
              onClick={handleSave}
              disabled={loading}
              className="bg-yellow-500 text-black hover:bg-yellow-400"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? "Saving..." : "Save Agent"}
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Create Your AI Agent</h1>
            <p className="text-gray-400">Define your agent's personality, capabilities, and behavior</p>
          </div>

          {/* Success/Error Messages */}
          {success && (
            <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400">
              {success}
            </div>
          )}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
              {error}
            </div>
          )}

          <Tabs defaultValue="basic" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 bg-gray-900">
              <TabsTrigger value="basic" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Basic Info
              </TabsTrigger>
              <TabsTrigger value="tools" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Tools & Capabilities
              </TabsTrigger>
              <TabsTrigger
                value="settings"
                className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black"
              >
                Settings
              </TabsTrigger>
              <TabsTrigger value="preview" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
                Preview
              </TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Bot className="h-5 w-5 mr-2 text-yellow-500" />
                    Agent Identity
                  </CardTitle>
                  <CardDescription>Define who your agent is and what it does</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="agent-name">Agent Name *</Label>
                      <Input
                        id="agent-name"
                        placeholder="e.g., Customer Support Assistant"
                        value={agentName}
                        onChange={(e) => setAgentName(e.target.value)}
                        className="bg-gray-900 border-gray-700 focus:border-yellow-500"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="agent-category">Category *</Label>
                      <Select value={agentCategory} onValueChange={setAgentCategory}>
                        <SelectTrigger className="bg-gray-900 border-gray-700 focus:border-yellow-500">
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent className="bg-gray-900 border-gray-700">
                          {agentCategories.map((category) => (
                            <SelectItem key={category} value={category}>
                              {category.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="agent-role">Role *</Label>
                    <Input
                      id="agent-role"
                      placeholder="e.g., Senior Customer Support Specialist"
                      value={agentRole}
                      onChange={(e) => setAgentRole(e.target.value)}
                      className="bg-gray-900 border-gray-700 focus:border-yellow-500"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="agent-goal">Goal *</Label>
                    <Textarea
                      id="agent-goal"
                      placeholder="e.g., Provide exceptional customer support by resolving issues quickly and efficiently"
                      value={agentGoal}
                      onChange={(e) => setAgentGoal(e.target.value)}
                      className="bg-gray-900 border-gray-700 focus:border-yellow-500 min-h-[80px]"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="agent-backstory">Backstory *</Label>
                    <Textarea
                      id="agent-backstory"
                      placeholder="e.g., You are an experienced customer support specialist with 5+ years of experience..."
                      value={agentBackstory}
                      onChange={(e) => setAgentBackstory(e.target.value)}
                      className="bg-gray-900 border-gray-700 focus:border-yellow-500 min-h-[120px]"
                      required
                    />
                    <div className="flex items-center space-x-2 text-sm text-gray-400">
                      <Wand2 className="h-4 w-4" />
                      <span>Tip: A good backstory helps the agent understand its context and personality</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tools" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Available Tools</CardTitle>
                  <CardDescription>Select the tools and capabilities your agent can use</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    {availableTools.map((tool) => (
                      <div
                        key={tool.id}
                        className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                          selectedTools.includes(tool.id)
                            ? "border-yellow-500 bg-yellow-500/10"
                            : "border-gray-700 hover:border-gray-600"
                        }`}
                        onClick={() => toggleTool(tool.id)}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{tool.name}</h4>
                          {selectedTools.includes(tool.id) && (
                            <Badge className="bg-yellow-500 text-black">Selected</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-400">{tool.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Agent Settings</CardTitle>
                  <CardDescription>Configure how your agent behaves and is shared</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>Tags</Label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="border-yellow-500/30 text-yellow-500">
                          {tag}
                          <button onClick={() => removeTag(tag)} className="ml-2 hover:text-red-400">
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Add a tag"
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyPress={(e) => e.key === "Enter" && addTag()}
                        className="bg-gray-900 border-gray-700 focus:border-yellow-500"
                      />
                      <Button
                        onClick={addTag}
                        size="sm"
                        variant="outline"
                        className="border-yellow-500/30 text-yellow-500 bg-transparent"
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>Verbose Output</Label>
                        <p className="text-sm text-gray-400">Agent provides detailed explanations</p>
                      </div>
                      <Switch checked={verbose} onCheckedChange={setVerbose} />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>Allow Delegation</Label>
                        <p className="text-sm text-gray-400">Agent can delegate tasks to other agents</p>
                      </div>
                      <Switch checked={allowDelegation} onCheckedChange={setAllowDelegation} />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>Enable Reasoning</Label>
                        <p className="text-sm text-gray-400">Agent explains its reasoning process</p>
                      </div>
                      <Switch checked={reasoning} onCheckedChange={setReasoning} />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>Make Public</Label>
                        <p className="text-sm text-gray-400">Allow others to discover and use your agent</p>
                      </div>
                      <Switch checked={isPublic} onCheckedChange={setIsPublic} />
                    </div>

                    {isPublic && (
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label>Allow Remixes</Label>
                          <p className="text-sm text-gray-400">Let others clone and modify your agent</p>
                        </div>
                        <Switch checked={allowRemixes} onCheckedChange={setAllowRemixes} />
                      </div>
                    )}
                  </div>

                  {isPublic && (
                    <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                      <div className="flex items-center space-x-2 mb-2">
                        <Share className="h-4 w-4 text-yellow-500" />
                        <span className="font-medium text-yellow-500">Public Agent</span>
                      </div>
                      <p className="text-sm text-gray-400">
                        Your agent will be visible in the marketplace and can be used by other users. You'll receive
                        credit and feedback from the community.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="preview" className="space-y-6">
              <Card className="bg-black border-yellow-500/20">
                <CardHeader>
                  <CardTitle>Agent Preview</CardTitle>
                  <CardDescription>Review your agent configuration before saving</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Name</h4>
                        <p>{agentName || "Untitled Agent"}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Role</h4>
                        <p>{agentRole || "No role defined"}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Category</h4>
                        <p>{agentCategory ? agentCategory.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') : "No category selected"}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Goal</h4>
                        <p className="text-sm">{agentGoal || "No goal defined"}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Selected Tools</h4>
                        <div className="flex flex-wrap gap-1">
                          {selectedTools.length > 0 ? (
                            selectedTools.map((toolId) => {
                              const tool = availableTools.find((t) => t.id === toolId)
                              return (
                                <Badge key={toolId} variant="outline" className="border-blue-400/30 text-blue-400">
                                  {tool?.name}
                                </Badge>
                              )
                            })
                          ) : (
                            <p className="text-gray-400 text-sm">No tools selected</p>
                          )}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Tags</h4>
                        <div className="flex flex-wrap gap-1">
                          {tags.length > 0 ? (
                            tags.map((tag) => (
                              <Badge key={tag} variant="outline" className="border-green-400/30 text-green-400">
                                {tag}
                              </Badge>
                            ))
                          ) : (
                            <p className="text-gray-400 text-sm">No tags added</p>
                          )}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Visibility</h4>
                        <Badge
                          variant={isPublic ? "default" : "secondary"}
                          className={isPublic ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}
                        >
                          {isPublic ? "Public" : "Private"}
                        </Badge>
                      </div>
                      <div>
                        <h4 className="font-medium text-yellow-500 mb-1">Behavior Settings</h4>
                        <div className="space-y-1 text-sm">
                          <p>Verbose: {verbose ? "Enabled" : "Disabled"}</p>
                          <p>Delegation: {allowDelegation ? "Enabled" : "Disabled"}</p>
                          <p>Reasoning: {reasoning ? "Enabled" : "Disabled"}</p>
                          {isPublic && <p>Remixes: {allowRemixes ? "Allowed" : "Not allowed"}</p>}
                        </div>
                      </div>
                    </div>
                  </div>

                  {agentBackstory && (
                    <div>
                      <h4 className="font-medium text-yellow-500 mb-1">Backstory</h4>
                      <p className="text-sm bg-gray-900/50 p-3 rounded-lg">{agentBackstory}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
