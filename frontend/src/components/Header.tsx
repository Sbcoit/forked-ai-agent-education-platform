import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 gradient-bg rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">nA</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold gradient-text">n-aible</span>
              <span className="text-xs text-gray-500">AI Agent Education</span>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/') 
                  ? 'text-primary-600 border-b-2 border-primary-600 pb-4' 
                  : 'text-gray-600 hover:text-primary-600'
              }`}
            >
              Home
            </Link>
            <Link
              to="/scenario-builder"
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/scenario-builder') 
                  ? 'text-primary-600 border-b-2 border-primary-600 pb-4' 
                  : 'text-gray-600 hover:text-primary-600'
              }`}
            >
              Create Scenario
            </Link>
            <Link
              to="/agent-creator"
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/agent-creator') 
                  ? 'text-primary-600 border-b-2 border-primary-600 pb-4' 
                  : 'text-gray-600 hover:text-primary-600'
              }`}
            >
              Design Agents
            </Link>
            <Link
              to="/simulation"
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/simulation') 
                  ? 'text-primary-600 border-b-2 border-primary-600 pb-4' 
                  : 'text-gray-600 hover:text-primary-600'
              }`}
            >
              Run Simulation
            </Link>
          </nav>

          {/* CTA Button */}
          <div className="flex items-center space-x-4">
            <button className="btn-primary">
              Start Creating
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 