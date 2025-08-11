from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'running', 'message': 'DEBUG Server - Investigando CSV'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("🔍 MODO DEBUG - INVESTIGANDO CSV...")
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        print(f"📁 Arquivo recebido: {file.filename}")
        
        # Lê arquivo
        raw_bytes = file.read()
        try:
            text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = raw_bytes.decode('latin-1', errors='ignore')
        
        print(f"📊 Tamanho: {len(text)} caracteres")
        
        # Mostra primeiras 10 linhas para debug
        linhas = text.split('\n')
        print(f"🔍 PRIMEIRAS 10 LINHAS DO CSV:")
        for i, linha in enumerate(linhas[:10]):
            print(f"  [{i}]: {linha[:200]}...")
        
        # Detecta header
        header_line = 0
        for i, linha in enumerate(linhas[:10]):
            if 'PRODUTO' in linha.upper():
                header_line = i
                print(f"✅ Header encontrado na linha {i}")
                break
        
        # Carrega CSV
        df = pd.read_csv(io.StringIO(text), sep=';', skiprows=header_line, decimal=',')
        print(f"📈 DataFrame carregado: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Mostra colunas originais
        print(f"🔍 COLUNAS ORIGINAIS: {list(df.columns)}")
        
        # Limpa colunas
        df.columns = [str(c).replace('\ufeff', '').strip().upper() for c in df.columns]
        print(f"🧹 COLUNAS LIMPAS: {list(df.columns)}")
        
        # Mapeia colunas
        mapping = {
            'PRODUTO': 'Produto',
            'STATUS': 'Status',
            'PRECO': 'Preço',
            'PREÇO': 'Preço', 
            'MAIS BARATO': 'Preço_Concorrente',
            'LOJISTA': 'Lojista'
        }
        
        colunas_mapeadas = []
        for old, new in mapping.items():
            if old in df.columns:
                df.rename(columns={old: new}, inplace=True)
                colunas_mapeadas.append(f"{old} -> {new}")
        
        print(f"🔄 MAPEAMENTOS APLICADOS: {colunas_mapeadas}")
        print(f"🔍 COLUNAS FINAIS: {list(df.columns)}")
        
        # Verifica colunas essenciais
        colunas_essenciais = ['Produto', 'Preço', 'Preço_Concorrente', 'Status']
        colunas_existentes = [col for col in colunas_essenciais if col in df.columns]
        colunas_faltando = [col for col in colunas_essenciais if col not in df.columns]
        
        print(f"✅ COLUNAS ENCONTRADAS: {colunas_existentes}")
        print(f"❌ COLUNAS FALTANDO: {colunas_faltando}")
        
        # Analisa primeiras 5 linhas de dados
        print(f"🔍 PRIMEIRAS 5 LINHAS DE DADOS:")
        for i in range(min(5, len(df))):
            linha = df.iloc[i]
            print(f"  Linha {i}:")
            for col in ['Produto', 'Status', 'Preço', 'Preço_Concorrente', 'Lojista']:
                if col in df.columns:
                    valor = linha.get(col, 'N/A')
                    print(f"    {col}: {valor} (tipo: {type(valor)})")
        
        # Tenta converter colunas numéricas e mostra resultado
        for col in ['Preço', 'Preço_Concorrente']:
            if col in df.columns:
                print(f"🔢 CONVERTENDO {col}:")
                valores_originais = df[col].head(3).tolist()
                print(f"  Valores originais: {valores_originais}")
                
                # Converte
                df[col] = df[col].astype(str).str.replace(',', '.').str.replace(r'[^\d.]', '', regex=True)
                valores_limpos = df[col].head(3).tolist()
                print(f"  Após limpeza: {valores_limpos}")
                
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                valores_finais = df[col].head(3).tolist()
                print(f"  Valores finais: {valores_finais}")
                
                # Estatísticas
                print(f"  Min: {df[col].min()}, Max: {df[col].max()}, Zeros: {(df[col] == 0).sum()}")
        
        # Analisa Status
        if 'Status' in df.columns:
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
            status_counts = df['Status'].value_counts()
            print(f"📊 STATUS ENCONTRADOS: {dict(status_counts.head(10))}")
        else:
            print("❌ COLUNA STATUS NÃO ENCONTRADA")
        
        # Tenta criar sugestões com debug detalhado
        suggestions = []
        print(f"🎯 TENTANDO CRIAR SUGESTÕES...")
        
        # Pega produtos GANHANDO ou amostra
        if 'Status' in df.columns and 'GANHANDO' in df['Status'].values:
            sample_df = df[df['Status'] == 'GANHANDO'].head(5)
            print(f"  ✅ Encontrou {len(sample_df)} produtos GANHANDO")
        else:
            sample_df = df.head(5)
            print(f"  📝 Usando amostra de {len(sample_df)} produtos")
        
        # Processa cada produto com debug
        for i, row in sample_df.iterrows():
            print(f"  🔍 Processando linha {i}:")
            
            produto = str(row.get('Produto', f'Produto_{i}'))
            print(f"    Produto: {produto[:50]}")
            
            preco_atual_raw = row.get('Preço', 0)
            print(f"    Preço atual raw: {preco_atual_raw} (tipo: {type(preco_atual_raw)})")
            
            try:
                preco_atual = float(preco_atual_raw) if preco_atual_raw != 0 else 0
                print(f"    Preço atual convertido: {preco_atual}")
            except:
                preco_atual = 0
                print(f"    ❌ Erro na conversão do preço atual")
            
            preco_concorrente_raw = row.get('Preço_Concorrente', 0)
            print(f"    Preço concorrente raw: {preco_concorrente_raw} (tipo: {type(preco_concorrente_raw)})")
            
            try:
                preco_concorrente = float(preco_concorrente_raw) if preco_concorrente_raw != 0 else 0
                print(f"    Preço concorrente convertido: {preco_concorrente}")
            except:
                preco_concorrente = 0
                print(f"    ❌ Erro na conversão do preço concorrente")
            
            # Verifica se pode criar sugestão
            if preco_atual > 0:
                print(f"    ✅ Preço atual válido, criando sugestão...")
                
                if preco_concorrente <= 0:
                    preco_concorrente = preco_atual * 1.2
                    print(f"    🔄 Estimando preço concorrente: {preco_concorrente}")
                
                preco_sugerido = round(preco_concorrente * 0.95, 2)
                valor_ajuste = round(preco_sugerido - preco_atual, 2) if preco_sugerido > preco_atual else 0
                
                suggestion = {
                    'Produto': produto[:100],
                    'Status': str(row.get('Status', 'ANALISAR')),
                    'Preço_Atual': float(preco_atual),
                    'Preço_Sugerido': float(preco_sugerido),
                    'Valor_Ajuste': float(valor_ajuste),
                    'Margem_Extra_RS': float(valor_ajuste),
                    'Percentual_Ajuste': float(valor_ajuste / preco_atual * 100) if preco_atual > 0 else 0.0,
                    'Lojista': str(row.get('Lojista', 'N/A'))[:50],
                    'Preço_Concorrente': float(preco_concorrente),
                    'Estrategia': 'Debug - Teste funcional'
                }
                
                suggestions.append(suggestion)
                print(f"    ✅ Sugestão criada: Ajuste de R$ {valor_ajuste}")
            else:
                print(f"    ❌ Preço atual inválido ({preco_atual}), pulando...")
        
        print(f"🎯 TOTAL DE SUGESTÕES CRIADAS: {len(suggestions)}")
        
        # Resultado
        result = {
            'data': suggestions,
            'ml_insights': {
                'total_produtos_analisados': len(suggestions),
                'produtos_com_oportunidade_margem': len([s for s in suggestions if s['Valor_Ajuste'] > 0]),
                'ganho_potencial_total_rs': sum(s['Margem_Extra_RS'] for s in suggestions),
                'ganho_medio_por_produto': sum(s['Margem_Extra_RS'] for s in suggestions) / max(len(suggestions), 1),
                'strategy': 'DEBUG - Investigação detalhada do CSV'
            },
            'status_counts': dict(df['Status'].value_counts()) if 'Status' in df.columns else {'TOTAL': len(df)}
        }
        
        print(f"🎉 RESULTADO FINAL: {len(result['data'])} produtos, R$ {result['ml_insights']['ganho_potencial_total_rs']:.2f} ganho")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro: {str(e)}'}), 500

if __name__ == '__main__':
    print("🔍 SERVIDOR DEBUG - PORTA 8000")
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
