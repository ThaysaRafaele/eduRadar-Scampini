# Exemplo de como integrar o sistema melhorado em uma aplicação Streamlit existente

import streamlit as st

# ===== EXEMPLO DE INTEGRAÇÃO COM CÓDIGO EXISTENTE =====

# Se você já tem um app.py funcionando, pode integrar assim:

def integrar_sistema_melhorado():
    """
    Exemplo de como integrar o sistema melhorado ao seu código existente
    """
    
    # 1. IMPORTS (adicionar no topo do seu arquivo)
    from leitor_excel_melhorado import LeitorDadosExcel
    from gestao_arquivos_melhorada import GestorArquivos  
    from analisador_dados_melhorado import AnalisadorDados
    
    # 2. INICIALIZAÇÃO (no início da função principal)
    if 'leitor_dados' not in st.session_state:
        st.session_state.leitor_dados = LeitorDadosExcel()
    if 'gestor_arquivos' not in st.session_state:
        st.session_state.gestor_arquivos = GestorArquivos()
    if 'analisador_dados' not in st.session_state:
        st.session_state.analisador_dados = AnalisadorDados()
    
    # 3. SIDEBAR MELHORADA (substitui sua sidebar atual)
    st.sidebar.title("📚 Sistema IA - Análise de Notas")
    
    # Nova interface de gestão de arquivos
    try:
        caminho_arquivo, bimestre_atual = st.session_state.gestor_arquivos.criar_interface_completa()
    except Exception as e:
        st.sidebar.error(f"Erro na gestão: {str(e)}")
        caminho_arquivo, bimestre_atual = None, None
    
    # 4. CARREGAMENTO DE DADOS MELHORADO
    if caminho_arquivo and ('dados_atuais' not in st.session_state or 
                           st.session_state.get('arquivo_anterior') != caminho_arquivo):
        
        with st.spinner("🔄 Carregando dados..."):
            dados_processados, info_bimestre = st.session_state.leitor_dados.obter_dados_completos(caminho_arquivo)
            
            if dados_processados:
                st.session_state.dados_atuais = dados_processados
                st.session_state.info_bimestre = info_bimestre
                st.session_state.arquivo_anterior = caminho_arquivo
                st.success(f"✅ Dados carregados: {info_bimestre.get('descricao', 'N/A')}")
            else:
                st.error("❌ Erro ao carregar dados")
                return
    
    # 5. VERIFICAR SE HÁ DADOS
    if 'dados_atuais' not in st.session_state:
        st.warning("📤 Faça upload de uma planilha na sidebar para começar")
        return
    
    dados = st.session_state.dados_atuais
    
    # 6. MENU DE NAVEGAÇÃO
    pagina = st.sidebar.selectbox(
        "Escolha a análise:",
        ["📊 Visão Geral", "🔍 Análise Detalhada", "⚠️ Alunos em Risco"]
    )
    
    # 7. CONTEÚDO BASEADO NA SELEÇÃO
    if pagina == "📊 Visão Geral":
        st.session_state.analisador_dados.criar_resumo_geral(dados)
        
    elif pagina == "🔍 Análise Detalhada":
        turmas = list(dados.get('turmas', {}).keys())
        if turmas:
            turma_selecionada = st.selectbox("Selecione a turma:", turmas)
            if turma_selecionada:
                st.session_state.analisador_dados.criar_analise_detalhada(dados, turma_selecionada)
        else:
            st.warning("Nenhuma turma encontrada")
            
    elif pagina == "⚠️ Alunos em Risco":
        st.session_state.analisador_dados.criar_lista_alunos_risco(dados)

# ===== EXEMPLO DE MIGRAÇÃO GRADUAL =====

def exemplo_migracao_gradual():
    """
    Como migrar gradualmente sem quebrar o sistema atual
    """
    
    st.title("🔄 Migração Gradual para Sistema Melhorado")
    
    st.markdown("""
    ## Passo a Passo da Migração:
    
    ### 1. 📥 Backup do Sistema Atual
    ```bash
    # Fazer backup dos arquivos atuais
    cp leitor_dados.py leitor_dados_backup.py
    cp gestao_arquivos.py gestao_arquivos_backup.py  
    cp app.py app_backup.py
    ```
    
    ### 2. 📂 Adicionar Novos Arquivos
    - Salvar `leitor_excel_melhorado.py`
    - Salvar `gestao_arquivos_melhorada.py`
    - Salvar `analisador_dados_melhorado.py`
    
    ### 3. 🔄 Atualizar app.py Gradualmente
    
    **Opção A - Substituição Completa:**
    ```python
    # Substituir conteúdo do app.py pelo app_principal_melhorado.py
    ```
    
    **Opção B - Integração Gradual:**
    ```python
    # No seu app.py atual, adicionar:
    
    # Início do arquivo - novos imports
    try:
        from leitor_excel_melhorado import LeitorDadosExcel
        from gestao_arquivos_melhorada import GestorArquivos
        from analisador_dados_melhorado import AnalisadorDados
        SISTEMA_MELHORADO_ATIVO = True
    except ImportError:
        # Fallback para sistema antigo
        SISTEMA_MELHORADO_ATIVO = False
    
    # Na função principal
    if SISTEMA_MELHORADO_ATIVO:
        # Usar sistema novo
        integrar_sistema_melhorado()
    else:
        # Manter sistema antigo funcionando
        usar_sistema_antigo()
    ```
    
    ### 4. 🧪 Testar Funcionalidades
    
    **Checklist de Testes:**
    - [ ] Upload de arquivos do 2º bimestre
    - [ ] Upload de arquivos do 3º bimestre  
    - [ ] Upload de arquivos do 4º bimestre (quando disponível)
    - [ ] Visualização da visão geral
    - [ ] Análise detalhada por turma
    - [ ] Lista de alunos em risco
    - [ ] Troca entre bimestres
    - [ ] Validação de arquivos
    
    ### 5. 🚀 Ativação Completa
    Uma vez testado, remover sistema antigo e manter apenas o novo.
    """)

