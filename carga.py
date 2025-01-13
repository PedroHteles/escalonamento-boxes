class Carga:
    def __init__(self, carga, volume,sequencia= 0, alocada=False,forcar_escala_box_veiculo=False,grupo=None,box=None):
        if box is None:
            box = []
        self.carga = carga  # Peso da carga
        self.volume = volume  # Volume da carga
        self.alocada = alocada  # Volume da carga
        self.grupo = grupo  # Volume da carga  
        self.sequencia = sequencia  # Sequencia carregamento
        self.forcar_escala_box_veiculo = forcar_escala_box_veiculo
        self.box = box

        
    def __repr__(self):
        return f"Carga(carga={self.carga}, volume={self.volume}, grupro={self.grupo}, alocada={self.alocada}, forcar_escala_box_veiculo={self.forcar_escala_box_veiculo} , box={self.box}) \n"
    
    def to_dict(self):
        return {
            "carga": self.carga,
            "volume": self.volume,
            "alocada": self.alocada,
            "grupo": self.grupo,
        }
        
    def forcar_escala(self):
        self.alocada = False
        self.forcar_escala_box_veiculo = True
        
    def desocupar(self):
        self.alocada = False
        
        
    def alocar_box(self, carga):
       self.box.append(carga)

    def atualizar_box(self, id_box, novo_box):
        """Método para atualizar o box com o id especificado."""
        # Verifica se o box já existe na lista de boxes da carga
        for idx, box in enumerate(self.box):
            if box.id == id_box:  # Supondo que o box tenha um atributo `id`
                self.box[idx] = novo_box  # Atualiza o box com o novo box
                return
        # Se o box não foi encontrado, adiciona um novo
        self.box.append(novo_box)
                
def verificar_carga_alocada(cargas):
    for carga in cargas:
        if carga.alocada:
            return True
    return False

def verificar_se_alguma_carga_alocada(cargas):
    return any(carga.alocada for carga in cargas)


def verificar_se_todos_volumes_e_superior(cargas, valor):
    return all(carga.volume > valor for carga in cargas)