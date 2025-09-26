# Aplicação principal do sistema de análise de notas

import streamlit as st
import os
from datetime import datetime
import traceback

# Importar os módulos usando a estrutura src/ existente
from src.leitura_dados import LeitorDadosExcel
from src.upload_arquivo import GestorArquivos
from src.analise_risco import AnalisadorDados

# Configuração da página
st.set_page_config(
    page_title="Sistema IA - Análise de Notas",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar aparência
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .success-card {
        background-color: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    .warning-card {
        background-color: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    .error-card {
        background-color: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

class AplicacaoPrincipal:
    def __init__(self):
        self.leitor_dados = LeitorDadosExcel()
        self.gestor_arquivos = GestorArquivos()
        self.analisador_dados = AnalisadorDados()
        
        # Estado da sessão
        if 'dados_carregados' not in st.session_state:
            st.session_state.dados_carregados = None
        if 'info_bimestre_atual' not in st.session_state:
            st.session_state.info_bimestre_atual = None
        if 'ultimo_arquivo_usado' not in st.session_state:
            st.session_state.ultimo_arquivo_usado = None

    def executar(self):
        """
        Função principal que executa a aplicação
        """
        # Cabeçalho principal
        self._criar_cabecalho()
        
        # Sidebar - Gestão de arquivos e navegação
        caminho_arquivo, bimestre_selecionado = self._criar_sidebar()
        
        # Verificar se precisa recarregar dados
        if self._precisa_recarregar_dados(caminho_arquivo):
            self._carregar_dados(caminho_arquivo, bimestre_selecionado)
        
        # Área principal - Conteúdo baseado na navegação
        self._criar_conteudo_principal()

    def _criar_cabecalho(self):
        """
        Cria cabeçalho principal da aplicação
        """
        st.markdown("""
        <div class="main-header">
            <h1>📚 Sistema de Análise - Turmas de Inteligência Artificial</h1>
            <p>Acompanhamento pedagógico e identificação de alunos em risco</p>
        </div>
        """, unsafe_allow_html=True)

    def _criar_sidebar(self):
        """
        Cria sidebar com navegação e gestão de arquivos
        """
        st.sidebar.title("🎯 Navegação")
        
        # Menu principal
        pagina = st.sidebar.selectbox(
            "Escolha a análise:",
            ["📊 Visão Geral", "🔍 Análise Detalhada", "⚠️ Alunos em Risco", "📋 Configurações"],
            help="Selecione o tipo de análise que deseja visualizar"
        )
        
        st.session_state.pagina_atual = pagina
        
        # Gestão de arquivos
        try:
            caminho_arquivo, bimestre_selecionado = self.gestor_arquivos.criar_interface_completa()
            return caminho_arquivo, bimestre_selecionado
        except Exception as e:
            st.sidebar.error(f"Erro na gestão de arquivos: {str(e)}")
            return None, None

    def _precisa_recarregar_dados(self, caminho_arquivo):
        """
        Verifica se precisa recarregar os dados
        """
        if not caminho_arquivo:
            return False
            
        if st.session_state.dados_carregados is None:
            return True
            
        if st.session_state.ultimo_arquivo_usado != caminho_arquivo:
            return True
            
        return False

    def _carregar_dados(self, caminho_arquivo, bimestre_selecionado):
        """
        Carrega dados do arquivo Excel
        """
        if not caminho_arquivo or not os.path.exists(caminho_arquivo):
            st.error("❌ Arquivo não encontrado")
            return
        
        try:
            # Mostrar progress bar
            progress_bar = st.sidebar.progress(0)
            status_text = st.sidebar.empty()
            
            status_text.text("🔍 Detectando formato do arquivo...")
            progress_bar.progress(25)
            
            status_text.text("📊 Carregando dados das turmas...")
            progress_bar.progress(50)
            
            # Carregar dados usando a classe melhorada
            dados_processados, info_bimestre = self.leitor_dados.obter_dados_completos(
                caminho_arquivo, bimestre_selecionado
            )
            
            progress_bar.progress(75)
            status_text.text("✅ Processando informações...")
            
            if dados_processados:
                st.session_state.dados_carregados = dados_processados
                st.session_state.info_bimestre_atual = info_bimestre
                st.session_state.ultimo_arquivo_usado = caminho_arquivo
                
                progress_bar.progress(100)
                status_text.text("🎉 Dados carregados com sucesso!")
                
                # Mostrar resumo do carregamento
                st.sidebar.success(f"✅ {info_bimestre.get('turmas_carregadas', 0)} turmas carregadas")
                
                # Limpar progress após 2 segundos
                import time
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
            else:
                st.sidebar.error("❌ Erro ao processar dados")
                progress_bar.empty()
                status_text.empty()
                
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao carregar dados: {str(e)}")
            st.sidebar.error("🔧 Verifique se o arquivo Excel está no formato correto")
            
            # Mostrar detalhes do erro em debug mode
            if st.sidebar.checkbox("🐛 Mostrar detalhes do erro"):
                st.sidebar.code(traceback.format_exc())

    def _criar_conteudo_principal(self):
        """
        Cria conteúdo principal baseado na página selecionada
        """
        pagina = st.session_state.get('pagina_atual', '📊 Visão Geral')
        dados = st.session_state.dados_carregados
        
        if not dados:
            self._mostrar_tela_inicial()
            return
        
        # Roteamento de páginas
        try:
            if pagina == "📊 Visão Geral":
                self._mostrar_visao_geral(dados)
            elif pagina == "🔍 Análise Detalhada":
                self._mostrar_analise_detalhada(dados)
            elif pagina == "⚠️ Alunos em Risco":
                self._mostrar_alunos_risco(dados)
            elif pagina == "📋 Configurações":
                self._mostrar_configuracoes()
                
        except Exception as e:
            st.error(f"❌ Erro ao processar os dados: {str(e)}")
            st.error("🔧 Verifique se o arquivo Excel está no formato correto")
            st.error("📋 Tente fazer upload de um novo arquivo usando a sidebar")
            
            # Mostrar detalhes do erro para debug
            if st.checkbox("🐛 Ver detalhes do erro"):
                st.code(traceback.format_exc())
            
            # Botão para limpar cache
            if st.button("🔄 Limpar dados e recarregar"):
                st.session_state.dados_carregados = None
                st.session_state.info_bimestre_atual = None
                st.session_state.ultimo_arquivo_usado = None
                st.rerun()

    def _mostrar_tela_inicial(self):
        """
        Mostra tela inicial quando não há dados carregados
        """
        st.markdown("""
        <div class="alert-card warning-card">
            <h3>👋 Bem-vinda ao Sistema de Análise de Turmas de IA!</h3>
            <p>Para começar, você precisa:</p>
            <ol>
                <li>📁 Selecionar um bimestre no menu lateral (se disponível)</li>
                <li>📤 Ou fazer upload de uma nova planilha</li>
                <li>⏳ Aguardar o processamento dos dados</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações sobre formatos suportados
        with st.expander("📋 Formatos de arquivo suportados"):
            st.write("""
            **Formatos aceitos:**
            - 📊 **2º Bimestre:** Planilhas com sufixo " - IA" (ex: "1º ano G - IA")
            - 📊 **3º Bimestre:** Planilhas sem sufixo (ex: "1º ano G")  
            - 📊 **4º Bimestre:** Planilhas com sufixo " - 4º Bim" (ex: "1º ano G - 4º Bim")
            
            **Turmas esperadas:**
            - 1º ano G, 1º ano E
            - 2º ano G, 2º ano D, 2º ano E  
            - 3º ano E
            
            **Estrutura esperada por planilha:**
            - Coluna A: Nome do aluno
            - Colunas B, D, F: Notas das UCPs 1, 2, 3
            - Colunas C, E, G: Faltas das UCPs 1, 2, 3
            - Coluna H: Nota do Projeto (opcional)
            - Coluna I: Faltas do Projeto (opcional)
            """)

    def _mostrar_visao_geral(self, dados):
        """
        Mostra página de visão geral
        """
        self.analisador_dados.criar_resumo_geral(dados)

    def _mostrar_analise_detalhada(self, dados):
        """
        Mostra página de análise detalhada
        """
        turmas_disponiveis = list(dados.get('turmas', {}).keys())
        
        if not turmas_disponiveis:
            st.warning("⚠️ Nenhuma turma disponível para análise")
            return
        
        # Seletor de turma
        turma_selecionada = st.selectbox(
            "Selecione a turma para análise detalhada:",
            turmas_disponiveis,
            format_func=lambda x: x.replace(' - IA', ''),
            help="Escolha uma turma para ver análise completa"
        )
        
        if turma_selecionada:
            self.analisador_dados.criar_analise_detalhada(dados, turma_selecionada)

    def _mostrar_alunos_risco(self, dados):
        """
        Mostra página de alunos em risco
        """
        self.analisador_dados.criar_lista_alunos_risco(dados)

    def _mostrar_configuracoes(self):
        """
        Mostra página de configurações
        """
        st.title("📋 Configurações do Sistema")
        
        # Informações do sistema
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ℹ️ Informações do Sistema")
            st.info(f"📅 Data atual: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            if st.session_state.info_bimestre_atual:
                info = st.session_state.info_bimestre_atual
                st.info(f"📊 Bimestre ativo: {info.get('descricao', 'N/A')}")
                st.info(f"🎯 Turmas carregadas: {info.get('turmas_carregadas', 0)}")
        
        with col2:
            st.subheader("🔧 Ações do Sistema")
            
            if st.button("🔄 Recarregar dados atuais"):
                st.session_state.dados_carregados = None
                st.success("✅ Dados serão recarregados na próxima navegação")
            
            if st.button("🗑️ Limpar cache completo"):
                for key in ['dados_carregados', 'info_bimestre_atual', 'ultimo_arquivo_usado']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Cache limpo com sucesso")
        
        # Configurações de visualização
        st.markdown("---")
        st.subheader("🎨 Configurações de Visualização")
        
        col1, col2 = st.columns(2)
        with col1:
            mostrar_detalhes_debug = st.checkbox("🐛 Mostrar informações de debug", value=False)
            tema_escuro = st.checkbox("🌙 Tema escuro (experimental)", value=False)
        
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=False)
            notificacoes_sound = st.checkbox("🔔 Notificações sonoras", value=False)
        
        if mostrar_detalhes_debug and st.session_state.dados_carregados:
            st.markdown("---")
            st.subheader("🐛 Informações de Debug")
            
            with st.expander("Ver dados brutos"):
                st.json(st.session_state.info_bimestre_atual)
            
            with st.expander("Ver estatísticas detalhadas"):
                dados = st.session_state.dados_carregados
                st.write("**Resumo geral:**", dados.get('resumo_geral', {}))
                st.write("**Número de turmas:**", len(dados.get('turmas', {})))

# Função principal
def main():
    """
    Função principal da aplicação
    """
    app = AplicacaoPrincipal()
    app.executar()

# Executar aplicação
if __name__ == "__main__":
    main()