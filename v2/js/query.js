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

