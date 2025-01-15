def criar_tabela_box():
    import sqlite3
    # Conectar ao banco de dados (ou criar um novo arquivo se não existir)
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a tabela 'box' se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS box (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            box TEXT NOT NULL,
            sequencia INTEGER NOT NULL,
            ocupado BOOLEAN NOT NULL DEFAULT 0,
            carga TEXT,
            volume REAL NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('carregamento','normal','filho','grupo')),
            id_pai INTEGER,
            id_grupo INTEGER,
            FOREIGN KEY (id_pai) REFERENCES box (id),
            FOREIGN KEY (id_grupo) REFERENCES grupo (id)
        )
    ''')

    # Criar a tabela 'grupo' se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            box TEXT NOT NULL,
            carga TEXT,
            volume REAL NOT NULL,
            sequencia INTEGER NOT NULL,
            ocupado BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()



def criar_trigger_box_grupo_com_trava_update():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger para garantir que o box do grupo seja ocupado corretamente
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS ocupar_box_grupo_com_trava
        BEFORE UPDATE OF ocupado ON grupo
        FOR EACH ROW
        WHEN NEW.ocupado = 1
        BEGIN
            -- Verificar se algum filho do grupo está ocupado
            -- Se algum filho estiver ocupado, o grupo será marcado como ocupado
            UPDATE box
            SET ocupado = 1
            WHERE id_grupo = NEW.id
              AND EXISTS (
                  SELECT 1
                  FROM box
                  WHERE id_grupo = NEW.id AND ocupado = 1
                  LIMIT 1
              );

            -- Se todos os filhos estão livres, o grupo pode ser ocupado
            -- Caso contrário, não permite a atualização
            UPDATE grupo
            SET ocupado = 1
            WHERE id = NEW.id
              AND NOT EXISTS (
                  SELECT 1
                  FROM box
                  WHERE id_grupo = NEW.id AND ocupado = 0
              );
        END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()


def criar_trigger_box_grupo_com_trava():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que atualiza os boxes relacionados quando um grupo é ocupado
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS ocupar_boxes_relacionados_com_trava
        AFTER UPDATE OF ocupado ON grupo
        FOR EACH ROW
        WHEN NEW.ocupado = 1
        BEGIN
            UPDATE box
            SET ocupado = 1
            WHERE id_grupo = NEW.id
              AND NOT EXISTS (
                  SELECT 1
                  FROM box
                  WHERE id_grupo = NEW.id AND (ocupado = 1 OR carga  IS NOT NULL )
              );
        END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()


def criar_trigger_box_grupo_libera_boxes():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que libera os boxes relacionados quando um grupo é liberado
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS liberar_boxes_relacionados
        AFTER UPDATE OF ocupado ON grupo
        FOR EACH ROW
        WHEN NEW.ocupado = 0
        BEGIN
            UPDATE box
            SET ocupado = 0
            WHERE id_grupo = NEW.id;
        END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()


def criar_trigger_liberar_grupo():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que desocupa o grupo quando todos os boxes do grupo estão disponíveis
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS liberar_grupo_se_todos_boxes_disponiveis
        AFTER UPDATE OF ocupado ON box
        FOR EACH ROW
        WHEN NEW.ocupado = 0
        BEGIN
            UPDATE grupo
            SET ocupado = 0
            WHERE id = OLD.id_grupo
            AND NOT EXISTS (
                SELECT 1
                FROM box
                WHERE id_grupo = OLD.id_grupo 
                AND (carga IS NOT NULL AND carga != '')
                AND ocupado = 1    
            );
        END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()


def criar_trigger_ocupar_grupo_se_box_alocado():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que ocupa o grupo quando um box do grupo recebe uma carga
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS ocupar_grupo_ao_alocar_carga_no_box
        AFTER UPDATE OF ocupado ON box
        FOR EACH ROW
        WHEN NEW.id_grupo IS NOT NULL and new.ocupado = 1
        BEGIN
            UPDATE grupo
            SET ocupado = 1
            WHERE id = NEW.id_grupo;
        END;
    ''')
    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()

