# Módulo responsável pelo upload e gestão de arquivos

import streamlit as st
import tempfile
import os
import shutil
from datetime import datetime

def criar_interface_upload():
    """
    Cria interface de upload na sidebar
    Retorna o caminho do arquivo a ser usado
    """
    st.sidebar.markdown("---")
    st.sidebar.title("📁 Gestão de Arquivos")
    
    # Mostrar arquivo atual
    st.sidebar.info("📂 Arquivo atual: NOTAS BIMESTRAIS EPT 2º bimestre.xlsx")
    
    # Upload de novo arquivo
    novo_arquivo = st.sidebar.file_uploader(
        "📤 Upload nova planilha:",
        type=['xlsx'],
        help="Selecione um arquivo Excel (.xlsx) com as notas bimestrais"
    )
    
    caminho_arquivo = "dados/NOTAS BIMESTRAIS EPT 2º bimestre.xlsx"  # Arquivo padrão
    
    if novo_arquivo is not None:
        # Mostrar informações do arquivo
        st.sidebar.success(f"✅ Arquivo carregado: {novo_arquivo.name}")
        st.sidebar.write(f"📊 Tamanho: {formatar_tamanho_arquivo(novo_arquivo.size)}")
        st.sidebar.write(f"🕐 Enviado: {datetime.now().strftime('%H:%M:%S')}")
        
        # Botões de ação
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            usar_novo = st.button("🔄 Usar Nova", help="Usar arquivo enviado")
        
        with col2:
            salvar_novo = st.button("💾 Salvar", help="Salvar na pasta dados/")
        
        # Se clicou para usar o arquivo novo
        if usar_novo:
            caminho_arquivo = salvar_arquivo_temporario(novo_arquivo)
            st.sidebar.success("📈 Usando arquivo enviado!")
            st.sidebar.balloons()  # Efeito visual divertido
        
        # Se clicou para salvar permanentemente
        if salvar_novo:
            if salvar_arquivo_permanente(novo_arquivo):
                st.sidebar.success("💾 Arquivo salvo com sucesso!")
                st.sidebar.balloons()
            else:
                st.sidebar.error("❌ Erro ao salvar arquivo")
    
    return caminho_arquivo

def formatar_tamanho_arquivo(bytes):
    """
    Converte bytes para formato legível
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{round(bytes / 1024, 1)} KB"
    else:
        return f"{round(bytes / (1024 * 1024), 1)} MB"

def salvar_arquivo_temporario(arquivo_uploaded):
    """
    Salva arquivo em pasta temporária para uso imediato
    """
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(arquivo_uploaded.getbuffer())
            return tmp_file.name
    except Exception as e:
        st.sidebar.error(f"Erro ao criar arquivo temporário: {e}")
        return None

def salvar_arquivo_permanente(arquivo_uploaded):
    """
    Salva arquivo na pasta dados/ substituindo o atual
    """
    try:
        # Criar backup do arquivo atual
        arquivo_atual = "dados/NOTAS BIMESTRAIS EPT 2º bimestre.xlsx"
        backup_nome = f"dados/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        if os.path.exists(arquivo_atual):
            shutil.copy2(arquivo_atual, backup_nome)
            st.sidebar.info(f"📋 Backup criado: {os.path.basename(backup_nome)}")
        
        # Salvar novo arquivo
        with open(arquivo_atual, "wb") as f:
            f.write(arquivo_uploaded.getbuffer())
        
        return True
        
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar: {e}")
        return False

def listar_backups():
    """
    Lista arquivos de backup disponíveis
    """
    try:
        pasta_dados = "dados/"
        backups = []
        
        if os.path.exists(pasta_dados):
            arquivos = os.listdir(pasta_dados)
            for arquivo in arquivos:
                if arquivo.startswith("backup_") and arquivo.endswith(".xlsx"):
                    caminho_completo = os.path.join(pasta_dados, arquivo)
                    tamanho = os.path.getsize(caminho_completo)
                    backups.append({
                        'nome': arquivo,
                        'tamanho': formatar_tamanho_arquivo(tamanho),
                        'caminho': caminho_completo
                    })
        
        return backups
        
    except Exception:
        return []

def mostrar_historico_arquivos():
    """
    Mostra histórico de arquivos de backup na sidebar
    """
    backups = listar_backups()
    
    if len(backups) > 0:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📚 Histórico de Arquivos")
        
        # Mostrar só os 5 mais recentes
        for backup in backups[-5:]:
            data_str = backup['nome'].replace('backup_', '').replace('.xlsx', '')
            try:
                data_formatada = datetime.strptime(data_str, '%Y%m%d_%H%M%S').strftime('%d/%m/%Y %H:%M')
            except:
                data_formatada = data_str
                
            st.sidebar.text(f"📅 {data_formatada}")
            st.sidebar.caption(f"Tamanho: {backup['tamanho']}")
        
        if len(backups) > 5:
            st.sidebar.caption(f"+ {len(backups) - 5} arquivos mais antigos")

def validar_estrutura_arquivo(caminho_arquivo):
    """
    Valida se o arquivo tem a estrutura esperada
    Retorna True se válido, False se inválido
    """
    try:
        import pandas as pd
        
        # Lista das turmas que devemos encontrar
        turmas_esperadas = [
            "1º ano G - IA", "2º ano G - IA", "1º ano E - IA", 
            "2º ano D - IA", "2º ano E - IA", "3º ano E -IA"
        ]
        
        # Verificar se o arquivo pode ser lido
        excel_file = pd.ExcelFile(caminho_arquivo)
        turmas_encontradas = excel_file.sheet_names
        
        # Contar quantas turmas de IA encontramos
        turmas_ia_encontradas = []
        for turma in turmas_esperadas:
            if turma in turmas_encontradas:
                turmas_ia_encontradas.append(turma)
        
        # Retornar resultado da validação
        return {
            'valido': len(turmas_ia_encontradas) >= 3,  # Pelo menos 3 turmas
            'turmas_encontradas': len(turmas_ia_encontradas),
            'total_planilhas': len(turmas_encontradas),
            'detalhes': turmas_ia_encontradas
        }
        
    except Exception as e:
        return {
            'valido': False,
            'erro': str(e)
        }

def mostrar_validacao_arquivo(caminho_arquivo):
    """
    Mostra status de validação do arquivo na sidebar
    """
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        validacao = validar_estrutura_arquivo(caminho_arquivo)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("✅ Status do Arquivo")
        
        if validacao['valido']:
            st.sidebar.success("📊 Arquivo válido!")
            st.sidebar.info(f"🎯 {validacao['turmas_encontradas']} turmas de IA encontradas")
            
            # Mostrar detalhes das turmas
            if 'detalhes' in validacao:
                st.sidebar.caption("Turmas disponíveis:")
                for turma in validacao['detalhes']:
                    st.sidebar.caption(f"• {turma}")
        else:
            st.sidebar.warning("⚠️ Arquivo com problemas")
            if 'erro' in validacao:
                st.sidebar.error(f"Erro: {validacao['erro']}")
            else:
                st.sidebar.info(f"Turmas IA: {validacao.get('turmas_encontradas', 0)}")