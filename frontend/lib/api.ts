// Real API client for connecting to the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`
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

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token')
  }
  return null
}

// Helper function to set auth token in localStorage
const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token)
  }
}

// Helper function to remove auth token from localStorage
const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
  }
}

// Helper function to make authenticated API requests
const apiRequest = async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
  const token = getAuthToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      
      // Handle specific authentication errors
      if (response.status === 401) {
        throw new Error(errorData.detail || "Invalid email or password. Please check your credentials and try again.")
      }
      
      // Handle other HTTP errors
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return response
  } catch (error) {
    // Handle network errors (server not running, CORS, etc.)
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
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
    setAuthToken(data.access_token)
    return data
  },

  register: async (data: RegisterData): Promise<{ user: User; access_token: string }> => {
    console.log('[DEBUG] API register called with data:', data)
    const response = await apiRequest('/users/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    
    const responseData = await response.json()
    setAuthToken(responseData.access_token)
    return responseData
  },

  logout: async (): Promise<void> => {
    removeAuthToken()
  },

  getCurrentUser: async (): Promise<User | null> => {
    try {
      const response = await apiRequest('/users/me')
      const user = await response.json()
      return user
    } catch (error) {
      console.log('No current user found:', error)
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
    const response = await apiRequest('/api/scenarios/')
    return response.json()
  },

  getUserScenarios: async (userId: number): Promise<Scenario[]> => {
    // For now, return all scenarios since user-specific scenarios endpoint doesn't exist
    // TODO: Add user-specific scenarios endpoint to backend
    const response = await apiRequest('/api/scenarios/')
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

  // Simulation methods - using available endpoints
  getSimulations: async (): Promise<any[]> => {
    // For now, return empty array since there's no GET /simulations/ endpoint
    // TODO: Add GET /simulations/ endpoint to backend
    return []
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

  // Utility methods
  isAuthenticated: (): boolean => {
    return getAuthToken() !== null
  },

  getAuthToken: (): string | null => {
    return getAuthToken()
  },

  // Generic authenticated request method
  apiRequest: async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
    return apiRequest(endpoint, options)
  },
} 