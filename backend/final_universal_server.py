from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import logging
import numpy as np
from io import StringIO
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def clean_price_value(value):
    """Converte valor monetário brasileiro para float"""
    if pd.isna(value):
        return 0.0
    
    # Se já for número
    if isinstance(value, (int, float)):
        return float(value)
    
    # Se for string, limpar
    if isinstance(value, str):
        # Remove espaços e caracteres especiais
        clean_value = re.sub(r'[^\d,.-]', '', str(value).strip())
        
        # Se string vazia, retorna 0
        if not clean_value:
            return 0.0
            
        # Substituir vírgula por ponto se for formato brasileiro
        if ',' in clean_value and '.' not in clean_value:
            clean_value = clean_value.replace(',', '.')
        elif ',' in clean_value and '.' in clean_value:
            # Formato brasileiro: 1.234,56
            clean_value = clean_value.replace('.', '').replace(',', '.')
        
        try:
            return float(clean_value)
        except ValueError:
            logger.warning(f"Não foi possível converter valor: {value}")
            return 0.0
    
    return 0.0

def detect_csv_structure(file_content):
    """Detecta a estrutura do CSV e os separadores"""
    lines = file_content.strip().split('\n')
    
    # Tenta diferentes separadores
    separators = [';', ',', '\t']
    best_separator = ';'  # padrão
    max_columns = 0
    
    for sep in separators:
        first_line_cols = len(lines[0].split(sep)) if lines else 0
        if first_line_cols > max_columns:
            max_columns = first_line_cols
            best_separator = sep
    
    logger.info(f"🔍 Separador detectado: '{best_separator}'")
    logger.info(f"🔍 Número de colunas: {max_columns}")
    
    # Analisa as primeiras linhas
    for i, line in enumerate(lines[:3]):
        columns = line.split(best_separator)
        logger.info(f"🔍 Linha {i+1}: {columns}")
    
    return best_separator, lines

def try_read_csv_multiple_ways(file_content, separator):
    """Tenta ler o CSV de diferentes formas"""
    methods_tried = []
    
    # Método 1: Leitura direta
    try:
        df = pd.read_csv(StringIO(file_content), sep=separator, encoding='utf-8')
        methods_tried.append("Leitura direta - SUCESSO")
        logger.info(f"✅ Método 1 - Leitura direta: {df.shape[0]} linhas, {df.shape[1]} colunas")
        logger.info(f"✅ Colunas encontradas: {list(df.columns)}")
        return df, methods_tried
    except Exception as e:
        methods_tried.append(f"Leitura direta - ERRO: {str(e)}")
        logger.warning(f"❌ Método 1 falhou: {e}")
    
    # Método 2: Skiprows=1 (pular primeira linha)
    try:
        df = pd.read_csv(StringIO(file_content), sep=separator, encoding='utf-8', skiprows=1)
        methods_tried.append("Skiprows=1 - SUCESSO")
        logger.info(f"✅ Método 2 - Skiprows=1: {df.shape[0]} linhas, {df.shape[1]} colunas")
        logger.info(f"✅ Colunas encontradas: {list(df.columns)}")
        return df, methods_tried
    except Exception as e:
        methods_tried.append(f"Skiprows=1 - ERRO: {str(e)}")
        logger.warning(f"❌ Método 2 falhou: {e}")
    
    # Método 3: Header=1 (segunda linha como header)
    try:
        df = pd.read_csv(StringIO(file_content), sep=separator, encoding='utf-8', header=1)
        methods_tried.append("Header=1 - SUCESSO")
        logger.info(f"✅ Método 3 - Header=1: {df.shape[0]} linhas, {df.shape[1]} colunas")
        logger.info(f"✅ Colunas encontradas: {list(df.columns)}")
        return df, methods_tried
    except Exception as e:
        methods_tried.append(f"Header=1 - ERRO: {str(e)}")
        logger.warning(f"❌ Método 3 falhou: {e}")
    
    # Método 4: Sem header, definir manualmente
    try:
        df = pd.read_csv(StringIO(file_content), sep=separator, encoding='utf-8', header=None)
        methods_tried.append("Sem header - SUCESSO")
        logger.info(f"✅ Método 4 - Sem header: {df.shape[0]} linhas, {df.shape[1]} colunas")
        logger.info(f"✅ Primeiras linhas: {df.head(2).values.tolist()}")
        return df, methods_tried
    except Exception as e:
        methods_tried.append(f"Sem header - ERRO: {str(e)}")
        logger.warning(f"❌ Método 4 falhou: {e}")
    
    return None, methods_tried

