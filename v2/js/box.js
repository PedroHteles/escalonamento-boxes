class Box {
    constructor(tipo) {
        this.tipo = tipo;  // Tipo do box: 'Pai' ou 'Filho'
        this.ocupado = false;
        this.cargas = [];  // Cargas alocadas no box
    }

    alocarCarga(carga, volume) {
        if (this.cargas.length < 2 && !this.ocupado) {
            if (carga.volume > volume && this.cargas.length === 0) {
                this.cargas.push(carga);
                this.ocupado = true;
                return true;
            } else if (this.cargas.length <= 2 && carga.volume <= volume) {
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
        const volumeTotal = this.cargas.reduce((soma, cargaAtual) => soma + cargaAtual.volume, 0) + carga.volume;
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
            boxesUsados += 1;
        }
        // Caso não possa ser alocada no box pai, tenta no box filho
        else if (boxFilho.alocarCarga(carga, volumeBoxFilho)) {
            if (boxFilho.cargas.length === 1) {
                carga.tipoBox = "normal";
            } else {
                carga.tipoBox = "filho";
            }
            boxFilho = new Box('Filho');
            boxesUsados += 1;
        }
        // Caso a carga não tenha sido alocada, marca como tipo "filho"
        else {
            carga.tipoBox = "filho";
        }
    }

    return boxesUsados;
}