export async function updateBoxes(db, cargas, tipo_escala) {
    const query = `
        UPDATE box
        SET ocupado = 1, carga = ?, sequencia_carga = ?, viagem_carga = ?
        WHERE id = (
            SELECT b.id
            FROM box b
            JOIN box b1 ON 
                CASE 
                    WHEN 'filho' = ? THEN b.id_pai = b1.id
                    ELSE b.id = b1.id
                END
            WHERE b.ocupado = 0
            AND b1.tipo = ?
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
    `;

    try {
        const results = [];

        for (const { carga, sequenciaCarregamento, viagem, tipoBox } of cargas) {
            const result = await new Promise((resolve, reject) => {
                db.run(query, [carga, sequenciaCarregamento, viagem, tipoBox, tipo_escala], function (err) {
                    if (err) {
                        reject(new Error(`Erro ao atualizar box para carga ${carga}: ${err.message}`));
                    } else {
                        resolve(this.changes); // Retorna a quantidade de linhas afetadas
                    }
                });
            });

            results.push(result); // Armazena o resultado do update
        }

        return results; // Retorna os resultados em ordem
    } catch (error) {
        throw new Error(`Erro ao executar updates: ${error.message}`);
    }
}

// Função para atualizar o estado de uma entrada na tabela 'grupo'
export async function updateGrupos(db, grupos) {
    const query = `
        UPDATE grupo 
        SET ocupado = 1
        ,carga = ? 
        ,sequencia_carga = ? 
        ,viagem_carga = ? 
        WHERE id = (
            SELECT g.id 
            FROM grupo g  
            WHERE ocupado = 0 
            ORDER BY sequencia 
            LIMIT 1
        );
    `;

    try {
        const results = [];

        for (const { carga, sequenciaCarregamento, viagem } of grupos) {
            const result = await new Promise((resolve, reject) => {
                db.run(query, [carga, sequenciaCarregamento, viagem], function (err) {
                    if (err) {
                        reject(new Error(`Erro ao executar a query para carga ${carga}: ${err.message}`));
                    } else {
                        if (this.changes > 0) {
                            console.log(`carga ${carga} atualizada com sucesso`);
                            resolve(carga); // Retorna a carga indicando sucesso
                        } else {
                            resolve(null); // Nenhum registro foi encontrado
                        }
                    }
                });
            });

            results.push(result); // Armazena o resultado da operação
        }

        return results; // Retorna os resultados em ordem
    } catch (error) {
        throw new Error(`Erro inesperado ao executar updates: ${error.message}`);
    }
}


// Função para atualizar o estado de uma entrada na tabela 'box'
export async function geraLogEscala(db, box, sequencia_carregamento, carga, sequencia_baixa, viagem, peso_carga, previsao_container) {
    // A transação começa sendo iniciada externamente, ou seja, no código que chama essa função
    const query = `
        INSERT INTO log_boxes (
            box,
            sequencia_carregamento,
            carga,
            sequencia_baixa,
            viagem,
            peso_carga,
            previsao_container,
            data_hora
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, DATETIME('now'))
        ON CONFLICT(carga) DO UPDATE SET
            box = excluded.box,
            sequencia_carregamento = excluded.sequencia_carregamento,
            sequencia_baixa = excluded.sequencia_baixa,
            viagem = excluded.viagem,
            peso_carga = excluded.peso_carga,
            previsao_container = excluded.previsao_container,
            data_hora = DATETIME('now');
    `;

    try {
        // Executa a query dentro da transação fornecida
        return new Promise((resolve, reject) => {
            db.run(query, [box, sequencia_carregamento, carga, sequencia_baixa, viagem, peso_carga, previsao_container], function (err) {
                if (err) {
                    reject(new Error(`Erro ao executar a query: ${err.message}`));
                } else {
                    if (this.changes > 0) {
                        console.log(`carga: ${this.changes}`);
                        resolve(carga); // Retorna a carga indicando sucesso
                    } else {
                        resolve(null); // Nenhum registro foi encontrado
                    }
                }
            });
        });

    } catch (error) {
        throw new Error(`Erro inesperado: ${error.message}`);
    }
}

export async function limparTabelaLog(db) {
    const query = `
       DELETE FROM log_boxes;
    `;

    try {
        // Executa a query dentro da transação fornecida
        return new Promise((resolve, reject) => {
            db.run(query, function (err) {
                if (err) {
                    reject(new Error(`Erro ao executar a query: ${err.message}`));
                } else {
                    if (this.changes > 0) {
                        console.log(`Registro(s) excluído(s): ${this.changes}`);
                        resolve(this.changes); // Retorna a quantidade de registros excluídos
                    } else {
                        resolve(null); // Nenhum registro foi excluído
                    }
                }
            });
        });

    } catch (error) {
        throw new Error(`Erro inesperado: ${error.message}`);
    }
}
