import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const PatternGenerator = () => {
  const [description, setDescription] = useState('');
  const [skillLevel, setSkillLevel] = useState('INTERMEDIATE');
  const [pattern, setPattern] = useState('');
  const [loading, setLoading] = useState(false);
  const [patternData, setPatternData] = useState(null);
  const navigate = useNavigate();

  const generatePattern = async () => {
    if (!description.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8081/generate-simple-pattern', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: description,
          skill_level: skillLevel
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPattern(data.pattern);
        setPatternData(data);
      } else {
        setPattern(`Error: ${data.error}`);
        setPatternData(null);
      }
    } catch (error) {
      setPattern(`Error: ${error.message}`);
      setPatternData(null);
    }
    setLoading(false);
  };

  const downloadPattern = () => {
    if (!pattern) return;
    const element = document.createElement('a');
    const file = new Blob([pattern], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'crochet_pattern.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadPDF = async () => {
    if (!pattern) return;
    try {
      const response = await axios.post('http://localhost:8081/generate-pdf', {
        pattern: pattern,
        title: `${description} - Crochet Pattern`
      }, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'crochet_pattern.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF');
    }
  };

  return (
    <div className="min-h-screen py-8" style={{backgroundColor: '#e1f7d5'}}>
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-8">
          <button 
            onClick={() => navigate('/')}
            className="mb-4 flex items-center mx-auto transition-colors duration-200 group"
            style={{color: '#c9c9ff'}}
          >
            <span className="transform group-hover:-translate-x-1 transition-transform duration-200">←</span>
            <span className="ml-2">Back to Home</span>
          </button>
          <h1 className="text-5xl font-bold mb-2" style={{color: '#c9c9ff'}}>
            Pattern Generator
          </h1>
          <p className="text-gray-600 text-lg">Describe your dream project and watch it come to life!</p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8" style={{border: '2px solid #f1cbff'}}>
          <div className="space-y-6">
            <div className="group">
              <label className="block text-lg font-semibold text-gray-700 mb-3">
                What would you like to crochet?
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Start typing..."
                className="w-full h-32 p-4 border-2 rounded-xl transition-all duration-200 resize-none text-gray-700 placeholder-gray-400"
                style={{borderColor: '#f1cbff'}}
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <label className="flex items-center space-x-3">
                <span className="text-lg font-semibold text-gray-700">Skill Level:</span>
                <select
                  value={skillLevel}
                  onChange={(e) => setSkillLevel(e.target.value)}
                  className="px-4 py-2 border-2 rounded-lg transition-all duration-200 bg-white"
                  style={{borderColor: '#f1cbff'}}
                >
                  <option value="BEGINNER">Beginner</option>
                  <option value="EASY">Easy</option>
                  <option value="INTERMEDIATE">Intermediate</option>
                  <option value="ADVANCED">Advanced</option>
                </select>
              </label>
            </div>

            <button
              onClick={generatePattern}
              disabled={loading || !description.trim()}
              className={`w-full py-4 px-8 rounded-xl font-bold text-lg transition-all duration-300 transform text-white ${
                loading || !description.trim()
                  ? 'cursor-not-allowed'
                  : 'hover:scale-105 hover:shadow-lg active:scale-95'
              }`}
              style={loading || !description.trim() ? {backgroundColor: '#ffbdbd', opacity: 0.5} : {backgroundColor: '#ffbdbd'}}
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  <span>Generating Magic...</span>
                </div>
              ) : (
                'Generate Pattern'
              )}
            </button>
          </div>
        </div>

        {/* Results */}
        {pattern && (
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden animate-fadeIn" style={{border: '2px solid #f1cbff'}}>
            {/* Header with download buttons */}
            <div className="p-6 text-white" style={{backgroundColor: '#c9c9ff'}}>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h2 className="text-2xl font-bold mb-1">Your Pattern is Ready!</h2>
                  <p className="opacity-90">Time to start crocheting!</p>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={downloadPattern}
                    className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    Download TXT
                  </button>

                </div>
              </div>
            </div>
            
            {/* Pattern Content */}
            <div className="p-8">
              {patternData && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 p-6 rounded-xl" style={{backgroundColor: '#e1f7d5'}}>
                  <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <div className="text-sm text-gray-600">Skill Level</div>
                    <div className="font-bold" style={{color: '#c9c9ff'}}>{skillLevel}</div>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <div className="text-sm text-gray-600">Training Examples</div>
                    <div className="font-bold" style={{color: '#c9c9ff'}}>{patternData.training_examples_used || 'N/A'}</div>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <div className="text-sm text-gray-600">Status</div>
                    <div className="font-bold text-green-600">Generated</div>
                  </div>
                </div>
              )}
              
              <div className="rounded-xl p-6 border-2 border-dashed" style={{backgroundColor: '#f1cbff', borderColor: '#c9c9ff'}}>
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  Pattern Instructions
                </h3>
                <div className="bg-white rounded-lg p-4 shadow-inner max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono leading-relaxed">
                    {pattern}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
};

export default PatternGenerator;