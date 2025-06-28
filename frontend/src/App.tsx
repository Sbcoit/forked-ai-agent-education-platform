import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import ScenarioBuilder from './components/ScenarioBuilder';
import AgentCreator from './components/AgentCreator';
import SimulationRunner from './components/SimulationRunner';
import Header from './components/Header';
import { BusinessScenario } from './services/api';
import './App.css';

function App() {
  const [currentStage, setCurrentStage] = useState(1);
  const [selectedScenario, setSelectedScenario] = useState<BusinessScenario | null>(null);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route 
              path="/scenario-builder" 
              element={
                <ScenarioBuilder 
                  currentStage={currentStage} 
                  setCurrentStage={setCurrentStage}
                  selectedScenario={selectedScenario}
                  setSelectedScenario={setSelectedScenario}
                />
              } 
            />
            <Route 
              path="/agent-creator" 
              element={
                <AgentCreator 
                  currentStage={currentStage} 
                  setCurrentStage={setCurrentStage}
                  selectedScenario={selectedScenario}
                />
              } 
            />
            <Route 
              path="/simulation" 
              element={
                <SimulationRunner 
                  currentStage={currentStage} 
                  setCurrentStage={setCurrentStage}
                  selectedScenario={selectedScenario}
                />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