def criar_trigger_ocupar_pai_se_filhos_ocupados():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que ocupa o pai quando todos os filhos estão ocupados
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS ocupar_pai_quando_todos_filhos_ocupados
        AFTER UPDATE OF ocupado, carga ON box
        FOR EACH ROW
        WHEN NEW.carga IS NOT NULL AND NEW.carga != '' and new.id_pai is not null
        BEGIN
            UPDATE box
            SET ocupado = 1
            WHERE id = NEW.id_pai
            AND EXISTS (
                SELECT 1
                FROM box
                WHERE id_pai = NEW.id_pai AND (carga IS NOT NULL AND carga != '')
            );
        END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()
    
def criar_trigger_ocupar_filhos_se_pai_ocupado_v3():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que ocupa os filhos quando o pai for ocupado
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS ocupar_filhos_quando_pai_ocupado_v3
        AFTER UPDATE OF ocupado ON box
        FOR EACH ROW
        WHEN NEW.ocupado = 0 
        BEGIN
            UPDATE box
            SET ocupado = 0
            WHERE id_pai = NEW.id;
        END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()
     
def criar_trigger_ocupar_filhos_se_pai_ocupado():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que ocupa os filhos quando o pai for ocupado
    cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS liberar_ocupar_filhos_se_pai_ocupado
            AFTER UPDATE OF ocupado ON box
            FOR EACH ROW
            WHEN NEW.ocupado = 1 and NEW.id_pai is null
            BEGIN
                UPDATE box
                SET ocupado = 1
                WHERE id_pai = NEW.id
                AND NOT EXISTS (
                    SELECT 1
                    FROM box
                    WHERE id_pai = NEW.id 
                    AND carga not null
                );
            END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()       
     
def criar_trigger_desocupar_filhos_se_pai_ocupado():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Criar a trigger que ocupa os filhos quando o pai for ocupado
    cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS liberar_pai_se_filhos_desocupados
            AFTER UPDATE OF ocupado ON box
            FOR EACH ROW
            WHEN NEW.ocupado = 0 and new.id_pai is not null
            BEGIN
                UPDATE box
                SET ocupado = 0
                WHERE id = OLD.id_pai
                AND NOT EXISTS (
                    SELECT 1
                    FROM box
                    WHERE id_pai = OLD.id_pai AND ocupado = 1
                );
            END;
    ''')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()    
    
def apagar_triggers():
    import sqlite3

    # Conectar ao banco de dados
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    # Apagar todas as triggers criadas
    triggers = [
        'ocupar_filhos_quando_pai_ocupado',
        'ocupar_boxes_relacionados',
        'ocupar_grupo_ao_alocar_carga',
        'ocupar_boxes_relacionados_com_trava',
        'liberar_grupo_se_todos_boxes_disponiveis',
        'ocupar_grupo_ao_alocar_carga_no_box',
        'liberar_filhos_quando_pai_liberado',
        'ocupar_filhos_quando_pai_ocupado_v2',
        'ocupar_filhos_quando_pai_ocupado_v3',
        'ocupar_pai_quando_todos_filhos_ocupados',
        'ocupar_grupo_se_box_alocado',
        'liberar_grupo',
        'ocupar_box_grupo_com_trava',
        'liberar_pai_se_filhos_desocupados',
        'liberar_ocupar_filhos_se_pai_ocupado',
        'alocar_carga_grupo',
        'liberar_boxes_relacionados'
    ]

    for trigger in triggers:
        cursor.execute(f'DROP TRIGGER IF EXISTS {trigger};')

    # Confirmar as mudanças e fechar a conexão
    conexao.commit()
    conexao.close()

def inserir_box(box, sequencia, ocupado, volume, tipo,carga=None, id_pai=None, id_grupo=None):
    import sqlite3
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    cursor.execute('''
        INSERT INTO box (box, sequencia, ocupado, carga, volume, tipo, id_pai, id_grupo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (box, sequencia, ocupado, carga, volume, tipo, id_pai, id_grupo))

    conexao.commit()
    conexao.close()

