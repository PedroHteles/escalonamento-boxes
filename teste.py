from pulp import LpProblem, LpVariable, LpMinimize
from carga import Carga,verificar_carga_alocada,verificar_se_alguma_carga_alocada
from box import Box
from dbUtils import criar_tabelas,contar_boxes_desocupados,inserir_boxes,recuperar_matriz,verificar_cargas_gravadas
from utils import plot_boxes

def mover_linha(bolean, linha_atual, coluna_atual, m):
    if not bolean:
        coluna_atual -= 1
        linha_atual = 0
    else:
        if linha_atual == m - 1:
            coluna_atual -= 1
            linha_atual = 1
        else:
            linha_atual += 1
    return linha_atual, coluna_atual

def alocar_carga_na_posicao(carga, linha, coluna, posicoes_ocupadas, prob, C):
    """Tenta alocar uma carga em uma posição específica."""
    if not posicoes_ocupadas[linha][coluna].ocupado and posicoes_ocupadas[linha][coluna].verificar_volume(carga):
        posicoes_ocupadas[linha][coluna].alocar_carga(carga)
        prob += C[linha][coluna] == 1, f"Carga_na_posicao_{linha}_{coluna}"
        carga.alocada = True
        return True
    return False


def alocar_em_linhas_impares(carga, linha_atual, coluna_atual, m, posicoes_ocupadas, prob, C):
    print(f"chamou carga {carga} linha_atual{linha_atual} coluna_atual{coluna_atual}")
    """
    Tenta alocar a carga em uma linha ímpar e na linha sucessora (caso estejam disponíveis).
    Retorna a posição atual (linha, coluna) e um booleano indicando se a alocação foi bem-sucedida.
    """
    while not carga.alocada:
        print(f"chamou carga {carga} linha_atual{linha_atual} coluna_atual{coluna_atual}")
        if linha_atual % 2 == 1 and not posicoes_ocupadas[linha_atual][coluna_atual].ocupado:
            # Verifica se a linha sucessora está disponível
            print(f"teste {linha_atual + 1 <= m and not posicoes_ocupadas[linha_atual + 1][coluna_atual].ocupado}")
            if linha_atual + 1 <= m and not posicoes_ocupadas[linha_atual + 1][coluna_atual].ocupado:
                # Tenta alocar a carga nas duas linhas
                if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga) and \
                   posicoes_ocupadas[linha_atual + 1][coluna_atual].alocar_carga(carga):

                    print(f"alocou: {linha_atual}")
                    prob += C[linha_atual][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual}_{coluna_atual}"
                    prob += C[linha_atual + 1][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual + 1}_{coluna_atual}"
                    carga.alocada = True
                    return carga,prob, linha_atual, coluna_atual, True
                
        # Verifica se a linha atual é a última        
        ultima_linha = linha_atual == m - 1        
        # Avança para a próxima linha
        linha_atual,coluna_atual =  mover_linha(not ultima_linha ,linha_atual, coluna_atual, m )
    return carga,prob, linha_atual, coluna_atual, False


