import math
import numpy as np 
from dataclasses import dataclass

@dataclass
class Objeto: 
   id: int
   tipo: int
   v1: float
   v2: float

@dataclass
class Agente:
   indice: int
   carregando: Objeto = None 

def print_atual(n, m, matriz_placa: np.ndarray) -> None: 
    for i in range(n):
        for j in range(m):
            print(matriz_placa[i][j], end = "")
        print()
    return

def carregar_dataset(nome_arquivo: str) -> list:
    vetor_objetos = []
    with open(nome_arquivo, "r") as arquivo:
        for indice, linha in enumerate(arquivo):
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            linha = linha.replace(',', ' ')
            dados = linha.split()
            if len(dados) < 3:
                continue

            valor1 = float(dados[0])
            valor2 = float(dados[1])
            valor_tipo = int(float(dados[2]))

            novo_objeto = Objeto(id=indice, v1=valor1, v2=valor2, tipo=valor_tipo)
            vetor_objetos.append(novo_objeto)
            
    return vetor_objetos

def normalizar_dados(lista_objetos: list) -> None:
    if not lista_objetos:
        return

    valores_v1 = [obj.v1 for obj in lista_objetos]
    valores_v2 = [obj.v2 for obj in lista_objetos]

    min_v1, max_v1 = min(valores_v1), max(valores_v1)
    min_v2, max_v2 = min(valores_v2), max(valores_v2)

    for obj in lista_objetos:
        if max_v1 != min_v1:
            obj.v1 = (obj.v1 - min_v1) / (max_v1 - min_v1)
        if max_v2 != min_v2:
            obj.v2 = (obj.v2 - min_v2) / (max_v2 - min_v2)

def calcular_distancia(obj1: Objeto, obj2: Objeto) -> float:
    return math.sqrt((obj1.v1 - obj2.v1)**2 + (obj1.v2 - obj2.v2)**2) #[cite: 1]

def calcular_alfa(lista_objetos: list) -> float:
    soma_distancias = 0
    contador = 0

    for i in range(len(lista_objetos)):
        for j in range(i + 1, len(lista_objetos)):
            soma_distancias += calcular_distancia(lista_objetos[i], lista_objetos[j])
            contador += 1

    return soma_distancias / contador if contador > 0 else 0

def calcular_similaridade(raio: int, indice_centro: int, objeto_alvo: Objeto, matriz_placa: np.ndarray, objetos_no_chao: dict, a: float) -> float:
    linhas, colunas = matriz_placa.shape
    origem_linha = indice_centro // colunas
    origem_coluna = indice_centro % colunas
    
    somatorio = 0.0
    s = 0 
    
    for visao_i in range(-raio, raio + 1):
        for visao_j in range(-raio, raio + 1):
            if visao_i == 0 and visao_j == 0:
                continue

            linha_vizinho = (origem_linha + visao_i) % linhas
            coluna_vizinho = (origem_coluna + visao_j) % colunas
            indice_vizinho = linha_vizinho * colunas + coluna_vizinho

            if matriz_placa[linha_vizinho, coluna_vizinho] % 2 == 1:
                s += 1
                objeto_vizinho = objetos_no_chao.get(indice_vizinho)
                
                if objeto_vizinho:
                    distancia = calcular_distancia(objeto_alvo, objeto_vizinho)
                    termo = 1 - (distancia / a)
                    somatorio += termo
                    
    if s == 0:
        return 0.0
        
    f_xi = (1 / (s ** 2)) * somatorio #[cite: 1]
    
    if f_xi <= 0: return 0.0 
    elif f_xi > 1: return 1.0
    return f_xi

def pick(raio: int, k1: float, a: float, indice_formiga: int, objeto_alvo: Objeto, matriz_placa: np.ndarray, objetos_no_chao: dict) -> bool:
    fobj = calcular_similaridade(raio, indice_formiga, objeto_alvo, matriz_placa, objetos_no_chao, a)
    possibilidade = (k1 / (k1 + fobj)) ** 2 #[cite: 1]
    return np.random.random() < possibilidade

def drop(raio: int, k2: float, a: float, indice_formiga: int, objeto_alvo: Objeto, matriz_placa: np.ndarray, objetos_no_chao: dict) -> bool:
    fobj = calcular_similaridade(raio, indice_formiga, objeto_alvo, matriz_placa, objetos_no_chao, a)
    possibilidade = (fobj / (k2 + fobj)) ** 2 #[cite: 1]
    return np.random.random() < possibilidade

