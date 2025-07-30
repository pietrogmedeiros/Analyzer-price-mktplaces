import { useRef } from 'react';

export default function UploadPage({ onFileSelect, selectedFile, onSubmit, isLoading }) {
  const fileInputRef = useRef(null);

  return (
    <div className="container">
      <header>
        <h1>WebPrice Analyzer</h1>
        <p>Faça o upload de um arquivo CSV e obtenha insights valiosos para otimizar seus preços.</p>
      </header>
      
      <section className="upload-section">
        <form onSubmit={onSubmit}>
          <div className="upload-box" onClick={() => fileInputRef.current.click()}>
            <p>{selectedFile ? `Arquivo: ${selectedFile.name}` : 'Clique para selecionar um arquivo'}</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={(e) => onFileSelect(e.target.files[0])}
            />
          </div>
          <button type="submit" disabled={isLoading || !selectedFile} className="upload-button">
            {isLoading ? 'Analisando...' : 'Analisar Arquivo'}
          </button>
        </form>
      </section>
    </div>
  );
}