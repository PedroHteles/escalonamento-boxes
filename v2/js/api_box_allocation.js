import express from 'express';
import sqlite3 from 'sqlite3';
import { updateBoxes, updateGrupo, geraLogEscala, limparTabelaLog } from './update_box.js';
import { checkCarga, buscarCargasEscaladas } from './query.js';
import { separarCargas, cargaComMenorSequencia } from './Carga.js';
import { Carga } from './Carga.js';
import { calcularBoxes } from './box.js';
import cors from 'cors';
import path from 'path';

const app = express();
app.use(cors());
app.use(express.json());
const port = 5000;

// Função para verificar e processar cargas
app.post('/verificar_cargas', async (req, res) => {
    const db = new sqlite3.Database('box_allocation.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error("Erro ao conectar ao banco de dados:", err);
            return res.status(500).json({ erro: "Erro ao conectar ao banco de dados" });
        }
    });

    try {
        // Recebendo os dados como JSON
        const cargasData = req.body;

        // Validando o formato dos dados
        if (!Array.isArray(cargasData)) {
            return res.status(400).json({ erro: "O corpo da requisição deve ser uma lista de cargas" });
        }

        // Convertendo os dados para objetos
        const cargas = cargasData.map(cargaData => {

            if (cargaData.carga == null || cargaData.previsaoContainer == null || cargaData.viagem == null) {
                throw new Error('Campo obrigatório ausente');
            }
            // Criando a instância de Carga corretamente
            return new Carga(
                cargaData.carga,
                cargaData.previsaoContainer,
                cargaData.sequenciaCarregamento || 999,
                cargaData.viagem || null,
                cargaData.prioridade_carregamento || false,
                cargaData.tipo_box || null,
                false // escalada default para false
            );
        });

        // Ordenando as cargas pela sequência
        const cargasSorted = cargas.sort((a, b) => a.sequenciaCarregamento - b.sequenciaCarregamento);

        // Separando as cargas por grupo
        const cargasPorviagem = cargasSorted.reduce((acc, item) => {
            // Verifica se o 'viagem_carga' já está no acumulador
            if (!acc[item.viagem]) {
                acc[item.viagem] = [];
            }
            // Adiciona o item ao grupo correspondente
            acc[item.viagem].push(item);
            return acc;
        }, {});

        // Inicia uma transação
        await new Promise((resolve, reject) => {
            db.run("BEGIN TRANSACTION;", (err) => {
                if (err) {
                    reject(new Error(`Erro ao iniciar a transação: ${err.message}`));
                } else {
                    resolve();
                }
            });
        });

        const volumeBoxPai = 12;
        const volumeBoxFilho = 6;

        // Processa cada grupo de cargas por viagem
        for (let viagem in cargasPorviagem) {
            const grupoCargas = cargasPorviagem[viagem].sort((a, b) => a.sequenciaCarregamento - b.sequenciaCarregamento);

            const alreadyEscalated = await Promise.all(grupoCargas.map(carga => checkCarga(carga.carga)));
            if (alreadyEscalated.some(result => result)) throw new Error(`Carga já foi escalada.`);

            // Ordena o grupo de cargas pela prioridade
            let resultado = calcularBoxes(grupoCargas, volumeBoxPai, volumeBoxFilho);
            let cargasFiltradas = separarCargas(grupoCargas, volumeBoxPai, volumeBoxFilho);
            const cargaMenorSequencia = cargaComMenorSequencia(cargasFiltradas.filhosPares, cargasFiltradas.normal);


            await updateBoxes(db, cargaMenorSequencia.sort((a, b) => a.sequenciaCarregamento - b.sequenciaCarregamento), "carregamento")
                .then(() => cargaMenorSequencia.forEach(carga => { carga.escalada = true; }))

            await Promise.all(cargasFiltradas.grupo.sort((a, b) => a.sequenciaCarregamento - b.sequenciaCarregamento).map(carga =>
                updateGrupo(db, carga.carga, carga.sequenciaCarregamento, carga.viagem)
                    .then(() => carga.escalada = true)
            ));

            await updateBoxes(db, grupoCargas.filter(carga => !carga.escalada).sort((a, b) => a.sequenciaCarregamento - b.sequenciaCarregamento), "normal")
                .then(() => grupoCargas.forEach(carga => { carga.escalada = true; }))


            // await Promise.all(grupoCargas.filter(carga => !carga.escalada).sort((a, b) => a.sequenciaCarregamento - b.sequenciaCarregamento).map(carga => {
            //     console.log("carga " + carga.carga + " tipoBox " + carga.tipoBox + " sequenciaCarregamento " + carga.sequenciaCarregamento)
            //     updateBox(db, carga.carga, carga.sequenciaCarregamento, carga.viagem, carga.tipoBox, "normal")
            //         .then(() => carga.escalada = true)
            // }

            // ));

        }

        // Se tudo correr bem, comita a transação
        await new Promise((resolve, reject) => {
            db.run("COMMIT;", (err) => {
                if (err) {
                    reject(new Error(`Erro ao commitar a transação: ${err.message}`));
                } else {
                    resolve();
                }
            });
        });
        const cargasEscalada = await buscarCargasEscaladas();

        return res.status(200).json({
            carga_pre_alocada: cargasEscalada
        });

    } catch (error) {
        return res.status(500).json({ erro: error.message });
    } finally {
        db.close(); // Fecha a conexão com o banco
    }
});

