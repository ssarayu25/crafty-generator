import React from 'react';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate('/upload');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center" style={{backgroundColor: '#e1f7d5'}}>
      <div className="text-center max-w-5xl mx-auto px-6">
        {/* Main title */}
        <div className="mb-8">
          <h1 className="text-7xl md:text-8xl font-bold mb-4" style={{color: '#c9c9ff'}}>
            Crafty Generator
          </h1>
        </div>
        
        <div className="bg-white rounded-2xl p-8 mb-12 shadow-lg border-2" style={{borderColor: '#f1cbff'}}>
          <p className="text-2xl mb-6 leading-relaxed font-medium" style={{color: '#c9c9ff'}}>
            AI-Powered Crochet Pattern Generator
          </p>
          <p className="text-lg text-gray-700 max-w-3xl mx-auto leading-relaxed">
            Upload a photo and/or description to get an AI generated crochet pattern, with skill level, estimated time, materials needed, and the pattern instructions.
          </p>
        </div>
        
        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
          <button
            onClick={handleStart}
            className="px-10 py-5 text-white text-xl font-bold rounded-2xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            style={{backgroundColor: '#ffbdbd'}}
          >
            Upload Image
          </button>
          
          <button
            onClick={() => navigate('/upload?mode=text')}
            className="px-10 py-5 text-white text-xl font-bold rounded-2xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            style={{backgroundColor: '#c9c9ff'}}
          >
            Describe Project
          </button>
        </div>
        
        {/* Feature highlights */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105" style={{borderLeft: '4px solid #f1cbff'}}>
            <h3 className="text-lg font-bold text-gray-800 mb-2">AI-Powered</h3>
            <p className="text-gray-600 text-sm">Advanced AI analyzes your images and descriptions to create perfect patterns</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105" style={{borderLeft: '4px solid #ffbdbd'}}>
            <h3 className="text-lg font-bold text-gray-800 mb-2">Downloadable</h3>
            <p className="text-gray-600 text-sm">Clean .txt files with patterns are instantly available for download</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105" style={{borderLeft: '4px solid #c9c9ff'}}>
            <h3 className="text-lg font-bold text-gray-800 mb-2">Trained on 1000+ Patterns</h3>
            <p className="text-gray-600 text-sm">Model trained on thousands of crochet patterns for accurate results</p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default HomePage;