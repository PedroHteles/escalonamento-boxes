import sqlite3 from 'sqlite3';

function criarTabelaBox() {
    // Conectar ao banco de dados (ou criar um novo arquivo se não existir)
    const db = new sqlite3.Database('box_allocation.db');

    // Criar a tabela 'box' se ela não existir
    db.serialize(() => {
        db.run(`
            CREATE TABLE IF NOT EXISTS box (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                box TEXT NOT NULL,
                sequencia INTEGER NOT NULL,
                ocupado BOOLEAN NOT NULL DEFAULT 0,
                carga TEXT,
                sequencia_carga INTEGER,
                viagem_carga TEXT,
                volume REAL NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('carregamento','normal','filho','grupo')),
                id_pai INTEGER,
                id_grupo INTEGER,
                FOREIGN KEY (id_pai) REFERENCES box (id),
                FOREIGN KEY (id_grupo) REFERENCES grupo (id)
            )
        `);

        // Criar a tabela 'grupo' se ela não existir
        db.run(`
            CREATE TABLE IF NOT EXISTS grupo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                box TEXT NOT NULL,
                carga TEXT,
                sequencia_carga INTEGER,
                viagem_carga TEXT,
                volume REAL NOT NULL,
                sequencia INTEGER NOT NULL,
                ocupado BOOLEAN NOT NULL DEFAULT 0
            )
        `);

        console.log('Tabelas criadas com sucesso!');
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}

function criarTriggerBoxGrupoComTravaUpdate() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger para garantir que o box do grupo seja ocupado corretamente
        db.run(`
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
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}



function criarTriggerBoxGrupoComTrava() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que atualiza os boxes relacionados quando um grupo é ocupado
        db.run(`
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
                      WHERE id_grupo = NEW.id AND (ocupado = 1 OR carga IS NOT NULL)
                  );
            END;
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}


function criarTriggerBoxGrupoLiberaBoxes() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que libera os boxes relacionados quando um grupo é liberado
        db.run(`
            CREATE TRIGGER IF NOT EXISTS liberar_boxes_relacionados
            AFTER UPDATE OF ocupado ON grupo
            FOR EACH ROW
            WHEN NEW.ocupado = 0
            BEGIN
                UPDATE box
                SET ocupado = 0
                WHERE id_grupo = NEW.id;
            END;
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}


function criarTriggerLiberarGrupo() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que desocupa o grupo quando todos os boxes do grupo estão disponíveis
        db.run(`
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
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}

function criarTriggerOcuparGrupoSeBoxAlocado() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que ocupa o grupo quando um box do grupo recebe uma carga
        db.run(`
            CREATE TRIGGER IF NOT EXISTS ocupar_grupo_ao_alocar_carga_no_box
            AFTER UPDATE OF ocupado ON box
            FOR EACH ROW
            WHEN NEW.id_grupo IS NOT NULL AND NEW.ocupado = 1
            BEGIN
                UPDATE grupo
                SET ocupado = 1
                WHERE id = NEW.id_grupo;
            END;
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}


function criarTriggerOcuparPaiSeFilhosOcupados() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que ocupa o pai quando todos os filhos estão ocupados
        db.run(`
            CREATE TRIGGER IF NOT EXISTS ocupar_pai_quando_todos_filhos_ocupados
            AFTER UPDATE OF ocupado, carga ON box
            FOR EACH ROW
            WHEN NEW.carga IS NOT NULL AND NEW.carga != '' AND NEW.id_pai IS NOT NULL
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
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}

function criarTriggerOcuparFilhosSePaiOcupadoV3() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que ocupa os filhos quando o pai for ocupado
        db.run(`
            CREATE TRIGGER IF NOT EXISTS ocupar_filhos_quando_pai_ocupado_v3
            AFTER UPDATE OF ocupado ON box
            FOR EACH ROW
            WHEN NEW.ocupado = 0
            BEGIN
                UPDATE box
                SET ocupado = 0
                WHERE id_pai = NEW.id;
            END;
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}


function criarTriggerOcuparFilhosSePaiOcupado() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que ocupa os filhos quando o pai for ocupado
        db.run(`
            CREATE TRIGGER IF NOT EXISTS liberar_ocupar_filhos_se_pai_ocupado
            AFTER UPDATE OF ocupado ON box
            FOR EACH ROW
            WHEN NEW.ocupado = 1 AND NEW.id_pai IS NULL
            BEGIN
                UPDATE box
                SET ocupado = 1
                WHERE id_pai = NEW.id
                AND NOT EXISTS (
                    SELECT 1
                    FROM box
                    WHERE id_pai = NEW.id 
                    AND carga IS NOT NULL
                );
            END;
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}


function criarTriggerDesocuparFilhosSePaiOcupado() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    db.serialize(() => {
        // Criar a trigger que desocupa o pai quando todos os filhos estão desocupados
        db.run(`
            CREATE TRIGGER IF NOT EXISTS liberar_pai_se_filhos_desocupados
            AFTER UPDATE OF ocupado ON box
            FOR EACH ROW
            WHEN NEW.ocupado = 0 AND NEW.id_pai IS NOT NULL
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
        `, (err) => {
            if (err) {
                console.error('Erro ao criar a trigger:', err.message);
            } else {
                console.log('Trigger criada com sucesso!');
            }
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}

function apagarTriggers() {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    const triggers = [
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
    ];

    db.serialize(() => {
        triggers.forEach((trigger) => {
            db.run(`DROP TRIGGER IF EXISTS ${trigger}`, (err) => {
                if (err) {
                    console.error(`Erro ao apagar a trigger ${trigger}:`, err.message);
                } else {
                    console.log(`Trigger ${trigger} apagada com sucesso!`);
                }
            });
        });
    });

    // Fechar a conexão com o banco de dados
    db.close((err) => {
        if (err) {
            console.error('Erro ao fechar a conexão com o banco de dados:', err.message);
        } else {
            console.log('Conexão com o banco de dados fechada.');
        }
    });
}