// Função para verificar e processar cargas
app.post('/inserir-log', (req, res) => {

    const db = new sqlite3.Database('box_allocation.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error("Erro ao conectar ao banco de dados:", err);
            return res.status(500).json({ erro: "Erro ao conectar ao banco de dados" });
        }
    });

    const cargas = req.body; // Espera-se uma lista de objetos

    if (!Array.isArray(cargas)) {
        return res.status(400).json({ erro: "O corpo da requisição deve ser uma lista de objetos." });
    }

    try {
        // Inicia uma transação
        new Promise((resolve, reject) => {
            db.run("BEGIN TRANSACTION;", (err) => {
                if (err) {
                    reject(new Error(`Erro ao iniciar a transação: ${err.message}`));
                } else {
                    resolve();
                }
            });
        });

        for (const carga of cargas) {
            const {
                boxCarga,
                sequenciaCarregamento,
                carga: cargaDetalhes,
                sequenciaBaixa,
                viagem,
                pesoCarga,
                previsaoContainer,
            } = carga;

            geraLogEscala(
                db,
                boxCarga,
                sequenciaCarregamento,
                cargaDetalhes,
                sequenciaBaixa,
                viagem,
                pesoCarga,
                previsaoContainer
            );
        }

        // Se tudo correr bem, comita a transação
        new Promise((resolve, reject) => {
            db.run("COMMIT;", (err) => {
                if (err) {
                    reject(new Error(`Erro ao commitar a transação: ${err.message}`));
                } else {
                    resolve();
                }
            });
        });

        return res.status(200).json({});
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    } finally {
        db.close(); // Fecha a conexão com o banco
    }
});

// Rota GET para buscar cargas escaladas
app.get('/cargas-escaladas', async (req, res) => {
    try {
        const cargas = await buscarCargasEscaladas();
        res.json({
            data: cargas,
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Erro ao buscar cargas escaladas.',
        });
    }
});

app.get('/download-db', (req, res) => {

    const db = new sqlite3.Database('box_allocation.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error("Erro ao conectar ao banco de dados:", err);
            return res.status(500).json({ erro: "Erro ao conectar ao banco de dados" });
        }
    });

    const dbFilePath = path.resolve('box_allocation.db');

    // Inicia a transação antes de enviar o arquivo
    db.run("BEGIN TRANSACTION;", (err) => {
        if (err) {
            console.error('Erro ao iniciar a transação:', err);
            return res.status(500).json({ erro: 'Erro ao iniciar a transação' });
        }

        // Limpa a tabela de logs antes de enviar o arquivo
        try {
            limparTabelaLog(db);
        } catch (error) {
            // Caso haja erro na limpeza, aborta a transação e envia a resposta de erro
            db.run("ROLLBACK;", (rollbackErr) => {
                if (rollbackErr) {
                    console.error('Erro ao fazer rollback da transação:', rollbackErr);
                }
            });
            return res.status(500).json({
                message: 'Erro ao limpar tarefa.',
            });
        }

        // Envia o arquivo após a transação ser iniciada e a tabela de logs limpa
        res.download(dbFilePath, 'box_allocation.db', (err) => {
            if (err) {
                console.error('Erro ao enviar o arquivo:', err);
                // Tenta dar rollback se houver erro ao enviar o arquivo
                db.run("ROLLBACK;", (rollbackErr) => {
                    if (rollbackErr) {
                        console.error('Erro ao fazer rollback após falha no download:', rollbackErr);
                    }
                });
                return res.status(500).send('Erro ao enviar o arquivo.');
            } else {
                // Se o arquivo foi enviado com sucesso, comita a transação
                db.run("COMMIT;", (err) => {
                    if (err) {
                        console.error('Erro ao commitar a transação:', err);
                        return res.status(500).json({ erro: 'Erro ao commitar a transação' });
                    } else {
                        console.log('Transação comitada com sucesso');
                    }
                });
            }
        });
    });
});

app.listen(port, () => {
    console.log(`Server rodando na porta ${port}`);
});
