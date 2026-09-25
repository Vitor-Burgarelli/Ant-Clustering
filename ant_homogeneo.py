import numpy as np

#momentos de estocasticidade:
#Distribuicao de elementos (x)
#Pegar ou largar(x)
#Onde andar(X) -> 1/4 pra cada cardinal 


#ESPECIFICACOES: 

#ESPACO VAZIO = 0
#FORMIGA MORTA (OBJETO) = 1
#FORMIGA VIVA = 2
#FORMIGAS VIVAS EM CIMA DE FORMIGAS MORTAS = 3
#FORMIGAS VIVAS CARREGANDO FORMIGAS MORTAS = 4
#FORMIGAS VIVAS CARREGANDO FORMIGAS MORTAS EM CIMA DE FORMIGAS MORTAS = 5

#FUNCAO SIMPLES DE PEGAR = 1-objetos/raio
#FUNCAO SIMPLES DE PEGAR = objetos/raio

def print_objetos(n, m, matriz_placa: np.ndarray) -> None:
    for i in range(n):
        for j in range(m):
            if matriz_placa[i, j] % 2 == 1:
                print("o", end = " ")
            else:
                print("  ", end = " ")
        print()
    return

def print_atual(n, m, matriz_placa: np.ndarray) -> None: 
    for i in range(n):
        for j in range(m):
            print(matriz_placa[i][j], end = "")
        print()
    return

def pegar_posicao (tipo, matriz_placa: np.ndarray, tam) -> np.ndarray:
    vetor_pos = []
    for i in range(tam):
        if matriz_placa.flat[i] == tipo:
            vetor_pos.append(i)
    return vetor_pos

def deslocamento(indice_formiga, matriz_placa: np.ndarray) -> np.ndarray:
    #nro de linhas/colunas
    linhas, colunas = matriz_placa.shape

    #como eu passei a posicao da formiga como indice do vetor preciso pegar o ij na matriz:
    origem_linha = indice_formiga // colunas
    origem_coluna = indice_formiga % colunas

    #achei esse o metodo mais clean de fazer a escolha ser aleatoria
    direcoes = [         (-1,0), 
                (0, -1),         (0, 1),
                         (1,0)]

    np.random.shuffle(direcoes)

    for deslocamento_i, deslocamento_j in direcoes:
        nova_linha = (origem_linha + deslocamento_i) % linhas
        nova_coluna = (origem_coluna + deslocamento_j) % colunas

        if matriz_placa[nova_linha, nova_coluna] < 2: 
            #calcula o quanto a formiga vale baseada nos valores (2 se nao estiver carregando objeto e 4 se estiver carregando objeto)
            peso_formiga = 4 if matriz_placa[origem_linha, origem_coluna] >= 4 else 2

            matriz_placa[origem_linha, origem_coluna] -= peso_formiga
            matriz_placa[nova_linha, nova_coluna] += peso_formiga

            #retorna a matriz com a posicao alterada da formiga
            novo_indice = nova_linha * colunas + nova_coluna    
            return novo_indice, matriz_placa

    #se chegar aqui signifca q n tem casas vagas
    return indice_formiga, matriz_placa

"""def visao_agente(raio, indice_formiga, matriz_placa: np.ndarray) -> int:
    contador = 0
    
    linhas, colunas = matriz_placa.shape

    #como eu passei a posicao da formiga em vetor preciso pegar o ij na matriz
    origem_linha = indice_formiga // colunas
    origem_coluna = indice_formiga % colunas

    #busca toroidal no i-1, j-1
    if matriz_placa[(origem_linha + (-1)) % linhas, (origem_coluna + (-1)) % colunas] % 2 == 1: 
        contador += 1
    #busca toroidal no i-1, j
    if matriz_placa[(origem_linha + (-1)) % linhas, (origem_coluna + (0)) % colunas] % 2 == 1: 
        contador += 1
    #busca toroidal no i-1, j+1
    if matriz_placa[(origem_linha + (-1)) % linhas, (origem_coluna + (1)) % colunas] % 2 == 1: 
        contador += 1
    #busca toroidal no i, j-1
    if matriz_placa[(origem_linha + (0)) % linhas, (origem_coluna + (-1)) % colunas] % 2 == 1: 
        contador += 1
    #busca toroidal no i, j+1
    if matriz_placa[(origem_linha + (0)) % linhas, (origem_coluna + (+1)) % colunas] % 2 == 1: 
        contador += 1
    #busca toroidal no i+1, j-1
    if matriz_placa[(origem_linha + (1)) % linhas, (origem_coluna + (-1)) % colunas] % 2 == 1: 
        contador += 1 
    #busca toroidal no i+1, j
    if matriz_placa[(origem_linha + (1)) % linhas, (origem_coluna + (0)) % colunas] % 2 == 1: 
        contador += 1
    #busca toroidal no i+1, j+1
    if matriz_placa[(origem_linha + (1)) % linhas, (origem_coluna + (+1)) % colunas] % 2 == 1: 
        contador += 1

    return contador
"""
#funcao visao_agente otimizada e funcionando com raio 
def visao(raio, indice_formiga ,matriz_placa: np.ndarray)-> int:
    linhas, colunas= matriz_placa.shape

    origem_linha = indice_formiga // colunas
    origem_coluna = indice_formiga % colunas

    contador = 0

    # verificacao de todas as celulas baseada no raio
    for visao_i in range(-raio, raio + 1):
        for visao_j in range(-raio, raio + 1):

            # se for (0, 0), eh o centro (a própria formiga)
            if visao_i == 0 and visao_j == 0:
                continue
            
            # calculo das linhas e colunas em formato toroidal para unir as bordas
            linha_vizinho = (origem_linha + visao_i) % linhas
            coluna_vizinho = (origem_coluna + visao_j) % colunas
            
            # se a celula for impar, contem uma formiga morta no chao (checar as especificacoes)
            if matriz_placa[linha_vizinho, coluna_vizinho] % 2 == 1: 
                contador += 1


    return contador

