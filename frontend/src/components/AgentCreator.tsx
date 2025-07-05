import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BusinessScenario, Agent, apiService } from '../services/api';

interface AgentCreatorProps {
  currentStage: number;
  setCurrentStage: (stage: number) => void;
  selectedScenario: BusinessScenario | null;
}

interface AgentConfig {
  name: string;
  role: string;
  icon: string;
  color: string;
  personality: string;
  expertise: string[];
  responsibilities: string;
}

const AgentCreator: React.FC<AgentCreatorProps> = ({ currentStage, setCurrentStage, selectedScenario }) => {
  const navigate = useNavigate();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [configuringAgent, setConfiguringAgent] = useState<AgentConfig | null>(null);
  const [agentForm, setAgentForm] = useState({
    personality: '',
    expertise: '',
    responsibilities: ''
  });

  // Default agent templates
  const defaultAgents: AgentConfig[] = [
    { 
      name: 'Alex', 
      role: 'Marketing', 
      icon: '📱', 
      color: 'bg-red-100',
      personality: 'Creative, data-driven, and customer-focused marketing professional',
      expertise: ['Digital Marketing', 'Brand Strategy', 'Market Research', 'Social Media', 'Content Strategy'],
      responsibilities: 'Develop marketing strategies, analyze market trends, manage brand positioning, and drive customer acquisition'
    },
    { 
      name: 'Morgan', 
      role: 'Finance', 
      icon: '💰', 
      color: 'bg-green-100',
      personality: 'Analytical, detail-oriented, and strategic financial expert',
      expertise: ['Financial Planning', 'Budget Management', 'Risk Assessment', 'Investment Analysis', 'Cost Control'],
      responsibilities: 'Manage budgets, analyze financial performance, assess risks, and provide strategic financial guidance'
    },
    { 
      name: 'Taylor', 
      role: 'Product', 
      icon: '⚡', 
      color: 'bg-slate-100',
      personality: 'Innovative, user-centric, and technically-minded product leader',
      expertise: ['Product Strategy', 'User Experience', 'Feature Development', 'Market Validation', 'Technical Leadership'],
      responsibilities: 'Define product vision, prioritize features, coordinate development, and ensure market fit'
    },
    { 
      name: 'Jordan', 
      role: 'Operations', 
      icon: '🔧', 
      color: 'bg-purple-100',
      personality: 'Efficient, process-oriented, and problem-solving operations specialist',
      expertise: ['Process Optimization', 'Supply Chain', 'Quality Management', 'Team Coordination', 'Logistics'],
      responsibilities: 'Streamline operations, manage processes, coordinate teams, and ensure efficient execution'
    }
  ];

  // Check if we have a selected scenario
  useEffect(() => {
    if (!selectedScenario) {
      navigate('/scenario-builder');
    }
  }, [selectedScenario, navigate]);

  // Load existing agents for this scenario
  useEffect(() => {
    if (selectedScenario) {
      loadAgents();
    }
  }, [selectedScenario]);

  const loadAgents = async () => {
    if (!selectedScenario) return;
    
    try {
      setLoading(true);
      const existingAgents = await apiService.getAgents(selectedScenario.id);
      setAgents(existingAgents);
    } catch (err) {
      console.error('Error loading agents:', err);
      setError('Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigureAgent = (agentConfig: AgentConfig) => {
    setConfiguringAgent(agentConfig);
    setAgentForm({
      personality: agentConfig.personality,
      expertise: agentConfig.expertise.join('\n'),
      responsibilities: agentConfig.responsibilities
    });
  };

  const handleSaveAgent = async () => {
    if (!selectedScenario || !configuringAgent) return;

    try {
      setLoading(true);
             const agent = await apiService.createAgent(selectedScenario.id, {
         name: configuringAgent.name,
         role: configuringAgent.role,
         expertise: agentForm.expertise,
         personality: agentForm.personality,
         authority_level: 'medium',
         responsibilities: agentForm.responsibilities,
         conversation_style: 'professional'
       });
      
      setAgents([...agents, agent]);
      setConfiguringAgent(null);
      setError(null);
    } catch (err) {
      console.error('Error creating agent:', err);
      setError('Failed to create agent');
    } finally {
      setLoading(false);
    }
  };

  const isAgentConfigured = (agentConfig: AgentConfig) => {
    return agents.some(agent => agent.name === agentConfig.name);
  };

  const handleContinueToSimulation = () => {
    if (agents.length === 0) {
      setError('Please configure at least one agent before continuing');
      return;
    }
    navigate('/simulation');
  };

  if (!selectedScenario) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Scenario Selected</h2>
          <p className="text-gray-600 mb-6">Please select a business scenario first.</p>
          <button 
            onClick={() => navigate('/scenario-builder')}
            className="btn-primary"
          >
            Go to Scenario Builder
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Scenario Info */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🏢</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{selectedScenario.title}</h2>
              <p className="text-gray-600">{selectedScenario.industry} • {selectedScenario.description}</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold gradient-text mb-4">🤖 Step 2: Create Your AI Agents</h1>
          <p className="text-gray-600 text-lg mb-8">
            Design intelligent agents with unique personalities and expertise areas for your {selectedScenario.title} simulation.
          </p>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800">{error}</p>
              <button 
                onClick={() => setError(null)}
                className="text-red-600 underline ml-2"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Agent Configuration Progress */}
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-gray-800">
              <strong>Progress:</strong> {agents.length} of {defaultAgents.length} agents configured
            </p>
          </div>
          
          {/* Agent Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {defaultAgents.map((agentConfig) => {
              const isConfigured = isAgentConfigured(agentConfig);
              return (
                <div key={agentConfig.name} className={`agent-card ${isConfigured ? 'ring-2 ring-green-400' : ''}`}>
                  <div className={`w-16 h-16 ${agentConfig.color} rounded-full flex items-center justify-center mx-auto mb-4 relative`}>
                    <span className="text-2xl">{agentConfig.icon}</span>
                    {isConfigured && (
                      <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-center mb-2">{agentConfig.name}</h3>
                  <p className="text-gray-600 text-center mb-4">{agentConfig.role} Specialist</p>
                  <button 
                    onClick={() => handleConfigureAgent(agentConfig)}
                    disabled={loading}
                    className={`w-full text-sm ${isConfigured ? 'btn-secondary' : 'btn-primary'} ${loading ? 'opacity-50' : ''}`}
                  >
                    {isConfigured ? 'Reconfigure' : 'Configure Agent'}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Continue Button */}
          <div className="text-center">
            <button 
              onClick={handleContinueToSimulation}
              disabled={agents.length === 0}
              className={`btn-primary ${agents.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              Continue to Simulation →
            </button>
            {agents.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">Configure at least one agent to continue</p>
            )}
          </div>
        </div>
      </div>

      {/* Agent Configuration Modal */}
      {configuringAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center space-x-4 mb-6">
                <div className={`w-12 h-12 ${configuringAgent.color} rounded-full flex items-center justify-center`}>
                  <span className="text-2xl">{configuringAgent.icon}</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Configure {configuringAgent.name}</h2>
                  <p className="text-gray-600">{configuringAgent.role} Specialist</p>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Personality & Tone:</label>
                  <textarea
                    rows={3}
                    value={agentForm.personality}
                    onChange={(e) => setAgentForm({...agentForm, personality: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Describe the agent's personality, communication style, and approach..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Expertise Areas (one per line):</label>
                  <textarea
                    rows={4}
                    value={agentForm.expertise}
                    onChange={(e) => setAgentForm({...agentForm, expertise: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Digital Marketing&#10;Brand Strategy&#10;Market Research"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Key Responsibilities:</label>
                  <textarea
                    rows={3}
                    value={agentForm.responsibilities}
                    onChange={(e) => setAgentForm({...agentForm, responsibilities: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="What are this agent's main responsibilities in the simulation?"
                  />
                </div>
              </div>

              <div className="flex space-x-4 mt-8">
                <button
                  onClick={() => setConfiguringAgent(null)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveAgent}
                  disabled={loading || !agentForm.personality || !agentForm.responsibilities}
                  className={`flex-1 btn-primary ${loading || !agentForm.personality || !agentForm.responsibilities ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {loading ? 'Saving...' : 'Save Agent'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentCreator; 