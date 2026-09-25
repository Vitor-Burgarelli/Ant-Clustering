#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

// Configurações e hiperparâmetros
#define MAX_OBJETOS 1000
#define N 55
#define M 55
#define RAIO 1
#define K1 0.05
#define K2 0.35
#define ITERACOES 10000000
#define QTD_VIVAS 25
#define ALPHA 0.6

typedef struct {
    int id;
    int tipo;
    float v1;
    float v2;
} Objeto;

typedef struct {
    int indice;
    Objeto* carregando;
} Agente;

typedef struct {
    int di;
    int dj;
} Direcao;

// === Funções Utilitárias e Matemáticas ===

void embaralhar(int *array, int n) {
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

void embaralhar_direcoes(Direcao *dirs) {
    for (int i = 3; i > 0; i--) {
        int j = rand() % (i + 1);
        Direcao temp = dirs[i];
        dirs[i] = dirs[j];
        dirs[j] = temp;
    }
}

int carregar_dataset(const char* nome_arquivo, Objeto* dataset) {
    FILE* file = fopen(nome_arquivo, "r");
    if (!file) {
        printf("Erro ao abrir %s\n", nome_arquivo);
        exit(1);
    }
    
    char linha[256];
    int qtd = 0;
    
    while (fgets(linha, sizeof(linha), file)) {
        if (linha[0] == '#' || linha[0] == '\n' || linha[0] == '\r') continue;
        
        // Troca vírgulas por espaços
        for(int i = 0; linha[i] != '\0'; i++) {
            if(linha[i] == ',') linha[i] = ' ';
        }
        
        float v1, v2, tipo_f;
        if (sscanf(linha, "%f %f %f", &v1, &v2, &tipo_f) == 3) {
            dataset[qtd].id = qtd;
            dataset[qtd].v1 = v1;
            dataset[qtd].v2 = v2;
            dataset[qtd].tipo = (int)tipo_f;
            qtd++;
            if (qtd >= MAX_OBJETOS) break;
        }
    }
    fclose(file);
    return qtd;
}

void normalizar_dados(Objeto* dataset, int n_obj) {
    if (n_obj == 0) return;
    
    float min_v1 = dataset[0].v1, max_v1 = dataset[0].v1;
    float min_v2 = dataset[0].v2, max_v2 = dataset[0].v2;
    
    for (int i = 1; i < n_obj; i++) {
        if (dataset[i].v1 < min_v1) min_v1 = dataset[i].v1;
        if (dataset[i].v1 > max_v1) max_v1 = dataset[i].v1;
        if (dataset[i].v2 < min_v2) min_v2 = dataset[i].v2;
        if (dataset[i].v2 > max_v2) max_v2 = dataset[i].v2;
    }
    
    for (int i = 0; i < n_obj; i++) {
        if (max_v1 != min_v1) dataset[i].v1 = (dataset[i].v1 - min_v1) / (max_v1 - min_v1);
        if (max_v2 != min_v2) dataset[i].v2 = (dataset[i].v2 - min_v2) / (max_v2 - min_v2);
    }
}

float calcular_distancia(Objeto* obj1, Objeto* obj2) {
    return sqrt(pow(obj1->v1 - obj2->v1, 2) + pow(obj1->v2 - obj2->v2, 2));
}

float calcular_alfa(Objeto* dataset, int n_obj) {
    float soma_distancias = 0;
    int contador = 0;

    for (int i = 0; i < n_obj; i++) {
        for (int j = i + 1; j < n_obj; j++) {
            soma_distancias += calcular_distancia(&dataset[i], &dataset[j]);
            contador++;
        }
    }
    return (contador > 0) ? (soma_distancias / contador) : 0;
}

// === Lógica das Formigas ===

float calcular_similaridade(int raio, int indice_centro, Objeto* objeto_alvo, int* matriz_placa, Objeto** objetos_no_chao, float a) {
    int origem_linha = indice_centro / M;
    int origem_coluna = indice_centro % M;
    
    float somatorio = 0.0f;
    
    // O 's' agora representa o total de casas na área de visão, não os dados encontrados.
    int s = (2 * raio + 1); 
    
    for (int visao_i = -raio; visao_i <= raio; visao_i++) {
        for (int visao_j = -raio; visao_j <= raio; visao_j++) {
            if (visao_i == 0 && visao_j == 0) continue;

            // Busca toroidal no C
            int linha_vizinho = ((origem_linha + visao_i) % N + N) % N;
            int coluna_vizinho = ((origem_coluna + visao_j) % M + M) % M;
            int indice_vizinho = linha_vizinho * M + coluna_vizinho;

            // Se encontrou um dado, incrementa o somatório da similaridade
            if (matriz_placa[indice_vizinho] % 2 == 1) {
                Objeto* objeto_vizinho = objetos_no_chao[indice_vizinho];
                
                if (objeto_vizinho) {
                    float dist = calcular_distancia(objeto_alvo, objeto_vizinho);
                    somatorio += 1.0f - (dist / a); //[cite: 1]
                }
            }
        }
    }
    
    // Proteção contra divisão por zero, caso o raio seja 0
    if (s == 0) return 0.0f;
    
    // Aplica a divisão pelo total de casas ao quadrado
    float f_xi = (1.0f / (s * s)) * somatorio; //[cite: 1]
    
    // Garante os limites matemáticos da probabilidade [0, 1]
    if (f_xi <= 0.0f) return 0.0f; //[cite: 1]
    if (f_xi > 1.0f) return 1.0f;
    
    return f_xi;
}

bool pick(int raio, float k1, float a, int indice_formiga, Objeto* objeto_alvo, int* matriz_placa, Objeto** objetos_no_chao) {
    float fobj = calcular_similaridade(raio, indice_formiga, objeto_alvo, matriz_placa, objetos_no_chao, a);
    float possibilidade = pow(k1 / (k1 + fobj), 2);
    float roleta = (float)rand() / RAND_MAX;
    return roleta < possibilidade;
}

bool drop(int raio, float k2, float a, int indice_formiga, Objeto* objeto_alvo, int* matriz_placa, Objeto** objetos_no_chao) {
    float fobj = calcular_similaridade(raio, indice_formiga, objeto_alvo, matriz_placa, objetos_no_chao, a);
    float possibilidade = pow(fobj / (k2 + fobj), 2);
    float roleta = (float)rand() / RAND_MAX;
    return roleta < possibilidade;
}

void deslocamento(Agente* agente, int* matriz_placa) {
    int origem_linha = agente->indice / M;
    int origem_coluna = agente->indice % M;

    Direcao direcoes[4] = {{-1, 0}, {0, -1}, {0, 1}, {1, 0}};
    embaralhar_direcoes(direcoes);

    for (int i = 0; i < 4; i++) {
        int nova_linha = ((origem_linha + direcoes[i].di) % N + N) % N;
        int nova_coluna = ((origem_coluna + direcoes[i].dj) % M + M) % M;
        int novo_indice = nova_linha * M + nova_coluna;

        if (matriz_placa[novo_indice] < 2) {
            int peso_formiga = (agente->carregando != NULL) ? 4 : 2;

            matriz_placa[agente->indice] -= peso_formiga;
            matriz_placa[novo_indice] += peso_formiga;

            agente->indice = novo_indice;
            return;
        }
    }
}

void acao(int raio, float k1, float k2, float a, Agente* agente, int* matriz_placa, Objeto** objetos_no_chao) {
    if (matriz_placa[agente->indice] == 3) {
        Objeto* objeto_alvo = objetos_no_chao[agente->indice];
        
        if (objeto_alvo && pick(raio, k1, a, agente->indice, objeto_alvo, matriz_placa, objetos_no_chao)) {
            agente->carregando = objetos_no_chao[agente->indice];
            objetos_no_chao[agente->indice] = NULL; // Equivalente ao .pop()
            matriz_placa[agente->indice] += 1; 
        }
    } 
    else if (matriz_placa[agente->indice] == 4 && agente->carregando != NULL) {
        if (drop(raio, k2, a, agente->indice, agente->carregando, matriz_placa, objetos_no_chao)) {
            objetos_no_chao[agente->indice] = agente->carregando;
            agente->carregando = NULL;
            matriz_placa[agente->indice] -= 1; 
        }
    }
    deslocamento(agente, matriz_placa);
}
void salvar_ppm(int* matriz_placa, Objeto** objetos_no_chao, const char* nome_arquivo) {
    // Paleta de cores baseada nas suas preferências
    static const int cores[4][3] = {
        {128, 0, 128}, // Tipo 1: Roxo
        {255, 0, 0},   // Tipo 2: Vermelho
        {0, 0, 255},   // Tipo 3: Azul
        {0, 255, 0}    // Tipo 4: Verde
    };

    FILE *file = fopen(nome_arquivo, "w");
    if (file == NULL) {
        printf("Erro ao criar o arquivo %s\n", nome_arquivo);
        return;
    }

    // Cabeçalho P3 (Texto), Largura (M), Altura (N) e Valor Máximo RGB (255)
    fprintf(file, "P3\n%d %d\n255\n", M, N);

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            int idx = i * M + j;

            // Se o valor da célula for ímpar e o ponteiro não for nulo, há um objeto no chão
            if (matriz_placa[idx] % 2 == 1 && objetos_no_chao[idx] != NULL) {
                // Recupera o tipo numérico (1, 2, 3 ou 4) do dataset[cite: 5]
                int tipo = objetos_no_chao[idx]->tipo;
                
                // Mapeia o tipo para o índice do array de cores (0 a 3)
                int cor_idx = (tipo >= 1 && tipo <= 4) ? (tipo - 1) : 0;
                
                fprintf(file, "%d %d %d  ", cores[cor_idx][0], cores[cor_idx][1], cores[cor_idx][2]);
            } else {
                // Imprime branco puro para os espaços vazios da grid
                fprintf(file, "255 255 255  ");
            }
        }
        fprintf(file, "\n"); // Quebra de linha após o término da coluna
    }

    fclose(file);
}

