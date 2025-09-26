// Real API client for connecting to the backend
import { debugLog } from './debug'
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side rendering - return a placeholder
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
  // Client-side - use environment variable or fallback
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  return `${getApiBaseUrl()}${endpoint}`
}

export interface User {
  id: number
  email: string
  full_name: string
  username: string
  bio?: string
  avatar_url?: string
  role: string
  public_agents_count: number
  public_tools_count: number
  total_downloads: number
  reputation_score: number
  profile_public: boolean
  allow_contact: boolean
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
}

export interface Agent {
  id: string
  name: string  
  description: string
  role: string
  personality: string
  expertise: string[]
  category?: string
  is_public?: boolean
  average_rating?: number
  backstory: string
  tags: string[]
  clone_count: number
  goal: string
  tools: string[]
  verbose: boolean
  allow_delegation: boolean
  reasoning: string
  is_template: boolean
  allow_remixes: boolean
  version: string
  version_notes: string
}

export interface Scenario {
  id: string
  title: string
  description: string
  difficulty: string
  category: string
  agents: Agent[]
  industry?: string
  source_type?: string
  challenge: string
  learning_objectives: string[]
  created_at: string
  clone_count: number
  is_template: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  full_name: string
  username: string
  password: string
  bio?: string
  avatar_url?: string
  profile_public?: boolean
  allow_contact?: boolean
}

// SECURITY: Secure authentication using HttpOnly cookies
// Tokens are now handled server-side via secure cookies, not localStorage
// This prevents XSS attacks from accessing authentication tokens
// Client-side token management has been removed for security

// Helper function to make authenticated API requests
const apiRequest = async (endpoint: string, options: RequestInit = {}, silentAuthError: boolean = false): Promise<Response> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  try {
    const response = await fetch(buildApiUrl(endpoint), {
      ...options,
      headers,
      credentials: 'include', // Include HttpOnly cookies in requests
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      
      // Handle specific authentication errors
      if (response.status === 401) {
        if (silentAuthError) {
          // Return the response without throwing for silent auth errors
          return response
        }
        throw new Error(errorData.detail || "Authentication failed. Please log in again.")
      }
      
      // Handle other HTTP errors
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return response
  } catch (error) {
    console.error('❌ API request failed:', error)
    console.error('❌ Error type:', typeof error)
    console.error('❌ Error message:', error instanceof Error ? error.message : String(error))
    
    // Handle network errors (server not running, CORS, etc.)
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      console.error('❌ Failed to fetch error detected - this usually means network/CORS issue')
      throw new Error("Unable to connect to the server. Please check if the backend is running and try again.")
    }
    
    // Re-throw other errors (including our custom authentication errors)
    throw error
  }
}