def map_columns_to_standard(df):
    """Mapeia as colunas encontradas para os nomes padrão"""
    column_mapping = {}
    columns = [str(col).upper().strip() for col in df.columns]
    
    logger.info(f"🔍 Mapeando colunas: {columns}")
    
    # Mapeamento flexível de colunas
    mapping_rules = {
        'produto': ['PRODUTO', 'PRODUTOS DISPONÍVEIS', 'PRODUTO A', 'PRODUTOS', 'ITEM'],
        'lojista': ['LOJISTA', 'LOJA', 'SELLER', 'VENDEDOR', 'STORE'],
        'preco': ['PREÇO', 'PRECO', 'PRICE', 'VALOR', 'CUSTO'],
        'status': ['STATUS', 'SITUACAO', 'SITUAÇÃO', 'STATE'],
        'ranking': ['RANKING', 'RANK', 'POSICAO', 'POSIÇÃO'],
        'mais_barato': ['MAIS BARATO', 'MENOR PREÇO', 'MENOR PRECO', 'CHEAPEST'],
        'marca': ['MARCA', 'BRAND'],
        'diferenca': ['DIFERENÇA', 'DIFERENCA', 'DIFF', 'DIFFERENCE'],
        'percentual': ['PERCENTUAL', 'PERCENT', '%', 'PCT']
    }
    
    # Para cada coluna padrão, encontra correspondência
    for standard_name, possible_names in mapping_rules.items():
        for col in columns:
            for possible in possible_names:
                if possible in col or col in possible:
                    original_col = df.columns[columns.index(col)]
                    column_mapping[standard_name] = original_col
                    logger.info(f"✅ Mapeado '{original_col}' -> '{standard_name}'")
                    break
            if standard_name in column_mapping:
                break
    
    return column_mapping

