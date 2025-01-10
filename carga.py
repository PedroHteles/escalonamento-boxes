class Carga:
    def __init__(self, carga, volume,sequencia= 0, alocada=False,forcar_escala_box_veiculo=False,grupo=None):
        self.carga = carga  # Peso da carga
        self.volume = volume  # Volume da carga
        self.alocada = alocada  # Volume da carga
        self.grupo = grupo  # Volume da carga  
        self.sequencia = sequencia  # Sequencia carregamento
        self.forcar_escala_box_veiculo = forcar_escala_box_veiculo

        
    def __repr__(self):
        return f"Carga(carga={self.carga}, volume={self.volume}, grupro={self.grupo}, alocada={self.alocada}, forcar_escala_box_veiculo={self.forcar_escala_box_veiculo}) \n"
    
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
                
def verificar_carga_alocada(cargas):
    for carga in cargas:
        if carga.alocada:
            return True
    return False

def verificar_se_alguma_carga_alocada(cargas):
    return any(carga.alocada for carga in cargas)


def verificar_se_todos_volumes_e_superior(cargas, valor):
    return all(carga.volume > valor for carga in cargas)