// src/components/DashboardPage.jsx

// Novo componente para o card de confiança
const ConfidenceCard = ({ ml_insights }) => {
  // Garante que ml_insights seja um objeto para evitar erros
  const insights = ml_insights || {};
  
  let confidence = 'Baixa';
  let className = 'confidence-low';
  let message = insights.message || "Não foi possível treinar o modelo.";

  if (insights.status === "Modelo treinado com sucesso!") {
    const importances = Object.values(insights.importancia_das_features || {});
    if (importances.length > 0 && Math.max(...importances) > 0.20) {
      confidence = 'Alta';
      className = 'confidence-high';
    } else {
      confidence = 'Média';
    }
    message = "O modelo identificou padrões nos dados.";
  }

  return (
    <div className="card">
      <h3>Confiança do Modelo ML</h3>
      <p className={className}>{confidence}</p>
      <span className="confidence-message">{message}</span>
    </div>
  );
};

const formatNumber = (value, key = '') => {
  if (typeof value !== 'number') {
    return value;
  }
  const keyLower = key.toLowerCase();
  if (keyLower.includes('percentual')) {
    return `${value.toFixed(2)}%`.replace('.', ',');
  }
  // --- CORREÇÃO PARA 'SUGESTAO PRECO' ---
  if (keyLower.includes('preço') || keyLower.includes('valor') || keyLower.includes('preco')) {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  return value;
};

export default function DashboardPage({ analysisResult, onReset }) {
  // --- CORREÇÃO NA DESESTRUTURAÇÃO ---
  // Adicionamos valores padrão para evitar erros se as chaves não existirem
  const { summary = {}, data = [], ml_insights = {} } = analysisResult || {};

  return (
    <div className="container">
      <header className="dashboard-header">
        <h1>Dashboard de Análise</h1>
        <button onClick={onReset} className="reset-button">Analisar Novo Arquivo</button>
      </header>

      <section className="summary-cards">
        <div className="card">
          <h3>Produtos para Ajuste</h3>
          <p>{summary.total_products || 0}</p>
        </div>
        <div className="card">
          <h3>Preço Médio (Amostra)</h3>
          <p>{formatNumber(summary.average_price, 'preço')}</p>
        </div>
        
        <ConfidenceCard ml_insights={ml_insights} />

      </section>

      <section className="grid-container">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                {data.length > 0 && Object.keys(data[0]).map(key => <th key={key}>{key.replace(/_/g, ' ')}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index}>
                  {Object.entries(row).map(([key, value]) => (
                    <td key={key}>
                      {formatNumber(value, key)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
            <h3>Insights do ML</h3>
            {ml_insights && ml_insights.importancia_das_features ? (
              <ul className="insights-list">
                {Object.entries(ml_insights.importancia_das_features)
                  .sort(([, a], [, b]) => b - a)
                  .map(([feature, importance]) => (
                  <li key={feature}>
                    <span>{feature.replace(/_/g, ' ')}</span>
                    <span>{(importance * 100).toFixed(2)}%</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-400">{ml_insights.message || "Não foi possível gerar insights."}</p>
            )}
        </div>
      </section>
    </div>
  );
}