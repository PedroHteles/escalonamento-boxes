from pulp import LpProblem, LpVariable, LpMinimize
import matplotlib.pyplot as plt
import sqlite3

import matplotlib.colors as mcolors


class Box:
    def __init__(self, linha, coluna, ocupado=False, cargas=None,volume=5):
        if cargas is None:
            cargas = []
        self.id = f"{linha}-{coluna}"  # ID único baseado nas coordenadas
        self.linha = linha
        self.coluna = coluna
        self.ocupado = ocupado
        self.cargas = cargas  # Agora, `cargas` é uma lista que pode armazenar até 2 cargas.
        self.volume = volume

    def __repr__(self):
        return f"Box(id={self.id}, ocupado={self.ocupado}, cargas={self.cargas}) \n"

    def verificar_carga(self):
        """Verifica se o box já possui alguma carga alocada."""
        return len(self.cargas) > 0  # Retorna True se houver cargas no box.
    
    def verificar_volume(self, carga):
        """Verifica se a soma do volume das cargas atuais e a carga a ser adicionada não ultrapassa o volume do box."""
        volume_total = sum(c.volume for c in self.cargas) + carga.volume
        return volume_total <= (self.volume * 2)

    def alocar_carga(self, carga):
        if len(self.cargas) < 2 and self.ocupado == False:

            if carga.volume > self.volume:
                self.cargas.append(carga)
                self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                return True  # Retorna True indicando que o box foi ocupado.
            else:
                if len(self.cargas) <= 2:
                    self.cargas.append(carga)
                    if len(self.cargas) == 2:
                        self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                        return True  # Retorna True indicando que o box foi ocupado.

        return False  # Retorna False caso o box não tenha sido ocupado (menos de 2 cargas).

class Carga:
    def __init__(self, carga, volume, alocada=False,grupo=None):
        self.carga = carga  # Peso da carga
        self.volume = volume  # Volume da carga
        self.alocada = alocada  # Volume da carga
        self.grupo = grupo  # Volume da carga

    def __repr__(self):
        return f"Carga(carga={self.carga}, volume={self.volume}, grupro={self.grupo})"
    
def verificar_carga_alocada(cargas):
    for carga in cargas:
        if carga.alocada:
            return True
    return False

def verificar_se_alguma_carga_alocada(cargas):
    return any(carga.alocada for carga in cargas)


def criar_tabelas():
    """
    Cria as tabelas boxes e cargas no banco de dados, caso elas não existam.
    """
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    # Tabela boxes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS boxes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linha INT NOT NULL,
        coluna INT NOT NULL,
        ocupado BOOLEAN DEFAULT FALSE,
        volume INT DEFAULT 5
    )
    """)

    # Tabela cargas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cargas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        box_id INT,
        carga INT NOT NULL,
        volume FLOAT NOT NULL,
        idGrupo INT DEFAULT NULL,
        FOREIGN KEY (box_id) REFERENCES boxes (id)
    )
    """)

    conn.commit()
    conn.close()


def atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo):
    """
    Atualiza a base de dados com a alocação de cargas nos boxes.
    """
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    for i in range(m):
        for j in range(n):
            box = posicoes_ocupadas[i][j]
            if box.ocupado:
                # Atualiza a tabela de boxes para refletir a ocupação
                cursor.execute("""
                    UPDATE boxes 
                    SET ocupado = ?, volume = ? 
                    WHERE linha = ? AND coluna = ?
                """, (box.ocupado, box.volume, i, j))

                # Atualiza a tabela de cargas associadas ao box
                for carga in box.cargas:
                    cursor.execute("""
                        INSERT INTO cargas (box_id, carga, volume, idGrupo) 
                        VALUES ((SELECT id FROM boxes WHERE linha = ? AND coluna = ?), ?, ?, ?)
                    """, (i, j, carga.carga, carga.volume, idGrupo))

    conn.commit()
    conn.close()

