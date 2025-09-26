# Arquivo responsável por ler os dados do Excel
import pandas as pd
import os
from datetime import datetime

class LeitorDadosExcel:
    def __init__(self):
        self.formatos_suportados = {
            '2_bimestre': {
                'sufixo': ' - IA',
                'turmas': [
                    "1º ano G - IA", "2º ano G - IA", "1º ano E - IA", 
                    "2º ano D - IA", "2º ano E - IA", "3º ano E -IA"
                ],
                'descricao': '2º Bimestre (com " - IA")'
            },
            '3_bimestre': {
                'sufixo': '',
                'turmas': [
                    "1º ano G", "2º ano G", "1º ano E",
                    "2º ano D", "2º ano E", "3º ano E"
                ],
                'descricao': '3º Bimestre (sem " - IA")'
            },
            '4_bimestre': {
                'sufixo': ' - 4º Bim',
                'turmas': [
                    "1º ano G - 4º Bim", "2º ano G - 4º Bim", "1º ano E - 4º Bim",
                    "2º ano D - 4º Bim", "2º ano E - 4º Bim", "3º ano E - 4º Bim"
                ],
                'descricao': '4º Bimestre (com " - 4º Bim")'
            }
        }
    
    def detectar_bimestre_arquivo(self, caminho_arquivo):
        """
        Detecta automaticamente qual bimestre está no arquivo
        """
        try:
            excel_file = pd.ExcelFile(caminho_arquivo)
            sheet_names = excel_file.sheet_names
            
            for bimestre, config in self.formatos_suportados.items():
                turmas_encontradas = 0
                for turma in config['turmas']:
                    if turma in sheet_names:
                        turmas_encontradas += 1
                
                if turmas_encontradas > 0:
                    return {
                        'bimestre': bimestre,
                        'descricao': config['descricao'],
                        'turmas_encontradas': turmas_encontradas,
                        'total_turmas': len(config['turmas']),
                        'formato': config
                    }
            
            return {
                'bimestre': 'desconhecido',
                'descricao': 'Formato não reconhecido',
                'turmas_encontradas': 0,
                'total_turmas': 0
            }
            
        except Exception as e:
            return {
                'bimestre': 'erro',
                'descricao': f'Erro ao detectar formato: {str(e)}',
                'turmas_encontradas': 0,
                'total_turmas': 0
            }
    
    def carregar_dados_bimestre(self, caminho_arquivo, bimestre_especifico=None):
        """
        Carrega dados de um bimestre específico ou detecta automaticamente
        """
        if bimestre_especifico and bimestre_especifico in self.formatos_suportados:
            formato_usar = self.formatos_suportados[bimestre_especifico]
            info_bimestre = {
                'bimestre': bimestre_especifico,
                'descricao': formato_usar['descricao'],
                'formato': formato_usar
            }
        else:
            info_bimestre = self.detectar_bimestre_arquivo(caminho_arquivo)
            if info_bimestre['bimestre'] in ['desconhecido', 'erro']:
                return None, info_bimestre
        
        dados_turmas = {}
        turmas_carregadas = 0
        
        print(f"Carregando dados do {info_bimestre['descricao']}...")
        
        for turma_nome in info_bimestre['formato']['turmas']:
            try:
                df = pd.read_excel(caminho_arquivo, sheet_name=turma_nome)
                
                # Normalizar nome da turma (remover sufixos para manter consistência)
                nome_base = turma_nome.replace(' - IA', '').replace(' - 4º Bim', '')
                chave_turma = f"{nome_base} - IA"  # Formato padrão interno
                
                dados_turmas[chave_turma] = {
                    'dataframe': df,
                    'nome_planilha': turma_nome,
                    'nome_normalizado': nome_base,
                    'bimestre': info_bimestre['bimestre']
                }
                turmas_carregadas += 1
                print(f"{turma_nome} carregada com sucesso!")
                
            except Exception as erro:
                print(f"{turma_nome} não encontrada: {str(erro)}")
        
        info_bimestre['turmas_carregadas'] = turmas_carregadas
        print(f"Total de turmas carregadas: {turmas_carregadas}")
        
        return dados_turmas, info_bimestre
    
    def processar_aluno_por_uc(self, linha_aluno):
        """
        Processa dados de um aluno separando por UC (matéria)
        ESTRUTURA CORRIGIDA: Número | Nome | Nota_UCP1 | Faltas_UCP1 | Nota_UCP2 | Faltas_UCP2 | Nota_UCP3 | Faltas_UCP3
        """
        # A primeira coluna é o número, segunda é o nome
        nome_aluno = linha_aluno.iloc[1]  # CORRIGIDO: Nome está na posição 1
        
        if pd.isna(nome_aluno) or nome_aluno == "":
            return None
        
        print(f"Processando: {nome_aluno}")
        
        # ESTRUTURA CORRIGIDA: Número | Nome | UCP1_Nota | UCP1_Faltas | UCP2_Nota | UCP2_Faltas | UCP3_Nota | UCP3_Faltas
        dados_aluno = {
            'nome': str(nome_aluno).strip(),
            'ucs': {
                'UCP 1': {
                    'nota': self._extrair_valor_numerico(linha_aluno.iloc[2]),      # Posição 2: Nota UCP1
                    'faltas': self._extrair_valor_numerico(linha_aluno.iloc[3])     # Posição 3: Faltas UCP1
                },
                'UCP 2': {
                    'nota': self._extrair_valor_numerico(linha_aluno.iloc[4]) if len(linha_aluno) > 4 else 0,    # Posição 4: Nota UCP2
                    'faltas': self._extrair_valor_numerico(linha_aluno.iloc[5]) if len(linha_aluno) > 5 else 0   # Posição 5: Faltas UCP2
                },
                'UCP 3': {
                    'nota': self._extrair_valor_numerico(linha_aluno.iloc[6]) if len(linha_aluno) > 6 else 0,    # Posição 6: Nota UCP3
                    'faltas': self._extrair_valor_numerico(linha_aluno.iloc[7]) if len(linha_aluno) > 7 else 0   # Posição 7: Faltas UCP3
                }
            },
            'projeto': {
                'nota': self._extrair_valor_numerico(linha_aluno.iloc[8]) if len(linha_aluno) > 8 else 0,       # Posição 8: Projeto
                'faltas': self._extrair_valor_numerico(linha_aluno.iloc[9]) if len(linha_aluno) > 9 else 0      # Posição 9: Faltas Projeto
            }
        }
        
        # Mostrar dados extraídos para verificação
        for uc_nome, uc_dados in dados_aluno['ucs'].items():
            if uc_dados['nota'] > 0:
                print(f"  {uc_nome}: Nota={uc_dados['nota']}, Faltas={uc_dados['faltas']}")
        
        # Calcular situação por UC
        dados_aluno['situacao_por_uc'] = {}
        for uc_nome, uc_dados in dados_aluno['ucs'].items():
            nota = uc_dados['nota']
            faltas = uc_dados['faltas']
            
            # Classificar risco por UC
            if nota < 5.0:
                if faltas > 10:
                    risco = 'ALTO_RISCO'
                elif faltas > 5:
                    risco = 'RISCO_MODERADO'
                else:
                    risco = 'ATENCAO'
            elif nota < 7.0 and faltas > 8:
                risco = 'RISCO_MODERADO'
            elif faltas > 12:
                risco = 'RISCO_MODERADO'
            else:
                risco = 'OK'
            
            dados_aluno['situacao_por_uc'][uc_nome] = risco
        
        # Calcular média geral (só das UCs, projeto é separado)
        notas_ucs = [uc['nota'] for uc in dados_aluno['ucs'].values() if uc['nota'] > 0]
        dados_aluno['media_geral'] = sum(notas_ucs) / len(notas_ucs) if notas_ucs else 0
        dados_aluno['total_faltas'] = sum(uc['faltas'] for uc in dados_aluno['ucs'].values())
        
        if dados_aluno['media_geral'] > 0:
            print(f"  Média: {dados_aluno['media_geral']:.1f}")
        
        # Situação geral do aluno
        situacoes = list(dados_aluno['situacao_por_uc'].values())
        if 'ALTO_RISCO' in situacoes:
            dados_aluno['situacao_geral'] = 'ALTO_RISCO'
        elif 'RISCO_MODERADO' in situacoes:
            dados_aluno['situacao_geral'] = 'RISCO_MODERADO'
        elif 'ATENCAO' in situacoes:
            dados_aluno['situacao_geral'] = 'ATENCAO'
        else:
            dados_aluno['situacao_geral'] = 'OK'
        
        return dados_aluno
    
    def _extrair_valor_numerico(self, valor):
        """
        Extrai valor numérico seguro, tratando diferentes tipos de dados
        """
        if pd.isna(valor):
            return 0.0
        
        if isinstance(valor, (int, float)):
            return float(valor)
        
        # Se for string, tentar converter
        if isinstance(valor, str):
            try:
                # Remover espaços e trocar vírgula por ponto
                valor_limpo = valor.strip().replace(',', '.')
                return float(valor_limpo)
            except (ValueError, AttributeError):
                return 0.0
        
        return 0.0
    
    def processar_turma_completa(self, df_turma, nome_turma, info_bimestre):
        """
        Processa todos os alunos de uma turma
        """
        alunos_processados = []
        
        print(f"Processando turma: {nome_turma}")
        print(f"Total de linhas na planilha: {len(df_turma)}")
        
        # Começar da linha 3 (índice 2) - pular cabeçalhos
        for index in range(2, len(df_turma)):
            linha = df_turma.iloc[index]
            aluno_dados = self.processar_aluno_por_uc(linha)
            
            if aluno_dados:
                aluno_dados['turma'] = nome_turma
                aluno_dados['bimestre'] = info_bimestre['bimestre']
                alunos_processados.append(aluno_dados)
        
        print(f"{nome_turma}: {len(alunos_processados)} alunos processados")
        return alunos_processados
    
    def obter_dados_completos(self, caminho_arquivo, bimestre_especifico=None):
        """
        Função principal que retorna todos os dados processados
        """
        print("Iniciando processamento completo dos dados...")
        
        dados_brutos, info_bimestre = self.carregar_dados_bimestre(caminho_arquivo, bimestre_especifico)
        
        if not dados_brutos:
            return None, info_bimestre
        
        dados_processados = {
            'info_bimestre': info_bimestre,
            'turmas': {},
            'resumo_geral': {
                'total_alunos': 0,
                'total_turmas': 0,
                'alunos_risco_alto': 0,
                'alunos_risco_moderado': 0,
                'alunos_atencao': 0,
                'alunos_ok': 0
            }
        }
        
        # Processar cada turma
        for nome_turma, dados_turma in dados_brutos.items():
            alunos = self.processar_turma_completa(
                dados_turma['dataframe'], 
                nome_turma, 
                info_bimestre
            )
            
            # Calcular estatísticas da turma
            total_alunos = len(alunos)
            if total_alunos > 0:
                medias_turma = [aluno['media_geral'] for aluno in alunos if aluno['media_geral'] > 0]
                media_turma = sum(medias_turma) / len(medias_turma) if medias_turma else 0
                
                # Contar por situação
                contadores = {'ALTO_RISCO': 0, 'RISCO_MODERADO': 0, 'ATENCAO': 0, 'OK': 0}
                for aluno in alunos:
                    contadores[aluno['situacao_geral']] += 1
                
                # Calcular percentual de risco
                alunos_problema = contadores['ALTO_RISCO'] + contadores['RISCO_MODERADO']
                percentual_risco = (alunos_problema / total_alunos * 100) if total_alunos > 0 else 0
                
                dados_processados['turmas'][nome_turma] = {
                    'alunos': alunos,
                    'estatisticas': {
                        'total_alunos': total_alunos,
                        'media_turma': round(media_turma, 2),
                        'percentual_risco': round(percentual_risco, 1),
                        'contadores_situacao': contadores
                    }
                }
                
                # Atualizar resumo geral
                dados_processados['resumo_geral']['total_alunos'] += total_alunos
                dados_processados['resumo_geral']['total_turmas'] += 1
                dados_processados['resumo_geral']['alunos_risco_alto'] += contadores['ALTO_RISCO']
                dados_processados['resumo_geral']['alunos_risco_moderado'] += contadores['RISCO_MODERADO']
                dados_processados['resumo_geral']['alunos_atencao'] += contadores['ATENCAO']
                dados_processados['resumo_geral']['alunos_ok'] += contadores['OK']
                
                print(f"Estatísticas {nome_turma}: Média={media_turma:.1f}, Risco={percentual_risco:.1f}%")
        
        print("Processamento completo concluído!")
        return dados_processados, info_bimestre

# Funções auxiliares para compatibilidade com código existente
def carregar_dados_excel(caminho_arquivo):
    """Função para compatibilidade - usa a nova classe"""
    leitor = LeitorDadosExcel()
    dados_processados, info = leitor.obter_dados_completos(caminho_arquivo)
    if dados_processados:
        return {nome: turma_dados['alunos'] for nome, turma_dados in dados_processados['turmas'].items()}
    return {}

def detectar_formato_planilha(caminho_arquivo):
    """Função para compatibilidade - usa a nova classe"""
    leitor = LeitorDadosExcel()
    info = leitor.detectar_bimestre_arquivo(caminho_arquivo)
    return info['bimestre'], info['descricao']

def obter_todas_turmas_processadas(caminho_arquivo):
    """Função para compatibilidade - usa a nova classe"""
    leitor = LeitorDadosExcel()
    dados_processados, info = leitor.obter_dados_completos(caminho_arquivo)
    if dados_processados:
        return {nome: turma_dados['alunos'] for nome, turma_dados in dados_processados['turmas'].items()}
    return {}