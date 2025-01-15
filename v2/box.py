class Box:
    def __init__(self,tipo,  ocupado=False, cargas=None):
        if cargas is None:
            cargas = []
        self.ocupado = ocupado
        self.tipo = tipo
        self.cargas = cargas  # Agora, `cargas` é uma lista que pode armazenar até 2 cargas.

    def to_dict(self):
        return {
            "ocupado": self.ocupado,
            "tipo": self.tipo,
            "cargas": [carga.to_dict() for carga in self.cargas]  # Assumindo que `cargas` sejam objetos da classe Carga
        }
        
    def __repr__(self):
        return f"Box(id={self.id}, ocupado={self.ocupado}, cargas={self.cargas}, box={self.box}) \n"

    def alocar_carga(self, carga,volume=5):
        if len(self.cargas) < 2 and self.ocupado == False:
            if carga.volume > volume and len(self.cargas) == 0:
                self.cargas.append(carga)
                self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                return True  # Retorna True indicando que o box foi ocupado.
            else:
                if len(self.cargas) <= 2 and carga.volume <= volume :
                    self.cargas.append(carga)
                    if len(self.cargas) == 2:
                        self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                        return True  # Retorna True indicando que o box foi ocupado.
                    return False

        return False  # Retorna False caso o box não tenha sido ocupado (menos de 2 cargas).
    
    def verificar_volume(self, carga,volume_parametro):

        """Verifica se a soma do volume das cargas atuais e a carga a ser adicionada não ultrapassa o volume do box."""
        volume_total = sum(c.volume for c in self.cargas) + carga.volume
        return volume_total > volume_parametro 
    
    
def calcular_boxes(cargas, volume_box_pai, volume_box_filho):
    """
    Método para calcular a quantidade de boxes necessários para alocar todas as cargas,
    dado o volume de cada box pai e filho.
    :param cargas: lista de objetos Carga.
    :param volume_box_pai: volume de cada box pai.
    :param volume_box_filho: volume de cada box filho.
    :return: Quantidade de boxes usados (pais e filhos).
    """
    # Inicializando a lista de boxes e o contador de boxes usados
    boxes_usados = 0
    box_pai = Box(tipo='Pai')
    box_filho = Box(tipo='Filho')

    for carga in cargas:
        if box_pai.verificar_volume(carga,volume_box_pai):
            carga.tipo_box = "grupo"
            boxes_usados += 1
        elif box_filho.alocar_carga(carga, volume_box_filho):
            if(len(box_filho.cargas) == 1):
                carga.tipo_box= "normal"
            else: 
                carga.tipo_box= "filho" 
            box_filho = Box(tipo='Filho')
            boxes_usados += 1
        else:
            carga.tipo_box= "filho" 
    return boxes_usados
