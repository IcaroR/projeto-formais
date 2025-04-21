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
        Usa uma abordagem de busca em largura para gerar cadeias em ordem crescente de complexidade.
        Não repete derivações já mostradas anteriormente.
        """
        import collections
        
        # Fila para busca em largura
        fila = collections.deque()
        
        # Adiciona o símbolo inicial à fila
        # Cada item da fila é uma tupla (forma_sentencial, derivação)
        fila.append((self.inicial, []))
        
        # Conjunto para rastrear formas sentenciais já visitadas
        visitados = set([self.inicial])
        
        # Contador para limitar o número de iterações
        contador = 0
        max_iteracoes = 1000
        
        while fila and contador < max_iteracoes:
            # Obtém a próxima forma sentencial e sua derivação
            forma_atual, derivacao_atual = fila.popleft()
            contador += 1
            
            # Verifica se a forma sentencial contém apenas terminais
            if not any(simbolo in self.variaveis for simbolo in forma_atual):
                # Encontramos uma cadeia terminal que ainda não foi mostrada
                derivacao_str = str(derivacao_atual)
                if derivacao_str not in self.derivacoes_geradas:
                    self.derivacoes_geradas.add(derivacao_str)
                    return forma_atual, derivacao_atual
            
            # Encontra o não-terminal mais à esquerda
            pos_nao_terminal = -1
            for i, simbolo in enumerate(forma_atual):
                if simbolo in self.variaveis:
                    pos_nao_terminal = i
                    break
            
            if pos_nao_terminal == -1:
                continue  # Não há não-terminais, mas já verificamos acima
            
            # Obtém o símbolo não-terminal a ser substituído
            simbolo = forma_atual[pos_nao_terminal]
            
            # Obtém as produções possíveis para o símbolo
            producoes_possiveis = self.producoes.get(simbolo, [])
            
            # Para cada produção possível, gera uma nova forma sentencial
            for producao in producoes_possiveis:
                # Substitui o não-terminal pela produção
                if producao == "epsilon":
                    nova_forma = forma_atual[:pos_nao_terminal] + forma_atual[pos_nao_terminal+1:]
                else:
                    nova_forma = forma_atual[:pos_nao_terminal] + producao + forma_atual[pos_nao_terminal+1:]
                
                # Se esta forma sentencial ainda não foi visitada, adiciona à fila
                if nova_forma not in visitados:
                    visitados.add(nova_forma)
                    
                    # Cria uma cópia da derivação atual e adiciona o novo passo
                    nova_derivacao = derivacao_atual.copy()
                    nova_derivacao.append((forma_atual, simbolo, producao, nova_forma))
                    
                    # Adiciona a nova forma sentencial e sua derivação à fila
                    fila.append((nova_forma, nova_derivacao))
        
        # Se não encontramos nenhuma nova cadeia terminal
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
        
    def gerar_opcoes_detalhado(self, forma_sentencial):
        """
        Retorna as opções de produção para o não-terminal mais à esquerda na forma sentencial atual.
        Usado para implementação do modo detalhado em interfaces web.
        
        Retorna:
            - simbolo: O símbolo não-terminal a ser substituído
            - pos_nao_terminal: A posição do símbolo na forma sentencial
            - producoes_possiveis: Lista de produções possíveis para o símbolo
            - forma_destacada: A forma sentencial com o símbolo destacado
            - is_terminal: True se a forma sentencial só contém terminais
        """
        # Verifica se a forma sentencial só contém terminais
        if not any(simbolo in self.variaveis for simbolo in forma_sentencial):
            return None, -1, [], forma_sentencial, True
        
        # Encontra o não-terminal mais à esquerda
        pos_nao_terminal = -1
        for i, simbolo in enumerate(forma_sentencial):
            if simbolo in self.variaveis:
                pos_nao_terminal = i
                break
        
        if pos_nao_terminal == -1:  # Não há não-terminais
            return None, -1, [], forma_sentencial, True
        
        # Obtém o símbolo não-terminal a ser substituído
        simbolo = forma_sentencial[pos_nao_terminal]
        producoes_possiveis = self.producoes.get(simbolo, [])
        
        # Destaca o símbolo não-terminal a ser substituído
        forma_destacada = forma_sentencial[:pos_nao_terminal] + '[' + simbolo + ']' + forma_sentencial[pos_nao_terminal+1:]
        
        return simbolo, pos_nao_terminal, producoes_possiveis, forma_destacada, False
        
    def aplicar_producao(self, forma_sentencial, pos_nao_terminal, producao_escolhida):
        """
        Aplica a produção escolhida à forma sentencial atual.
        
        Retorna:
            - nova_forma: A nova forma sentencial após a substituição
            - simbolo: O símbolo que foi substituído
            - producao_escolhida: A produção que foi aplicada
        """
        simbolo = forma_sentencial[pos_nao_terminal]
        
        # Substitui o não-terminal pela produção escolhida
        if producao_escolhida == "epsilon":
            nova_forma = forma_sentencial[:pos_nao_terminal] + forma_sentencial[pos_nao_terminal+1:]
        else:
            nova_forma = forma_sentencial[:pos_nao_terminal] + producao_escolhida + forma_sentencial[pos_nao_terminal+1:]
            
        return nova_forma, simbolo, producao_escolhida


# Exemplo de uso
if __name__ == "__main__":
    arquivo = 'gramatica_teste.txt'  # Caminho para o arquivo da gramática
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
