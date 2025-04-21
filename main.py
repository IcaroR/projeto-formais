import streamlit as st
from gerador import GeradorGLC
import os

st.set_page_config(page_title="Gerador de Cadeias", page_icon=":robot_face:")
st.title("Gerador de Cadeias para Gramáticas Livres de Contexto")

# Inicialização das variáveis de sessão
if 'forma_sentencial' not in st.session_state:
    st.session_state.forma_sentencial = ""
if 'derivacao' not in st.session_state:
    st.session_state.derivacao = []
if 'is_terminal' not in st.session_state:
    st.session_state.is_terminal = False
if 'derivacoes_geradas' not in st.session_state:
    st.session_state.derivacoes_geradas = set()
if 'modo_detalhado_ativo' not in st.session_state:
    st.session_state.modo_detalhado_ativo = False
if 'producao_selecionada' not in st.session_state:
    st.session_state.producao_selecionada = ""
if 'gerador_inicializado' not in st.session_state:
    st.session_state.gerador_inicializado = False
if 'gerador' not in st.session_state:
    st.session_state.gerador = None

# Função para reiniciar o modo detalhado
def reiniciar_modo_detalhado():
    st.session_state.forma_sentencial = st.session_state.gerador.inicial
    st.session_state.derivacao = []
    st.session_state.is_terminal = False
    st.session_state.modo_detalhado_ativo = True

# Função para aplicar uma produção selecionada
def aplicar_producao_callback():
    if not st.session_state.producao_selecionada:
        return
    
    # Obtém as opções de produção
    simbolo, pos_nao_terminal, producoes_possiveis, _, _ = st.session_state.gerador.gerar_opcoes_detalhado(st.session_state.forma_sentencial)
    
    # Extrai a produção da opção selecionada
    producao = st.session_state.producao_selecionada.split("→")[1].strip()
    
    # Aplica a produção
    nova_forma, simbolo, producao_escolhida = st.session_state.gerador.aplicar_producao(
        st.session_state.forma_sentencial, pos_nao_terminal, producao
    )
    
    # Adiciona o passo de derivação
    st.session_state.derivacao.append((st.session_state.forma_sentencial, simbolo, producao_escolhida, nova_forma))
    
    # Atualiza a forma sentencial
    st.session_state.forma_sentencial = nova_forma
    
    # Verifica se a forma sentencial só contém terminais
    st.session_state.is_terminal = not any(s in st.session_state.gerador.variaveis for s in nova_forma)

