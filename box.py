class Box:
    def __init__(self, linha, coluna, ocupado=False, cargas=None,volume=5, box=None):
        if cargas is None:
            cargas = []
        self.id = f"{linha}-{coluna}"  # ID único baseado nas coordenadas
        self.linha = linha
        self.coluna = coluna
        self.ocupado = ocupado
        self.cargas = cargas  # Agora, `cargas` é uma lista que pode armazenar até 2 cargas.
        self.volume = volume
        self.box = box

    def to_dict(self):
        return {
            "id": self.id,
            "box": self.box,
            "linha": self.linha,
            "coluna": self.coluna,
            "ocupado": self.ocupado,
            "volume": self.volume,
            "cargas": [carga.to_dict() for carga in self.cargas]  # Assumindo que `cargas` sejam objetos da classe Carga
        }
        
    def __repr__(self):
        return f"Box(id={self.id}, ocupado={self.ocupado}, cargas={self.cargas}, box={self.box}) \n"

    def verificar_carga(self):
        """Verifica se o box já possui alguma carga alocada."""
        return len(self.cargas) > 0  # Retorna True se houver cargas no box.
    
    def verificar_volume(self, carga,volume_parametro):

        """Verifica se a soma do volume das cargas atuais e a carga a ser adicionada não ultrapassa o volume do box."""
        volume_total = sum(c.volume for c in self.cargas) + carga.volume
        print(f"volume_total:{volume_total} volume_parametro:{volume_parametro}")
        return volume_total <= volume_parametro 

    def alocar_carga(self, carga,volume=5):
        if len(self.cargas) < 2 and self.ocupado == False:
            print(f"carga:{ carga.volume} volume:{self.volume} cargas:{len(self.cargas)}")
            if carga.volume > volume and len(self.cargas) == 0:
                self.cargas.append(carga)
                self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                return True  # Retorna True indicando que o box foi ocupado.
            else:
                print("consigo lhe ver")
                if len(self.cargas) <= 2 and carga.volume <= volume :
                    self.cargas.append(carga)
                    if len(self.cargas) == 2:
                        self.ocupado = True  # O box fica ocupado quando 2 cargas estão alocadas.
                    return True  # Retorna True indicando que o box foi ocupado.

        return False  # Retorna False caso o box não tenha sido ocupado (menos de 2 cargas).
    

    def desocupar(self):
        self.cargas = []  # Limpa a lista de cargas.
        self.ocupado = False  # Define o box como não ocupado.

def desocupar_boxes(posicoes, cargas):
    for i in range(len(posicoes)):
        for j in range(len(posicoes[i])):
            box = posicoes[i][j]
            
            # Verifica se alguma carga de 'cargas' está contida em 'box.cargas'
            if any(carga in box.cargas for carga in cargas):
                box.desocupar()
                
def preencher_parametro_box(matriz):
    # Iniciar os números para preenchimento
    numero_inicial_primeira_linha = 31
    numero_restante = 89  # Começa no maior número
    
    linhas = len(matriz)
    colunas = len(matriz[0])
    
    nova_matriz = []  # Nova matriz para armazenar os novos objetos

    # Preenchendo a primeira linha
    for i, linha in enumerate(matriz):
        nova_linha = []
        if i == 0:
            for box in linha:
                if numero_inicial_primeira_linha <= 40:
                    novo_box = Box(
                        linha=box.linha,
                        coluna=box.coluna,
                        ocupado=box.ocupado,
                        cargas=list(box.cargas),
                        volume=box.volume
                    )
                    novo_box.box = numero_inicial_primeira_linha
                    numero_inicial_primeira_linha += 1
                else:
                    novo_box = Box(
                        linha=box.linha,
                        coluna=box.coluna,
                        ocupado=box.ocupado,
                        cargas=list(box.cargas),
                        volume=box.volume
                    )
                nova_linha.append(novo_box)
            nova_matriz.append(nova_linha)
        else:
            nova_matriz.append([None] * colunas)

    # Preenchendo o restante por coluna, de baixo para cima, mas para i > 0
    for j in range(colunas):
        for i in range(linhas-1, 0, -1):  # Começa da última linha para a segunda
            box = matriz[i][j]
            if numero_restante >= 50:  # Verifica se ainda tem números no intervalo
                novo_box = Box(
                    linha=box.linha,
                    coluna=box.coluna,
                    ocupado=box.ocupado,
                    cargas=list(box.cargas),
                    volume=box.volume
                )
                novo_box.box = numero_restante
                numero_restante -= 1  # Decrementa o número
            else:
                novo_box = Box(
                    linha=box.linha,
                    coluna=box.coluna,
                    ocupado=box.ocupado,
                    cargas=list(box.cargas),
                    volume=box.volume
                )
            nova_matriz[i][j] = novo_box


    return nova_matriz
