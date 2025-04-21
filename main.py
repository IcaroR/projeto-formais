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
if 'modo_detalhado_ativo' not in st.session_state:
    st.session_state.modo_detalhado_ativo = False

# Função para reiniciar o modo detalhado
def reiniciar_modo_detalhado(simbolo_inicial):
    st.session_state.forma_sentencial = simbolo_inicial
    st.session_state.derivacao = []
    st.session_state.is_terminal = False
    st.session_state.modo_detalhado_ativo = True

# Função para aplicar uma produção selecionada
def aplicar_producao_callback(gerador, forma_sentencial, pos_nao_terminal, producao):
    nova_forma, simbolo, producao_escolhida = gerador.aplicar_producao(forma_sentencial, pos_nao_terminal, producao)
    
    # Adiciona o passo de derivação
    st.session_state.derivacao.append((forma_sentencial, simbolo, producao_escolhida, nova_forma))
    
    # Atualiza a forma sentencial
    st.session_state.forma_sentencial = nova_forma
    
    # Verifica se a forma sentencial só contém terminais
    st.session_state.is_terminal = not any(s in gerador.variaveis for s in nova_forma)

# Upload do arquivo de gramática
upload_file = st.file_uploader("Faça upload do arquivo de gramática", type="txt")

# Inicialização do gerador
gerador = None

if upload_file is not None:
    # Salva o arquivo carregado temporariamente
    with open("gramatica_temp.txt", "wb") as f:
        f.write(upload_file.getbuffer())
    
    # Inicializa o gerador com o arquivo carregado
    gerador = GeradorGLC("gramatica_temp.txt")
    
    # Exibe informações da gramática
    st.subheader("Informações da Gramática")
    st.write(f"Variáveis: {', '.join(gerador.variaveis)}")
    st.write(f"Símbolo inicial: {gerador.inicial}")
    st.write(f"Terminais: {', '.join(gerador.terminais)}")
    
    st.subheader("Produções:")
    for var, prods in gerador.producoes.items():
        st.write(f"{var} → {' | '.join(prods)}")
    
    # Seleção do modo
    modo = st.radio("Selecione o modo", ["Rápido", "Detalhado"])
    
    if modo == "Rápido":
        # Desativa o modo detalhado se estava ativo
        if st.session_state.modo_detalhado_ativo:
            st.session_state.modo_detalhado_ativo = False
        
        if st.button("Gerar Cadeia"):
            cadeia, derivacao = gerador.gerar_cadeia_rapido()
            
            if isinstance(cadeia, str) and not cadeia.startswith("Todas as"):
                st.success(f"Cadeia gerada: {cadeia}")
                
                st.subheader("Derivação mais à esquerda:")
                st.write(f"Forma inicial: {gerador.inicial}")
                
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
        if st.button("Iniciar Derivação Detalhada") or not st.session_state.modo_detalhado_ativo:
            reiniciar_modo_detalhado(gerador.inicial)
        
        # Se o modo detalhado está ativo
        if st.session_state.modo_detalhado_ativo:
            st.subheader("Derivação Detalhada")
            
            # Exibe a forma sentencial atual
            st.markdown(f"**Forma sentencial atual:** {st.session_state.forma_sentencial}")
            
            # Se a forma sentencial não é terminal
            if not st.session_state.is_terminal:
                # Obtém as opções de produção
                simbolo, pos_nao_terminal, producoes_possiveis, forma_destacada, _ = gerador.gerar_opcoes_detalhado(st.session_state.forma_sentencial)
                
                # Exibe a forma sentencial com destaque
                st.markdown(f"**Forma sentencial com destaque:** {forma_destacada}")
                
                # Cria um dropdown para selecionar a produção
                st.markdown(f"**Escolha uma produção para o símbolo '{simbolo}':**")
                
                # Formata as opções para o dropdown
                opcoes = [f"{simbolo} → {prod}" for prod in producoes_possiveis]
                producao_selecionada = st.selectbox("Produções disponíveis", opcoes, key="producao_dropdown")
                
                # Extrai a produção da opção selecionada
                producao = producao_selecionada.split("→")[1].strip()
                
                # Botão para aplicar a produção
                if st.button("Aplicar Produção"):
                    aplicar_producao_callback(gerador, st.session_state.forma_sentencial, pos_nao_terminal, producao)
            else:
                st.success(f"Derivação completa! Cadeia gerada: {st.session_state.forma_sentencial}")
            
            # Exibe os passos da derivação
            if st.session_state.derivacao:
                st.subheader("Passos da Derivação:")
                st.write(f"Forma inicial: {gerador.inicial}")
                
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