def inserir_boxes(matriz):
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    for row in matriz:
        for box in row:
            # Verificar se o box já existe com base na linha e coluna
            cursor.execute("SELECT COUNT(*) FROM boxes WHERE linha = ? AND coluna = ?", (box.linha, box.coluna))
            if cursor.fetchone()[0] > 0:
                print(f"Box na posição ({box.linha}, {box.coluna}) já existe. Pulando inserção.")
                continue  # Pula a inserção se o box já existir

            # Inserir o novo box
            cursor.execute("INSERT INTO boxes (linha, coluna, ocupado, volume) VALUES (?, ?, ?, ?)", 
                           (box.linha, box.coluna, box.ocupado, box.volume))
            box_id = cursor.lastrowid  # Obtém o ID do box inserido

            # Inserir as cargas associadas ao box
            for carga in box.cargas:
                cursor.execute("INSERT INTO cargas (box_id, carga, volume) VALUES (?, ?, ?)", 
                               (box_id, carga.carga, carga.volume))

    conn.commit()
    conn.close()

def recuperar_matriz(m, n):
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    # Recupera todas as caixas
    cursor.execute("SELECT id, linha, coluna, ocupado, volume FROM boxes")
    boxes = cursor.fetchall()

    # Recupera todas as cargas
    cursor.execute("SELECT id,box_id, carga,volume,idGrupo FROM cargas")
    cargas = cursor.fetchall()
    conn.close()

    # Cria um dicionário para agrupar cargas por id do box
    cargas_por_box = {}
    for carga in cargas:
        box_id = carga[1]
        if box_id not in cargas_por_box:
            cargas_por_box[box_id] = []
        cargas_por_box[box_id].append(Carga(carga=carga[2], volume=carga[3], grupo=carga[4]))

    matriz = [[None for _ in range(n)] for _ in range(m)]

    for box in boxes:
        box_id, linha, coluna, ocupado, volume = box

        # Verifique se os índices de linha e coluna são válidos
        if linha >= m or coluna >= n or linha < 0 or coluna < 0:
            print(f"Índices inválidos: linha={linha}, coluna={coluna}")
            continue  # Pula a iteração se os índices forem inválidos
        
        # Obtém as cargas associadas ao box
        cargas_associadas = cargas_por_box.get(box_id, [])
        
        box_obj = Box(linha, coluna, ocupado, cargas_associadas, volume)

        # Criação do objeto Box
        print(f"Box criado para (linha={linha}, coluna={coluna}): {box_obj}")
        
        # Insere o box na matriz
        matriz[linha][coluna] = box_obj

    # Verifique o estado final da matriz
    print("Matriz final:")
    for linha in matriz:
        print(linha)

    return matriz

