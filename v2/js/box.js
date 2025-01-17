class Box {
    constructor(tipo) {
        this.tipo = tipo;  // Tipo do box: 'Pai' ou 'Filho'
        this.ocupado = false;
        this.cargas = [];  // Cargas alocadas no box
    }

    alocarCarga(carga, volume) {
        if (this.cargas.length < 2 && !this.ocupado) {
            if (carga.previsaoContainer > volume && this.cargas.length === 0) {
                this.cargas.push(carga);
                this.ocupado = true;
                return true;
            } else if (this.cargas.length < 2 && carga.previsaoContainer <= volume) {
                this.cargas.push(carga);
                if (this.cargas.length === 2) {
                    this.ocupado = true;
                    return true;
                }
                return false;
            }
        }
        return false;
    }

    verificarVolume(carga, volume) {
        const volumeTotal = this.cargas.reduce((soma, cargaAtual) => soma + cargaAtual.volume, 0) + carga.previsaoContainer;
        return volumeTotal > volume;
    }
}

export function calcularBoxes(cargas, volumeBoxPai, volumeBoxFilho) {

    let boxesUsados = 0;
    let boxPai = new Box('Pai');
    let boxFilho = new Box('Filho');

    for (let carga of cargas) {
        // Verifica se a carga pode ser alocada no box pai
        if (boxPai.verificarVolume(carga, volumeBoxPai)) {
            carga.tipoBox = "grupo";
            carga.alocada = true
            boxesUsados += 1;
        }
        // Caso não possa ser alocada no box pai, tenta no box filho
        else if (boxFilho.alocarCarga(carga, volumeBoxFilho)) {
            if (boxFilho.cargas.length === 1) {
                carga.tipoBox = "normal";
                carga.alocada = true
            } else {
                carga.tipoBox = "filho";
                carga.alocada = true
            }
            boxFilho = new Box('filho');
            boxesUsados += 1;
        }
        // Caso a carga não tenha sido alocada, marca como tipo "filho"
        else {
            if (carga.previsaoContainer >= volumeBoxFilho) {
                carga.tipoBox = "normal";
                boxesUsados += 1;
            } else {
                carga.tipoBox = "filho";
            }
        }
    }

    return boxesUsados;
}