void print_objetos(int* matriz_placa, Objeto** objetos_no_chao) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            int idx = i * M + j;
            if (matriz_placa[idx] % 2 == 1) {
                if (objetos_no_chao[idx] != NULL) {
                    printf(" %d ", objetos_no_chao[idx]->tipo);
                } else {
                    printf("? ");
                }
            } else {
                printf("  ");
            }
        }
        printf("\n");
    }
}

// === Função Principal ===

int main() {
    srand(time(NULL));

    Objeto dataset[MAX_OBJETOS];
    int quantidade_objetos = carregar_dataset("dataset1.txt", dataset);
    
    if(quantidade_objetos == 0) {
        printf("Nenhum dado carregado. Verifique o arquivo dataset.txt\n");
        return 1;
    }

    normalizar_dados(dataset, quantidade_objetos);
    //float a_constante = calcular_alfa(dataset, quantidade_objetos);
    float a_constante = ALPHA;
    printf("Dataset carregado (%d itens). Valor de 'alpha' calculado: %.4f\n", quantidade_objetos, a_constante);

    // Arrays contíguos alocados dinamicamente na stack
    int matriz_placa[N * M] = {0};
    Objeto* objetos_no_chao[N * M] = {NULL};

    // Gera lista de posições e embaralha para distribuir os objetos
    int posicoes[N * M];
    for (int i = 0; i < N * M; i++) posicoes[i] = i;
    embaralhar(posicoes, N * M);

    for (int i = 0; i < quantidade_objetos; i++) {
        int pos = posicoes[i];
        matriz_placa[pos] = 1;
        objetos_no_chao[pos] = &dataset[i];
    }

    // Coleta casas vazias e distribui formigas
    int casas_vazias[N * M];
    int qtd_vazias = 0;
    for (int i = 0; i < N * M; i++) {
        if (matriz_placa[i] == 0) {
            casas_vazias[qtd_vazias++] = i;
        }
    }
    embaralhar(casas_vazias, qtd_vazias);

    Agente lista_agentes[QTD_VIVAS];
    for (int i = 0; i < QTD_VIVAS; i++) {
        int pos = casas_vazias[i];
        matriz_placa[pos] += 2;
        lista_agentes[i].indice = pos;
        lista_agentes[i].carregando = NULL;
    }

    printf("\nEstado INICIAL:\n");
    print_objetos(matriz_placa, objetos_no_chao);
    printf("\nSimulando agrupamento...\n");

    salvar_ppm(matriz_placa, objetos_no_chao, "inicio.ppm");


    for (int j = 0; j < ITERACOES; j++) {
        for (int i = 0; i < QTD_VIVAS; i++) {
            acao(RAIO, K1, K2, a_constante, &lista_agentes[i], matriz_placa, objetos_no_chao);
        }
    }

    printf("\nFinalizando itens residuais...\n");
    for (int i = 0; i < QTD_VIVAS; i++) {
        int tentativas = 0;
        while (lista_agentes[i].carregando != NULL && tentativas < 1500) {
            if (matriz_placa[lista_agentes[i].indice] == 4) {
                float fobj = calcular_similaridade(RAIO, lista_agentes[i].indice, lista_agentes[i].carregando, matriz_placa, objetos_no_chao, a_constante);
                if (fobj > 0 || tentativas > 1400) {
                    objetos_no_chao[lista_agentes[i].indice] = lista_agentes[i].carregando;
                    lista_agentes[i].carregando = NULL;
                    matriz_placa[lista_agentes[i].indice] -= 1;
                    break;
                }
            }
            deslocamento(&lista_agentes[i], matriz_placa);
            tentativas++;
        }
    }

    printf("\nEstado FINAL (Clusters Esperados):\n");
    print_objetos(matriz_placa, objetos_no_chao);

    // Salva o estado da grid em uma imagem
    salvar_ppm(matriz_placa, objetos_no_chao, "fim.ppm");

    return 0;

    return 0;
}
