

def plot_boxes(m, n, posicoes_ocupadas):
    
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    
    fig, ax = plt.subplots(figsize=(8, 8))

    # Criar uma grade
    for i in range(m + 1):
        ax.plot([0, n], [i, i], color="gray", linewidth=0.5)
    for j in range(n + 1):
        ax.plot([j, j], [0, m], color="gray", linewidth=0.5)

    # Extrair os grupos únicos para atribuir cores
    grupos = set()
    for row in posicoes_ocupadas:
        for box in row:
            if box.ocupado:
                grupos.update(carga.grupo for carga in box.cargas)

    # Utilizar cores vivas da paleta do Matplotlib
    cores_vivas = list(mcolors.TABLEAU_COLORS.values()) + list(mcolors.CSS4_COLORS.values())
    grupo_to_color = {grupo: cores_vivas[i % len(cores_vivas)] for i, grupo in enumerate(grupos)}

    # Adicionar os números dos boxes e as cargas
    for i in range(m):
        for j in range(n):
            box = posicoes_ocupadas[i][j]

            # Mostrar a posição do box
            ax.text(j + 0.5, m - i - 0.5, f"({i},{j})", fontsize=7, ha="center", va="center")

            # Marcar cargas alocadas
            if box.ocupado:
                
                # Criar lista com as cargas como string
                cargas_exibidas = [str(carga.carga) for carga in box.cargas]
                
                # Unir as cargas em uma única string separada por "/"
                carga_exibida_final = "/".join(cargas_exibidas)
                
                # Pegar o grupo (já que é único para o box)
                grupo = box.cargas[0].grupo if box.cargas else None
                cor = grupo_to_color.get(grupo, "black")
                
                # Posição do ponto no gráfico
                ponto_x = j + 0.5
                ponto_y = m - i - 0.5
                
                # Marcar o ponto com a cor do grupo
                ax.plot(ponto_x, ponto_y, 'o', color=cor, markersize=10)
                
                # Exibir o texto com a cor do grupo abaixo do ponto
                ax.text(ponto_x, ponto_y - 0.3,  # Ajustando a posição Y para exibir abaixo
                        carga_exibida_final, fontsize=9, ha="center", va="center", color=cor)
            

    ax.set_xlim(0, n)
    ax.set_ylim(0, m)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title("Matriz de Boxes com Alocações de Cargas")
    plt.show()




# Função para gerar a nova matriz
def transformar_matriz(matriz):
    # Criando a matriz resultante
    matriz_resultado = []
    
    # Para cada linha da matriz original
    for i in range(len(matriz)):
        nova_linha = []
        
        # Na primeira linha, mantemos os valores originais
        if i == 0:
            nova_linha = matriz[i].copy()
            matriz_resultado.append(nova_linha)
        elif i == 1:
            # Para i == 1, realizamos a mesclagem das linhas 1 e 2
            nova_linha = []
            for j in range(5, 10):
                nova_linha.append(matriz[2][j])  # Depois da linha 2
                nova_linha.append(matriz[1][j])  # Primeiro da linha 1
     
            matriz_resultado.append(nova_linha)
        elif i == 2:
            # Para i == 2, realizamos a mesclagem das linhas 3 e 4
            nova_linha = []
            for j in range(5, 10):
                nova_linha.append(matriz[4][j])  # Depois da linha 4
                nova_linha.append(matriz[3][j])  # Primeiro da linha 3
              
            matriz_resultado.append(nova_linha)
        elif i == 3:
            # Para i == 3, realizamos a mesclagem das linhas 5 e 6
            nova_linha = []
            for j in range(5, 10):
                nova_linha.append(matriz[6][j])  # Depois da linha 6
                nova_linha.append(matriz[5][j])  # Primeiro da linha 5
            matriz_resultado.append(nova_linha)
        elif i == 4:
            # Para i == 4, realizamos a mesclagem das linhas 7 e 8
            nova_linha = []
            for j in range(5, 10):
                nova_linha.append(matriz[8][j])  # Depois da linha 8
                nova_linha.append(matriz[7][j])  # Primeiro da linha 7
            matriz_resultado.append(nova_linha)
        
        # Adiciona a nova linha à matriz finals
    return matriz_resultado

def imprimir_tamanho_matriz(matriz):
    # Número de linhas da matriz
    num_linhas = len(matriz)
    
    # Número de colunas da matriz (assumindo que todas as linhas têm o mesmo número de colunas)
    num_colunas = len(matriz[0]) if num_linhas > 0 else 0
    
    print(f"Tamanho da matriz: {num_linhas} linhas x {num_colunas} colunas")