def inserir_grupo(box,sequencia, ocupado, volume,carga=None):
    import sqlite3
    conexao = sqlite3.connect('box_allocation.db')
    cursor = conexao.cursor()

    cursor.execute('''
        INSERT INTO grupo (box, sequencia, ocupado,carga, volume)
        VALUES (?, ?, ?, ?, ?)
    ''', (box,sequencia, ocupado,carga, volume))

    conexao.commit()
    conexao.close()
    
        
def criar_tabelas_e_trigger():
    criar_tabela_box()
    apagar_triggers()
    criar_trigger_box_grupo_com_trava()
    criar_trigger_liberar_grupo()
    criar_trigger_ocupar_grupo_se_box_alocado()
    criar_trigger_desocupar_filhos_se_pai_ocupado()
    criar_trigger_ocupar_pai_se_filhos_ocupados()
    criar_trigger_box_grupo_libera_boxes()
    criar_trigger_ocupar_filhos_se_pai_ocupado_v3()
    criar_trigger_ocupar_filhos_se_pai_ocupado()
    


def update_box(carga, tipo_box, tipo_escala):
    print(f"carga={carga} tipo_box={tipo_box} tipo_escala={tipo_escala}")
    
    from flask import g
    import sqlite3
    """
    Atualiza o estado de uma entrada na tabela 'box' com base em condições específicas.

    Args:
        carga (int): O valor de carga que será atribuído ao registro.
        tipo_box (str): Tipo de box usado na lógica condicional.
        tipo_escala (str): Tipo de escala usado na lógica condicional.

    Returns:
        int: ID do registro atualizado ou None se nenhum registro foi encontrado.
    """
    query = """
    UPDATE box 
    SET ocupado = 1, carga = :carga
    WHERE id = (
    SELECT b.id
        FROM box b
        JOIN box b1 ON 
            CASE 
                WHEN 'filho' = :tipo_box THEN b.id_pai = b1.id
                ELSE b.id = b1.id
            END
        WHERE b.ocupado = 0
        AND b1.tipo = :tipo_escala
        ORDER BY 
            CASE 
                WHEN b1.tipo = 'carregamento' THEN b1.sequencia
                ELSE NULL
            END DESC,
            CASE 
                WHEN b1.tipo != 'carregamento' THEN b1.sequencia
                ELSE NULL
            END ASC
    LIMIT 1
    );
    """
    try:
        # Executa o UPDATE dentro da transação controlada pelo Flask
        cursor = g.db.cursor()
        cursor.execute(query, {"carga": carga, "tipo_box": tipo_box, "tipo_escala": tipo_escala})

        # Verifica quantas linhas foram afetadas
        if cursor.rowcount > 0:
            print(f"carga: {cursor.rowcount }")
            return carga  # Retorna a carga para indicar sucesso
        else:
            return None  # Nenhum registro foi encontrado

    except sqlite3.Error as e:
        return  ValueError(f"Erro ao atualizar a tabela 'box': {e}")



def update_grupo(carga, tipo_box, tipo_escala):
    print(f"carga={carga} tipo_box={tipo_box} tipo_escala={tipo_escala}")
    
    from flask import g
    import sqlite3
    """
    Atualiza o estado de uma entrada na tabela 'box' com base em condições específicas.

    Args:
        carga (int): O valor de carga que será atribuído ao registro.
        tipo_box (str): Tipo de box usado na lógica condicional.
        tipo_escala (str): Tipo de escala usado na lógica condicional.

    Returns:
        int: ID do registro atualizado ou None se nenhum registro foi encontrado.
    """
    query = """
    UPDATE grupo 
    SET ocupado = 1, carga = :carga
    WHERE id = (
    SELECT g.id 
    from grupo g  
    where ocupado = 0 
    ORDER by sequencia 
    LIMIT 1
    );
    """
    try:
        # Executa o UPDATE dentro da transação controlada pelo Flask
        cursor = g.db.cursor()
        cursor.execute(query, {"carga": carga})

        # Verifica quantas linhas foram afetadas
        if cursor.rowcount > 0:
            print(f"carga: {cursor.rowcount }")
            return carga  # Retorna a carga para indicar sucesso
        else:
            return None  # Nenhum registro foi encontrado

    except sqlite3.Error as e:
        return  ValueError(f"Erro ao atualizar a tabela 'box': {e}")


