# Módulo responsável pelo upload e gestão de arquivos com seleção de bimestre

import streamlit as st
import tempfile
import os
import shutil
from datetime import datetime
import pandas as pd

class GestorArquivos:
    def __init__(self):
        self.pasta_dados = "dados/"
        self.arquivos_suportados = {
            '2_bimestre': 'NOTAS BIMESTRAIS EPT 2º bimestre.xlsx',
            '3_bimestre': 'NOTAS BIMESTRAIS EPT 3º bimestre.xlsx', 
            '4_bimestre': 'NOTAS BIMESTRAIS EPT 4º bimestre.xlsx'
        }
        self.bimestre_atual = None
        self.caminho_atual = None

    def criar_interface_completa(self):
        """
        Cria interface completa na sidebar com seleção de bimestre
        """
        st.sidebar.markdown("---")
        st.sidebar.title("📁 Gestão de Arquivos")
        
        # Seção 1: Seleção de Bimestre
        self._criar_selecao_bimestre()
        
        # Seção 2: Status do arquivo atual
        self._mostrar_status_arquivo()
        
        # Seção 3: Upload de novo arquivo
        self._criar_interface_upload()
        
        # Seção 4: Histórico e backups
        self._mostrar_historico()
        
        return self.caminho_atual, self.bimestre_atual
    
    def _criar_selecao_bimestre(self):
        """
        Interface para seleção do bimestre a ser analisado
        """
        st.sidebar.subheader("📅 Selecionar Bimestre")
        
        # Verificar quais arquivos existem
        bimestres_disponiveis = {}
        for bim, arquivo in self.arquivos_suportados.items():
            caminho_completo = os.path.join(self.pasta_dados, arquivo)
            if os.path.exists(caminho_completo):
                bimestres_disponiveis[bim] = {
                    'nome': arquivo,
                    'caminho': caminho_completo,
                    'tamanho': self._formatar_tamanho(os.path.getsize(caminho_completo)),
                    'modificado': datetime.fromtimestamp(os.path.getmtime(caminho_completo))
                }
        
        if not bimestres_disponiveis:
            st.sidebar.warning("⚠️ Nenhum arquivo de bimestre encontrado")
            st.sidebar.info("📤 Faça upload de uma planilha abaixo")
            return
        
        # Criar opções para o selectbox
        opcoes_bimestre = {}
        for bim, dados in bimestres_disponiveis.items():
            nome_display = self._get_nome_bimestre_display(bim)
            modificado_str = dados['modificado'].strftime("%d/%m/%Y %H:%M")
            opcoes_bimestre[f"{nome_display} ({modificado_str})"] = bim
        
        # Selectbox para escolher bimestre
        if len(opcoes_bimestre) == 1:
            # Se só tem um, usar automaticamente
            bimestre_selecionado = list(opcoes_bimestre.values())[0]
            nome_display = list(opcoes_bimestre.keys())[0]
            st.sidebar.info(f"📊 **Usando:** {nome_display}")
        else:
            # Se tem múltiplos, deixar usuário escolher
            escolha = st.sidebar.selectbox(
                "Escolha o bimestre:",
                options=list(opcoes_bimestre.keys()),
                help="Selecione qual bimestre deseja analisar"
            )
            bimestre_selecionado = opcoes_bimestre[escolha]
        
        # Definir arquivo atual baseado na seleção
        self.bimestre_atual = bimestre_selecionado
        self.caminho_atual = bimestres_disponiveis[bimestre_selecionado]['caminho']
        
        # Mostrar informações do bimestre selecionado
        dados_arquivo = bimestres_disponiveis[bimestre_selecionado]
        st.sidebar.success(f"✅ **{self._get_nome_bimestre_display(bimestre_selecionado)}**")
        st.sidebar.caption(f"📄 {dados_arquivo['nome']}")
        st.sidebar.caption(f"📊 Tamanho: {dados_arquivo['tamanho']}")
        st.sidebar.caption(f"🕐 Modificado: {dados_arquivo['modificado'].strftime('%d/%m/%Y %H:%M')}")
    
    def _get_nome_bimestre_display(self, bimestre_codigo):
        """
        Converte código do bimestre para nome amigável
        """
        nomes = {
            '2_bimestre': '2º Bimestre',
            '3_bimestre': '3º Bimestre', 
            '4_bimestre': '4º Bimestre'
        }
        return nomes.get(bimestre_codigo, bimestre_codigo)
    
    def _mostrar_status_arquivo(self):
        """
        Mostra validação e status do arquivo atual
        """
        if not self.caminho_atual:
            return
            
        st.sidebar.markdown("---")
        st.sidebar.subheader("✅ Status do Arquivo")
        
        validacao = self._validar_estrutura_arquivo(self.caminho_atual)
        
        if validacao['valido']:
            st.sidebar.success("📊 Arquivo válido!")
            st.sidebar.info(f"🎯 {validacao['turmas_encontradas']} turmas de IA encontradas")
            st.sidebar.info(f"📋 Formato: {validacao.get('formato_detectado', 'Desconhecido')}")
            
            # Mostrar turmas disponíveis (colapsável)
            with st.sidebar.expander("Ver turmas disponíveis"):
                if 'turmas_detalhes' in validacao:
                    for turma in validacao['turmas_detalhes']:
                        st.write(f"• {turma}")
        else:
            st.sidebar.error("❌ Arquivo com problemas!")
            if 'erro' in validacao:
                st.sidebar.error(f"Erro: {validacao['erro']}")
    
    def _criar_interface_upload(self):
        """
        Interface para upload de novos arquivos
        """
        st.sidebar.markdown("---")
        st.sidebar.subheader("📤 Upload Nova Planilha")
        
        # Informação sobre bimestre a ser substituído
        if self.bimestre_atual:
            nome_bim = self._get_nome_bimestre_display(self.bimestre_atual)
            st.sidebar.info(f"🔄 Substituirá: **{nome_bim}**")
        
        novo_arquivo = st.sidebar.file_uploader(
            "Selecionar arquivo Excel:",
            type=['xlsx'],
            help="Arquivo será salvo substituindo o bimestre atual selecionado"
        )
        
        if novo_arquivo is not None:
            # Mostrar informações do arquivo
            st.sidebar.success(f"✅ **{novo_arquivo.name}** carregado")
            st.sidebar.write(f"📊 Tamanho: {self._formatar_tamanho(novo_arquivo.size)}")
            
            # Detectar formato do arquivo enviado
            formato_detectado = self._detectar_formato_upload(novo_arquivo)
            st.sidebar.info(f"🔍 Formato detectado: **{formato_detectado['descricao']}**")
            
            # Botões de ação
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("🔄 Usar Agora", help="Usar arquivo temporariamente"):
                    caminho_temp = self._salvar_temporario(novo_arquivo)
                    if caminho_temp:
                        self.caminho_atual = caminho_temp
                        st.sidebar.success("📈 Usando arquivo temporário!")
                        st.experimental_rerun()
            
            with col2:
                if st.button("💾 Salvar", help="Salvar permanentemente"):
                    if self._salvar_permanente(novo_arquivo, formato_detectado):
                        st.sidebar.success("💾 Salvo com sucesso!")
                        st.sidebar.balloons()
                        st.experimental_rerun()
    
    def _detectar_formato_upload(self, arquivo_uploaded):
        """
        Detecta formato de arquivo uploadado
        """
        try:
            # Salvar temporariamente para análise
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(arquivo_uploaded.getbuffer())
                tmp_path = tmp_file.name
            
            # Analisar planilhas
            excel_file = pd.ExcelFile(tmp_path)
            sheet_names = excel_file.sheet_names
            
            # Verificar formatos
            if any("- IA" in sheet for sheet in sheet_names):
                formato = "2º Bimestre (com ' - IA')"
                codigo = '2_bimestre'
            elif any("- 4º Bim" in sheet for sheet in sheet_names):
                formato = "4º Bimestre (com ' - 4º Bim')"
                codigo = '4_bimestre'
            elif any(sheet in ["1º ano G", "2º ano G", "1º ano E", "2º ano D", "2º ano E", "3º ano E"] for sheet in sheet_names):
                formato = "3º Bimestre (sem sufixo)"
                codigo = '3_bimestre'
            else:
                formato = "Formato não reconhecido"
                codigo = 'desconhecido'
            
            # Limpar arquivo temporário
            os.unlink(tmp_path)
            
            return {'descricao': formato, 'codigo': codigo}
            
        except Exception as e:
            return {'descricao': f'Erro: {str(e)}', 'codigo': 'erro'}
    
    def _salvar_permanente(self, arquivo_uploaded, formato_info):
        """
        Salva arquivo permanentemente na pasta dados
        """
        try:
            # Determinar nome do arquivo baseado no formato
            if formato_info['codigo'] in self.arquivos_suportados:
                nome_arquivo = self.arquivos_suportados[formato_info['codigo']]
            else:
                # Se formato não reconhecido, usar nome genérico com timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"planilha_upload_{timestamp}.xlsx"
            
            caminho_destino = os.path.join(self.pasta_dados, nome_arquivo)
            
            # Criar backup se arquivo existe
            if os.path.exists(caminho_destino):
                backup_nome = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_arquivo}"
                backup_path = os.path.join(self.pasta_dados, backup_nome)
                shutil.copy2(caminho_destino, backup_path)
                st.sidebar.info(f"📋 Backup criado: {backup_nome}")
            
            # Salvar novo arquivo
            os.makedirs(self.pasta_dados, exist_ok=True)
            with open(caminho_destino, "wb") as f:
                f.write(arquivo_uploaded.getbuffer())
            
            return True
            
        except Exception as e:
            st.sidebar.error(f"Erro ao salvar: {str(e)}")
            return False
    
    def _salvar_temporario(self, arquivo_uploaded):
        """
        Salva arquivo temporariamente para uso imediato
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(arquivo_uploaded.getbuffer())
                return tmp_file.name
        except Exception as e:
            st.sidebar.error(f"Erro ao criar arquivo temporário: {str(e)}")
            return None
    
    def _mostrar_historico(self):
        """
        Mostra histórico de backups
        """
        backups = self._listar_backups()
        
        if backups:
            st.sidebar.markdown("---")
            with st.sidebar.expander(f"📚 Histórico ({len(backups)} backups)"):
                for backup in backups[-5:]:  # Mostrar só os 5 mais recentes
                    data_str = backup['nome'].replace('backup_', '').split('_')[0:2]
                    try:
                        if len(data_str) >= 2:
                            data_formatada = datetime.strptime(
                                f"{data_str[0]}_{data_str[1]}", '%Y%m%d_%H%M%S'
                            ).strftime('%d/%m/%Y %H:%M')
                        else:
                            data_formatada = backup['nome']
                    except:
                        data_formatada = backup['nome']
                    
                    st.write(f"📅 {data_formatada}")
                    st.caption(f"Tamanho: {backup['tamanho']}")
    
    def _listar_backups(self):
        """
        Lista arquivos de backup disponíveis
        """
        backups = []
        try:
            if os.path.exists(self.pasta_dados):
                arquivos = os.listdir(self.pasta_dados)
                for arquivo in arquivos:
                    if arquivo.startswith("backup_") and arquivo.endswith(".xlsx"):
                        caminho_completo = os.path.join(self.pasta_dados, arquivo)
                        tamanho = os.path.getsize(caminho_completo)
                        backups.append({
                            'nome': arquivo,
                            'tamanho': self._formatar_tamanho(tamanho),
                            'caminho': caminho_completo
                        })
                # Ordenar por data (mais recente primeiro)
                backups.sort(key=lambda x: x['nome'], reverse=True)
        except Exception:
            pass
        return backups
    
    def _validar_estrutura_arquivo(self, caminho_arquivo):
        """
        Valida estrutura do arquivo Excel
        """
        try:
            excel_file = pd.ExcelFile(caminho_arquivo)
            sheet_names = excel_file.sheet_names
            
            # Definir formatos suportados
            formatos = {
                '2º Bimestre': [
                    "1º ano G - IA", "2º ano G - IA", "1º ano E - IA", 
                    "2º ano D - IA", "2º ano E - IA", "3º ano E -IA"
                ],
                '3º Bimestre': [
                    "1º ano G", "2º ano G", "1º ano E",
                    "2º ano D", "2º ano E", "3º ano E"
                ],
                '4º Bimestre': [
                    "1º ano G - 4º Bim", "2º ano G - 4º Bim", "1º ano E - 4º Bim",
                    "2º ano D - 4º Bim", "2º ano E - 4º Bim", "3º ano E - 4º Bim"
                ]
            }
            
            # Verificar qual formato tem mais turmas
            melhor_formato = None
            mais_turmas = 0
            turmas_encontradas = []
            
            for formato_nome, turmas_formato in formatos.items():
                count = 0
                turmas_deste_formato = []
                
                for turma in turmas_formato:
                    if turma in sheet_names:
                        count += 1
                        turmas_deste_formato.append(turma)
                
                if count > mais_turmas:
                    mais_turmas = count
                    melhor_formato = formato_nome
                    turmas_encontradas = turmas_deste_formato
            
            return {
                'valido': mais_turmas >= 1,
                'turmas_encontradas': mais_turmas,
                'total_planilhas': len(sheet_names),
                'formato_detectado': melhor_formato or 'Desconhecido',
                'turmas_detalhes': turmas_encontradas
            }
            
        except Exception as e:
            return {
                'valido': False,
                'erro': str(e),
                'turmas_encontradas': 0,
                'total_planilhas': 0
            }
    
    def _formatar_tamanho(self, bytes_size):
        """
        Formata tamanho em bytes para formato legível
        """
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{round(bytes_size / 1024, 1)} KB"
        else:
            return f"{round(bytes_size / (1024 * 1024), 1)} MB"

# Funções auxiliares para compatibilidade
def criar_interface_upload():
    """
    Função de compatibilidade - usa nova classe
    """
    gestor = GestorArquivos()
    return gestor.criar_interface_completa()

def mostrar_validacao_arquivo(caminho_arquivo):
    """
    Função de compatibilidade - usa nova classe
    """
    gestor = GestorArquivos()
    gestor.caminho_atual = caminho_arquivo
    gestor._mostrar_status_arquivo()

def mostrar_historico_arquivos():
    """
    Função de compatibilidade - usa nova classe
    """
    gestor = GestorArquivos()
    gestor._mostrar_historico()

def formatar_tamanho_arquivo(bytes_size):
    """
    Função de compatibilidade
    """
    gestor = GestorArquivos()
    return gestor._formatar_tamanho(bytes_size)

def validar_estrutura_arquivo(caminho_arquivo):
    """
    Função de compatibilidade
    """
    gestor = GestorArquivos()
    return gestor._validar_estrutura_arquivo(caminho_arquivo)