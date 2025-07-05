import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, BusinessScenario } from '../services/api';

interface ScenarioBuilderProps {
  currentStage: number;
  setCurrentStage: (stage: number) => void;
  selectedScenario: BusinessScenario | null;
  setSelectedScenario: (scenario: BusinessScenario) => void;
}

const ScenarioBuilder: React.FC<ScenarioBuilderProps> = ({ 
  currentStage, 
  setCurrentStage, 
  selectedScenario, 
  setSelectedScenario 
}) => {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState('predefined');
  const [scenarios, setScenarios] = useState<BusinessScenario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Custom scenario form state
  const [customScenario, setCustomScenario] = useState({
    title: '',
    description: '',
    industry: '',
    challenge: '',
    learning_objectives: ''
  });

  // PDF upload state
  const [uploadingPDF, setUploadingPDF] = useState(false);
  const [pdfFile, setPdfFile] = useState<File | null>(null);

  // Fetch predefined scenarios
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        setLoading(true);
        const data = await apiService.getScenarios();
        setScenarios(data.filter(s => s.source_type === 'predefined'));
      } catch (err) {
        setError('Failed to load scenarios. Please check your backend connection.');
        console.error('Error fetching scenarios:', err);
      } finally {
        setLoading(false);
      }
    };

    if (selectedTab === 'predefined') {
      fetchScenarios();
    }
  }, [selectedTab]);

  const handleSelectScenario = (scenario: BusinessScenario) => {
    setSelectedScenario(scenario);
    navigate('/agent-creator');
  };

  const handleCreateCustomScenario = async () => {
    try {
      setLoading(true);
      const scenario = await apiService.createScenario({
        title: customScenario.title,
        description: customScenario.description,
        industry: customScenario.industry,
        challenge: customScenario.challenge,
        learning_objectives: customScenario.learning_objectives.split('\n').filter(obj => obj.trim()),
        source_type: 'custom',
        source_data: customScenario,
        created_by: 1 // Placeholder user ID
      });
      setSelectedScenario(scenario);
      navigate('/agent-creator');
    } catch (err) {
      setError('Failed to create custom scenario. Please try again.');
      console.error('Error creating scenario:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePDFUpload = async (file: File) => {
    try {
      setUploadingPDF(true);
      const scenario = await apiService.processPDF(file);
      setSelectedScenario(scenario);
      navigate('/agent-creator');
    } catch (err) {
      setError('Failed to process PDF. Please try again.');
      console.error('Error processing PDF:', err);
    } finally {
      setUploadingPDF(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
      handlePDFUpload(file);
    } else {
      setError('Please select a valid PDF file.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-4">🏢 Step 1: Choose Your Business Scenario</h1>
          <p className="text-gray-600 text-lg">
            Select from pre-defined business scenarios, create your own, or upload a PDF case study to build your simulation.
          </p>
          {selectedScenario && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800">
                ✅ Selected: <strong>{selectedScenario.title}</strong>
              </p>
            </div>
          )}
        </div>

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

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex">
              {[
                { id: 'predefined', label: '📋 Pre-defined Scenarios', icon: '📋' },
                { id: 'upload', label: '📄 Upload PDF Case Study', icon: '📄' },
                { id: 'custom', label: '✨ Create Custom', icon: '✨' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`flex-1 py-4 px-6 text-sm font-medium transition-colors duration-200 ${
                    selectedTab === tab.id
                      ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                      : 'text-gray-500 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-8">
            {/* Pre-defined Scenarios Tab */}
            {selectedTab === 'predefined' && (
              <div className="space-y-6">
                {loading ? (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">🔄</div>
                    <p className="text-gray-600">Loading scenarios...</p>
                  </div>
                ) : scenarios.length > 0 ? (
                  <div className="grid md:grid-cols-2 gap-6">
                    {scenarios.map((scenario) => (
                      <div key={scenario.id} className="card p-6 cursor-pointer hover:shadow-xl transition-all duration-300">
                        <div className="flex items-start space-x-4">
                          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                            <span className="text-2xl">🏢</span>
                          </div>
                          <div className="flex-1">
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">{scenario.title}</h3>
                            <p className="text-gray-600 mb-3">{scenario.description}</p>
                            <p className="text-sm text-gray-500 mb-3">
                              <strong>Industry:</strong> {scenario.industry}
                            </p>
                            <p className="text-sm text-gray-500 mb-3">
                              <strong>Challenge:</strong> {scenario.challenge}
                            </p>
                            <p className="text-sm text-gray-500 mb-4">
                              <strong>Learning Objectives:</strong> {scenario.learning_objectives.join(', ')}
                            </p>
                            <button 
                              onClick={() => handleSelectScenario(scenario)}
                              className="btn-primary w-full"
                            >
                              Select This Scenario
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">📋</div>
                    <p className="text-gray-600">No predefined scenarios available.</p>
                    <p className="text-sm text-gray-500 mt-2">Try creating a custom scenario or uploading a PDF.</p>
                  </div>
                )}
              </div>
            )}

            {/* Upload PDF Tab */}
            {selectedTab === 'upload' && (
              <div className="text-center py-12">
                <div className="border-3 border-dashed border-gray-300 rounded-xl p-12 hover:border-primary-400 transition-colors duration-200">
                  <div className="text-6xl mb-6">📄</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Upload Your PDF Case Study</h3>
                  <p className="text-gray-600 mb-6">Drop your PDF here or click to browse</p>
                  <p className="text-sm text-gray-500 mb-6">
                    Supported formats: PDF (max 10MB)<br/>
                    Examples: Harvard Business Review cases, company case studies, research papers
                  </p>
                  
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="pdf-upload"
                  />
                  <label 
                    htmlFor="pdf-upload" 
                    className={`btn-primary inline-block cursor-pointer ${uploadingPDF ? 'opacity-50' : ''}`}
                  >
                    {uploadingPDF ? 'Processing PDF...' : 'Choose PDF File'}
                  </label>
                  
                  {pdfFile && (
                                    <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <p className="text-gray-800">Selected: {pdfFile.name}</p>
                </div>
                  )}
                </div>
              </div>
            )}

            {/* Custom Creation Tab */}
            {selectedTab === 'custom' && (
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Business Name:</label>
                    <input
                      type="text"
                      value={customScenario.title}
                      onChange={(e) => setCustomScenario({...customScenario, title: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Enter your business name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Industry Focus:</label>
                    <select 
                      value={customScenario.industry}
                      onChange={(e) => setCustomScenario({...customScenario, industry: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="">Select an industry...</option>
                      <option value="eco-friendly">EcoFriendly Products</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="fintech">FinTech</option>
                      <option value="education">Education Technology</option>
                      <option value="retail">Retail</option>
                      <option value="manufacturing">Manufacturing</option>
                      <option value="services">Services</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Business Description:</label>
                  <textarea
                    rows={3}
                    value={customScenario.description}
                    onChange={(e) => setCustomScenario({...customScenario, description: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Describe your business concept..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Business Challenge Description:</label>
                  <textarea
                    rows={4}
                    value={customScenario.challenge}
                    onChange={(e) => setCustomScenario({...customScenario, challenge: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Describe the main business challenge students will need to solve..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Learning Objectives (one per line):</label>
                  <textarea
                    rows={3}
                    value={customScenario.learning_objectives}
                    onChange={(e) => setCustomScenario({...customScenario, learning_objectives: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="What should students learn from this simulation?&#10;Example:&#10;Strategic planning&#10;Financial management&#10;Team collaboration"
                  />
                </div>
                <button 
                  onClick={handleCreateCustomScenario}
                  disabled={loading || !customScenario.title || !customScenario.description}
                  className={`btn-primary w-full ${loading || !customScenario.title || !customScenario.description ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {loading ? 'Creating Scenario...' : 'Create Custom Scenario'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Next Step */}
        {selectedScenario && (
          <div className="mt-8 text-center">
            <button 
              onClick={() => navigate('/agent-creator')}
              className="btn-primary"
            >
              Continue to Agent Creation →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScenarioBuilder; 