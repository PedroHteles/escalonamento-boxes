class Carga:
    def __init__(self, carga, volume,sequencia= 0, alocada=False,grupo=None):
        self.carga = carga  # Peso da carga
        self.volume = volume  # Volume da carga
        self.alocada = alocada  # Volume da carga
        self.grupo = grupo  # Volume da carga  
        self.sequencia = sequencia  # Sequencia carregamento

    def __repr__(self):
        return f"Carga(carga={self.carga}, volume={self.volume}, grupro={self.grupo})"
    
    def to_dict(self):
        return {
            "carga": self.carga,
            "volume": self.volume,
            "alocada": self.alocada,
            "grupo": self.grupo,
        }

def verificar_carga_alocada(cargas):
    for carga in cargas:
        if carga.alocada:
            return True
    return False

def verificar_se_alguma_carga_alocada(cargas):
    return any(carga.alocada for carga in cargas)

