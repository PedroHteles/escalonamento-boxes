class Box:
    def __init__(self, linha, coluna, ocupado=False, cargas=None,volume=5):
        if cargas is None:
            cargas = []
        self.id = f"{linha}-{coluna}"  # ID único baseado nas coordenadas
        self.linha = linha
        self.coluna = coluna
        self.ocupado = ocupado
        self.cargas = cargas  # Agora, `cargas` é uma lista que pode armazenar até 2 cargas.
        self.volume = volume

    def to_dict(self):
        return {
            "id": self.id,
            "linha": self.linha,
            "coluna": self.coluna,
            "ocupado": self.ocupado,
            "volume": self.volume,
            "cargas": [carga.to_dict() for carga in self.cargas]  # Assumindo que `cargas` sejam objetos da classe Carga
        }
        
    def __repr__(self):
        return f"Box(id={self.id}, ocupado={self.ocupado}, cargas={self.cargas}) \n"

    def verificar_carga(self):
        """Verifica se o box já possui alguma carga alocada."""
        return len(self.cargas) > 0  # Retorna True se houver cargas no box.
    
    def verificar_volume(self, carga,volume):
        """Verifica se a soma do volume das cargas atuais e a carga a ser adicionada não ultrapassa o volume do box."""
        volume_total = sum(c.volume for c in self.cargas) + carga.volume
        return volume_total <= volume 

    def alocar_carga(self, carga,volume=5):
        if len(self.cargas) < 2 and self.ocupado == False:

            if carga.volume > volume:
                self.cargas.append(carga)
                self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                return True  # Retorna True indicando que o box foi ocupado.
            else:
                if len(self.cargas) <= 2:
                    self.cargas.append(carga)
                    if len(self.cargas) == 2:
                        self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                        return True  # Retorna True indicando que o box foi ocupado.

        return False  # Retorna False caso o box não tenha sido ocupado (menos de 2 cargas).