def deslocamento(agente: Agente, matriz_placa: np.ndarray) -> np.ndarray:
    linhas, colunas = matriz_placa.shape
    origem_linha = agente.indice // colunas
    origem_coluna = agente.indice % colunas

    direcoes = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    np.random.shuffle(direcoes)

    for deslocamento_i, deslocamento_j in direcoes:
        nova_linha = (origem_linha + deslocamento_i) % linhas
        nova_coluna = (origem_coluna + deslocamento_j) % colunas

        if matriz_placa[nova_linha, nova_coluna] < 2:
            peso_formiga = 4 if agente.carregando else 2

            matriz_placa[origem_linha, origem_coluna] -= peso_formiga
            matriz_placa[nova_linha, nova_coluna] += peso_formiga

            agente.indice = nova_linha * colunas + nova_coluna    
            return matriz_placa

    return matriz_placa

def acao(raio: int, k1: float, k2: float, a: float, agente: Agente, matriz_placa: np.ndarray, objetos_no_chao: dict) -> np.ndarray:
    if matriz_placa.flat[agente.indice] == 3:
        objeto_alvo = objetos_no_chao.get(agente.indice)
        
        if objeto_alvo and pick(raio, k1, a, agente.indice, objeto_alvo, matriz_placa, objetos_no_chao):
            agente.carregando = objetos_no_chao.pop(agente.indice) #[cite: 3]
            matriz_placa.flat[agente.indice] += 1 

    elif matriz_placa.flat[agente.indice] == 4 and agente.carregando:
        if drop(raio, k2, a, agente.indice, agente.carregando, matriz_placa, objetos_no_chao):
            objetos_no_chao[agente.indice] = agente.carregando #[cite: 3]
            agente.carregando = None
            matriz_placa.flat[agente.indice] -= 1 

    matriz_placa = deslocamento(agente, matriz_placa)
    return matriz_placa

def print_objetos(n, m, matriz_placa: np.ndarray, objetos_no_chao: dict) -> None:
    for i in range(n):
        for j in range(m):
            if matriz_placa[i, j] % 2 == 1:
                indice_1d = i * m + j
                if indice_1d in objetos_no_chao:
                    tipo_objeto = objetos_no_chao[indice_1d].tipo
                    print(f"{tipo_objeto} ", end="")
                else:
                    print("? ", end="")
            else:
                print(" ", end="")
        print()

if __name__ == "__main__": 
    n = 80
    m = 80 
    
    # Parâmetros do algoritmo
    raio = 1
    k1 = 0.1
    k2 = 0.1
    iteracoes = 1000000 
    quantidade_de_vivas = 50
    arquivo_nome = "dataset1.txt" 

    lista_dados = carregar_dataset(arquivo_nome)
    
    # Normalização e cálculo do Alfa
    normalizar_dados(lista_dados)
    #a_constante = calcular_alfa(lista_dados)

    a_constante = 0.5
    print(f"Dataset carregado. Valor de 'alpha' estático calculado: {a_constante:.4f}")

    quantidade_objetos = len(lista_dados)
    matriz_placa = np.zeros((n, m), dtype=int)    
    
    # Posicionamento aleatório dos objetos no chão
    pos_objeto = np.random.choice(n * m, size=quantidade_objetos, replace=False)
    objetos_no_chao = {}

    for i in range(quantidade_objetos):
        posicao_sorteada = pos_objeto[i]
        matriz_placa.flat[posicao_sorteada] = 1
        objetos_no_chao[posicao_sorteada] = lista_dados[i]

    # Posicionamento das formigas vivas
    casas_vazias = np.where(matriz_placa.flat == 0)[0] 
    pos_formiga_viva = np.random.choice(casas_vazias, size=quantidade_de_vivas, replace=False) 
    
    # Instanciando a classe Agente na memória
    lista_agentes = []
    for pos in pos_formiga_viva:
        matriz_placa.flat[pos] += 2
        lista_agentes.append(Agente(indice=pos))

    print("\nEstado INICIAL:")
    print_objetos(n, m, matriz_placa, objetos_no_chao)

    print("\nSimulando agrupamento (Isso pode levar alguns minutos)...")
    
    # O Loop Principal de simulação
    for j in range(iteracoes):
        for agente in lista_agentes:
            matriz_placa = acao(raio, k1, k2, a_constante, agente, matriz_placa, objetos_no_chao)

    print("\nFinalizando e forçando formigas a soltarem itens residuais...")
    for agente in lista_agentes:
        tentativas = 0
        while agente.carregando:
            if matriz_placa.flat[agente.indice] == 4:
                # Força uma avaliação contínua até largar ou estourar as tentativas
                fobj = calcular_similaridade(raio, agente.indice, agente.carregando, matriz_placa, objetos_no_chao, a_constante)
                if fobj > 0:
                    objetos_no_chao[agente.indice] = agente.carregando
                    agente.carregando = None
                    matriz_placa.flat[agente.indice] -= 1
                    break
            matriz_placa = deslocamento(agente, matriz_placa)
            tentativas += 1

    print("\nEstado FINAL (Clusters Esperados):")
    print_objetos(n, m, matriz_placa, objetos_no_chao)