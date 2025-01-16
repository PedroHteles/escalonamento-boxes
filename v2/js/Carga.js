// Carga.js
class Carga {
    constructor(carga, volume, sequencia = 0, viagemCarga = null, prioridadeCarregamento = false, tipoBox = null, escalada = false) {
        this.carga = carga;  // Peso da carga
        this.volume = volume;  // Volume da carga
        this.viagemCarga = viagemCarga;  // Viagem da carga
        this.sequencia = sequencia;  // Sequência do carregamento
        this.prioridadeCarregamento = prioridadeCarregamento;  // Se tem prioridade no carregamento
        this.tipoBox = tipoBox;  // Tipo do box (será preenchido na alocação)
        this.escalada = escalada;  // Se é escalada
    }
}

export function separarCargas(cargas) {
    // Separando as cargas pelos tipos
    const filhos = cargas.filter(carga => carga.tipoBox === "filho");
    const grupo = cargas.filter(carga => carga.tipoBox === "grupo");
    const normal = cargas.filter(carga => carga.tipoBox === "normal");

    // Agrupando as cargas do tipo "filho" em pares
    const filhosPares = [];
    for (let i = 0; i < filhos.length; i += 2) {
        filhosPares.push(filhos.slice(i, i + 2));
    }

    return { filhosPares, grupo, normal };
}


export function cargaComMenorSequencia(filhosPares, normal) {
    // Combina todas as cargas dos filhos (pares) e normal em uma lista
    const todasAsCargas = filhosPares.flat().concat(normal);

    // Encontra a carga com a menor sequência
    let cargaMenorSequencia = todasAsCargas.reduce((menor, cargaAtual) =>
        cargaAtual.sequencia < menor.sequencia ? cargaAtual : menor
    );

    // Verifica se a carga com menor sequência pertence a um par
    for (const par of filhosPares) {
        if (par.includes(cargaMenorSequencia)) {
            return par; // Retorna o par se a carga for do tipo "filho"
        }
    }

    // Se não pertencer a um par, retorna apenas a carga normal
    return cargaMenorSequencia;
}


// Exportando a classe Carga
export { Carga };
