import sqlite3
from pulp import LpProblem, LpVariable, LpMinimize
import matplotlib.pyplot as plt

class Box:
    def __init__(self, linha, coluna, ocupado=False, cargas=None, volume=5):
        if cargas is None:
            cargas = []
        self.id = f"{linha}-{coluna}"
        self.linha = linha
        self.coluna = coluna
        self.ocupado = ocupado
        self.cargas = cargas
        self.volume = volume

    def __repr__(self):
        return f"Box(id={self.id}, ocupado={self.ocupado}, cargas={self.cargas})"

    def verificar_volume(self, carga):
        volume_total = sum(c.volume for c in self.cargas) + carga.volume
        return volume_total <= self.volume

    def alocar_carga(self, carga):
        if len(self.cargas) < 2 and not self.ocupado and self.verificar_volume(carga):
            self.cargas.append(carga)
            if len(self.cargas) == 2 or sum(c.volume for c in self.cargas) >= self.volume:
                self.ocupado = True
            return True
        return False

class Carga:
    def __init__(self, carga, volume, alocada=False):
        self.carga = carga
        self.volume = volume
        self.alocada = alocada

    def __repr__(self):
        return f"Carga(carga={self.carga}, volume={self.volume})"

def criar_tabelas():
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS boxes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linha INT NOT NULL,
        coluna INT NOT NULL,
        ocupado BOOLEAN DEFAULT FALSE,
        volume INT DEFAULT 5
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cargas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        box_id INT,
        carga INT NOT NULL,
        volume FLOAT NOT NULL,
        FOREIGN KEY (box_id) REFERENCES boxes (id)
    )
    """)
    conn.commit()
    conn.close()

def inserir_boxes(matriz):
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()
    for row in matriz:
        for box in row:
            cursor.execute("INSERT INTO boxes (linha, coluna, ocupado, volume) VALUES (?, ?, ?, ?)", 
                           (box.linha, box.coluna, box.ocupado, box.volume))
            box_id = cursor.lastrowid
            for carga in box.cargas:
                cursor.execute("INSERT INTO cargas (box_id, carga, volume) VALUES (?, ?, ?)", 
                               (box_id, carga.carga, carga.volume))
    conn.commit()
    conn.close()

import sqlite3

def recuperar_matriz(m, n):
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    # Recupera todas as caixas
    cursor.execute("SELECT id, linha, coluna, ocupado, volume FROM boxes")
    boxes = cursor.fetchall()

    # Recupera todas as cargas
    cursor.execute("SELECT id, box_id, carga, volume FROM cargas")
    cargas = cursor.fetchall()
    conn.close()

    # Cria um dicionário para agrupar cargas por id do box
    cargas_por_box = {}
    for carga in cargas:
        box_id = carga[1]
        if box_id not in cargas_por_box:
            cargas_por_box[box_id] = []
        cargas_por_box[box_id].append(Carga(carga=carga[2], volume=carga[3]))

    # Reconstrói a matriz
    matriz = [[None for _ in range(n)] for _ in range(m)]
    for box in boxes:
        box_id, linha, coluna, ocupado, volume = box
        cargas_associadas = cargas_por_box.get(box_id, [])


        print(cargas_associadas)
        matriz[linha][coluna] = Box(linha, coluna, ocupado, cargas_associadas, volume)

    return matriz


def plot_boxes(m, n, matriz):
    fig, ax = plt.subplots(figsize=(8, 8))
    for i in range(m + 1):
        ax.plot([0, n], [i, i], color="gray", linewidth=0.5)
    for j in range(n + 1):
        ax.plot([j, j], [0, m], color="gray", linewidth=0.5)

    for i in range(m):
        for j in range(n):
            box = matriz[i][j]
            ax.text(j + 0.5, m - i - 0.5, f"({i},{j})", fontsize=7, ha="center", va="center")
            if box.ocupado:
                ax.plot(j + 0.5, m - i - 0.5, 'ro', markersize=10)
                for idx, carga in enumerate(box.cargas):
                    ax.text(j + 0.5, m - i - 0.5 - (idx * 0.3), carga.carga, fontsize=9, ha="center", va="center", color="white")

    ax.set_xlim(0, n)
    ax.set_ylim(0, m)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title("Matriz de Boxes com Alocações de Cargas")
    plt.show()

def alocar_cargas(m, n, cargas, matriz):
    for carga in cargas:
        for i in range(m):
            for j in range(n):
                box = matriz[i][j]
                if box.alocar_carga(carga):
                    carga.alocada = True
                    break
            if carga.alocada:
                break
    return matriz

# Configuração inicial
m, n = 5, 10
matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
cargas = [Carga(carga=i, volume=5) for i in range(1, 11)]

# Criação e preenchimento do banco de dados
criar_tabelas()
inserir_boxes(matriz_inicial)

# Recuperar a matriz do banco de dados
matriz = recuperar_matriz(m, n)

# Alocar as cargas
matriz = alocar_cargas(m, n, cargas, matriz)

# Exibir o resultado
plot_boxes(m, n, matriz)
