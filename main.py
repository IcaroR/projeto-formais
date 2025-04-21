import streamlit as st
from gerador import GeradorGLC
import os

st.set_page_config(page_title="Gerador de Cadeias", page_icon=":robot_face:")
st.title("Gerador de Cadeias para Gramáticas Livres de Contexto")

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
    
    if st.button("Gerar Cadeia"):
        if modo == "Rápido":
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
        else:
            # Modo detalhado não é adequado para interface web
            # pois requer interação do usuário a cada passo
            st.warning("O modo detalhado requer interação a cada passo e não está disponível na interface web.")
            st.info("Use o modo rápido ou execute o programa via terminal para usar o modo detalhado.")
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
