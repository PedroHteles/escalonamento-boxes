from pulp import LpProblem, LpVariable, LpMinimize
import matplotlib.pyplot as plt

# Plotar a matriz de boxes (10x10)
def plot_boxes(m, n, carga_positions):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Criar uma grade
    for i in range(m + 1):
        ax.plot([0, n], [i, i], color="gray", linewidth=0.5)
    for j in range(n + 1):
        ax.plot([j, j], [0, m], color="gray", linewidth=0.5)

    # Adicionar os números dos boxes
    for i in range(m):
        for j in range(n):
            ax.text(j + 0.5, m - i - 0.5, f"({i},{j})", fontsize=7, ha="center", va="center")

    # Marcar os pontos das cargas alocadas
    for k, (i, j) in enumerate(carga_positions):
        ax.plot(j + 0.5, m - i - 0.5, 'ro', markersize=10)  # Ponto vermelho para a carga
        ax.text(j + 0.5, m - i - 0.5, f"C{k}", fontsize=9, ha="center", va="center", color="white")

    ax.set_xlim(0, n)
    ax.set_ylim(0, m)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title("Matriz de Boxes (5x5) com Alocações de Cargas")
    plt.show()

# Exemplo de matriz de boxes (5x5)
m, n = 4, 5
boxes = [[(i, j) for j in range(n)] for i in range(m)]

# Definir o problema de otimização
prob = LpProblem("Alocacao_de_Boxes", LpMinimize)

# Variáveis para alocar as cargas (1 se a carga k for colocada no box i,j, 0 caso contrário)
cargas = 18
C = LpVariable.dicts("Carga", (range(cargas), range(m), range(n)), cat="Binary")

# Função objetivo: Minimizar a distância total (apenas ilustrativo, pois temos regras fixas)
prob += 0  # Sem objetivo direto, restrições determinam alocação

# Inicializa a quantidade de cargas
total_cargas = 0 

# Matriz para controlar as posições já alocadas
posicoes_ocupadas = [[False] * n for _ in range(m)]  # Inicializa com False (nenhuma posição ocupada)

linha_atual = 0  # Linha inicial para a primeira carga
coluna_atual = n- 1  # Coluna inicial

for k in range(cargas):
    alocada = False  # Variável para garantir que a carga seja alocada em uma posição única
    
    while not alocada:  # Loop até que a carga seja alocada
        # Verifica se a posição (linha_atual, coluna_atual) está disponível
        if linha_atual < m and coluna_atual >= 0 and not posicoes_ocupadas[linha_atual][coluna_atual]:
            # Alocar a carga na posição (linha_atual, coluna_atual)
            prob += C[k][linha_atual][coluna_atual] == 1, f"Carga_{k}_na_posicao_{linha_atual}_{coluna_atual}"
            total_cargas += 1  # A carga foi alocada
            posicoes_ocupadas[linha_atual][coluna_atual] = True  # Marcar a posição como ocupada
            alocada = True  # Marcar a carga como alocada

            # Se a linha foi preenchida, move para a próxima coluna
            if linha_atual == m - 1:  # Se a carga foi alocada na última linha
                # Avança para a próxima coluna e reinicia a linha
                coluna_atual -= 1  # Avança para a próxima coluna (de maior para menor)
                linha_atual = 0  # Reinicia a linha para 0
            else:
                linha_atual += 1  # Caso contrário, avança para a próxima linha

# Resolver o problema
prob.solve()

# Resultados: alocação das cargas
carga_positions = []
for k in range(cargas):
    for i in range(m):
        for j in range(n):
            if C[k][i][j].varValue == 1:
                print(f"Carga {k} alocada no box ({i}, {j})")
                carga_positions.append((i, j))

# Plotar o resultado
plot_boxes(m, n, carga_positions)
