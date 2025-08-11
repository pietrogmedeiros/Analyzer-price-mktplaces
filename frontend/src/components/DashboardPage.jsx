// src/components/DashboardPage.jsx
import React from 'react';

const formatNumber = (value, key = '') => {
  if (value === null || value === undefined) return '';
  if (typeof value !== 'number') {
    return value;
  }
  const k = key.toLowerCase();
  if (k.includes('desconto') || k.includes('percentual')) {
    return `${value.toFixed(2).replace('.', ',')}%`;
  }
  if (k.includes('preço') || k.includes('preco') || k.includes('valor')) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL'}).format(value);
  }
  return new Intl.NumberFormat('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2}).format(value);
};

const InsightsCard = ({ ml_insights }) => {
  const insights = ml_insights || {};
  return (
    <div className="card insights-card">
      <h3>Análise Competitiva</h3>
      <div className="insights-content">
        <div className="insight-item">
          <span className="insight-label">Produtos Analisados:</span>
          <span className="insight-value">{insights.total_produtos_analisados || 0}</span>
        </div>
        <div className="insight-item">
          <span className="insight-label">Com Oportunidade:</span>
          <span className="insight-value highlight">{insights.produtos_com_oportunidade_margem || 0}</span>
        </div>
        <div className="insight-item">
          <span className="insight-label">Ganho Potencial:</span>
          <span className="insight-value gain">{formatNumber(insights.ganho_potencial_total_rs, 'valor')}</span>
        </div>
        <div className="strategy-info">
          <small>Estratégia: {insights.strategy || 'Proteção de margem'}</small>
        </div>
      </div>
    </div>
  );
};

export default function DashboardPage({ analysisResult, onReset }) {
  // CORREÇÃO: O backend retorna os dados em 'analise', não em 'data' e 'ml_insights'
  const { analise = {} } = analysisResult || {};
  const { 
    produtos_ganhando = 0,
    total_produtos = 0,
    margem_media_ganho = 0,
    detalhes_produtos = []
  } = analise;

  // Simular ml_insights baseado nos dados de analise
  const ml_insights = {
    total_produtos_analisados: total_produtos,
    produtos_com_oportunidade_margem: produtos_ganhando,
    ganho_potencial_total_rs: margem_media_ganho * produtos_ganhando || 0,
    strategy: 'Proteção de margem mantendo competitividade'
  };

  // Usar detalhes_produtos como data
  const data = detalhes_produtos;
  const filteredData = data.map(row => {
    const { Prioridade_Valor, ...rest } = row; // remove se vier
    return rest;
  });

  return (
    <div className="container">
      <header className="dashboard-header">
        <h1>Análise de Otimização de Preços</h1>
        <div className="page-navigation" style={{justifyContent:'flex-end'}}>
          <button onClick={onReset} className="reset-button">Analisar Novo Arquivo</button>
        </div>
      </header>

      <section className="summary-cards">
        <div className="card">
          <h3>Produtos "Ganhando"</h3>
          <p className="card-number">{produtos_ganhando}</p>
          <small>Liderando no ranking</small>
        </div>
        <div className="card">
          <h3>Oportunidades de Margem</h3>
          <p className="card-number highlight">{filteredData.filter(p => (p.margem_percentual || 0) > 0).length}</p>
          <small>Com potencial de ajuste</small>
        </div>
        <div className="card">
          <h3>Análise Competitiva</h3>
          <p className="card-number">Produtos Analisados:{total_produtos}</p>
          <p className="card-number">Com Oportunidade:{produtos_ganhando}</p>
          <small>Ganho Potencial: Estratégia: Proteção de margem</small>
        </div>
        <InsightsCard ml_insights={ml_insights} />
      </section>

      <section className="table-section">
        {filteredData.length === 0 && (
          <div style={{color:'#ccc', padding:'1rem 0'}}>{ml_insights?.message || 'Nenhum item para ajuste encontrado.'}</div>
        )}
        {filteredData.length > 0 && (
          <div className="table-container full-width">
            <table>
              <thead>
                <tr>
                  {Object.keys(filteredData[0]).map(key => (
                    <th key={key}>{key.replace(/_/g,' ').replace('Tipo Ajuste','Tipo de Ajuste')}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredData.map((row, idx) => (
                  <tr key={idx}>
                    {Object.entries(row).map(([k,v]) => (
                      <td key={k}>{formatNumber(v,k)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
