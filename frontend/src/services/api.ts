import axios from 'axios';

// Base API configuration
const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface BusinessScenario {
  id: number;
  title: string;
  description: string;
  industry: string;
  challenge: string;
  learning_objectives: string[];
  source_type: 'predefined' | 'pdf' | 'custom';
  source_data: any;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: number;
  name: string;
  role: string;
  expertise: string;
  personality: string;
  authority_level: string;
  responsibilities: string;
  conversation_style: string;
  scenario_id: number;
  created_at: string;
}

export interface Simulation {
  id: number;
  scenario_id: number;
  status: 'active' | 'paused' | 'completed';
  current_turn: number;
  created_at: string;
  updated_at: string;
}

// API Functions
export const apiService = {
  // Scenarios
  getScenarios: async (): Promise<BusinessScenario[]> => {
    const response = await api.get('/scenarios/');
    return response.data;
  },

  getScenario: async (id: number): Promise<BusinessScenario> => {
    const response = await api.get(`/scenarios/${id}`);
    return response.data;
  },

  createScenario: async (scenario: Partial<BusinessScenario>): Promise<BusinessScenario> => {
    const response = await api.post('/scenarios/', scenario);
    return response.data;
  },

  // Agents
  getAgents: async (scenarioId: number): Promise<Agent[]> => {
    const response = await api.get(`/scenarios/${scenarioId}/agents`);
    return response.data;
  },

  createAgent: async (scenarioId: number, agent: Partial<Agent>): Promise<Agent> => {
    const agentData = {
      ...agent,
      scenario_id: scenarioId
    };
    const response = await api.post('/agents/', agentData);
    return response.data;
  },

  // Simulations
  createSimulation: async (scenarioId: number): Promise<Simulation> => {
    const response = await api.post('/simulations', { scenario_id: scenarioId });
    return response.data;
  },

  getSimulation: async (id: number): Promise<Simulation> => {
    const response = await api.get(`/simulations/${id}`);
    return response.data;
  },

  // PDF Processing
  processPDF: async (file: File): Promise<BusinessScenario> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/process-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default apiService; 