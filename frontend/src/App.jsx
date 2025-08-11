import { useState } from 'react';
import axios from 'axios';
import UploadPage from './components/UploadPage';
import DashboardPage from './components/DashboardPage';

// --- ALTERAÇÃO AQUI ---
// Lê a URL da API da variável de ambiente VITE_API_URL.
// Se não estiver definida, usa um valor padrão para garantir que funcione.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Por favor, selecione um arquivo CSV.');
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    setIsLoading(true);
    setError('');
    try {
      // --- ALTERAÇÃO AQUI ---
      // Usa a constante API_URL para construir o endpoint completo.
      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAnalysisResult(response.data);
    } catch (err) {
      setError('Ocorreu um erro ao analisar o arquivo. Verifique se o backend está rodando.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setError('');
  };

  return (
    <div>
      {error && <div style={{ backgroundColor: 'red', color: 'white', textAlign: 'center', padding: '0.5rem' }}>{error}</div>}
      
      {!analysisResult ? (
        <UploadPage 
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      ) : (
        <DashboardPage 
          analysisResult={analysisResult}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

export default App;