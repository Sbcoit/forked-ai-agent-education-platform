import React, { useState } from 'react';
import { BusinessScenario } from '../services/api';

interface SimulationRunnerProps {
  currentStage: number;
  setCurrentStage: (stage: number) => void;
  selectedScenario: BusinessScenario | null;
}

const SimulationRunner: React.FC<SimulationRunnerProps> = ({ currentStage, setCurrentStage, selectedScenario }) => {
  const [messages] = useState([
    {
      type: 'system',
      content: 'Welcome to your business simulation! You are the CEO of SunRGY Shell. Your agents are ready to help you make strategic decisions.',
      timestamp: new Date().toISOString()
    }
  ]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="gradient-bg text-white rounded-xl p-8 mb-8">
          <h1 className="text-3xl font-bold mb-4">🚀 Business Simulation in Action</h1>
          <p className="text-lg text-blue-100">
            You are the CEO of SunRGY Shell. Guide your team through critical business decisions.
          </p>
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-semibold">Budget:</span> $500K
            </div>
            <div>
              <span className="font-semibold">Timeline:</span> 12 weeks
            </div>
            <div>
              <span className="font-semibold">Market:</span> Competitive
            </div>
            <div>
              <span className="font-semibold">Team Morale:</span> 80%
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Chat Area */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">💬 Live Agent Conversation</h2>
              </div>
              
              <div className="p-6 h-96 overflow-y-auto">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`mb-4 p-4 rounded-lg ${
                      message.type === 'system' 
                        ? 'bg-blue-50 border-l-4 border-blue-400' 
                        : 'bg-gray-50'
                    }`}
                  >
                    <p className="text-gray-800">{message.content}</p>
                  </div>
                ))}
              </div>

              <div className="p-6 border-t border-gray-200">
                <div className="flex space-x-4">
                  <input
                    type="text"
                    placeholder="Type your message to the team..."
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <button className="btn-primary">
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Agents Panel */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 Your Team</h3>
              <div className="space-y-4">
                {[
                  { name: 'Alex', role: 'Marketing', status: 'online', color: 'bg-red-100' },
                  { name: 'Morgan', role: 'Finance', status: 'online', color: 'bg-green-100' },
                  { name: 'Taylor', role: 'Product', status: 'online', color: 'bg-blue-100' },
                  { name: 'Jordan', role: 'Operations', status: 'online', color: 'bg-purple-100' }
                ].map((agent) => (
                  <div key={agent.name} className="flex items-center space-x-3">
                    <div className={`w-10 h-10 ${agent.color} rounded-full flex items-center justify-center`}>
                      <span className="text-sm font-semibold">{agent.name[0]}</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{agent.name}</p>
                      <p className="text-sm text-gray-500">{agent.role}</p>
                    </div>
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Simulation Metrics</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Decisions Made</span>
                    <span>3/10</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full" style={{width: '30%'}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Team Alignment</span>
                    <span>85%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{width: '85%'}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Business Impact</span>
                    <span>Medium</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{width: '60%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationRunner; 