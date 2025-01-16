import express from 'express';
import sqlite3 from 'sqlite3';
import { updateBox, updateGrupo } from './update_box.js';
import { checkCarga } from './query.js';
import { separarCargas, cargaComMenorSequencia } from './Carga.js';
import { Carga } from './Carga.js';
import { calcularBoxes } from './box.js';

const app = express();
const port = 3000;

app.use(express.json()); // Para que o Express entenda requisições JSON

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

            if (!cargaData.carga || !cargaData.volume || !cargaData.sequencia || !cargaData.viagem_carga) {
                throw new Error('Campo obrigatório ausente');
            }
            // Criando a instância de Carga corretamente
            return new Carga(
                cargaData.carga,
                cargaData.volume,
                cargaData.sequencia,
                cargaData.viagem_carga || null,
                cargaData.prioridade_carregamento || false,
                cargaData.tipo_box || null,
                false // escalada default para false
            );
        });

        // Ordenando as cargas pela sequência
        const cargasSorted = cargas.sort((a, b) => a.sequencia - b.sequencia);

        // Separando as cargas por grupo
        const cargasPorViagemCarga = cargasSorted.reduce((acc, item) => {
            // Verifica se o 'viagem_carga' já está no acumulador
            if (!acc[item.viagemCarga]) {
                acc[item.viagemCarga] = [];
            }
            // Adiciona o item ao grupo correspondente
            acc[item.viagemCarga].push(item);
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
        for (let viagemCarga in cargasPorViagemCarga) {
            const grupoCargas = cargasPorViagemCarga[viagemCarga];

            // Ordena o grupo de cargas pela prioridade
            let resultado = calcularBoxes(grupoCargas, volumeBoxPai, volumeBoxFilho);
            let cargasFiltradas = separarCargas(grupoCargas, volumeBoxPai, volumeBoxFilho);
            const cargaMenorSequencia = cargaComMenorSequencia(cargasFiltradas.filhosPares, cargasFiltradas.normal);

            for (let carga of cargaMenorSequencia) {
                const result = await checkCarga(carga.carga)
                if (result) throw new Error(`Carga ${carga.carga} já foi escalada.`);
                await updateBox(db, carga.carga, carga.sequencia, carga.viagemCarga, carga.tipoBox, "carregamento");
                carga.escalada = true
            }

            for (let carga of cargasFiltradas.grupo) {

                const result = await checkCarga(carga.carga)
                if (result) throw new Error(`Carga ${carga.carga} já foi escalada.`);
                await updateGrupo(db, carga.carga, carga.sequencia, carga.viagemCarga);
                carga.escalada = true
            }

            for (let carga of grupoCargas) {
                if (!carga.escalada) {
                    const result = await checkCarga(carga.carga)
                    if (result) throw new Error(`Carga ${carga.carga} já foi escalada.`);
                    await updateBox(db, carga.carga, carga.sequencia, carga.viagemCarga, carga.tipoBox, "normal");
                    carga.escalada = true
                }
            }
        }

        // Se tudo correr bem, comita a transação
        await new Promise((resolve, reject) => {
            db.run("COMMIT;", (err) => {
                if (err) {
                    reject(new Error(`Erro ao commitar a transação: ${err.message}`));
                } else {
                    console.log("commitou")
                    resolve();
                }
            });
        });

        return res.status(200).json({
            carga_pre_alocada: cargasSorted
        });

    } catch (error) {
        return res.status(500).json({ erro: error.message });
    } finally {
        db.close(); // Fecha a conexão com o banco
    }
});

app.listen(port, () => {
    console.log(`Server rodando na porta ${port}`);
});
