

def plot_boxes(m, n, posicoes_ocupadas):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from box import Box
    
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

    # Agrupar cargas por grupo e adicionar a cor
    cargas_por_grupo = {}

    for row in posicoes_ocupadas:
        for box in row:
            if box.ocupado:
                for carga in box.cargas:
                    grupo = carga.grupo
                    cor = grupo_to_color.get(grupo, "black")
                    
                    # Verificar se a carga já foi adicionada no grupo
                    if grupo not in cargas_por_grupo:
                        cargas_por_grupo[grupo] = {'cargas': [], 'cor': cor, 'boxes': []}
                    
                    # Verificar se a carga já existe no grupo antes de adicionar
                    if carga not in cargas_por_grupo[grupo]['cargas']:
                        cargas_por_grupo[grupo]['cargas'].append(carga)
                    
                    # Adicionar o box ao grupo
                    cargas_por_grupo[grupo]['boxes'].append(box)



    # Adicionar os números dos boxes e as cargas
    for i in range(m):
        for j in range(n):
            box = posicoes_ocupadas[i][j]

            # Exibir o nome do box no centro da célula
            ax.text(j + 0.5, m - i - 0.5, f"{box.box}", fontsize=9, ha="center", va="center", color="black")

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

    # Adicionar legenda com as cores dos grupos e as cargas
    legend_x = n + 1  # Localização da legenda à direita
    for i, (grupo, info) in enumerate(cargas_por_grupo.items()):
        ax.plot(legend_x, m - i - 0.5, 'o', color=info['cor'], markersize=10)  # Ponto com cor do grupo
        
        # Exibir o nome do grupo
        ax.text(legend_x + 0.2, m - i - 0.5, f"Grupo {grupo}", fontsize=9, ha="left", va="center", color=info['cor'])

        # Exibir as cargas associadas ao grupo com quebra de linha
        y_offset = m - i - 1.0
        for j, carga in enumerate(info['cargas']):
            # Filtrar o box baseado no ID
            if(len(carga.box) > 1):
                    print(f"deu ruim carga:{carga.carga}")
                    # Filtrar o box baseado no ID
                    
                    menor_id = min([box.id for box in carga.box], key=lambda x: int(x.split('-')[0]))

                    box_encontrado = next((b for b in info['boxes'] if b.id == menor_id), None)
                    
                    novo_box = Box(
                            linha=box_encontrado.linha,
                            coluna=box_encontrado.coluna,
                            ocupado=box_encontrado.ocupado,
                            cargas=list(box_encontrado.cargas),
                            volume=box_encontrado.volume,
                            box = f"{box_encontrado.box}1" 
                    )
                    ax.text(legend_x + 0.2, y_offset, 
                                f"carga:{carga.carga} pc:{carga.volume} box {novo_box.box}",
                                fontsize=9, ha="left", va="center", color=info['cor'])
                    y_offset -= 0.4
            else:
      
                # Verificar se o box atual está em 'info['boxes']' comparando pelo ID
                box_encontrado = next((b for b in info['boxes'] if b.id == carga.box[0].id), None)
                
                if box_encontrado:  # Se encontrar o box no grupo
                    ax.text(legend_x + 0.2, y_offset, 
                            f"carga:{carga.carga} pc:{carga.volume} box {box_encontrado.box}",
                            fontsize=9, ha="left", va="center", color=info['cor'])

                    y_offset -= 0.4  # Ajusta a posição para a próxima linha


    ax.set_xlim(0, n + 5)  # Ajustando o limite para incluir a legenda
    ax.set_ylim(0, m)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title("Matriz de Boxes com Alocações de Cargas")
    plt.show()



def plot_boxes_v1(m, n, posicoes_ocupadas):
    print(f"plot_boxes_v1:{posicoes_ocupadas}")
    
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


def definir_pares(posicoes_ocupadas):
    from box import Box
    # Extrair os grupos únicos para atribuir cores
    grupos = set()
    for row in posicoes_ocupadas:
        for box in row:
            if box.ocupado:
                grupos.update(carga.grupo for carga in box.cargas)

    # Agrupar cargas por grupo e adicionar a cor
    cargas_por_grupo = {}
    for row in posicoes_ocupadas:
        for box in row:
            if box.ocupado:
                for carga in box.cargas:
                    grupo = carga.grupo
                    
                    # Verificar se a carga já foi adicionada no grupo
                    if grupo not in cargas_por_grupo:
                        cargas_por_grupo[grupo] = {'cargas': [], 'boxes': []}
                    
                    # Verificar se a carga já existe no grupo antes de adicionar
                    if carga not in cargas_por_grupo[grupo]['cargas']:
                        cargas_por_grupo[grupo]['cargas'].append(carga)
                    
                    # Adicionar o box ao grupo
                    cargas_por_grupo[grupo]['boxes'].append(box)

    for i, (grupo, info) in enumerate(cargas_por_grupo.items()):
        for j, carga in enumerate(info['cargas']):
            if(len(carga.box) > 1):
                
                menor_id = min([box.id for box in carga.box], key=lambda x: int(x.split('-')[0]))

                box_encontrado = next((b for b in info['boxes'] if b.id == menor_id), None)
                
                novo_box = Box(
                        linha=box_encontrado.linha,
                        coluna=box_encontrado.coluna,
                        ocupado=box_encontrado.ocupado,
                        cargas=list(box_encontrado.cargas),
                        volume=box_encontrado.volume,
                        box = f"{box_encontrado.box}1" 
                )
                print(novo_box)
                       
        
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



def reconstruir_matriz(matriz_transformada):
    # Criando a matriz original
    matriz_original = []
    
    # Adicionar a primeira linha diretamente
    matriz_original.append(matriz_transformada[0].copy())
    
    # Para as linhas mescladas
    for i in range(1, len(matriz_transformada)):
        linha1 = []
        linha2 = []
        
        # Desfazendo a mesclagem
        for j in range(0, len(matriz_transformada[i]), 2):
            linha1.append(matriz_transformada[i][j + 1])  # Primeiro elemento
            linha2.append(matriz_transformada[i][j])      # Segundo elemento
        
        # Inserindo as linhas restauradas no lugar correto
        matriz_original.append(linha1)
        matriz_original.append(linha2)
    
    return matriz_original


def imprimir_tamanho_matriz(matriz):
    # Número de linhas da matriz
    num_linhas = len(matriz)
    
    # Número de colunas da matriz (assumindo que todas as linhas têm o mesmo número de colunas)
    num_colunas = len(matriz[0]) if num_linhas > 0 else 0
    
    print(f"Tamanho da matriz: {num_linhas} linhas x {num_colunas} colunas")
