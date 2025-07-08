import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

function FileUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [patternData, setPatternData] = useState(null);
  const [userPrompt, setUserPrompt] = useState('');
  const [textMode, setTextMode] = useState(false);
  const [textDescription, setTextDescription] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  // Check URL parameter to set initial mode
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    if (urlParams.get('mode') === 'text') {
      setTextMode(true);
    }
  }, [location]);



  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setPatternData(null);
  };

  const handleImageSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert('Please select a file to upload.');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('style', 'standard');
    formData.append('model_type', 'yarn_master');
    formData.append('user_prompt', userPrompt);

    try {
      const response = await axios.post('http://127.0.0.1:8081/generate-pattern', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setPatternData(response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
      console.error('Error details:', error.response?.data || error.message);
      alert(`Failed to generate pattern: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTextSubmit = async (event) => {
    event.preventDefault();
    if (!textDescription.trim()) {
      alert('Please provide a description.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8081/generate-pattern-from-text', {
        description: textDescription,
        style: 'standard',
        model_type: 'yarn_master'
      });
      setPatternData(response.data);
    } catch (error) {
      console.error('Error generating pattern:', error);
      console.error('Error details:', error.response?.data || error.message);
      alert(`Failed to generate pattern: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadPattern = () => {
    if (!patternData) return;
    const element = document.createElement('a');
    const file = new Blob([patternData.pattern], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'crochet_pattern.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadPDF = async () => {
    if (!patternData) return;
    try {
      const response = await axios.post('http://127.0.0.1:8081/generate-pdf', {
        pattern: patternData.pattern,
        title: 'Crochet Pattern'
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
            className="mb-4 flex items-center mx-auto transition-all duration-200 group"
            style={{color: '#c9c9ff'}}
          >
            <span className="transform group-hover:-translate-x-1 transition-transform duration-200">←</span>
            <span className="ml-2">Back to Home</span>
          </button>
          <h1 className="text-5xl font-bold mb-2" style={{color: '#c9c9ff'}}>
            Generate Your Pattern
          </h1>
          <p className="text-gray-600 text-lg">Choose your preferred method and let the magic begin!</p>
        </div>

        {/* Mode Selection */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8" style={{border: '2px solid #f1cbff'}}>
          <div className="flex justify-center mb-8">
            <div className="bg-gray-100 rounded-xl p-2 flex">
              <button
                onClick={() => setTextMode(false)}
                className={`px-6 py-3 rounded-lg transition-all duration-300 font-semibold ${
                  !textMode 
                    ? 'text-white shadow-lg transform scale-105' 
                    : 'text-gray-600 hover:bg-white/50'
                }`}
                style={!textMode ? {backgroundColor: '#c9c9ff'} : {}}
              >
                Upload Image
              </button>
              <button
                onClick={() => setTextMode(true)}
                className={`px-6 py-3 rounded-lg transition-all duration-300 font-semibold ${
                  textMode 
                    ? 'text-white shadow-lg transform scale-105' 
                    : 'text-gray-600 hover:bg-white/50'
                }`}
                style={textMode ? {backgroundColor: '#c9c9ff'} : {}}
              >
                Text Description
              </button>
            </div>
          </div>



          {/* Input Forms */}
          {!textMode ? (
            <form onSubmit={handleImageSubmit} className="space-y-6">
              <div className="group">
                <label className="block text-lg font-semibold text-gray-700 mb-3">
                  Upload Your Inspiration Image
                </label>
                <div className="relative">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="w-full p-4 border-2 border-dashed rounded-xl transition-all duration-200"
                    style={{
                      borderColor: '#f1cbff'
                    }}
                  />
                  <style jsx>{`
                    input[type="file"]::-webkit-file-upload-button {
                      background-color: #ffbdbd;
                      color: white;
                      border: none;
                      padding: 8px 16px;
                      border-radius: 8px;
                      margin-right: 16px;
                      cursor: pointer;
                      font-weight: 600;
                    }
                    input[type="file"]::file-selector-button {
                      background-color: #ffbdbd;
                      color: white;
                      border: none;
                      padding: 8px 16px;
                      border-radius: 8px;
                      margin-right: 16px;
                      cursor: pointer;
                      font-weight: 600;
                    }
                  `}</style>
                </div>
              </div>
              
              {preview && (
                <div className="flex justify-center animate-fadeIn">
                  <div className="relative group">
                    <img
                      src={preview}
                      alt="Preview"
                      className="w-64 h-64 object-cover rounded-2xl shadow-lg group-hover:shadow-xl transition-all duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </div>
                </div>
              )}
              
              <div className="group">
                <label className="block text-lg font-semibold text-gray-700 mb-3">
                  Additional Details (Optional)
                </label>
                <textarea
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  placeholder="Start typing..."
                  className="w-full p-4 border-2 rounded-xl transition-all duration-200 resize-none"
                  style={{borderColor: '#f1cbff'}}
                  rows="3"
                />
              </div>
              
              <button
                type="submit"
                disabled={loading || !selectedFile}
                className={`w-full py-4 px-8 rounded-xl font-bold text-lg transition-all duration-300 transform text-white ${
                  loading || !selectedFile
                    ? 'cursor-not-allowed'
                    : 'hover:scale-105 hover:shadow-lg active:scale-95'
                }`}
                style={loading || !selectedFile ? {backgroundColor: '#ffbdbd', opacity: 0.5} : {backgroundColor: '#ffbdbd'}}
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                    <span>Analyzing Image...</span>
                  </div>
                ) : (
                  'Generate Pattern from Image'
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleTextSubmit} className="space-y-6">
              <div className="group">
                <label className="block text-lg font-semibold text-gray-700 mb-3">
                  Describe Your Dream Project
                </label>
                <textarea
                  value={textDescription}
                  onChange={(e) => setTextDescription(e.target.value)}
                  placeholder="Start typing..."
                  className="w-full h-32 p-4 border-2 rounded-xl transition-all duration-200 resize-none"
                  style={{borderColor: '#f1cbff'}}
                  required
                />
              </div>
              
              <button
                type="submit"
                disabled={loading || !textDescription.trim()}
                className={`w-full py-4 px-8 rounded-xl font-bold text-lg transition-all duration-300 transform text-white ${
                  loading || !textDescription.trim()
                    ? 'cursor-not-allowed'
                    : 'hover:scale-105 hover:shadow-lg active:scale-95'
                }`}
                style={loading || !textDescription.trim() ? {backgroundColor: '#ffbdbd', opacity: 0.5} : {backgroundColor: '#ffbdbd'}}
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                    <span>Creating Magic...</span>
                  </div>
                ) : (
                  'Generate Pattern from Description'
                )}
              </button>
            </form>
          )}
        </div>

        {/* Results */}
        {patternData && patternData.success && (
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden animate-fadeIn" style={{border: '2px solid #f1cbff'}}>
            {/* Header with download buttons */}
            <div className="p-6 text-white" style={{backgroundColor: '#c9c9ff'}}>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h2 className="text-3xl font-bold mb-1">Your Pattern is Ready!</h2>
                  <p className="opacity-90">Time to start your crochet adventure!</p>
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
            
            <div className="p-8">
              {/* Pattern Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="text-center p-6 rounded-xl" style={{backgroundColor: '#f1cbff', border: '1px solid #c9c9ff'}}>
                  <div className="text-sm text-gray-600 mb-1">Difficulty Level</div>
                  <div className="font-bold text-xl text-gray-800">{patternData.difficulty || 'Intermediate'}</div>
                </div>
                <div className="text-center p-6 rounded-xl" style={{backgroundColor: '#ffbdbd', border: '1px solid #c9c9ff'}}>
                  <div className="text-sm text-gray-600 mb-1">Estimated Time</div>
                  <div className="font-bold text-xl text-gray-800">{patternData.estimated_time || '4-6 hours'}</div>
                </div>
              </div>
              
              {/* Materials */}
              {patternData.materials && patternData.materials.length > 0 && (
                <div className="mb-8 p-6 rounded-xl" style={{backgroundColor: '#e1f7d5', border: '1px solid #c9c9ff'}}>
                  <h3 className="text-xl font-bold text-gray-800 mb-4">
                    Materials
                  </h3>
                  <div className="space-y-2">
                    {patternData.materials.map((material, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-white rounded-lg shadow-sm">
                        <span className="text-green-600 mt-1">•</span>
                        <span className="text-gray-700 flex-1">{material.replace(/^•\s*/, '')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Pattern Text */}
              <div className="rounded-xl p-6 border-2 border-dashed" style={{backgroundColor: '#f1cbff', borderColor: '#c9c9ff'}}>
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  Pattern Instructions
                </h3>
                <div className="bg-white rounded-lg p-4 shadow-inner max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono leading-relaxed">
                    {patternData.pattern}
                  </pre>
                </div>
              </div>
              
              <div className="mt-6 text-center">
                <div className="inline-flex items-center space-x-4 px-4 py-2 rounded-full text-sm text-gray-600" style={{backgroundColor: '#e1f7d5'}}>
                  <span>Generated in {patternData.generation_time}</span>
                  <span>•</span>
                  <span>Style: {patternData.style_used}</span>
                  <span>•</span>
                  <span>{patternData.model_used}</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {patternData && !patternData.success && (
          <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 animate-fadeIn">
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-3">❌</span>
              <h3 className="text-xl font-bold text-red-800">Oops! Something went wrong</h3>
            </div>
            <p className="text-red-700 mb-4">{patternData.error}</p>
            <button 
              onClick={() => setPatternData(null)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
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
}

export default FileUpload;