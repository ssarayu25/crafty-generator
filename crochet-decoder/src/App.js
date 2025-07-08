import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import FileUpload from './FileUpload';
import PatternGenerator from './components/PatternGenerator';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<FileUpload />} />
        <Route path="/generate" element={<PatternGenerator />} />
      </Routes>
    </Router>
  );
}

export default App;
