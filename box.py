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

    def __repr__(self):
        return f"Box(id={self.id}, ocupado={self.ocupado}, cargas={self.cargas}) \n"

    def verificar_carga(self):
        """Verifica se o box já possui alguma carga alocada."""
        return len(self.cargas) > 0  # Retorna True se houver cargas no box.
    
    def verificar_volume(self, carga):
        """Verifica se a soma do volume das cargas atuais e a carga a ser adicionada não ultrapassa o volume do box."""
        volume_total = sum(c.volume for c in self.cargas) + carga.volume
        return volume_total <= (self.volume * 2)

    def alocar_carga(self, carga):
        if len(self.cargas) < 2 and self.ocupado == False:

            if carga.volume > self.volume:
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
