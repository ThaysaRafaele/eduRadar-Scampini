# app.py
# Dashboard principal do EduRadar Scampini

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.leitura_dados import obter_todas_turmas_processadas
from src.analise_risco import analisar_turma_completa, obter_alunos_por_classificacao

# Configuração da página
st.set_page_config(
    page_title="EduRadar Scampini",
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("🎯 EduRadar Scampini")
st.subheader("Sistema Inteligente de Monitoramento Pedagógico")
st.markdown("**Identificação Precoce de Risco de Aprendizagem - Escola Estadual Padre José Scampini**")

# Sidebar para navegação
st.sidebar.title("📚 Navegação")
opcao_menu = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["🏠 Visão Geral", "📊 Análise por Turma", "👥 Alunos em Risco", "📈 Comparativo"]
)

# Cache para carregar dados apenas uma vez
@st.cache_data
def carregar_dados():
    """Carrega e processa todos os dados das turmas"""
    caminho_arquivo = "dados/NOTAS BIMESTRAIS EPT 2º bimestre.xlsx"
    return obter_todas_turmas_processadas(caminho_arquivo)

# Carregar dados
try:
    with st.spinner("Carregando dados das turmas..."):
        dados_todas_turmas = carregar_dados()
    
    # Processar análises de todas as turmas
    analises_completas = {}
    for nome_turma, alunos_turma in dados_todas_turmas.items():
        analises_completas[nome_turma] = analisar_turma_completa(alunos_turma)
    
    # PÁGINA: VISÃO GERAL
    if opcao_menu == "🏠 Visão Geral":
        st.markdown("---")
        st.header("📊 Resumo Geral das Turmas de IA")
        
        # Calcular totais gerais
        total_alunos_geral = 0
        total_alto_risco = 0
        total_risco_moderado = 0
        total_atencao = 0
        total_ok = 0
        
        for nome_turma, analise in analises_completas.items():
            stats = analise['estatisticas']
            total_alunos_geral += stats['total_alunos']
            total_alto_risco += stats['alto_risco']
            total_risco_moderado += stats['risco_moderado']
            total_atencao += stats['atencao']
            total_ok += stats['situacao_ok']
        
        # Métricas principais
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("👥 Total de Alunos", total_alunos_geral)
        
        with col2:
            st.metric("🚨 Alto Risco", total_alto_risco, delta=f"-{round(total_alto_risco/total_alunos_geral*100, 1)}%")
        
        with col3:
            st.metric("⚠️ Risco Moderado", total_risco_moderado)
        
        with col4:
            st.metric("⚡ Atenção", total_atencao)
        
        with col5:
            st.metric("✅ Situação OK", total_ok, delta=f"{round(total_ok/total_alunos_geral*100, 1)}%")
        
        # Gráfico de distribuição geral
        st.subheader("🎯 Distribuição de Risco - Visão Geral")
        
        labels = ['Alto Risco', 'Risco Moderado', 'Atenção', 'Situação OK']
        values = [total_alto_risco, total_risco_moderado, total_atencao, total_ok]
        colors = ['#FF4B4B', '#FFA500', '#FFFF00', '#00FF00']
        
        fig_pizza = px.pie(
            values=values,
            names=labels,
            title="Distribuição de Alunos por Classificação de Risco",
            color_discrete_sequence=colors
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        # Resumo por turma
        st.subheader("📚 Resumo por Turma")
        
        # Criar tabela resumo
        dados_resumo = []
        for nome_turma, analise in analises_completas.items():
            stats = analise['estatisticas']
            dados_resumo.append({
                'Turma': nome_turma,
                'Total Alunos': stats['total_alunos'],
                'Alto Risco': stats['alto_risco'], 
                'Risco Moderado': stats['risco_moderado'],
                'Atenção': stats['atencao'],
                'Situação OK': stats['situacao_ok'],
                'Média da Turma': stats['media_turma'],
                '% Risco': f"{stats['percentual_risco']}%"
            })
        
        st.dataframe(dados_resumo, use_container_width=True)
    
    # PÁGINA: ANÁLISE POR TURMA  
    elif opcao_menu == "📊 Análise por Turma":
        st.markdown("---")
        
        # Seletor de turma
        turma_selecionada = st.selectbox(
            "📚 Selecione uma turma para análise detalhada:",
            list(analises_completas.keys())
        )
        
        if turma_selecionada:
            analise_turma = analises_completas[turma_selecionada]
            stats = analise_turma['estatisticas']
            
            st.header(f"📊 Análise Detalhada: {turma_selecionada}")
            
            # Métricas da turma
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Total de Alunos", stats['total_alunos'])
            
            with col2:
                st.metric("📖 Média da Turma", f"{stats['media_turma']}")
            
            with col3:
                st.metric("📅 Média de Faltas", f"{stats['media_faltas']}")
            
            with col4:
                st.metric("⚠️ % em Risco", f"{stats['percentual_risco']}%")
            
            # Distribuição de risco da turma
            col_grafico1, col_grafico2 = st.columns(2)
            
            with col_grafico1:
                # Gráfico de barras por classificação
                classificacoes = ['Alto Risco', 'Risco Moderado', 'Atenção', 'Situação OK']
                quantidades = [stats['alto_risco'], stats['risco_moderado'], stats['atencao'], stats['situacao_ok']]
                
                fig_barras = px.bar(
                    x=classificacoes,
                    y=quantidades,
                    title=f"Distribuição de Alunos - {turma_selecionada}",
                    color=classificacoes,
                    color_discrete_sequence=['#FF4B4B', '#FFA500', '#FFFF00', '#00FF00']
                )
                st.plotly_chart(fig_barras, use_container_width=True)
            
            with col_grafico2:
                # Ranking dos 10 melhores alunos
                alunos_ordenados = sorted(
                    analise_turma['alunos'], 
                    key=lambda x: x['media'], 
                    reverse=True
                )[:10]
                
                nomes = [aluno['nome'].split()[0] + " " + aluno['nome'].split()[-1] for aluno in alunos_ordenados]
                medias = [aluno['media'] for aluno in alunos_ordenados]
                
                fig_ranking = px.bar(
                    x=medias,
                    y=nomes,
                    orientation='h',
                    title="Top 10 Maiores Médias",
                    color=medias,
                    color_continuous_scale='Viridis'
                )
                fig_ranking.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_ranking, use_container_width=True)
    
    # PÁGINA: ALUNOS EM RISCO
    elif opcao_menu == "👥 Alunos em Risco":
        st.markdown("---")
        st.header("🚨 Alunos que Necessitam Atenção Especial")
        
        # Filtros
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            turmas_filtro = st.multiselect(
                "📚 Filtrar por turmas:",
                list(analises_completas.keys()),
                default=list(analises_completas.keys())
            )
        
        with col_filtro2:
            classificacao_filtro = st.selectbox(
                "⚠️ Filtrar por classificação:",
                ["Todas", "ALTO RISCO", "RISCO MODERADO", "ATENÇÃO"]
            )
        
        # Coletar alunos em risco
        alunos_risco_geral = []
        
        for nome_turma in turmas_filtro:
            if nome_turma in analises_completas:
                analise = analises_completas[nome_turma]
                
                for aluno in analise['alunos']:
                    if classificacao_filtro == "Todas" or aluno['classificacao'] == classificacao_filtro:
                        if aluno['classificacao'] != "SITUAÇÃO OK":
                            aluno['turma'] = nome_turma
                            alunos_risco_geral.append(aluno)
        
        # Exibir alunos em risco
        if len(alunos_risco_geral) > 0:
            st.subheader(f"📋 {len(alunos_risco_geral)} aluno(s) necessitam atenção")
            
            # Ordenar por maior risco
            ordem_risco = {"ALTO RISCO": 0, "RISCO MODERADO": 1, "ATENÇÃO": 2}
            alunos_risco_geral.sort(key=lambda x: (ordem_risco[x['classificacao']], -x['media']))
            
            for aluno in alunos_risco_geral:
                # Definir cor do card baseado no risco
                if aluno['classificacao'] == "ALTO RISCO":
                    st.error(f"""
                    **{aluno['nome']}** - {aluno['turma']}
                    - 📊 Média: {aluno['media']}
                    - 📅 Total de Faltas: {aluno['total_faltas']}
                    - 🚨 Classificação: {aluno['classificacao']}
                    """)
                elif aluno['classificacao'] == "RISCO MODERADO":
                    st.warning(f"""
                    **{aluno['nome']}** - {aluno['turma']}
                    - 📊 Média: {aluno['media']}
                    - 📅 Total de Faltas: {aluno['total_faltas']}
                    - ⚠️ Classificação: {aluno['classificacao']}
                    """)
                else:
                    st.info(f"""
                    **{aluno['nome']}** - {aluno['turma']}
                    - 📊 Média: {aluno['media']}
                    - 📅 Total de Faltas: {aluno['total_faltas']}
                    - ⚡ Classificação: {aluno['classificacao']}
                    """)
        else:
            st.success("🎉 Nenhum aluno encontrado com os critérios selecionados!")
    
    # PÁGINA: COMPARATIVO
    elif opcao_menu == "📈 Comparativo":
        st.markdown("---")
        st.header("📈 Análise Comparativa entre Turmas")
        
        # Gráfico comparativo de médias
        nomes_turmas = []
        medias_turmas = []
        percentuais_risco = []
        
        for nome_turma, analise in analises_completas.items():
            stats = analise['estatisticas']
            nomes_turmas.append(nome_turma.replace(" - IA", ""))
            medias_turmas.append(stats['media_turma'])
            percentuais_risco.append(stats['percentual_risco'])
        
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            fig_medias = px.bar(
                x=nomes_turmas,
                y=medias_turmas,
                title="Média Geral por Turma",
                color=medias_turmas,
                color_continuous_scale='RdYlGn'
            )
            fig_medias.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_medias, use_container_width=True)
        
        with col_comp2:
            fig_risco = px.bar(
                x=nomes_turmas,
                y=percentuais_risco,
                title="Percentual de Alunos em Risco por Turma",
                color=percentuais_risco,
                color_continuous_scale='RdYlBu_r'
            )
            fig_risco.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_risco, use_container_width=True)

except FileNotFoundError:
    st.error("Arquivo de dados não encontrado!")
    st.info("Certifique-se de que o arquivo 'NOTAS BIMESTRAIS EPT 2º bimestre.xlsx' está na pasta 'dados/'")
except Exception as e:
    st.error(f"Erro ao processar os dados: {str(e)}")
    st.info("Verifique se todas as dependências estão instaladas e o arquivo Excel está no formato correto")

# Rodapé
st.markdown("---")
st.markdown("**EduRadar Scampini** - Sistema desenvolvido pelos alunos do 2º ano E - Turma de IA")
st.markdown("*Escola Estadual Padre José Scampini - Campo Grande/MS - 2025*")