def alocar_cargas(m, n, cargas, posicoes_iniciais_ocupadas=None):
    prob = LpProblem("Alocacao_de_Boxes", LpMinimize)
    C = LpVariable.dicts("Carga", (range(m), range(n)), cat="Binary")

    prob += 0  # Sem objetivo direto, as restrições determinam alocação

    # Matriz para controlar as posições já alocadas
    posicoes_ocupadas = [
        [Box(i, j, ocupado=box.ocupado, cargas=box.cargas) for j, box in enumerate(row)] 
        for i, row in enumerate(posicoes_iniciais_ocupadas)
    ]

    if posicoes_iniciais_ocupadas:
        for i in range(m):
            for j in range(n):
                if posicoes_iniciais_ocupadas[i][j].ocupado:
                    prob += C[i][j] == 1, f"Box_{i}_{j}_ocupado"
                    posicoes_ocupadas[i][j].ocupado = True


            # Encontrando a última coluna ocupada
        ultima_coluna_ocupada = -1
        for i in range(m):
            for j in range(n):
                if posicoes_ocupadas[i][j].ocupado:
                    ultima_coluna_ocupada = max(ultima_coluna_ocupada, j)

            # Definindo a coluna atual como a próxima coluna
        if ultima_coluna_ocupada != -1:
            coluna_atual = ultima_coluna_ocupada + 1
        else:
            coluna_atual = 0             

    linha_atual, coluna_atual = 0, n - 1
    primeira_carga_alocada = False 
    teste = False
    for carga in cargas:

        while not carga.alocada:

            if (linha_atual < m and 
                coluna_atual >= 0 and 
                posicoes_ocupadas[linha_atual][coluna_atual].ocupado == False 
                and (len(posicoes_ocupadas[i][j].cargas) ==  0  or  (
                                                                     (len(posicoes_ocupadas[linha_atual][coluna_atual].cargas)  and 
                                                                      posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga) == True) or
                                                                       (len(posicoes_ocupadas[linha_atual][coluna_atual].cargas) == 0 )
                                                                       ))): 
              
                    if(posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga) == False ):
                        if not posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga):

                            while linha_atual <= m:
                                # Verifica se é uma linha ímpar e se está disponível
                                if linha_atual % 2 == 1 and not posicoes_ocupadas[linha_atual][coluna_atual].ocupado:
                                    # Verifica se a linha sucessora também está disponível
                                    if linha_atual + 1 <= m and not posicoes_ocupadas[linha_atual + 1][coluna_atual].ocupado:
                                        # Aloca a carga na linha atual e na sucessora
                                        if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga) and \
                                            posicoes_ocupadas[linha_atual + 1][coluna_atual].alocar_carga(carga):

                                            prob += C[linha_atual][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual}_{coluna_atual}"
                                            prob += C[linha_atual + 1][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual + 1}_{coluna_atual}"
                                            carga.alocada = True
                                            break  # Saia do loop ao alocar com sucesso
                                # Avança para a próxima linha
                                linha_atual += 1
                    else: 
                        if ( primeira_carga_alocada == False and  verificar_se_alguma_carga_alocada(cargas) == True) or primeira_carga_alocada == True or  primeira_carga_alocada== False :
                            print(f"caiu estou { verificar_se_alguma_carga_alocada(cargas)}")
                            if(primeira_carga_alocada == False and  verificar_se_alguma_carga_alocada(cargas) == True) and \
                                teste == False:
                                coluna_atual = n - 1
                                linha_atual = 0  
                                teste = True
                           
                            if (linha_atual < m and 
                                coluna_atual >= 0 and 
                                (verificar_se_alguma_carga_alocada(cargas) == False or 
                                    ( verificar_se_alguma_carga_alocada(cargas) == True and ( (primeira_carga_alocada == False and linha_atual == 0) or (primeira_carga_alocada == True and linha_atual >= 0) ) ))and 
                                posicoes_ocupadas[linha_atual][coluna_atual].ocupado == False): 
                            
                                # Adiciona a carga ao box
                                if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga):
                                    print("wtf")
                                    prob += C[linha_atual][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual}_{coluna_atual}"
                                carga.alocada = True


                                if primeira_carga_alocada == True and \
                                   posicoes_ocupadas[linha_atual][coluna_atual].ocupado == True and \
                                   posicoes_ocupadas[linha_atual][coluna_atual - 1].ocupado == False:
                                   
                                    coluna_atual = n - 1
                                    linha_atual = 0  

                                # Marca que a primeira carga foi alocada e reseta a coluna
                                if  primeira_carga_alocada == False and \
                                    (posicoes_ocupadas[linha_atual][coluna_atual].ocupado == True or posicoes_ocupadas[linha_atual][coluna_atual].verificar_carga() == True ):
                                    primeira_carga_alocada = True

                            else:
                                if( primeira_carga_alocada == False or verificar_carga_alocada(cargas) == False):
                                    coluna_atual -= 1
                                    linha_atual = 0
                                else:
                                    if linha_atual == m - 1:
                                        coluna_atual -= 1
                                        linha_atual = 1
                                    else:
                                        linha_atual += 1
                        else:
                                if(verificar_carga_alocada(cargas) == False):
                                    coluna_atual -= 1
                                else:
                                    if linha_atual == m - 1:
                                        coluna_atual -= 1
                                        linha_atual = 1
                                    else:
                                        linha_atual += 1
                                  
            else:
                if(verificar_carga_alocada(cargas) == False):
                    coluna_atual -= 1
                else:
                    if linha_atual == m - 1:
                        coluna_atual -= 1
                        linha_atual = 1
                    else:
                        linha_atual += 1

    prob.solve()

    carga_positions = []
    for i in range(m):
        for j in range(n):
            if len(posicoes_ocupadas[i][j].cargas) > 0:
                carga_positions.append((i, j))
                posicoes_ocupadas[i][j].ocupado = True

    return carga_positions, posicoes_ocupadas


def plot_boxes(m, n, posicoes_ocupadas):
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


# Configuração de exemplo
m, n = 9, 10  # Dimensões da matriz
matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
inserir_boxes(matriz_inicial)
criar_tabelas()

