from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import logging
from io import StringIO
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def clean_price_value(value):
    """Converte valor monetário brasileiro para float"""
    if pd.isna(value):
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        clean_value = re.sub(r'[^\d,.-]', '', str(value).strip())
        if not clean_value:
            return 0.0
        
        if ',' in clean_value and '.' not in clean_value:
            clean_value = clean_value.replace(',', '.')
        elif ',' in clean_value and '.' in clean_value:
            clean_value = clean_value.replace('.', '').replace(',', '.')
        
        try:
            return float(clean_value)
        except ValueError:
            return 0.0
    
    return 0.0

@app.route('/analyze', methods=['POST'])
def analyze_file():
    logger.info("📊 Nova análise iniciada")
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    try:
        # Ler arquivo
        file_content = file.read().decode('utf-8')
        logger.info(f"📁 Arquivo recebido: {file.filename}")
        
        # Carregar CSV - headers na segunda linha
        df = pd.read_csv(StringIO(file_content), sep=';', header=1)
        logger.info(f"✅ CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
        logger.info(f"✅ Colunas: {list(df.columns)}")
        
        # Mapear colunas para análise - baseado nas suas especificações
        columns = df.columns.tolist()
        column_mapping = {}
        
        # Mapeamento completo baseado nas colunas especificadas:
        # "PRODUTO, MARCA, N° DE LOJAS, MAIS BARATO, STATUS, CÓDIGO CLUSTER, CÓDIGO INTERNO, RANKING, LOJISTA, SELLERS, PREÇO, DIFERENÇA, PERCENTUAL"
        for col in columns:
            col_upper = str(col).upper().strip()
            if 'PRODUTO' in col_upper and 'produto' not in column_mapping:
                column_mapping['produto'] = col
            elif 'MARCA' in col_upper:
                column_mapping['marca'] = col
            elif 'LOJA' in col_upper and 'N°' in col_upper:
                column_mapping['num_lojas'] = col
            elif 'BARATO' in col_upper:
                column_mapping['mais_barato'] = col
            elif 'STATUS' in col_upper:
                column_mapping['status'] = col
            elif 'CLUSTER' in col_upper:
                column_mapping['codigo_cluster'] = col
            elif 'INTERNO' in col_upper or 'CÓDIGO INTERNO' in col_upper:
                column_mapping['codigo_interno'] = col
            elif 'RANKING' in col_upper:
                column_mapping['ranking'] = col
            elif ('LOJISTA' in col_upper or 'LOJA' in col_upper) and 'N°' not in col_upper:
                column_mapping['lojista'] = col
            elif 'SELLER' in col_upper:
                column_mapping['sellers'] = col
            elif 'PREÇO' in col_upper or 'PRECO' in col_upper:
                column_mapping['preco'] = col
            elif 'DIFERENÇA' in col_upper or 'DIFERENCA' in col_upper:
                column_mapping['diferenca'] = col
            elif 'PERCENTUAL' in col_upper or 'PERCENT' in col_upper:
                column_mapping['percentual'] = col
        
        logger.info(f"🔍 Mapeamento de colunas: {column_mapping}")
        
        # Análise dos dados - foco em produtos GANHANDO
        total_produtos = len(df)
        
        # Filtrar apenas produtos com status GANHANDO
        if 'status' in column_mapping:
            df_ganhando = df[df[column_mapping['status']].astype(str).str.upper() == 'GANHANDO']
            produtos_ganhando = len(df_ganhando)
            produtos_perdendo = len(df[df[column_mapping['status']].astype(str).str.upper() == 'PERDENDO'])
        else:
            df_ganhando = df  # Se não tem status, analisa todos
            produtos_ganhando = 0
            produtos_perdendo = 0
        
        logger.info(f"🎯 Produtos GANHANDO encontrados: {produtos_ganhando}")
        logger.info(f"📊 Produtos PERDENDO encontrados: {produtos_perdendo}")
        
        # Detalhes dos produtos
        detalhes = []
        margem_total_ganho = 0
        margem_total_perda = 0
        count_ganho = 0
        count_perda = 0
        
        # Processar cada produto (focando nos GANHANDO)
        df_to_process = df_ganhando if produtos_ganhando > 0 else df
        
        for idx, row in df_to_process.iterrows():
            produto = str(row[column_mapping['produto']]) if 'produto' in column_mapping else f"Produto {idx}"
            lojista = str(row[column_mapping['lojista']]) if 'lojista' in column_mapping else f"Loja {idx}"
            preco = clean_price_value(row[column_mapping['preco']]) if 'preco' in column_mapping else 0
            status = str(row[column_mapping['status']]).upper() if 'status' in column_mapping else "DESCONHECIDO"
            mais_barato = clean_price_value(row[column_mapping['mais_barato']]) if 'mais_barato' in column_mapping else 0
            ranking = str(row[column_mapping['ranking']]) if 'ranking' in column_mapping else "N/A"
            
            # Usar diferença e percentual se disponíveis
            diferenca_raw = clean_price_value(row[column_mapping['diferenca']]) if 'diferenca' in column_mapping else None
            percentual_raw = clean_price_value(row[column_mapping['percentual']]) if 'percentual' in column_mapping else None
            
            # Calcular margem
            margem = 0
            if diferenca_raw is not None:
                margem = diferenca_raw
            elif percentual_raw is not None:
                margem = percentual_raw
            elif preco > 0 and mais_barato > 0:
                margem = ((preco - mais_barato) / mais_barato) * 100
            
            # Contar por status
            if status == 'GANHANDO':
                margem_total_ganho += margem
                count_ganho += 1
            elif status == 'PERDENDO':
                margem_total_perda += margem
                count_perda += 1
            
            detalhes.append({
                'produto': produto,
                'lojista': lojista,
                'preco': preco,
                'mais_barato': mais_barato,
                'status': status,
                'ranking': ranking,
                'margem_percentual': round(margem, 2),
                'diferenca_valor': diferenca_raw if diferenca_raw is not None else round(preco - mais_barato, 2) if (preco > 0 and mais_barato > 0) else 0
            })
        
        # Calcular médias
        margem_media_ganho = round(margem_total_ganho / count_ganho, 2) if count_ganho > 0 else 0
        margem_media_perda = round(margem_total_perda / count_perda, 2) if count_perda > 0 else 0
        
        # Resumo por lojista
        resumo_lojistas = {}
        for detail in detalhes:
            loj = detail['lojista']
            if loj not in resumo_lojistas:
                resumo_lojistas[loj] = {'produtos': 0, 'ganhando': 0, 'perdendo': 0, 'receita_total': 0}
            
            resumo_lojistas[loj]['produtos'] += 1
            resumo_lojistas[loj]['receita_total'] += detail['preco']
            
            if detail['status'] == 'GANHANDO':
                resumo_lojistas[loj]['ganhando'] += 1
            elif detail['status'] == 'PERDENDO':
                resumo_lojistas[loj]['perdendo'] += 1
        
        # Alertas
        alertas = []
        if produtos_perdendo > produtos_ganhando:
            alertas.append("⚠️ Mais produtos perdendo do que ganhando - revisar precificação")
        if margem_media_perda < -20:
            alertas.append(f"🚨 Margem de perda muito alta: {margem_media_perda}%")
        
        resultado = {
            'success': True,
            'arquivo': file.filename,
            'linhas_processadas': total_produtos,
            'colunas_detectadas': list(df.columns),
            'colunas_mapeadas': column_mapping,
            'analise': {
                'total_produtos': total_produtos,
                'produtos_ganhando': produtos_ganhando,
                'produtos_perdendo': produtos_perdendo,
                'margem_media_ganho': margem_media_ganho,
                'margem_media_perda': margem_media_perda,
                'detalhes_produtos': detalhes,
                'resumo_por_lojista': resumo_lojistas,
                'alertas': alertas
            }
        }
        
        logger.info(f"✅ Análise concluída: {produtos_ganhando} ganhando, {produtos_perdendo} perdendo")
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        return jsonify({'error': f'Erro na análise: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando!'})

if __name__ == '__main__':
    print("🚀 SERVIDOR DE ANÁLISE COMPETITIVA - VERSÃO ESTÁVEL")
    print("🌐 Porta 5001")
    app.run(debug=False, host='0.0.0.0', port=5001)