def check_carga(carga):
    import sqlite3
    """
    Verifica se existe algum valor na coluna 'carga' das tabelas 'box' ou 'grupo' 
    com o valor especificado.

    Args:
        carga (int): O valor que estamos buscando na coluna 'carga'.

    Returns:
        bool: Retorna True se algum valor foi encontrado, caso contrário, False.
    """
    query = """
    SELECT b.carga
    FROM box b
    WHERE b.carga = ?
    UNION ALL
    SELECT g.carga
    FROM grupo g
    WHERE g.carga = ?
    LIMIT 1;
    """
    
    try:
        # Conecta ao banco de dados SQLite
        conexao = sqlite3.connect('box_allocation.db')
        cursor = conexao.cursor()

        # Executa a consulta com o valor de carga fornecido
        cursor.execute(query, (carga, carga))
        
        # Verifica se algum valor foi retornado
        result = cursor.fetchone()

        # Retorna True se algum valor foi encontrado, caso contrário, False
        return result is not None
    except sqlite3.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False
    finally:
        # Fecha a conexão com o banco de dados
        conexao.close()
      

criar_tabelas_e_trigger()   
# Exemplo de uso
# # Exemplo de uso

# if check_carga(carga):
#     print(f"Valor {carga} encontrado nas tabelas.")
# else:
#     print(f"Valor {carga} não encontrado nas tabelas.")
# updated_id = update_box(11,tipo_box, tipo_escala)


# # Exemplo de uso
# tipo_box = "filho"
# tipo_escala = "normal"

# updated_id = update_box(12,tipo_box, tipo_escala)
# updated_id = update_box(13,tipo_box, tipo_escala)





# Criar as tabelas e testar os métodos de inserção
# inserir_box("31", 1, False,5.0, "carregamento")
# inserir_box("32", 2, False,5.0, "carregamento")
# inserir_box("33", 3, False,5.0, "carregamento")
# inserir_box("34", 4, False,5.0, "carregamento")
# inserir_box("35", 5, False,5.0, "carregamento")
# inserir_box("36", 6, False,5.0, "carregamento")
# inserir_box("37", 7, False,5.0, "carregamento")
# inserir_box("38", 8, False,5.0, "carregamento")
# inserir_box("39", 9, False,5.0, "carregamento")
# inserir_box("40", 10, False,5.0, "carregamento")

# inserir_box("31A", 1, False,5.0, "filho")
# inserir_box("31B", 2, False,5.0, "filho")

# inserir_box("32A", 1, False,5.0, "filho")
# inserir_box("32B", 2, False,5.0, "filho")

# inserir_box("33A", 1, False,5.0, "filho")
# inserir_box("33B", 2, False,5.0, "filho")

# inserir_box("34A", 1, False,5.0, "filho")
# inserir_box("34B", 2, False,5.0, "filho")

# inserir_box("35A", 1, False,5.0, "filho")
# inserir_box("35B", 2, False,5.0, "filho")

# inserir_box("36A", 1, False,5.0, "filho")
# inserir_box("36B", 2, False,5.0, "filho")

# inserir_box("37A", 1, False,5.0, "filho")
# inserir_box("37B", 2, False,5.0, "filho")

# inserir_box("38A", 1, False,5.0, "filho")
# inserir_box("38B", 2, False,5.0, "filho")

# inserir_box("39A", 1, False,5.0, "filho")
# inserir_box("39B", 2, False,5.0, "filho")

# inserir_box("40A", 1, False,5.0, "filho")
# inserir_box("40B", 2, False,5.0, "filho")


