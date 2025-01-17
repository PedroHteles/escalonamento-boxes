// Carga.js
class Carga {
    constructor(carga, previsaoContainer, sequenciaCarregamento = 0, viagem = null, prioridadeCarregamento = false, tipoBox = null, escalada = false, alocada = false) {
        this.carga = carga;  // Peso da carga
        this.previsaoContainer = previsaoContainer;  // Volume da carga
        this.viagem = viagem;  // Viagem da carga
        this.sequenciaCarregamento = sequenciaCarregamento;  // Sequência do carregamento
        this.prioridadeCarregamento = prioridadeCarregamento;  // Se tem prioridade no carregamento
        this.tipoBox = tipoBox;  // Tipo do box (será preenchido na alocação)
        this.escalada = escalada;  // Se é escalada
        this.alocada = alocada;  // Se é escalada
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

    // Verifica se há cargas para processar
    if (todasAsCargas.length === 0) {
        return []; // Retorna uma lista vazia se não houver cargas
    }

    // Encontra a carga com a menor sequência
    let cargaMenorSequencia = todasAsCargas.reduce((menor, cargaAtual) =>
        cargaAtual.sequenciaCarregamento < menor.sequenciaCarregamento ? cargaAtual : menor
    );

    // Verifica se a carga com menor sequência pertence a um par
    for (const par of filhosPares) {
        if (par.includes(cargaMenorSequencia)) {
            return par; // Retorna o par como está
        }
    }

    // Se não pertencer a um par, retorna a carga individual dentro de uma lista
    return [cargaMenorSequencia];
}



// Exportando a classe Carga
export { Carga };