def analyze_competitive_pricing(df, column_mapping):
    """Análise de precificação competitiva"""
    logger.info("🚀 Iniciando análise de precificação competitiva...")
    
    results = {
        'total_produtos': len(df),
        'produtos_ganhando': 0,
        'produtos_perdendo': 0,
        'margem_media_ganho': 0,
        'margem_media_perda': 0,
        'detalhes_produtos': [],
        'resumo_por_lojista': {},
        'alertas': []
    }
    
    # Colunas essenciais
    produto_col = column_mapping.get('produto')
    lojista_col = column_mapping.get('lojista')
    preco_col = column_mapping.get('preco')
    status_col = column_mapping.get('status')
    mais_barato_col = column_mapping.get('mais_barato')
    
    logger.info(f"🔍 Usando colunas: produto={produto_col}, lojista={lojista_col}, preco={preco_col}")
    
    if not produto_col or not lojista_col or not preco_col:
        logger.error("❌ Colunas essenciais não encontradas")
        return results
    
    # Processar cada linha
    for idx, row in df.iterrows():
        produto = str(row[produto_col]) if produto_col else f"Produto {idx}"
        lojista = str(row[lojista_col]) if lojista_col else f"Loja {idx}"
        preco = clean_price_value(row[preco_col]) if preco_col else 0
        status = str(row[status_col]).upper() if status_col else "DESCONHECIDO"
        mais_barato = clean_price_value(row[mais_barato_col]) if mais_barato_col else 0
        
        # Calcular margem
        margem = 0
        if preco > 0 and mais_barato > 0:
            margem = ((preco - mais_barato) / mais_barato) * 100
        
        # Análise de status
        if 'GANHAND' in status:
            results['produtos_ganhando'] += 1
            results['margem_media_ganho'] += margem
        elif 'PERDEND' in status:
            results['produtos_perdendo'] += 1  
            results['margem_media_perda'] += margem
        
        # Resumo por lojista
        if lojista not in results['resumo_por_lojista']:
            results['resumo_por_lojista'][lojista] = {
                'produtos': 0,
                'ganhando': 0,
                'perdendo': 0,
                'receita_total': 0
            }
        
        results['resumo_por_lojista'][lojista]['produtos'] += 1
        results['resumo_por_lojista'][lojista]['receita_total'] += preco
        
        if 'GANHAND' in status:
            results['resumo_por_lojista'][lojista]['ganhando'] += 1
        elif 'PERDEND' in status:
            results['resumo_por_lojista'][lojista]['perdendo'] += 1
        
        # Detalhes do produto
        results['detalhes_produtos'].append({
            'produto': produto,
            'lojista': lojista,
            'preco': preco,
            'mais_barato': mais_barato,
            'status': status,
            'margem': round(margem, 2)
        })
    
    # Calcular médias
    if results['produtos_ganhando'] > 0:
        results['margem_media_ganho'] = round(results['margem_media_ganho'] / results['produtos_ganhando'], 2)
    
    if results['produtos_perdendo'] > 0:
        results['margem_media_perda'] = round(results['margem_media_perda'] / results['produtos_perdendo'], 2)
    
    # Alertas estratégicos
    if results['produtos_perdendo'] > results['produtos_ganhando']:
        results['alertas'].append("⚠️ Mais produtos perdendo do que ganhando - revisar precificação")
    
    if results['margem_media_perda'] < -20:
        results['alertas'].append(f"🚨 Margem de perda muito alta: {results['margem_media_perda']}%")
    
    logger.info(f"✅ Análise concluída: {results['produtos_ganhando']} ganhando, {results['produtos_perdendo']} perdendo")
    
    return results

@app.route('/analyze', methods=['POST'])
def analyze_file():
    logger.info("📊 NOVA ANÁLISE INICIADA")
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Ler conteúdo do arquivo
        file_content = file.read().decode('utf-8')
        logger.info(f"📁 Arquivo recebido: {file.filename}")
        
        # Detectar estrutura do CSV
        separator, lines = detect_csv_structure(file_content)
        
        # Tentar diferentes métodos de leitura
        df, methods_tried = try_read_csv_multiple_ways(file_content, separator)
        
        if df is None:
            return jsonify({
                'error': 'Não foi possível ler o arquivo CSV',
                'methods_tried': methods_tried
            }), 400
        
        # Mapear colunas
        column_mapping = map_columns_to_standard(df)
        
        if not column_mapping:
            return jsonify({
                'error': 'Não foi possível mapear as colunas',
                'available_columns': list(df.columns),
                'methods_tried': methods_tried
            }), 400
        
        # Analisar dados
        results = analyze_competitive_pricing(df, column_mapping)
        
        return jsonify({
            'success': True,
            'arquivo': file.filename,
            'linhas_processadas': len(df),
            'colunas_mapeadas': column_mapping,
            'methods_tried': methods_tried,
            'analise': results
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {str(e)}")
        return jsonify({'error': f'Erro na análise: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Servidor de Análise Competitiva funcionando!'})

if __name__ == '__main__':
    print("🚀 SERVIDOR UNIVERSAL DE ANÁLISE COMPETITIVA")
    print("🎯 Detecta automaticamente estrutura do CSV")
    print("📊 Mapeia colunas flexivelmente")
    print("🌐 Porta 5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
