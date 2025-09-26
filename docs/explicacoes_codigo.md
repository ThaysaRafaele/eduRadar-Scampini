# 📖 Explicações do Código

## Como o EduRadar Funciona - Explicação Simples

### 🧠 Conceitos Básicos que Vocês Já Conhecem

Vocês já sabem:
- **Variáveis**: `nome = "João"`
- **If/else**: `if nota < 6: print("Precisa estudar")`
- **While**: `while contador < 10:`

Agora vamos usar isso para resolver um problema real!

---

## 📊 Como Lemos os Dados do Excel

### O que fazemos:
```python
# 1. Abrimos o arquivo Excel
df = pd.read_excel("notas.xlsx", sheet_name="1º ano G - IA")

# 2. Pegamos cada linha (cada aluno)
linha_atual = 3  # Começar depois dos cabeçalhos
while linha_atual < len(df):
    linha = df.iloc[linha_atual]  # Pega a linha
    nome = linha.iloc[0]          # Primeira coluna = nome
    nota = linha.iloc[1]          # Segunda coluna = primeira nota
```

### Por que fazemos assim:
- **Excel** é como uma tabela gigante
- **Pandas** nos ajuda a ler essa tabela
- **While** percorre linha por linha
- **iloc[0]** significa "primeira coluna desta linha"

---

## 🔍 Como Analisamos o Risco

### Lógica simples que vocês entendem:
```python
def classificar_risco_aluno(media, total_faltas):
    # Se a média é muito baixa = PERIGO!
    if media < 5.0:
        return "ALTO RISCO"
    
    # Se a média é baixa = cuidado
    elif media < 6.0:
        return "RISCO MODERADO"
    
    # Se a média está ok, mas tem muitas faltas = atenção
    elif total_faltas > 15:
        return "RISCO MODERADO"
    
    # Se está tudo bem
    else:
        return "SITUAÇÃO OK"
```

### O que isso faz:
- Usa **if/elif/else** (que vocês já sabem!)
- Verifica primeiro a **média**
- Depois verifica as **faltas**
- Retorna uma **classificação**

---

## 🧮 Como Calculamos a Média

### Processo passo a passo:
```python
def calcular_media_aluno(notas_dict):
    notas_validas = []  # Lista vazia
    
    # Para cada nota do aluno
    for disciplina, nota in notas_dict.items():
        # Se a nota é um número válido
        if isinstance(nota, (int, float)) and nota > 0:
            notas_validas.append(nota)  # Adiciona na lista
    
    # Se tem pelo menos uma nota
    if len(notas_validas) > 0:
        soma = 0
        contador = 0
        
        # Somar todas as notas (usando while)
        while contador < len(notas_validas):
            soma = soma + notas_validas[contador]
            contador = contador + 1
        
        media = soma / len(notas_validas)
        return media
    else:
        return 0
```

### Por que assim:
- **Lista** para guardar só as notas válidas
- **While** para somar (vocês sabem fazer!)
- **Divisão** para calcular a média
- **If** para verificar se tem notas

---

## 📱 Como Criamos o Dashboard

### Streamlit = Mágica Simples
```python
import streamlit as st

# Título da página
st.title("EduRadar Scampini")

# Mostrar um número importante
st.metric("Total de Alunos", 209)

# Fazer um gráfico
fig = px.bar(x=["Alto Risco", "OK"], y=[10, 50])
st.plotly_chart(fig)
```

### Como funciona:
- **st.title()** = cria título bonito
- **st.metric()** = mostra número grande com destaque
- **st.plotly_chart()** = mostra gráfico interativo
- **Streamlit** transforma código em página web!

---

## 🏗️ Estrutura do Projeto (Como Organizamos)

### Por que dividir em arquivos:
```
leitura_dados.py    → Só lê o Excel
analise_risco.py    → Só calcula risco  
app.py             → Só faz a interface
```

### Vantagens:
- **Organização**: cada arquivo tem uma função
- **Trabalho em equipe**: cada pessoa pode trabalhar em um arquivo
- **Facilita debug**: se dá erro, sabemos onde procurar
- **Reuso**: podemos usar a mesma função em vários lugares

---

## 🎯 Conceitos Novos (Que Vamos Explicar Juntos)

### 1. Funções (def)
```python
def somar_numeros(a, b):
    resultado = a + b
    return resultado

# Como usar:
total = somar_numeros(5, 3)  # total = 8
```
- **def** = "definir uma função"
- **return** = "devolver um resultado"
- **Parâmetros** = informações que a função precisa

### 2. Dicionários
```python
aluno = {
    'nome': 'João',
    'nota': 8.5,
    'faltas': 2
}

print(aluno['nome'])  # Mostra: João
```
- **Chaves** entre aspas: 'nome', 'nota'
- **Valores** depois dos dois pontos: 'João', 8.5
- **Acesso** com aluno['chave']

### 3. For (mais simples que while às vezes)
```python
notas = [8, 7, 9, 6]

for nota in notas:
    print(nota)
```
- **For** percorre uma lista automaticamente
- **Mais fácil** que while quando sabemos o tamanho

---

## 💡 Dicas para Entender o Código

### 1. Leia os Comentários
```python
# Este comentário explica o que vem abaixo
nome = "João"  # Comentário na linha
```

### 2. Execute Linha por Linha
- Use **print()** para ver o que está acontecendo
- Teste pequenos pedaços primeiro

### 3. Não Tenham Medo de Erros
- **Erro** = Python tentando te ajudar
- **Leia a mensagem** de erro
- **Google** é seu amigo para erros

### 4. Usem Nomes Descritivos
```python
# BOM
media_aluno = 7.5
total_faltas = 3

# RUIM  
x = 7.5
y = 3
```

---

## 🏃‍♂️ Próximos Passos

### O que vamos fazer nas próximas reuniões:
1. **Instalar Python** no computador de vocês
2. **Executar** o código passo a passo
3. **Modificar** pequenas coisas para ver o que acontece
4. **Cada dupla** vai trabalhar com sua turma
5. **Criar melhorias** no dashboard

### Como vão aprender:
- **Fazendo**: mexer no código
- **Perguntando**: qualquer dúvida é válida
- **Testando**: tentar coisas novas
- **Colaborando**: ajudar os colegas

---

## 🤝 Como Vamos Trabalhar em Equipe

### GitHub = Nosso "Google Drive" do código
- **Todos** podem ver o código
- **Cada um** trabalha em sua parte
- **Integramos** tudo no final
- **Histórico** de todas as mudanças

### Divisão de Tarefas:
- **Matias + Pedro**: 1º ano G - IA
- **Luanna + ?**: 2º ano G - IA
- **Outros**: distribuir as outras turmas

### Objetivo Final:
- **Sistema funcionando** para a feira
- **Todos** entendendo como funciona
- **Apresentação** convincente
- **Possível premiação**! 🏆

---

*Lembrem-se: vocês não precisam entender tudo de uma vez. Vamos construir conhecimento aos poucos, sempre baseado no que já sabem!*