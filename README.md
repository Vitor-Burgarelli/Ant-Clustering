# Ant Clustering

Este repositório contém implementações de algoritmos de **Ant Clustering** (Agrupamento baseado em Colônia de Formigas). O projeto explora diferentes abordagens do algoritmo, incluindo modelos com formigas **homogêneas** e **heterogêneas**, implementados em Python e C.

## 📂 Estrutura do Repositório

O projeto é composto pelos seguintes arquivos principais:

### Implementações em Python
* `ant_homogeneo.py`: Implementação do algoritmo padrão de clustering, onde todas as formigas possuem o mesmo comportamento e parâmetros (modelo homogêneo).
* `ant_heterogeneo.py`: Implementação do algoritmo com formigas heterogêneas, onde diferentes agentes podem possuir características e regras de percepção distintas.

### Implementações em C
* `ant_heterogeneo4.c`: Versão otimizada em C do algoritmo heterogêneo (variação 4).
* `ant_heterogeneo15.c`: Versão otimizada em C do algoritmo heterogêneo (variação 15).
*(Nota: As implementações em C geralmente são utilizadas para processar bases de dados maiores com maior eficiência computacional).*

### Conjuntos de Dados (Datasets)
* `dataset1.txt`: Base de dados de teste 1 para validação do agrupamento.
* `dataset2.txt`: Base de dados de teste 2 para validação do agrupamento.

## 🚀 Como Executar

### Pré-requisitos
* Para os scripts em Python: Ter o **Python 3.x** instalado.
* Para os scripts em C: Ter um compilador C (como o **GCC**) instalado.

### Executando as versões em Python
Para executar o modelo homogêneo:
```bash
python ant_homogeneo.py
```

Para executar o modelo heterogêneo:
```bash
python ant_heterogeneo.py
```
*(Certifique-se de verificar dentro do código fonte como os datasets (`dataset1.txt` ou `dataset2.txt`) são carregados e se é necessário passá-los como argumento).*

### Compilando e Executando as versões em C
Para compilar e rodar a versão `ant_heterogeneo4.c`, utilize o terminal:
```bash
# Compilando
gcc ant_heterogeneo4.c -o ant4 -lm

# Executando
./ant4
```

## 🧠 Sobre o Algoritmo
O Ant Clustering Algorithm (ACA) é um algoritmo inspirado na natureza que simula o comportamento das formigas ao organizar cadáveres ou larvas em seus ninhos. Os agentes (formigas) movem-se aleatoriamente por um grid, pegando ou largando itens de dados com base na similaridade com os itens vizinhos, resultando em um agrupamento (clustering) emergente dos dados originais.