# inserir_box("50", 1, False,5.0, "normal")
# inserir_box("54", 2, False,5.0, "normal")
# inserir_box("51", 3, False,5.0, "normal")
# inserir_box("55", 4, False,5.0, "normal")
# inserir_box("52", 5, False,5.0, "normal")
# inserir_box("56", 6, False,5.0, "normal")
# inserir_box("53", 7, False,5.0, "normal")
# inserir_box("57", 8, False,5.0, "normal")
# inserir_box("58", 9, False,5.0, "normal")
# inserir_box("62", 10, False,5.0, "normal")
# inserir_box("59", 11, False,5.0, "normal")
# inserir_box("63", 12, False,5.0, "normal")
# inserir_box("60", 13, False,5.0, "normal")
# inserir_box("64", 14, False,5.0, "normal")
# inserir_box("61", 15, False,5.0, "normal")
# inserir_box("65", 16, False,5.0, "normal")
# inserir_box("66", 17, False,5.0, "normal")
# inserir_box("70", 18, False,5.0, "normal")
# inserir_box("67", 19, False,5.0, "normal")
# inserir_box("71", 20, False,5.0, "normal")
# inserir_box("68", 21, False,5.0, "normal")
# inserir_box("72", 22, False,5.0, "normal")
# inserir_box("69", 23, False,5.0, "normal")
# inserir_box("73", 24, False,5.0, "normal")
# inserir_box("74", 25, False,5.0, "normal")
# inserir_box("78", 26, False,5.0, "normal")
# inserir_box("75", 27, False,5.0, "normal")
# inserir_box("79", 28, False,5.0, "normal")
# inserir_box("76", 29, False,5.0, "normal")
# inserir_box("80", 30, False,5.0, "normal")
# inserir_box("77", 31, False,5.0, "normal")
# inserir_box("81", 32, False,5.0, "normal")
# inserir_box("82", 33, False,5.0, "normal")
# inserir_box("86", 34, False,5.0, "normal")
# inserir_box("83", 35, False,5.0, "normal")
# inserir_box("87", 36, False,5.0, "normal")
# inserir_box("84", 37, False,5.0, "normal")
# inserir_box("88", 38, False,5.0, "normal")
# inserir_box("85", 39, False,5.0, "normal")
# inserir_box("89", 40, False,5.0, "normal")


