import streamlit as st

class GeradorGLC:
    def __init__(self, arquivo):
        self.variaveis = []
        self.terminais = []
        self.producoes = {}
        self.inicial = None
        self.derivacoes_geradas = set()  # Conjunto para armazenar derivações já geradas
        
        self.ler_gramatica(arquivo)
        
    def ler_gramatica(self, arquivo):
        """
        Lê a gramática a partir de um arquivo com o formato especificado.
        """
        with open(arquivo, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            
            # Parse das variáveis, terminais e produção inicial
            for line in lines:
                if line.startswith('variaveis:'):
                    self.variaveis = line.split(':', 1)[1].split(',')
                elif line.startswith('inicial:'):
                    self.inicial = line.split(':', 1)[1].strip()
                elif line.startswith('terminais:'):
                    self.terminais = line.split(':', 1)[1].split(',')
                elif line == 'producoes':
                    # Marca o início das produções
                    continue
                elif ':' in line:
                    # Linha de produção
                    left, right = line.split(':', 1)
                    left = left.strip()
                    
                    # Cada produção deve estar em uma linha diferente
                    if left not in self.producoes:
                        self.producoes[left] = []
                    
                    # Separa as produções por vírgula e adiciona cada uma individualmente
                    producoes_separadas = right.strip().split(',')
                    for producao in producoes_separadas:
                        self.producoes[left].append(producao.strip())

    def gerar_cadeia_rapido(self):
        """
        Gera uma cadeia no modo rápido, mostrando a derivação mais à esquerda.
        Não repete derivações já mostradas anteriormente.
        """
        # Tentamos gerar uma derivação que ainda não foi mostrada
        max_tentativas = 100  # Limite para evitar loop infinito
        for _ in range(max_tentativas):
            cadeia, derivacao_passos = self._gerar_mais_a_esquerda(self.inicial)
            
            # Extrair apenas a cadeia final
            if derivacao_passos and len(derivacao_passos) > 1 and isinstance(derivacao_passos[-1], tuple) and len(derivacao_passos[-1]) == 4:
                cadeia = derivacao_passos[-1][3]  # Última forma sentencial
            elif derivacao_passos and not isinstance(derivacao_passos[0], tuple):
                # Se não há derivação (só o símbolo inicial), retorna o símbolo inicial
                cadeia = derivacao_passos[0]
            
            # Convertemos a derivação em uma string para poder armazená-la no conjunto
            derivacao_str = str(derivacao_passos)
            
            # Se esta derivação ainda não foi mostrada, a retornamos
            if derivacao_str not in self.derivacoes_geradas:
                self.derivacoes_geradas.add(derivacao_str)
                return cadeia, derivacao_passos
        
        # Se todas as derivações possíveis já foram mostradas
        return "Todas as derivações possíveis já foram mostradas.", []

    def _gerar_mais_a_esquerda(self, forma_sentencial, derivacao=None):
        """
        Gera uma cadeia com a derivação mais à esquerda.
        Recebe uma forma sentencial e retorna a cadeia gerada e a derivação completa.
        """
        if derivacao is None:
            derivacao = [forma_sentencial]
        
        # Se não há não-terminais, retornamos a forma sentencial como está
        if not any(simbolo in self.variaveis for simbolo in forma_sentencial):
            return forma_sentencial, derivacao
        
        # Encontra o não-terminal mais à esquerda
        pos_nao_terminal = -1
        for i, simbolo in enumerate(forma_sentencial):
            if simbolo in self.variaveis:
                pos_nao_terminal = i
                break
        
        if pos_nao_terminal == -1:  # Não há não-terminais
            return forma_sentencial, derivacao
        
        # Obtém o símbolo não-terminal a ser substituído
        simbolo = forma_sentencial[pos_nao_terminal]
        
        # Obtém as produções possíveis para o símbolo
        producoes_possiveis = self.producoes.get(simbolo, [])
        if not producoes_possiveis:
            raise ValueError(f"Não há produções possíveis para o símbolo {simbolo}")
        
        # Escolhe uma produção de forma sistemática (não aleatória)
        import random
        producao = producoes_possiveis[random.randint(0, len(producoes_possiveis) - 1)]
        
        # Substitui o não-terminal pela produção escolhida
        if producao == "epsilon":
            nova_forma = forma_sentencial[:pos_nao_terminal] + forma_sentencial[pos_nao_terminal+1:]
        else:
            nova_forma = forma_sentencial[:pos_nao_terminal] + producao + forma_sentencial[pos_nao_terminal+1:]
        
        # Adiciona a nova forma sentencial à derivação
        derivacao.append((forma_sentencial, simbolo, producao, nova_forma))
        
        # Continua a derivação recursivamente
        return self._gerar_mais_a_esquerda(nova_forma, derivacao)
    
    def gerar_cadeia_detalhado(self):
        """
        Gera uma cadeia no modo detalhado, permitindo que o usuário escolha as produções.
        """
        # Inicia a derivação com o símbolo inicial
        forma_sentencial = self.inicial
        derivacao = []
        
        print(f"\nModo Detalhado - Derivação mais à esquerda")
        print(f"Forma sentencial inicial: {forma_sentencial}")
        
        # Enquanto houver não-terminais na forma sentencial
        while any(simbolo in self.variaveis for simbolo in forma_sentencial):
            # Encontra o não-terminal mais à esquerda
            pos_nao_terminal = -1
            for i, simbolo in enumerate(forma_sentencial):
                if simbolo in self.variaveis:
                    pos_nao_terminal = i
                    break
            
            if pos_nao_terminal == -1:
                break  # Não há mais não-terminais
            
            simbolo = forma_sentencial[pos_nao_terminal]
            producoes_possiveis = self.producoes.get(simbolo, [])
            
            if not producoes_possiveis:
                raise ValueError(f"Não há produções possíveis para o símbolo {simbolo}")
            
            # Destaca o símbolo não-terminal a ser substituído
            forma_destacada = forma_sentencial[:pos_nao_terminal] + '[' + simbolo + ']' + forma_sentencial[pos_nao_terminal+1:]
            print(f"\nForma sentencial atual (com destaque): {forma_destacada}")
            
            # Exibe as opções para o usuário
            print(f"Escolha uma produção para o símbolo '{simbolo}':")
            for i, prod in enumerate(producoes_possiveis):
                print(f"{i + 1}. {simbolo} -> {prod}")
            
            # Obtém a escolha do usuário
            escolha = int(input(f"Digite o número da produção (1-{len(producoes_possiveis)}): "))
            producao_escolhida = producoes_possiveis[escolha - 1]
            
            # Substitui o não-terminal pela produção escolhida
            if producao_escolhida == "epsilon":
                nova_forma = forma_sentencial[:pos_nao_terminal] + forma_sentencial[pos_nao_terminal+1:]
            else:
                nova_forma = forma_sentencial[:pos_nao_terminal] + producao_escolhida + forma_sentencial[pos_nao_terminal+1:]
            
            # Adiciona o passo de derivação
            derivacao.append((forma_sentencial, simbolo, producao_escolhida, nova_forma))
            
            # Atualiza a forma sentencial
            forma_sentencial = nova_forma
            print(f"Nova forma sentencial: {forma_sentencial}")
        
        print("\nDerivação completa:")
        print(f"Forma inicial: {self.inicial}")
        for i, (forma_antiga, simbolo, producao, forma_nova) in enumerate(derivacao):
            # Encontra a posição do símbolo na forma antiga
            pos = forma_antiga.find(simbolo)
            forma_destacada = forma_antiga[:pos] + '[' + simbolo + ']' + forma_antiga[pos+1:]
            print(f"Passo {i+1}: {forma_destacada} => {forma_nova} (substituindo [{simbolo}] por {producao})")
        
        return forma_sentencial
    
    def _gerar_detalhado(self, simbolo, derivacao):
        """
        Método auxiliar para o modo detalhado (não utilizado na implementação atual).
        """
        pass


# Exemplo de uso
if __name__ == "__main__":
    arquivo = 'gramatica.txt'  # Caminho para o arquivo da gramática
    gerador = GeradorGLC(arquivo)
    
    while True:
        print("\n==== Gerador de Cadeias para Gramáticas Livres de Contexto ====")
        print("1. Modo Rápido")
        print("2. Modo Detalhado")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção (1-3): ")
        
        if opcao == "1":
            # Modo rápido
            print("\nModo Rápido:")
            cadeia, derivacao = gerador.gerar_cadeia_rapido()
            if isinstance(cadeia, str) and not cadeia.startswith("Todas as"):
                print("Cadeia gerada:", cadeia)
                print("\nDerivação mais à esquerda:")
                print(f"Forma inicial: {gerador.inicial}")
                # Verifica o formato da derivação
                if derivacao and isinstance(derivacao[0], tuple) and len(derivacao[0]) == 4:
                    # Formato novo: tuplas (forma_antiga, simbolo, producao, forma_nova)
                    for i, (forma_antiga, simbolo, producao, forma_nova) in enumerate(derivacao):
                        # Encontra a posição do símbolo na forma antiga
                        pos = forma_antiga.find(simbolo)
                        forma_destacada = forma_antiga[:pos] + '[' + simbolo + ']' + forma_antiga[pos+1:]
                        print(f"Passo {i+1}: {forma_destacada} => {forma_nova} (substituindo [{simbolo}] por {producao})")
                else:
                    # Formato antigo ou outro formato
                    for i, passo in enumerate(derivacao):
                        print(f"  Passo {i+1}: {passo}")
            else:
                print(cadeia)  # Mensagem de que todas as derivações foram mostradas
            
            input("\nPressione Enter para continuar...")
            
        elif opcao == "2":
            # Modo detalhado
            cadeia_detalhada = gerador.gerar_cadeia_detalhado()
            print("\nCadeia final gerada:", cadeia_detalhada)
            input("\nPressione Enter para continuar...")
            
        elif opcao == "3":
            print("Saindo...")
            break
            
        else:
            print("Opção inválida. Tente novamente.")
