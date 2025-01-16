import sqlite3 from 'sqlite3';

function inserirBox(box, sequencia, ocupado, volume, tipo, carga = null, sequencia_carga = null, viagem_carga = null, id_pai = null, id_grupo = null) {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    const query = `
        INSERT INTO box (box, sequencia, ocupado, carga, sequencia_carga, viagem_carga, volume, tipo, id_pai, id_grupo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(query, [box, sequencia, ocupado, carga, sequencia_carga, viagem_carga, volume, tipo, id_pai, id_grupo], function (err) {
        if (err) {
            console.error('Erro ao inserir box:', err.message);
        } else {
            console.log(`Box inserido com sucesso! ID do novo box: ${this.lastID}`);
        }
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

function inserirGrupo(box, sequencia, ocupado, volume, carga = null, sequencia_carga = null, viagem_carga = null) {
    // Conectar ao banco de dados
    const db = new sqlite3.Database('box_allocation.db');

    const query = `
        INSERT INTO grupo (box, sequencia, ocupado, carga, sequencia_carga, viagem_carga, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(query, [box, sequencia, ocupado, carga, sequencia_carga, viagem_carga, volume], function (err) {
        if (err) {
            console.error('Erro ao inserir grupo:', err.message);
        } else {
            console.log(`Grupo inserido com sucesso! ID do novo grupo: ${this.lastID}`);
        }
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