# Função para processar o arquivo carregado
def processar_arquivo_carregado(uploaded_file):
    if uploaded_file is not None:
        # Salva o arquivo carregado temporariamente
        with open("gramatica_temp.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Inicializa o gerador com o arquivo carregado
        st.session_state.gerador = GeradorGLC("gramatica_temp.txt")
        st.session_state.gerador_inicializado = True
        return True
    return False

# Upload do arquivo de gramática
uploaded_file = st.file_uploader("Faça upload do arquivo de gramática", type="txt")

# Processa o arquivo se foi carregado
if uploaded_file and (st.session_state.gerador is None or not st.session_state.gerador_inicializado):
    processar_arquivo_carregado(uploaded_file)

# Exibe informações da gramática se o gerador foi inicializado
if st.session_state.gerador_inicializado:
    # Exibe informações da gramática
    st.subheader("Informações da Gramática")
    st.write(f"Variáveis: {', '.join(st.session_state.gerador.variaveis)}")
    st.write(f"Símbolo inicial: {st.session_state.gerador.inicial}")
    st.write(f"Terminais: {', '.join(st.session_state.gerador.terminais)}")
    
    st.subheader("Produções:")
    for var, prods in st.session_state.gerador.producoes.items():
        st.write(f"{var} → {' | '.join(prods)}")
    
    # Seleção do modo
    modo = st.radio("Selecione o modo", ["Rápido", "Detalhado"])
    
    if modo == "Rápido":
        # Desativa o modo detalhado se estava ativo
        if st.session_state.modo_detalhado_ativo:
            st.session_state.modo_detalhado_ativo = False
        
        if st.button("Gerar Cadeia"):
            cadeia, derivacao = st.session_state.gerador.gerar_cadeia_rapido()
            
            if isinstance(cadeia, str) and not cadeia.startswith("Todas as"):
                st.success(f"Cadeia gerada: {cadeia}")
                
                st.subheader("Derivação mais à esquerda:")
                st.write(f"Forma inicial: {st.session_state.gerador.inicial}")
                
                # Verifica o formato da derivação
                if derivacao and isinstance(derivacao[0], tuple) and len(derivacao[0]) == 4:
                    # Formato novo: tuplas (forma_antiga, simbolo, producao, forma_nova)
                    for i, (forma_antiga, simbolo, producao, forma_nova) in enumerate(derivacao):
                        # Encontra a posição do símbolo na forma antiga
                        pos = forma_antiga.find(simbolo)
                        forma_destacada = forma_antiga[:pos] + '[' + simbolo + ']' + forma_antiga[pos+1:]
                        st.write(f"Passo {i+1}: {forma_destacada} => {forma_nova} (substituindo [{simbolo}] por {producao})")
                else:
                    # Formato antigo ou outro formato
                    for i, passo in enumerate(derivacao):
                        st.write(f"Passo {i+1}: {passo}")
            else:
                st.warning(cadeia)  # Mensagem de que todas as derivações foram mostradas
    else:  # Modo Detalhado
        # Botão para iniciar/reiniciar o modo detalhado
        if st.button("Iniciar Derivação Detalhada"):
            reiniciar_modo_detalhado()
        
        # Se o modo detalhado não está ativo, ativa-o
        if not st.session_state.modo_detalhado_ativo and modo == "Detalhado":
            reiniciar_modo_detalhado()
        
        # Se o modo detalhado está ativo
        if st.session_state.modo_detalhado_ativo:
            st.subheader("Derivação Detalhada")
            
            # Exibe a forma sentencial atual
            st.markdown(f"**Forma sentencial atual:** {st.session_state.forma_sentencial}")
            
            # Se a forma sentencial não é terminal
            if not st.session_state.is_terminal:
                # Obtém as opções de produção
                simbolo, pos_nao_terminal, producoes_possiveis, forma_destacada, _ = st.session_state.gerador.gerar_opcoes_detalhado(st.session_state.forma_sentencial)
                
                # Exibe a forma sentencial com destaque
                st.markdown(f"**Forma sentencial com destaque:** {forma_destacada}")
                
                # Cria um dropdown para selecionar a produção
                st.markdown(f"**Escolha uma produção para o símbolo '{simbolo}':**")
                
                # Formata as opções para o dropdown
                opcoes = [f"{simbolo} → {prod}" for prod in producoes_possiveis]
                st.selectbox(
                    "Produções disponíveis", 
                    opcoes, 
                    key="producao_selecionada"
                )
                
                # Botão para aplicar a produção
                st.button("Aplicar Produção", on_click=aplicar_producao_callback)
            else:
                st.success(f"Derivação completa! Cadeia gerada: {st.session_state.forma_sentencial}")
            
            # Exibe os passos da derivação
            if st.session_state.derivacao:
                st.subheader("Passos da Derivação:")
                st.write(f"Forma inicial: {st.session_state.gerador.inicial}")
                
                for i, (forma_antiga, simbolo, producao, forma_nova) in enumerate(st.session_state.derivacao):
                    # Encontra a posição do símbolo na forma antiga
                    pos = forma_antiga.find(simbolo)
                    forma_destacada = forma_antiga[:pos] + '[' + simbolo + ']' + forma_antiga[pos+1:]
                    st.write(f"Passo {i+1}: {forma_destacada} => {forma_nova} (substituindo [{simbolo}] por {producao})")
else:
    st.info("Faça o upload de um arquivo de gramática para começar.")
    st.markdown("""
    ### Formato do arquivo:
    ```
    variaveis:S,A,B
    inicial:S
    terminais:a,b,c,d
    producoes
    S: aA
    S: bB
    A: epsilon
    B: c
    ```
    """)
    
    # Exemplo de uso
    st.subheader("Exemplo de Uso:")
    st.markdown("""
    1. Faça o upload de um arquivo de gramática no formato especificado acima.
    2. Escolha o modo de derivação:
       - **Modo Rápido**: Gera automaticamente uma cadeia e mostra a derivação completa.
       - **Modo Detalhado**: Permite que você escolha cada produção usando menus dropdown.
    3. No modo detalhado, você verá a forma sentencial atual com o não-terminal mais à esquerda destacado.
    4. Selecione uma produção no menu dropdown e clique em "Aplicar Produção".
    5. Continue até obter uma cadeia composta apenas por símbolos terminais.
    """)
