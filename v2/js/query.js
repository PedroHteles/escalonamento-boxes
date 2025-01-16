import sqlite3 from 'sqlite3';


export function checkCarga(carga) {
    const query = `
    SELECT b.carga
      FROM box b
    WHERE b.carga = ?
    UNION ALL
    SELECT g.carga
      FROM grupo g
    WHERE g.carga = ?
    LIMIT 1;
  `;

    return new Promise((resolve, reject) => {
        // Conecta ao banco de dados SQLite
        const db = new sqlite3.Database('box_allocation.db', (err) => {
            if (err) {
                console.error('Erro ao conectar ao banco de dados:', err.message);
                reject(false);
            }
        });

        // Executa a consulta com o valor de carga fornecido
        db.get(query, [carga, carga], (err, row) => {
            if (err) {
                console.error('Erro ao consultar o banco de dados:', err.message);
                reject(false);
            } else {
                // Retorna true se algum valor foi encontrado, caso contrário, false
                resolve(row !== undefined);
            }

            // Fecha a conexão com o banco de dados
            db.close((closeErr) => {
                if (closeErr) {
                    console.error('Erro ao fechar o banco de dados:', closeErr.message);
                }
            });
        });
    });
}


export function buscarCargasEscaladas() {
    const query = `
      SELECT id,
             box,
             carga,
             viagem_carga,
             sequencia_carga
      FROM grupo
      WHERE ocupado > 0 AND carga IS NOT NULL
      UNION ALL
      SELECT id,
             box,
             carga,
             viagem_carga,
             sequencia_carga
      FROM box
      WHERE ocupado > 0 
        AND tipo IN ('normal', 'carregamento', 'filho') 
        AND carga IS NOT NULL
      ORDER BY viagem_carga, sequencia_carga;
    `;

    return new Promise((resolve, reject) => {
        // Conecta ao banco de dados SQLite
        const db = new sqlite3.Database('box_allocation.db', (err) => {
            if (err) {
                console.error('Erro ao conectar ao banco de dados:', err.message);
                reject([]);
            }
        });

        // Executa a consulta
        db.all(query, [], (err, rows) => {
            if (err) {
                console.error('Erro ao executar a consulta:', err.message);
                reject([]);
            } else {
                // Transforma os resultados em uma lista de objetos
                const result = rows.map((row) => ({
                    id: row.id,
                    box: row.box,
                    carga: row.carga,
                    viagemCarga: row.viagem_carga,
                    sequenciaCarga: row.sequencia_carga,
                }));
                resolve(result);
            }

            // Fecha a conexão com o banco de dados
            db.close((closeErr) => {
                if (closeErr) {
                    console.error('Erro ao fechar o banco de dados:', closeErr.message);
                }
            });
        });
    });
}

