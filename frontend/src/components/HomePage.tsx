import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="gradient-bg text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              🎓 AI Agent Education Platform
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-gray-300 max-w-3xl mx-auto">
              Empowering educators to create dynamic business simulations with AI agents. 
              Transform your classroom with interactive, AI-powered learning experiences.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/scenario-builder" className="btn-secondary bg-white hover:bg-gray-100 text-primary-600">
                🚀 Start Creating
              </Link>
              <button className="bg-primary-800 hover:bg-primary-900 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200">
                📖 Learn More
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Transform Education with <span className="gradient-text">AI Agents</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Create immersive business simulations where students interact with custom AI agents, 
              learning through realistic scenario-based experiences.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card p-8 text-center animate-slide-up">
              <div className="w-16 h-16 gradient-bg rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🏢</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Multi-Modal Scenario Creation</h3>
              <p className="text-gray-600 mb-6">
                Create scenarios from templates, upload PDF case studies, or build completely custom business challenges.
              </p>
              <ul className="text-sm text-gray-500 space-y-2">
                <li>• Pre-defined business scenarios</li>
                <li>• PDF case study analysis</li>
                <li>• Custom scenario builder</li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="card p-8 text-center animate-slide-up" style={{animationDelay: '0.1s'}}>
              <div className="w-16 h-16 gradient-bg rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">AI-Powered Agent Creation</h3>
              <p className="text-gray-600 mb-6">
                Design intelligent agents with unique personalities, expertise areas, and decision-making capabilities.
              </p>
              <ul className="text-sm text-gray-500 space-y-2">
                <li>• Conversational agent design</li>
                <li>• Custom personalities & expertise</li>
                <li>• Authority levels & decision criteria</li>
              </ul>
            </div>

            {/* Feature 3 */}
            <div className="card p-8 text-center animate-slide-up" style={{animationDelay: '0.2s'}}>
              <div className="w-16 h-16 gradient-bg rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Interactive Simulations</h3>
              <p className="text-gray-600 mb-6">
                Run live business simulations where students make decisions and receive real-time feedback from AI agents.
              </p>
              <ul className="text-sm text-gray-500 space-y-2">
                <li>• CEO-perspective decision making</li>
                <li>• Multi-agent conversations</li>
                <li>• Real-time business impact analysis</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Create powerful educational experiences in four simple steps
            </p>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-center space-y-8 md:space-y-0 md:space-x-8">
            {[
              { number: 1, title: "Setup Business", desc: "Choose or create your business scenario" },
              { number: 2, title: "Create Agents", desc: "Design AI agents with unique roles" },
              { number: 3, title: "Configure Roles", desc: "Set authority levels and responsibilities" },
              { number: 4, title: "Run Simulation", desc: "Launch interactive learning experience" }
            ].map((step, index) => (
              <div key={step.number} className="flex flex-col items-center text-center">
                <div className="stage-indicator active mb-4">
                  {step.number}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-sm text-gray-600 max-w-32">{step.desc}</p>
                {index < 3 && (
                  <div className="hidden md:block w-16 h-0.5 bg-primary-300 mt-8"></div>
                )}
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link to="/scenario-builder" className="btn-primary">
              Get Started Now →
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-bg text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to revolutionize your classroom?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join educators worldwide who are transforming business education with AI-powered simulations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/scenario-builder" className="btn-secondary bg-white hover:bg-gray-100 text-primary-600">
              Create Your First Scenario
            </Link>
            <a 
              href="https://www.n-aible.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-primary-800 hover:bg-primary-900 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200"
            >
              Learn About n-aible
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage; 