def pick(objetos_redor, total_casas)-> bool:
    total_casas = ((2 * raio + 1) ** 2) - 1

    possibilidade = 1- objetos_redor / total_casas
    if np.random.random() < possibilidade: 
        return True
    return False 

def drop(objetos_redor, total_casas)-> bool:
    total_casas = ((2 * raio + 1) ** 2) - 1

    possibilidade = objetos_redor / total_casas
    if np.random.random() < possibilidade: 
        return True
    return False 

"""for i in range(quantidade_de_vivas):
formiga_atual = vetor_vivas[i]
tentativas = 0

while matriz_placa.flat[formiga_atual] >= 4 and tentativas < 1000:

if matriz_placa.flat[formiga_atual] == 4: 
    objetos_redor = visao(raio, formiga_atual, matriz_placa)
    if objetos_redor > 0 or tentativas > 950:
        # Correção 3: Inclusão do .flat no mapeamento de estado
        matriz_placa.flat[formiga_atual] -= 1
        break

formiga_atual, matriz_placa = deslocamento(formiga_atual, matriz_placa)
tentativas += 1

vetor_vivas[i] = formiga_atual"""

def acao(raio, indice_formiga, matriz_placa: np.ndarray) -> np.ndarray:

    total_casas = ((2 * raio + 1) ** 2) - 1
    objetos_redor = visao(raio, indice_formiga, matriz_placa)

    if matriz_placa.flat[indice_formiga] == 3:
        if pick(objetos_redor, total_casas):
            matriz_placa.flat[indice_formiga] += 1
    if matriz_placa.flat[indice_formiga] == 4:
        if drop(objetos_redor, total_casas):
            matriz_placa.flat[indice_formiga] -= 1


    novo_indice, matriz_placa = deslocamento(indice_formiga, matriz_placa)

    return novo_indice, matriz_placa


if __name__ == "__main__":

    raio = 5

    n = 50
    m = 50

    matriz_placa = np.zeros((n,m), dtype=int)

    quantidade_de_uns = 600
    quantidade_de_vivas = 15

    pos_objeto = np.random.choice(n * m, size=quantidade_de_uns, replace=False)
    matriz_placa.flat[pos_objeto] = 1

    pos_formiga_viva = np.random.choice(n * m, size=quantidade_de_vivas, replace=False)
    matriz_placa.flat[pos_formiga_viva] += 2


    print("______________________________INICIO___________________________")
    print_objetos(n, m, matriz_placa)

    vetor_vivas = []
    for i in range(n*m):
        if matriz_placa.flat[i] > 1:
            vetor_vivas.append(i)

    print()
    print("AGRUPANDO...")
    print()

    for j in range(100000):
        for i in range(quantidade_de_vivas):
            novo_indice, matriz_placa = acao(raio, vetor_vivas[i], matriz_placa)
            vetor_vivas[i] = novo_indice


    print("\nFINALIZANDO...")
    formigas_carregando = []

    for i in range(quantidade_de_vivas):
        if matriz_placa.flat[vetor_vivas[i]] >= 4:
            formigas_carregando.append(vetor_vivas[i])

    for i in range(len(formigas_carregando)):
        formiga_atual = formigas_carregando[i]

        while matriz_placa.flat[formiga_atual] >= 4:
            
            if matriz_placa.flat[formiga_atual] == 4: 
                objetos_redor = visao(raio, formiga_atual, matriz_placa)
                

                if objetos_redor > 0:
                    matriz_placa.flat[formiga_atual] -= 1
                    break
            
            formiga_atual, matriz_placa = deslocamento(formiga_atual, matriz_placa)



    print("______________________________RESULTADO_____________________________")

    print_objetos(n, m, matriz_placa)