# inserir_box("50A", 1, False,5.0, "filho")
# inserir_box("50B", 2, False,5.0, "filho")
# inserir_box("54A", 1, False,5.0, "filho")
# inserir_box("54B", 2, False,5.0, "filho")
# inserir_box("51A", 1, False,5.0, "filho")
# inserir_box("51B", 2, False,5.0, "filho")
# inserir_box("55A", 1, False,5.0, "filho")
# inserir_box("55B", 2, False,5.0, "filho")
# inserir_box("52A", 1, False,5.0, "filho")
# inserir_box("52B", 2, False,5.0, "filho")
# inserir_box("56A", 1, False,5.0, "filho")
# inserir_box("56B", 2, False,5.0, "filho")
# inserir_box("53A", 1, False,5.0, "filho")
# inserir_box("53B", 2, False,5.0, "filho")
# inserir_box("57A", 1, False,5.0, "filho")
# inserir_box("57B", 2, False,5.0, "filho")
# inserir_box("58A", 1, False,5.0, "filho")
# inserir_box("58B", 2, False,5.0, "filho")
# inserir_box("62A", 1, False,5.0, "filho")
# inserir_box("62B", 2, False,5.0, "filho")
# inserir_box("59A", 1, False,5.0, "filho")
# inserir_box("59B", 2, False,5.0, "filho")
# inserir_box("63A", 1, False,5.0, "filho")
# inserir_box("63B", 2, False,5.0, "filho")
# inserir_box("60A", 1, False,5.0, "filho")
# inserir_box("60B", 2, False,5.0, "filho")
# inserir_box("64A", 1, False,5.0, "filho")
# inserir_box("64B", 2, False,5.0, "filho")
# inserir_box("61A", 1, False,5.0, "filho")
# inserir_box("61B", 2, False,5.0, "filho")
# inserir_box("65A", 1, False,5.0, "filho")
# inserir_box("65B", 2, False,5.0, "filho")
# inserir_box("66A", 1, False,5.0, "filho")
# inserir_box("66B", 2, False,5.0, "filho")
# inserir_box("70A", 1, False,5.0, "filho")
# inserir_box("70B", 2, False,5.0, "filho")
# inserir_box("67A", 1, False,5.0, "filho")
# inserir_box("67B", 2, False,5.0, "filho")
# inserir_box("71A", 1, False,5.0, "filho")
# inserir_box("71B", 2, False,5.0, "filho")
# inserir_box("68A", 1, False,5.0, "filho")
# inserir_box("68B", 2, False,5.0, "filho")
# inserir_box("72A", 1, False,5.0, "filho")
# inserir_box("72B", 2, False,5.0, "filho")
# inserir_box("69A", 1, False,5.0, "filho")
# inserir_box("69B", 2, False,5.0, "filho")
# inserir_box("73A", 1, False,5.0, "filho")
# inserir_box("73B", 2, False,5.0, "filho")
# inserir_box("74A", 1, False,5.0, "filho")
# inserir_box("74B", 2, False,5.0, "filho")
# inserir_box("78A", 1, False,5.0, "filho")
# inserir_box("78B", 2, False,5.0, "filho")
# inserir_box("75A", 1, False,5.0, "filho")
# inserir_box("75B", 2, False,5.0, "filho")
# inserir_box("79A", 1, False,5.0, "filho")
# inserir_box("79B", 2, False,5.0, "filho")
# inserir_box("76A", 1, False,5.0, "filho")
# inserir_box("76B", 2, False,5.0, "filho")
# inserir_box("80A", 1, False,5.0, "filho")
# inserir_box("80B", 2, False,5.0, "filho")
# inserir_box("77A", 1, False,5.0, "filho")
# inserir_box("77B", 2, False,5.0, "filho")
# inserir_box("81A", 1, False,5.0, "filho")
# inserir_box("81B", 2, False,5.0, "filho")
# inserir_box("82A", 1, False,5.0, "filho")
# inserir_box("82B", 2, False,5.0, "filho")
# inserir_box("86A", 1, False,5.0, "filho")
# inserir_box("86B", 2, False,5.0, "filho")
# inserir_box("83A", 1, False,5.0, "filho")
# inserir_box("83B", 2, False,5.0, "filho")
# inserir_box("87A", 1, False,5.0, "filho")
# inserir_box("87B", 2, False,5.0, "filho")
# inserir_box("84A", 1, False,5.0, "filho")
# inserir_box("84B", 2, False,5.0, "filho")
# inserir_box("88A", 1, False,5.0, "filho")
# inserir_box("88B", 2, False,5.0, "filho")
# inserir_box("85A", 1, False,5.0, "filho")
# inserir_box("85B", 2, False,5.0, "filho")
# inserir_box("89A", 1, False,5.0, "filho")
# inserir_box("89B", 2, False,5.0, "filho")


# inserir_grupo("501", 1, False,5.0)
# inserir_grupo("511", 2, False,5.0)
# inserir_grupo("521", 3, False,5.0)
# inserir_grupo("531", 4, False,5.0)
# inserir_grupo("581", 5, False,5.0)
# inserir_grupo("591", 6, False,5.0)
# inserir_grupo("601", 7, False,5.0)
# inserir_grupo("611", 8, False,5.0)
# inserir_grupo("661", 9, False,5.0)
# inserir_grupo("671", 10, False,5.0)
# inserir_grupo("681", 11, False,5.0)
# inserir_grupo("691", 12, False,5.0)
# inserir_grupo("741", 13, False,5.0)
# inserir_grupo("751", 14, False,5.0)
# inserir_grupo("761", 15, False,5.0)
# inserir_grupo("771", 16, False,5.0)
# inserir_grupo("821", 17, False,5.0)
# inserir_grupo("831", 18, False,5.0)
# inserir_grupo("841", 19, False,5.0)
# inserir_grupo("851", 20, False,5.0)




print("Tabelas criadas e registros inseridos com sucesso.")