// Real API client
export const apiClient = {
  // Auth methods
  login: async (credentials: LoginCredentials): Promise<{ user: User; access_token: string }> => {
    const response = await apiRequest('/users/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
    
    const data = await response.json()
    // Token is now handled server-side via HttpOnly cookies
    return data
  },

  register: async (data: RegisterData): Promise<{ user: User; access_token: string }> => {
    // Log sanitized data (without password)
    const sanitizedData = { ...data, password: '[REDACTED]' }
    debugLog('API register called with data:', sanitizedData)
    
    try {
      console.log('🔍 About to make registration request to:', buildApiUrl('/users/register'))
      const response = await apiRequest('/users/register', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      
      console.log('✅ Registration response received:', response.status, response.statusText)
      const responseData = await response.json()
      console.log('✅ Registration data parsed successfully')
      // Token is now handled server-side via HttpOnly cookies
      return responseData
    } catch (error) {
      console.error('❌ Registration request failed:', error)
      throw error
    }
  },

  logout: async (): Promise<void> => {
    // Call server logout endpoint to clear HttpOnly cookies
    try {
      await apiRequest('/users/logout', { method: 'POST' })
    } catch (error) {
      // Continue with logout even if server call fails
      console.warn('Server logout failed, continuing with client logout:', error)
    }
  },

  // Clear all cached data
  clearAllCache: (): void => {
    if (typeof window !== 'undefined') {
      // Clear localStorage
      const itemsToClear = [
        'auth_token',
        'user_data',
        'session_data',
        'oauth_state',
        'google_oauth_data',
        'chatboxScenario', // From simulation builder
        'sidebar_state' // From sidebar component
      ]
      
      itemsToClear.forEach(item => {
        localStorage.removeItem(item)
      })
      
      // Clear sessionStorage
      sessionStorage.clear()
      
      // Clear any cookies (if any)
      document.cookie.split(";").forEach(cookie => {
        const eqPos = cookie.indexOf("=")
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie
        document.cookie = `${name.trim()}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
      })
      
      console.log('All cache cleared successfully')
    }
  },

  getCurrentUser: async (): Promise<User | null> => {
    try {
      const response = await apiRequest('/users/me')
      const user = await response.json()
      return user
    } catch (error) {
      debugLog('No current user found:', error)
      return null
    }
  },

  // Agent methods
  getAgents: async (): Promise<Agent[]> => {
    // For now, return empty array since agents endpoint doesn't exist yet
    return []
  },

  getUserAgents: async (userId: number): Promise<Agent[]> => {
    // For now, return empty array since agents endpoint doesn't exist yet
    return []
  },

  createAgent: async (agentData: any): Promise<Agent> => {
    // For now, throw error since agents endpoint doesn't exist yet
    throw new Error('Agent creation not implemented yet')
  },

  updateAgent: async (agentId: string, agentData: any): Promise<Agent> => {
    // For now, throw error since agents endpoint doesn't exist yet
    throw new Error('Agent update not implemented yet')
  },

  deleteAgent: async (agentId: string): Promise<void> => {
    // For now, throw error since agents endpoint doesn't exist yet
    throw new Error('Agent deletion not implemented yet')
  },

  // Scenario methods
  getScenarios: async (): Promise<Scenario[]> => {
    const response = await apiRequest('/api/scenarios/?status=active')
    return response.json()
  },

  getUserScenarios: async (userId: number): Promise<Scenario[]> => {
    // For now, return all scenarios since user-specific scenarios endpoint doesn't exist
    // TODO: Add user-specific scenarios endpoint to backend
    const response = await apiRequest('/api/scenarios/?status=active')
    return response.json()
  },

  createScenario: async (scenarioData: any): Promise<Scenario> => {
    // For now, throw error since scenario creation endpoint doesn't exist yet
    throw new Error('Scenario creation not implemented yet')
  },

  updateScenario: async (scenarioId: string, scenarioData: any): Promise<Scenario> => {
    // For now, throw error since scenario update endpoint doesn't exist yet
    throw new Error('Scenario update not implemented yet')
  },

  deleteScenario: async (scenarioId: string): Promise<void> => {
    // For now, throw error since scenario deletion endpoint doesn't exist yet
    throw new Error('Scenario deletion not implemented yet')
  },

  updateScenarioStatus: async (scenarioId: number, status: string): Promise<any> => {
    const response = await apiRequest(`/api/scenarios/${scenarioId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
    
    if (!response.ok) {
      throw new Error('Failed to update scenario status')
    }
    
    return response.json()
  },

  deleteDraftScenario: async (scenarioId: number): Promise<any> => {
    const response = await apiRequest(`/api/scenarios/drafts/${scenarioId}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      throw new Error('Failed to delete draft scenario')
    }
    
    return response.json()
  },

  getDraftScenario: async (scenarioId: number): Promise<any> => {
    const response = await apiRequest(`/api/scenarios/drafts/${scenarioId}`, {
      method: 'GET',
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch draft scenario')
    }
    
    return response.json()
  },

  // Simulation methods - using available endpoints
  getSimulations: async (): Promise<any[]> => {
    try {
      // Fetch both published and draft scenarios
      const [publishedResponse, draftResponse] = await Promise.all([
        apiRequest('/api/scenarios/?status=active', { method: 'GET' }),
        apiRequest('/api/scenarios/drafts/', { method: 'GET' })
      ])
      
      if (!publishedResponse.ok || !draftResponse.ok) {
        throw new Error('Failed to fetch simulations')
      }
      
      const publishedScenarios = await publishedResponse.json()
      const draftScenarios = await draftResponse.json()
      
      // Combine scenarios but filter out drafts that have published versions
      const allScenarios = [...publishedScenarios, ...draftScenarios]
      
      // Filter out duplicates by title - keep only the most recent version of each scenario
      const scenarioMap = new Map()
      
      // Process scenarios and keep only the most recent version of each title
      allScenarios.forEach((scenario: any) => {
        const key = scenario.title
        const existing = scenarioMap.get(key)
        
        if (!existing) {
          // First scenario with this title
          scenarioMap.set(key, scenario)
        } else {
          // Compare scenarios and keep the most recent one
          const existingDate = new Date(existing.updated_at || existing.created_at)
          const currentDate = new Date(scenario.updated_at || scenario.created_at)
          
          if (currentDate > existingDate) {
            scenarioMap.set(key, scenario)
          }
        }
      })
      
      const filteredScenarios = Array.from(scenarioMap.values())
      
      return filteredScenarios.map((scenario: any) => ({
        id: scenario.id,
        title: scenario.title,
        description: scenario.description,
        status: scenario.is_draft ? 'Draft' : 'Active',
        statusColor: scenario.is_draft ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800',
        date: new Date(scenario.created_at).toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        }),
        students: scenario.personas?.length || 0, // Use personas count as student count for now
        created_at: scenario.created_at,
        is_draft: scenario.is_draft,
        published_version_id: scenario.published_version_id
      }))
    } catch (error) {
      console.error('Failed to fetch simulations:', error)
      return []
    }
  },

  createSimulation: async (simulationData: any): Promise<any> => {
    const response = await apiRequest('/simulations/', {
      method: 'POST',
      body: JSON.stringify(simulationData),
    })
    return response.json()
  },

  getSimulation: async (simulationId: string): Promise<any> => {
    // For now, return simulation status since there's no direct GET endpoint
    const response = await apiRequest(`/simulations/${simulationId}/status/`)
    return response.json()
  },

  // User profile methods
  updateProfile: async (profileData: any): Promise<User> => {
    const response = await apiRequest('/users/me', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    })
    return response.json()
  },

  changePassword: async (passwordData: { current_password: string; new_password: string }): Promise<{ message: string }> => {
    const response = await apiRequest('/users/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    })
    return response.json()
  },

  // Cohort methods
  getCohorts: async (): Promise<any[]> => {
    const response = await apiRequest('/cohorts/')
    return response.json()
  },

  getCohort: async (cohortId: string): Promise<any> => {
    const response = await apiRequest(`/cohorts/${cohortId}`)
    return response.json()
  },

  getCohortStudents: async (cohortId: string): Promise<any[]> => {
    const response = await apiRequest(`/cohorts/${cohortId}/students`)
    return response.json()
  },

  getCohortSimulations: async (cohortId: string): Promise<any[]> => {
    const response = await apiRequest(`/cohorts/${cohortId}/simulations`)
    return response.json()
  },

  assignSimulationToCohort: async (cohortId: number, simulationData: any): Promise<any> => {
    const response = await apiRequest(`/cohorts/${cohortId}/simulations`, {
      method: 'POST',
      body: JSON.stringify(simulationData),
    })
    return response.json()
  },

  removeSimulationFromCohort: async (cohortId: number, simulationAssignmentId: number): Promise<any> => {
    const response = await apiRequest(`/cohorts/${cohortId}/simulations/${simulationAssignmentId}`, {
      method: 'DELETE',
    })
    return response.json()
  },

  createCohort: async (cohortData: any): Promise<any> => {
    const response = await apiRequest('/cohorts/', {
      method: 'POST',
      body: JSON.stringify(cohortData),
    })
    return response.json()
  },

  updateCohort: async (cohortId: string, cohortData: any): Promise<any> => {
    const response = await apiRequest(`/cohorts/${cohortId}`, {
      method: 'PUT',
      body: JSON.stringify(cohortData),
    })
    return response.json()
  },

  deleteCohort: async (cohortId: string): Promise<void> => {
    await apiRequest(`/cohorts/${cohortId}`, {
      method: 'DELETE',
    })
  },

  // Student cohort methods
  getStudentCohorts: async (): Promise<any> => {
    const response = await apiRequest('/student/cohorts', { method: 'GET' })
    if (!response.ok) throw new Error('Failed to get student cohorts')
    return response.json()
  },

  // Student simulation instance methods
  getStudentSimulationInstances: async (statusFilter?: string, cohortId?: number): Promise<any> => {
    const params = new URLSearchParams()
    if (statusFilter) params.append('status_filter', statusFilter)
    if (cohortId) params.append('cohort_id', cohortId.toString())
    
    const response = await apiRequest(`/student-simulation-instances?${params.toString()}`, {
      method: 'GET',
    })
    if (!response.ok) throw new Error('Failed to get student simulation instances')
    return response.json()
  },

  createStudentSimulationInstance: async (cohortAssignmentId: number): Promise<any> => {
    const response = await apiRequest('/student-simulation-instances', {
      method: 'POST',
      body: JSON.stringify({ cohort_assignment_id: cohortAssignmentId, student_id: 0 }), // student_id will be set by backend
    })
    if (!response.ok) throw new Error('Failed to create student simulation instance')
    return response.json()
  },

  startSimulationInstance: async (instanceId: number): Promise<any> => {
    const response = await apiRequest(`/student-simulation-instances/${instanceId}/start`, {
      method: 'POST',
    })
    if (!response.ok) throw new Error('Failed to start simulation instance')
    return response.json()
  },

  completeSimulationInstance: async (instanceId: number): Promise<any> => {
    const response = await apiRequest(`/student-simulation-instances/${instanceId}/complete`, {
      method: 'POST',
    })
    if (!response.ok) throw new Error('Failed to complete simulation instance')
    return response.json()
  },

  updateSimulationInstance: async (instanceId: number, updateData: any): Promise<any> => {
    const response = await apiRequest(`/student-simulation-instances/${instanceId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    })
    if (!response.ok) throw new Error('Failed to update simulation instance')
    return response.json()
  },

  // Utility methods
  isAuthenticated: (): boolean => {
    // Authentication is now determined by server-side HttpOnly cookies
    // This method is deprecated - use the auth context's isAuthenticated instead
    console.warn('apiClient.isAuthenticated() is deprecated. Use the auth context instead.')
    return false
  },

  // Generic authenticated request method
  apiRequest: async (endpoint: string, options: RequestInit = {}, silentAuthError: boolean = false): Promise<Response> => {
    return apiRequest(endpoint, options, silentAuthError)
  },
} 