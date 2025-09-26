# Arquivo responsável por analisar o risco acadêmico dos alunos

def calcular_media_aluno(notas_dict):
    """
    Calcula a média das notas de um aluno
    Recebe um dicionário com as notas e retorna a média
    """
    notas_validas = []
    
    # Para cada disciplina, verificar se a nota é válida
    for disciplina, nota in notas_dict.items():
        # Se a nota é um número e maior que 0
        if isinstance(nota, (int, float)) and nota > 0:
            notas_validas.append(nota)
    
    # Se tem pelo menos uma nota válida
    if len(notas_validas) > 0:
        soma_notas = 0
        contador = 0
        
        # Somar todas as notas válidas
        while contador < len(notas_validas):
            soma_notas = soma_notas + notas_validas[contador]
            contador = contador + 1
        
        media = soma_notas / len(notas_validas)
        return round(media, 2)
    else:
        return 0

def calcular_total_faltas(faltas_dict):
    """
    Calcula o total de faltas de um aluno
    """
    total_faltas = 0
    
    for disciplina, faltas in faltas_dict.items():
        if isinstance(faltas, (int, float)) and faltas > 0:
            total_faltas = total_faltas + faltas
    
    return total_faltas

def classificar_risco_aluno(media, total_faltas):
    """
    Classifica o risco acadêmico do aluno baseado na média e faltas
    """
    # Primeiro verificar a média
    if media < 5.0:
        return "ALTO RISCO"
    elif media < 6.0:
        return "RISCO MODERADO" 
    elif media < 7.0:
        return "ATENÇÃO"
    
    # Se a média está boa, verificar as faltas
    if total_faltas > 15:
        return "RISCO MODERADO"
    elif total_faltas > 10:
        return "ATENÇÃO"
    
    return "SITUAÇÃO OK"

def analisar_aluno(dados_aluno):
    """
    Analisa um aluno completo e retorna suas informações com classificação
    """
    nome = dados_aluno['nome']
    notas = dados_aluno['notas']
    faltas = dados_aluno['faltas']
    
    # Calcular métricas
    media = calcular_media_aluno(notas)
    total_faltas = calcular_total_faltas(faltas)
    classificacao = classificar_risco_aluno(media, total_faltas)
    
    # Retornar análise completa
    analise = {
        'nome': nome,
        'media': media,
        'total_faltas': total_faltas,
        'classificacao': classificacao,
        'notas_detalhadas': notas,
        'faltas_detalhadas': faltas
    }
    
    return analise

def analisar_turma_completa(alunos_turma):
    """
    Analisa uma turma inteira e retorna estatísticas
    """
    analises_alunos = []
    
    # Analisar cada aluno
    contador = 0
    while contador < len(alunos_turma):
        aluno = alunos_turma[contador]
        analise = analisar_aluno(aluno)
        analises_alunos.append(analise)
        contador = contador + 1
    
    # Calcular estatísticas da turma
    estatisticas = calcular_estatisticas_turma(analises_alunos)
    
    return {
        'alunos': analises_alunos,
        'estatisticas': estatisticas
    }

def calcular_estatisticas_turma(analises_alunos):
    """
    Calcula estatísticas gerais da turma
    """
    total_alunos = len(analises_alunos)
    
    # Contadores por classificação
    alto_risco = 0
    risco_moderado = 0  
    atencao = 0
    situacao_ok = 0
    
    # Somas para médias
    soma_medias = 0
    soma_faltas = 0
    
    contador = 0
    while contador < total_alunos:
        aluno = analises_alunos[contador]
        
        # Contar classificações
        if aluno['classificacao'] == "ALTO RISCO":
            alto_risco = alto_risco + 1
        elif aluno['classificacao'] == "RISCO MODERADO":
            risco_moderado = risco_moderado + 1
        elif aluno['classificacao'] == "ATENÇÃO":
            atencao = atencao + 1  
        elif aluno['classificacao'] == "SITUAÇÃO OK":
            situacao_ok = situacao_ok + 1
        
        # Somar para médias
        soma_medias = soma_medias + aluno['media']
        soma_faltas = soma_faltas + aluno['total_faltas']
        
        contador = contador + 1
    
    # Calcular médias
    media_turma = round(soma_medias / total_alunos, 2) if total_alunos > 0 else 0
    media_faltas = round(soma_faltas / total_alunos, 2) if total_alunos > 0 else 0
    
    estatisticas = {
        'total_alunos': total_alunos,
        'alto_risco': alto_risco,
        'risco_moderado': risco_moderado,
        'atencao': atencao, 
        'situacao_ok': situacao_ok,
        'media_turma': media_turma,
        'media_faltas': media_faltas,
        'percentual_risco': round((alto_risco + risco_moderado) / total_alunos * 100, 1) if total_alunos > 0 else 0
    }
    
    return estatisticas

def obter_alunos_por_classificacao(analises_alunos, classificacao_desejada):
    """
    Filtra alunos por uma classificação específica
    """
    alunos_filtrados = []
    
    contador = 0
    while contador < len(analises_alunos):
        aluno = analises_alunos[contador]
        
        if aluno['classificacao'] == classificacao_desejada:
            alunos_filtrados.append(aluno)
        
        contador = contador + 1
    
    return alunos_filtrados