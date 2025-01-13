import sqlite3
from carga import Carga
from box import Box

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS boxes_reais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linha INT NOT NULL,
        coluna INT NOT NULL,
        ocupado BOOLEAN DEFAULT FALSE,
        volume INT DEFAULT 5
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS boxes_pares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        box1_id INTEGER NOT NULL,
        box2_id INTEGER NOT NULL,
        UNIQUE(box1_id, box2_id),
        FOREIGN KEY(box1_id) REFERENCES boxes(id),
        FOREIGN KEY(box2_id) REFERENCES boxes(id)
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
    # Tabela cargas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cargas_teste (
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

import sqlite3

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
                    UPDATE boxes_reais 
                    SET ocupado = ?, volume = ? 
                    WHERE linha = ? AND coluna = ?
                """, (box.ocupado, box.volume, i, j))

                # Atualiza a tabela de cargas associadas ao box
                for carga in box.cargas:
                    # Verifica se a combinação (box_id, carga, volume, idGrupo) já existe
                    cursor.execute("""
                        SELECT 1 FROM cargas 
                        WHERE box_id = (SELECT id FROM boxes_reais WHERE linha = ? AND coluna = ?) 
                        AND carga = ? AND volume = ?
                    """, (i, j, carga.carga, carga.volume))

                    # Se o registro não existir (resultado vazio), insere a carga
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO cargas (box_id, carga, volume, idGrupo) 
                            VALUES (
                                (SELECT id FROM boxes_reais WHERE linha = ? AND coluna = ?), 
                                ?, ?, ?
                            )
                        """, (i, j, carga.carga, carga.volume, idGrupo))

    conn.commit()
    conn.close()
    
def atualizar_banco_com_cargas_old(m, n, posicoes_ocupadas, idGrupo):
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
                    # Verifica se a combinação (box_id, carga, volume, idGrupo) já existe
                    cursor.execute("""
                        SELECT 1 FROM cargas_teste 
                        WHERE box_id = (SELECT id FROM boxes WHERE linha = ? AND coluna = ?) 
                        AND carga = ? AND volume = ?
                    """, (i, j, carga.carga, carga.volume))

                    # Se o registro não existir (resultado vazio), insere a carga
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO cargas_teste (box_id, carga, volume, idGrupo) 
                            VALUES (
                                (SELECT id FROM boxes WHERE linha = ? AND coluna = ?), 
                                ?, ?, ?
                            )
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


def inserir_boxes(matriz):
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    for row in matriz:
        for box in row:
            # Verificar se o box já existe com base na linha e coluna
            cursor.execute("SELECT COUNT(*) FROM boxes WHERE linha = ? AND coluna = ?", (box.linha, box.coluna))
            if cursor.fetchone()[0] > 0:
                continue  # Pula a inserção se o box já existir

            # Inserir o novo box
            cursor.execute("INSERT INTO boxes (linha, coluna, ocupado, volume) VALUES (?, ?, ?, ?)", 
                           (box.linha, box.coluna, box.ocupado, box.volume))
            box_id = cursor.lastrowid  # Obtém o ID do box inserido

            # Inserir as cargas associadas ao box
            for carga in box.cargas:
                cursor.execute("INSERT INTO cargas_teste (box_id, carga, volume) VALUES (?, ?, ?)", 
                               (box_id, carga.carga, carga.volume))

    conn.commit()
    conn.close()
    
def inserir_boxes_reais(matriz):
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    for row in matriz:
        for box in row:
            # Verificar se o box já existe com base na linha e coluna
            cursor.execute("SELECT COUNT(*) FROM boxes_reais WHERE linha = ? AND coluna = ?", (box.linha, box.coluna))
            if cursor.fetchone()[0] > 0:
                continue  # Pula a inserção se o box já existir

            # Inserir o novo box
            cursor.execute("INSERT INTO boxes_reais (linha, coluna, ocupado, volume) VALUES (?, ?, ?, ?)", 
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
    cursor.execute("SELECT id, box_id, carga, volume, idGrupo FROM cargas_teste")
    cargas = cursor.fetchall()
    conn.close()

    # Cria um dicionário para agrupar cargas por id do box
    cargas_por_box = {}
    for carga in cargas:
        box_id = carga[1]
        if carga[0] not in cargas_por_box:
            cargas_por_box[carga[0]] = []
        cargas_por_box[carga[0]].append({
            "box_id": box_id,
            "carga": carga[2],
            "volume": carga[3],
            "grupo": carga[4]
        })

    matriz = [[None for _ in range(n)] for _ in range(m)]
    box_objs = {}

    for box in boxes:
        box_id, linha, coluna, ocupado, volume = box

        # Verifique se os índices de linha e coluna são válidos
        if linha >= m or coluna >= n or linha < 0 or coluna < 0:
            print(f"Índices inválidos: linha={linha}, coluna={coluna}")
            continue  # Pula a iteração se os índices forem inválidos
        
        # Cria o objeto Box
        box_obj = Box(linha, coluna, ocupado, [], volume)
        box_objs[box_id] = box_obj  # Armazena para referência futura

        # Insere o box na matriz
        matriz[linha][coluna] = box_obj

    # Associa as cargas aos boxes
    for carga_id, carga_data in cargas_por_box.items():
        # Lista para os boxes associados a essa carga
        boxes_associados = [box_objs[data["box_id"]] for data in carga_data if data["box_id"] in box_objs]

        # Cria o objeto Carga e associa os boxes
        carga_obj = Carga(
            carga=carga_data[0]["carga"],
            volume=carga_data[0]["volume"],
            grupo=carga_data[0]["grupo"],
            box=boxes_associados
        )

        # Atualiza os objetos Box com a carga associada
        for box in boxes_associados:
            box.cargas.append(carga_obj)

    return matriz



def contar_boxes_desocupados():
    """
    Conta quantos boxes estão desocupados (ocupado = 0).
    """
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()

    # Conta o número de boxes desocupados
    cursor.execute("SELECT COUNT(*) FROM boxes WHERE ocupado = FALSE")
    count = cursor.fetchone()[0]

    conn.close()
    
    return count

def verificar_cargas_gravadas(cargas):
    """
    Verifica se as cargas da lista já estão gravadas na tabela 'cargas'.
    Retorna uma lista com o status de cada carga (True se já gravada, False caso contrário).
    """
    conn = sqlite3.connect("boxes.db")
    cursor = conn.cursor()
    print(cargas)
    status_cargas = []

    for carga in cargas:
        # Verifica se a carga já existe na tabela 'cargas'
        cursor.execute("""
            SELECT 1 FROM cargas_teste
            WHERE carga = ? AND volume = ? AND idGrupo = ?
        """, (carga.carga, carga.volume, carga.grupo))

        # filtra para inserir apenas novas cargas
        if not cursor.fetchone():
            status_cargas.append(carga)

    conn.close()

    return status_cargas

