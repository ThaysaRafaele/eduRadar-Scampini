# Arquivo responsável por ler os dados do Excel de forma simples

import pandas as pd

def carregar_dados_excel(caminho_arquivo):
    """
    Carrega todas as turmas de IA do arquivo Excel
    Retorna um dicionário com os dados de cada turma
    """
    # Lista das turmas que vamos analisar
    turmas_ia = [
        "1º ano G - IA",      # 1° G vespertino 
        "2º ano G - IA",      # 2º G vespertino 
        "1º ano E - IA",      # 1° E matutino 
        "2º ano D - IA",      # 2º D matutino 
        "2º ano E - IA",      # 2° E matutino 
        "3º ano E -IA"        # 3° E matutino 
    ]
    
    # Dicionário para guardar os dados de cada turma
    dados_turmas = {}
    
    # Para cada turma, carregar os dados
    contador_turma = 0
    while contador_turma < len(turmas_ia):
        nome_turma = turmas_ia[contador_turma]
        
        try:
            # Ler a planilha da turma específica
            df = pd.read_excel(caminho_arquivo, sheet_name=nome_turma)
            dados_turmas[nome_turma] = df
            print(f"Turma {nome_turma} carregada com sucesso!")
            
        except Exception as erro:
            print(f"Erro ao carregar {nome_turma}: {erro}")
        
        contador_turma = contador_turma + 1
    
    return dados_turmas

def processar_alunos_turma(df_turma):
    """
    Processa os dados de uma turma e retorna lista de alunos
    com suas notas organizadas
    """
    alunos = []
    
    # Começar da linha 3 (índice 2) pois as 3 primeiras são cabeçalhos
    linha_atual = 3
    
    while linha_atual < len(df_turma):
        # Pegar os dados da linha atual
        linha = df_turma.iloc[linha_atual]
        
        # Verificar se tem nome de aluno nesta linha
        nome_aluno = linha.iloc[0]
        
        if pd.notna(nome_aluno) and nome_aluno != "":
            # Extrair as notas (colunas ímpares: 1, 3, 5, 7)
            nota_ucp1 = linha.iloc[1] if pd.notna(linha.iloc[1]) else 0
            nota_ucp2 = linha.iloc[3] if pd.notna(linha.iloc[3]) else 0  
            nota_ucp3 = linha.iloc[5] if pd.notna(linha.iloc[5]) else 0
            nota_projeto = linha.iloc[7] if pd.notna(linha.iloc[7]) else 0
            
            # Extrair as faltas (colunas pares: 2, 4, 6, 8)
            faltas_ucp1 = linha.iloc[2] if pd.notna(linha.iloc[2]) else 0
            faltas_ucp2 = linha.iloc[4] if pd.notna(linha.iloc[4]) else 0
            faltas_ucp3 = linha.iloc[6] if pd.notna(linha.iloc[6]) else 0  
            faltas_projeto = linha.iloc[8] if len(linha) > 8 and pd.notna(linha.iloc[8]) else 0
            
            # Criar dicionário com dados do aluno
            dados_aluno = {
                'nome': nome_aluno,
                'notas': {
                    'UCP 1': nota_ucp1,
                    'UCP 2': nota_ucp2, 
                    'UCP 3': nota_ucp3,
                    'Projeto': nota_projeto
                },
                'faltas': {
                    'UCP 1': faltas_ucp1,
                    'UCP 2': faltas_ucp2,
                    'UCP 3': faltas_ucp3, 
                    'Projeto': faltas_projeto
                }
            }
            
            alunos.append(dados_aluno)
        
        linha_atual = linha_atual + 1
    
    return alunos

def obter_todas_turmas_processadas(caminho_arquivo):
    """
    Função principal que retorna todos os dados processados
    """
    print("Iniciando carregamento dos dados...")
    
    # Carregar dados do Excel
    dados_brutos = carregar_dados_excel(caminho_arquivo)
    
    # Processar cada turma  
    dados_processados = {}
    
    for nome_turma, df_turma in dados_brutos.items():
        alunos = processar_alunos_turma(df_turma)
        dados_processados[nome_turma] = alunos
        print(f"📊 {nome_turma}: {len(alunos)} alunos processados")
    
    print("Processamento concluído!")
    return dados_processados