cargas = [ Carga(carga=6, volume=15,grupo=2), Carga(carga=13, volume=15,grupo=2),
           Carga(carga=7, volume=1,grupo=2), Carga(carga=14, volume=1,grupo=2), 
           Carga(carga=8, volume=1,grupo=2), Carga(carga=15, volume=1,grupo=2),
           Carga(carga=9, volume=1,grupo=2), Carga(carga=16, volume=1,grupo=2),
           Carga(carga=10, volume=1,grupo=2), Carga(carga=17,volume=1,grupo=2),
           Carga(carga=10, volume=1,grupo=2), Carga(carga=17,volume=1,grupo=2)]


cargas_ordenadas = sorted(cargas, key=lambda carga: carga.volume,reverse=True)

matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
cargas = [Carga(carga=i, volume=5) for i in range(1, 11)]

# Recuperar a matriz do banco de dados
matriz = recuperar_matriz(m, n)

print("agora")
_, posicoes_ocupadas  = alocar_cargas(m, n, cargas_ordenadas, matriz)

# atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=1)

cargas = [ Carga(carga=20, volume=5,grupo=3), Carga(carga=22, volume=5,grupo=3),
           Carga(carga=21, volume=1,grupo=3), Carga(carga=23, volume=1,grupo=3), ]

cargas_ordenadas = sorted(cargas, key=lambda carga: carga.volume,reverse=True)


_, posicoes_ocupadas  = alocar_cargas(m, n, cargas_ordenadas, posicoes_ocupadas)

cargas = [ Carga(carga=24, volume=12,grupo=4), Carga(carga=55, volume=1,grupo=4),
           Carga(carga=25, volume=1,grupo=4), Carga(carga=56, volume=1,grupo=4), 
           Carga(carga=26, volume=1,grupo=4), Carga(carga=57, volume=1,grupo=4),
           Carga(carga=27, volume=1,grupo=4), Carga(carga=58, volume=1,grupo=4),
           Carga(carga=28, volume=1,grupo=4), Carga(carga=59, volume=1,grupo=4),
           Carga(carga=29, volume=1,grupo=4), Carga(carga=60, volume=1,grupo=4),
           Carga(carga=30, volume=1,grupo=4), Carga(carga=61, volume=1,grupo=4),
           Carga(carga=31, volume=1,grupo=4), Carga(carga=62, volume=1,grupo=4),
           Carga(carga=32, volume=1,grupo=4), Carga(carga=63, volume=1,grupo=4),
           Carga(carga=33, volume=1,grupo=4), Carga(carga=64, volume=1,grupo=4),
           Carga(carga=34, volume=1,grupo=4), Carga(carga=65, volume=1,grupo=4),
           Carga(carga=35, volume=1,grupo=4), Carga(carga=66, volume=1,grupo=4),
           Carga(carga=36, volume=1,grupo=4), Carga(carga=67, volume=1,grupo=4),
           Carga(carga=37, volume=1,grupo=4), Carga(carga=68, volume=1,grupo=4), 
           Carga(carga=38, volume=1,grupo=4), Carga(carga=69, volume=1,grupo=4),
           Carga(carga=39, volume=1,grupo=4), Carga(carga=70, volume=1,grupo=4),
           Carga(carga=40, volume=1,grupo=4), Carga(carga=71, volume=1,grupo=4),
           Carga(carga=41, volume=12,grupo=4), Carga(carga=72, volume=1,grupo=4)
        ]


cargas_ordenadas = sorted(cargas, key=lambda carga: carga.volume,reverse=True)

_, posicoes_ocupadas  = alocar_cargas(m, n, cargas_ordenadas, posicoes_ocupadas)


cargas = [ Carga(carga=99, volume=1,grupo=5), Carga(carga=100, volume=1,grupo=5),
           Carga(carga=101, volume=1,grupo=5), Carga(carga=102, volume=1,grupo=5), ]

cargas_ordenadas = sorted(cargas, key=lambda carga: carga.volume,reverse=True)

print("caso4")
_, posicoes_ocupadas  = alocar_cargas(m, n, cargas_ordenadas, posicoes_ocupadas)

# atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=1)
# print(posicoes_ocupadas)
# Plotar o resultado
plot_boxes(m, n, posicoes_ocupadas)
