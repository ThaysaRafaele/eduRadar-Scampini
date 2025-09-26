# Módulo responsável pela análise e visualização dos dados melhorada

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AnalisadorDados:
    def __init__(self):
        self.cores_situacao = {
            'ALTO_RISCO': '#FF4B4B',      # Vermelho
            'RISCO_MODERADO': '#FFA500',   # Laranja
            'ATENCAO': '#FFD700',          # Amarelo
            'OK': '#00C851'                # Verde
        }
        self.labels_situacao = {
            'ALTO_RISCO': 'Alto Risco',
            'RISCO_MODERADO': 'Risco Moderado',
            'ATENCAO': 'Atenção',
            'OK': 'Situação OK'
        }

    def criar_resumo_geral(self, dados_processados):
        """
        Cria resumo geral com informações do bimestre
        """
        if not dados_processados:
            st.error("❌ Nenhum dado disponível para análise")
            return
        
        info_bimestre = dados_processados.get('info_bimestre', {})
        resumo = dados_processados.get('resumo_geral', {})
        
        # Cabeçalho com informação do bimestre
        st.title("📚 Resumo por Turma")
        
        # Mostrar qual bimestre está sendo analisado
        if info_bimestre:
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"📅 **Bimestre:** {info_bimestre.get('descricao', 'N/A')}")
            with col_info2:
                st.info(f"📊 **Turmas carregadas:** {info_bimestre.get('turmas_carregadas', 0)}")
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total de Alunos", 
                resumo.get('total_alunos', 0),
                help="Número total de alunos em todas as turmas de IA"
            )
        
        with col2:
            st.metric(
                "Alto Risco", 
                resumo.get('alunos_risco_alto', 0),
                delta=f"-{resumo.get('alunos_risco_alto', 0)}" if resumo.get('alunos_risco_alto', 0) > 0 else None,
                delta_color="inverse",
                help="Alunos com nota baixa e/ou muitas faltas"
            )
        
        with col3:
            st.metric(
                "Risco Moderado", 
                resumo.get('alunos_risco_moderado', 0),
                delta=f"-{resumo.get('alunos_risco_moderado', 0)}" if resumo.get('alunos_risco_moderado', 0) > 0 else None,
                delta_color="inverse",
                help="Alunos que precisam de acompanhamento"
            )
        
        with col4:
            percentual_sucesso = 0
            total = resumo.get('total_alunos', 0)
            if total > 0:
                alunos_ok = resumo.get('alunos_ok', 0) + resumo.get('alunos_atencao', 0)
                percentual_sucesso = round((alunos_ok / total) * 100, 1)
            
            st.metric(
                "% Situação Boa", 
                f"{percentual_sucesso}%",
                help="Percentual de alunos com situação OK ou que precisam apenas de atenção"
            )
        
        # Tabela resumo por turma
        self._criar_tabela_resumo_turmas(dados_processados)
    
    def _criar_tabela_resumo_turmas(self, dados_processados):
        """
        Cria tabela resumo por turma
        """
        st.subheader("📊 Detalhamento por Turma")
        
        turmas_dados = dados_processados.get('turmas', {})
        if not turmas_dados:
            st.warning("Nenhuma turma encontrada")
            return
        
        # Preparar dados para tabela
        tabela_dados = []
        
        for nome_turma, dados_turma in turmas_dados.items():
            stats = dados_turma['estatisticas']
            contadores = stats['contadores_situacao']
            
            tabela_dados.append({
                'Turma': nome_turma.replace(' - IA', ''),
                'Total Alunos': stats['total_alunos'],
                'Alto Risco': contadores['ALTO_RISCO'],
                'Risco Moderado': contadores['RISCO_MODERADO'],
                'Atenção': contadores['ATENCAO'],
                'Situação OK': contadores['OK'],
                'Média da Turma': stats['media_turma'],
                '% Risco': stats['percentual_risco']
            })
        
        # Criar DataFrame e mostrar
        df_resumo = pd.DataFrame(tabela_dados)
        
        # Estilizar tabela
        def colorir_percentual_risco(val):
            if val >= 50:
                return 'background-color: #ffebee'
            elif val >= 25:
                return 'background-color: #fff3e0'
            elif val >= 10:
                return 'background-color: #fffde7'
            else:
                return 'background-color: #e8f5e8'
        
        def colorir_media(val):
            if val < 5:
                return 'background-color: #ffebee; color: #c62828'
            elif val < 7:
                return 'background-color: #fff3e0; color: #ef6c00'
            else:
                return 'background-color: #e8f5e8; color: #2e7d32'
        
        # Aplicar estilos
        styled_df = df_resumo.style.applymap(
            colorir_percentual_risco, subset=['% Risco']
        ).applymap(
            colorir_media, subset=['Média da Turma']
        ).format({
            'Média da Turma': '{:.1f}',
            '% Risco': '{:.1f}%'
        })
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de barras das turmas
        self._criar_grafico_turmas(df_resumo)
    
    def _criar_grafico_turmas(self, df_resumo):
        """
        Cria gráfico de barras mostrando situação por turma
        """
        st.subheader("📊 Visualização por Turmas")
        
        # Preparar dados para gráfico empilhado
        fig = go.Figure()
        
        turmas = df_resumo['Turma']
        
        # Adicionar barras empilhadas
        fig.add_trace(go.Bar(
            name='Alto Risco',
            x=turmas,
            y=df_resumo['Alto Risco'],
            marker_color=self.cores_situacao['ALTO_RISCO']
        ))
        
        fig.add_trace(go.Bar(
            name='Risco Moderado',
            x=turmas,
            y=df_resumo['Risco Moderado'],
            marker_color=self.cores_situacao['RISCO_MODERADO']
        ))
        
        fig.add_trace(go.Bar(
            name='Atenção',
            x=turmas,
            y=df_resumo['Atenção'],
            marker_color=self.cores_situacao['ATENCAO']
        ))
        
        fig.add_trace(go.Bar(
            name='OK',
            x=turmas,
            y=df_resumo['Situação OK'],
            marker_color=self.cores_situacao['OK']
        ))
        
        fig.update_layout(
            barmode='stack',
            title='Distribuição de Alunos por Situação e Turma',
            xaxis_title='Turmas',
            yaxis_title='Número de Alunos',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def criar_analise_detalhada(self, dados_processados, turma_selecionada):
        """
        Cria análise detalhada de uma turma específica
        """
        if not dados_processados or not turma_selecionada:
            st.error("❌ Dados ou turma não disponível")
            return
        
        turmas_dados = dados_processados.get('turmas', {})
        info_bimestre = dados_processados.get('info_bimestre', {})
        
        if turma_selecionada not in turmas_dados:
            st.error(f"❌ Turma {turma_selecionada} não encontrada")
            return
        
        dados_turma = turmas_dados[turma_selecionada]
        alunos = dados_turma['alunos']
        stats = dados_turma['estatisticas']
        
        # Cabeçalho
        st.title(f"🔍 Análise Detalhada - {turma_selecionada.replace(' - IA', '')}")
        st.info(f"📅 **Bimestre:** {info_bimestre.get('descricao', 'N/A')}")
        
        # Métricas da turma
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Alunos", stats['total_alunos'])
        with col2:
            st.metric("Média da Turma", f"{stats['media_turma']:.1f}")
        with col3:
            st.metric("% em Risco", f"{stats['percentual_risco']:.1f}%")
        with col4:
            alunos_problema = stats['contadores_situacao']['ALTO_RISCO'] + stats['contadores_situacao']['RISCO_MODERADO']
            st.metric("Alunos Problemáticos", alunos_problema)
        
        # Análise por UC (matérias)
        self._criar_analise_por_uc(alunos)
        
        # Lista detalhada de alunos
        self._criar_lista_detalhada_alunos(alunos)
    
    def _criar_analise_por_uc(self, alunos):
        """
        Cria análise específica por UC (matéria)
        """
        st.subheader("📚 Análise por UC (Matérias)")
        
        # Coletar dados por UC
        dados_ucs = {'UCP 1': [], 'UCP 2': [], 'UCP 3': []}
        
        for aluno in alunos:
            for uc_nome, uc_dados in aluno['ucs'].items():
                if uc_dados['nota'] > 0:  # Só considerar notas lançadas
                    dados_ucs[uc_nome].append({
                        'nome': aluno['nome'],
                        'nota': uc_dados['nota'],
                        'faltas': uc_dados['faltas'],
                        'situacao': aluno['situacao_por_uc'][uc_nome]
                    })
        
        # Criar tabs para cada UC
        tabs = st.tabs(['UCP 1', 'UCP 2', 'UCP 3'])
        
        for i, (uc_nome, tab) in enumerate(zip(dados_ucs.keys(), tabs)):
            with tab:
                dados_uc = dados_ucs[uc_nome]
                
                if not dados_uc:
                    st.info(f"📝 Nenhuma nota lançada ainda para {uc_nome}")
                    continue
                
                # Estatísticas da UC
                notas = [d['nota'] for d in dados_uc]
                faltas = [d['faltas'] for d in dados_uc]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Média UC", f"{sum(notas)/len(notas):.1f}")
                with col2:
                    st.metric("Maior Nota", f"{max(notas):.1f}")
                with col3:
                    st.metric("Menor Nota", f"{min(notas):.1f}")
                with col4:
                    st.metric("Média Faltas", f"{sum(faltas)/len(faltas):.1f}")
                
                # Contar situações nesta UC
                contadores_uc = {'ALTO_RISCO': 0, 'RISCO_MODERADO': 0, 'ATENCAO': 0, 'OK': 0}
                for d in dados_uc:
                    contadores_uc[d['situacao']] += 1
                
                # Gráfico pizza da situação na UC
                fig_pizza = go.Figure(data=[go.Pie(
                    labels=[self.labels_situacao[k] for k in contadores_uc.keys()],
                    values=list(contadores_uc.values()),
                    marker_colors=[self.cores_situacao[k] for k in contadores_uc.keys()],
                    hole=0.3
                )])
                
                fig_pizza.update_layout(
                    title=f'Distribuição de Situações - {uc_nome}',
                    height=400
                )
                
                st.plotly_chart(fig_pizza, use_container_width=True)
                
                # Lista de alunos em risco nesta UC
                alunos_risco_uc = [d for d in dados_uc if d['situacao'] in ['ALTO_RISCO', 'RISCO_MODERADO']]
                if alunos_risco_uc:
                    st.subheader(f"⚠️ Alunos em Risco em {uc_nome}")
                    for aluno_risco in alunos_risco_uc:
                        situacao_cor = self.cores_situacao[aluno_risco['situacao']]
                        st.markdown(f"""
                        <div style="padding: 10px; margin: 5px; border-left: 5px solid {situacao_cor}; background-color: #f8f9fa;">
                            <strong>{aluno_risco['nome']}</strong><br>
                            📊 Nota: {aluno_risco['nota']:.1f} | 📅 Faltas: {aluno_risco['faltas']}<br>
                            🚨 Situação: {self.labels_situacao[aluno_risco['situacao']]}
                        </div>
                        """, unsafe_allow_html=True)

    def _criar_lista_detalhada_alunos(self, alunos):
        """
        Cria lista detalhada de todos os alunos
        """
        st.subheader("👥 Lista Completa de Alunos")
        
        # Filtros
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            situacao_filtro = st.selectbox(
                "Filtrar por situação:",
                ["Todos", "Alto Risco", "Risco Moderado", "Atenção", "OK"]
            )
        
        with col_filtro2:
            ordem_filtro = st.selectbox(
                "Ordenar por:",
                ["Nome", "Média", "Total de Faltas", "Situação"]
            )
        
        # Aplicar filtros
        alunos_filtrados = alunos.copy()
        
        if situacao_filtro != "Todos":
            mapa_filtro = {
                "Alto Risco": "ALTO_RISCO",
                "Risco Moderado": "RISCO_MODERADO", 
                "Atenção": "ATENCAO",
                "OK": "OK"
            }
            alunos_filtrados = [a for a in alunos_filtrados if a['situacao_geral'] == mapa_filtro[situacao_filtro]]
        
        # Aplicar ordenação
        if ordem_filtro == "Nome":
            alunos_filtrados.sort(key=lambda x: x['nome'])
        elif ordem_filtro == "Média":
            alunos_filtrados.sort(key=lambda x: x['media_geral'], reverse=True)
        elif ordem_filtro == "Total de Faltas":
            alunos_filtrados.sort(key=lambda x: x['total_faltas'], reverse=True)
        elif ordem_filtro == "Situação":
            ordem_situacao = ['ALTO_RISCO', 'RISCO_MODERADO', 'ATENCAO', 'OK']
            alunos_filtrados.sort(key=lambda x: ordem_situacao.index(x['situacao_geral']))
        
        # Mostrar resultados
        st.info(f"📊 Mostrando {len(alunos_filtrados)} de {len(alunos)} alunos")
        
        # Criar cards para cada aluno
        for aluno in alunos_filtrados:
            situacao_cor = self.cores_situacao[aluno['situacao_geral']]
            
            with st.expander(f"{aluno['nome']} - {self.labels_situacao[aluno['situacao_geral']]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📊 Notas por UC:**")
                    for uc_nome, uc_dados in aluno['ucs'].items():
                        situacao_uc = aluno['situacao_por_uc'][uc_nome]
                        cor_uc = self.cores_situacao[situacao_uc]
                        st.markdown(f"""
                        <div style="padding: 5px; margin: 2px; border-left: 3px solid {cor_uc};">
                            {uc_nome}: <strong>{uc_dados['nota']:.1f}</strong> (Faltas: {uc_dados['faltas']})
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.write("**📈 Resumo Geral:**")
                    st.write(f"Média Geral: **{aluno['media_geral']:.1f}**")
                    st.write(f"Total de Faltas: **{aluno['total_faltas']}**")
                    if aluno['projeto']['nota'] > 0:
                        st.write(f"Projeto: **{aluno['projeto']['nota']:.1f}** (Faltas: {aluno['projeto']['faltas']})")

    def criar_lista_alunos_risco(self, dados_processados):
        """
        Cria lista específica de alunos que necessitam atenção
        """
        if not dados_processados:
            st.error("❌ Nenhum dado disponível")
            return
        
        info_bimestre = dados_processados.get('info_bimestre', {})
        turmas_dados = dados_processados.get('turmas', {})
        
        # Cabeçalho
        st.title("⚠️ Alunos que Necessitam Atenção Especial")
        st.info(f"📅 **Bimestre:** {info_bimestre.get('descricao', 'N/A')}")
        
        # Coletar todos os alunos em risco
        alunos_risco = []
        
        for nome_turma, dados_turma in turmas_dados.items():
            for aluno in dados_turma['alunos']:
                if aluno['situacao_geral'] in ['ALTO_RISCO', 'RISCO_MODERADO']:
                    aluno_info = aluno.copy()
                    aluno_info['nome_turma'] = nome_turma.replace(' - IA', '')
                    
                    # Identificar UCs específicas em risco
                    ucs_risco = []
                    for uc_nome, situacao_uc in aluno['situacao_por_uc'].items():
                        if situacao_uc in ['ALTO_RISCO', 'RISCO_MODERADO']:
                            ucs_risco.append({
                                'uc': uc_nome,
                                'nota': aluno['ucs'][uc_nome]['nota'],
                                'faltas': aluno['ucs'][uc_nome]['faltas'],
                                'situacao': situacao_uc
                            })
                    
                    aluno_info['ucs_risco'] = ucs_risco
                    alunos_risco.append(aluno_info)
        
        if not alunos_risco:
            st.success("🎉 Nenhum aluno necessita atenção especial no momento!")
            return
        
        # Ordenar por gravidade
        ordem_gravidade = ['ALTO_RISCO', 'RISCO_MODERADO']
        alunos_risco.sort(key=lambda x: (ordem_gravidade.index(x['situacao_geral']), x['media_geral']))
        
        # Estatísticas gerais
        col1, col2, col3 = st.columns(3)
        
        alto_risco = len([a for a in alunos_risco if a['situacao_geral'] == 'ALTO_RISCO'])
        risco_moderado = len([a for a in alunos_risco if a['situacao_geral'] == 'RISCO_MODERADO'])
        
        with col1:
            st.metric("Total em Risco", len(alunos_risco))
        with col2:
            st.metric("Alto Risco", alto_risco, delta=f"-{alto_risco}", delta_color="inverse")
        with col3:
            st.metric("Risco Moderado", risco_moderado, delta=f"-{risco_moderado}", delta_color="inverse")
        
        st.markdown("---")
        
        # Lista detalhada
        for i, aluno in enumerate(alunos_risco, 1):
            situacao_cor = self.cores_situacao[aluno['situacao_geral']]
            
            st.markdown(f"""
            <div style="padding: 15px; margin: 10px 0; border-left: 5px solid {situacao_cor}; background-color: #f8f9fa; border-radius: 5px;">
                <h4 style="margin: 0; color: #333;">
                    <strong>{i}</strong> - {aluno['nome']} - {aluno['nome_turma']}
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**🎯 UCs em Risco:**")
                for uc_risco in aluno['ucs_risco']:
                    cor_uc = self.cores_situacao[uc_risco['situacao']]
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 5px 0; border-left: 3px solid {cor_uc}; background-color: #ffffff;">
                        <strong>{uc_risco['uc']}:</strong> Nota {uc_risco['nota']:.1f} | Faltas: {uc_risco['faltas']}<br>
                        <small>Situação: {self.labels_situacao[uc_risco['situacao']]}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.write("**📊 Resumo:**")
                st.write(f"Média Geral: **{aluno['media_geral']:.1f}**")
                st.write(f"Total de Faltas: **{aluno['total_faltas']}**")
                st.write(f"Classificação: **{self.labels_situacao[aluno['situacao_geral']]}**")
            
            if i < len(alunos_risco):
                st.markdown("---")

# Instância global para usar em outras partes do código
analisador_global = AnalisadorDados()