# ===== PRINCIPAIS MELHORIAS IMPLEMENTADAS =====

def resumo_melhorias():
    """
    Resumo das principais melhorias implementadas
    """
    
    st.title("✨ Principais Melhorias Implementadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Problemas Corrigidos:")
        
        st.markdown("""
        #### 1. ❌ Médias Zeradas Corrigidas
        - **Antes:** Médias apareciam como 0 mesmo com notas lançadas
        - **Agora:** Cálculo correto das médias por UC e geral
        
        #### 2. 🏷️ Identificação do Bimestre
        - **Antes:** Não mostrava qual bimestre estava sendo analisado  
        - **Agora:** Indica claramente o bimestre em todas as telas
        
        #### 3. 👤 Nomes dos Alunos
        - **Antes:** Lista de alunos em risco sem nomes
        - **Agora:** Nomes completos e informações detalhadas
        
        #### 4. 📚 Análise por UC
        - **Antes:** Média geral de 3 UCs (incorreto)
        - **Agora:** Análise separada por UC + situação específica
        """)
    
    with col2:
        st.subheader("🆕 Novas Funcionalidades:")
        
        st.markdown("""
        #### 1. 🔄 Troca Entre Bimestres
        - Interface para selecionar qual bimestre analisar
        - Suporte automático para 2º, 3º e 4º bimestre
        
        #### 2. 📊 Análise Detalhada por UC
        - Visualização separada de UCP 1, UCP 2, UCP 3
        - Identificação específica de problemas por matéria
        
        #### 3. 🎯 Sistema de Risco Melhorado
        - Classificação por UC individual
        - Identificação precisa de onde o aluno precisa de ajuda
        
        #### 4. 📁 Gestão de Arquivos Avançada  
        - Backup automático
        - Validação de estrutura
        - Histórico de arquivos
        """)
    
    st.markdown("---")
    st.subheader("🔮 Preparação para o Futuro:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **4º Bimestre**
        ✅ Sistema já preparado
        ✅ Detecção automática
        ✅ Sem necessidade de mudanças
        """)
    
    with col2:
        st.info("""
        **Novos Formatos**
        ✅ Estrutura extensível
        ✅ Fácil adição de novos tipos
        ✅ Backward compatibility
        """)
    
    with col3:
        st.info("""
        **Escalabilidade**
        ✅ Suporte a mais turmas
        ✅ Performance otimizada
        ✅ Código modular
        """)

# ===== EXEMPLO DE USO RÁPIDO =====

def exemplo_uso_rapido():
    """
    Exemplo de uso rápido para testar o sistema
    """
    
    st.title("⚡ Uso Rápido - Teste o Sistema")
    
    st.markdown("""
    ## Como testar rapidamente:
    
    ### 1. Preparar ambiente:
    ```bash
    pip install streamlit pandas plotly openpyxl
    ```
    
    ### 2. Estrutura de arquivos:
    ```
    projeto/
    ├── app.py                           # Aplicação principal
    ├── leitor_excel_melhorado.py        # Novo leitor  
    ├── gestao_arquivos_melhorada.py     # Nova gestão
    ├── analisador_dados_melhorado.py    # Novo analisador
    └── dados/
        ├── NOTAS BIMESTRAIS EPT 2º bimestre.xlsx
        ├── NOTAS BIMESTRAIS EPT 3º bimestre.xlsx  
        └── (outros arquivos...)
    ```
    
    ### 3. Executar:
    ```bash
    streamlit run app.py
    ```
    
    ### 4. Testar funcionalidades:
    1. **📁 Upload de arquivo** - Sidebar > Upload nova planilha
    2. **🔄 Troca de bimestre** - Sidebar > Selecionar bimestre  
    3. **📊 Visão geral** - Verificar métricas e tabelas
    4. **🔍 Análise detalhada** - Escolher turma e ver UCs
    5. **⚠️ Alunos em risco** - Ver lista com nomes e detalhes
    """)
    
    st.success("""
    🎉 **Pronto!** Seu sistema agora está muito mais robusto e preparado para o futuro!
    """)

# Interface para mostrar exemplos
def main():
    st.set_page_config(page_title="Exemplos de Integração", layout="wide")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Integração", "📋 Migração", "✨ Melhorias", "⚡ Uso Rápido"
    ])
    
    with tab1:
        integrar_sistema_melhorado()
    
    with tab2:
        exemplo_migracao_gradual()
    
    with tab3:
        resumo_melhorias()
        
    with tab4:
        exemplo_uso_rapido()

if __name__ == "__main__":
    main()