def alocar_cargas(m, n, cargas, posicoes_iniciais_ocupadas=None):
    prob = LpProblem("Alocacao_de_Boxes", LpMinimize)
    C = LpVariable.dicts("Carga", (range(m), range(n)), cat="Binary")

    prob += 0  # Sem objetivo direto, as restrições determinam alocação

    # Matriz para controlar as posições já alocadas
    posicoes_ocupadas = [
        [Box(i, j, ocupado=box.ocupado, cargas=box.cargas) for j, box in enumerate(row)] 
        for i, row in enumerate(posicoes_iniciais_ocupadas)
    ]

    if posicoes_iniciais_ocupadas:
        for i in range(m):
            for j in range(n):
                if posicoes_iniciais_ocupadas[i][j].ocupado:
                    prob += C[i][j] == 1, f"Box_{i}_{j}_ocupado"
                    posicoes_ocupadas[i][j].ocupado = True

        # Encontrando a última coluna ocupada
        ultima_coluna_ocupada = -1
        for i in range(m):
            for j in range(n):
                if posicoes_ocupadas[i][j].ocupado:
                    ultima_coluna_ocupada = max(ultima_coluna_ocupada, j)

        # Definindo a coluna atual como a próxima coluna
        if ultima_coluna_ocupada != -1:
            coluna_atual = ultima_coluna_ocupada + 1
        else:
            coluna_atual = 0             

    linha_atual, coluna_atual = 0, n - 1
    primeira_carga_alocada = False 
    teste = False
    qtd_carga_alocada = 0

    for carga in cargas:
        while not carga.alocada:
           
            posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado

            if ( linha_atual < m and coluna_atual >= 0 and not posicao_atual_ocupada ) : 
              
                if not posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga) :
                    # print("q merda {aproxima_carga_grande}")
                    # if(not aproxima_carga_grande):
                    #     print()
                    #     aproxima_carga_grande = True
                    #     coluna_atual = n - 1
                    #     linha_atual = 0  
                    #     posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado
                    # Verifica se é possível alocar em linha ímpar
                    carga, prob, linha_atual, coluna_atual, sucesso = alocar_em_linhas_impares(
                        carga, 0, n - 1, m, posicoes_ocupadas, prob, C
                    )
                    
                    if sucesso:
                        qtd_carga_alocada += 1
                        break  # Sai do loop se a alocação foi bem-sucedida
                else: 
                    print("entrou")
                    if ( not primeira_carga_alocada and  verificar_se_alguma_carga_alocada(cargas)) or primeira_carga_alocada or  not primeira_carga_alocada:
                        if(not primeira_carga_alocada and  verificar_se_alguma_carga_alocada(cargas)) and \
                            teste == False:

                            coluna_atual = n - 1
                            linha_atual = 0  
                            posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado
                            teste = True
                        
                        
                        if (linha_atual < m and 
                            coluna_atual >= 0 and 
                            (not verificar_se_alguma_carga_alocada(cargas) or 
                            (verificar_se_alguma_carga_alocada(cargas) and 
                            ((not primeira_carga_alocada and linha_atual == 0) or 
                            (primeira_carga_alocada and linha_atual >= 0)))) and 
                            not posicao_atual_ocupada):
                        
                            # Adiciona a carga ao box
                            if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga):
                                prob += C[linha_atual][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual}_{coluna_atual}"
                                posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado
                            
                            carga.alocada = True
                            qtd_carga_alocada += 1

                            if primeira_carga_alocada and posicao_atual_ocupada and \
                                posicoes_ocupadas[linha_atual][coluna_atual - 1].ocupado == False:
            
                                coluna_atual = n - 1
                                linha_atual = 0  
                                posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado

                            # Marca que a primeira carga foi alocada e reseta a coluna
                            if (not primeira_carga_alocada and \
                                (posicao_atual_ocupada or posicoes_ocupadas[linha_atual][coluna_atual].verificar_carga() )):
                                    primeira_carga_alocada = True

                        else:
                            if( not primeira_carga_alocada or  not verificar_carga_alocada(cargas)):
                                coluna_atual -= 1
                                linha_atual = 0
                            else:
                                if linha_atual == m - 1:
                                    coluna_atual -= 1
                                    linha_atual = 1
                                else:
                                    linha_atual += 1
                    else:
                        linha_atual,coluna_atual =  mover_linha(verificar_carga_alocada(cargas),linha_atual, coluna_atual, m )               
            else:
                linha_atual,coluna_atual =  mover_linha(verificar_carga_alocada(cargas) ,linha_atual, coluna_atual, m )

    prob.solve()

    carga_positions = []
    for i in range(m):
        for j in range(n):
            if len(posicoes_ocupadas[i][j].cargas) > 0:
                carga_positions.append((i, j))
                posicoes_ocupadas[i][j].ocupado = True

    return carga_positions, posicoes_ocupadas, qtd_carga_alocada


def iniciar_alocacao(m,n):
    criar_tabelas()
    matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
    inserir_boxes(matriz_inicial)


def alocar(m,n, cargas):    
    matriz = recuperar_matriz(m, n)
    cargas_filtradas = verificar_cargas_gravadas(cargas)
    _, posicoes_ocupadas,qtd_carga_alocada  = alocar_cargas(m, n, cargas_filtradas, matriz)
    gravou =  qtd_carga_alocada <= contar_boxes_desocupados()
    return gravou ,posicoes_ocupadas ,matriz

