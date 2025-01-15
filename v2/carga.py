class Carga:
    def __init__(self, carga, volume,sequencia= 0,grupo=None, prioridade_carregamento = False, tipo_box=None,escalada=False):
        self.carga = carga  # Peso da carga
        self.volume = volume  # Volume da carga
        self.grupo = grupo  # Volume da carga  
        self.sequencia = sequencia  # Sequencia carregamento
        self.prioridade_carregamento = prioridade_carregamento
        self.tipo_box = tipo_box
        self.escalada = escalada
        
    def __repr__(self):
        return f"Carga(carga={self.carga}, escalada={self.escalada},sequencia={self.sequencia},volume={self.volume}, grupro={self.grupo}, prioridade_carregamento={self.prioridade_carregamento}, tipo_box={self.tipo_box})\n"
       
    def to_dict(self):
        return {
            "carga": self.carga,
            "volume": self.volume,
            "sequencia": self.sequencia,
            "grupo": self.grupo,
        }

# Função para separar as cargas
def separar_cargas(cargas):
    filhos = [carga for carga in cargas if carga.tipo_box == "filho"]
    grupo = [carga for carga in cargas if carga.tipo_box == "grupo"]
    normal = [carga for carga in cargas if carga.tipo_box == "normal"]
    
    # Agrupar as cargas do tipo "filho" em pares
    filhos_pares = [filhos[i:i + 2] for i in range(0, len(filhos), 2)]
    
    return filhos_pares, grupo, normal

# Função para encontrar a carga com menor sequência e lidar com pares ou carga normal
def carga_com_menor_sequencia(filhos_pares, normal):
    # Combina todas as cargas dos filhos (pares) e normal em uma lista
    todas_as_cargas = [carga for par in filhos_pares for carga in par] + normal
    
    # Encontra a carga com a menor sequência
    carga_menor_sequencia = min(todas_as_cargas, key=lambda carga: carga.sequencia)
    
    # Verifica se a carga com menor sequência é de um par
    for par in filhos_pares:
        if carga_menor_sequencia in par:
            return par  # Retorna o par se a carga for do tipo "filho"
    
    # Se não for do tipo "filho", retorna apenas a carga normal
    return carga_menor_sequencia