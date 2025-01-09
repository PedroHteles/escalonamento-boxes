from pulp import LpProblem, LpVariable, LpMinimize
from carga import verificar_carga_alocada,verificar_se_alguma_carga_alocada
from box import Box
from dbUtils import criar_tabelas,contar_boxes_desocupados,inserir_boxes,recuperar_matriz,verificar_cargas_gravadas

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


def alocar_em_linhas_impares(carga, linha_atual, coluna_atual, m, posicoes_ocupadas, prob, C,volume = 5):
    """
    Tenta alocar a carga em uma linha ímpar e na linha sucessora (caso estejam disponíveis).
    Retorna a posição atual (linha, coluna) e um booleano indicando se a alocação foi bem-sucedida.
    """
    while not carga.alocada:
        
        if linha_atual >= m or (linha_atual == m - 1 and coluna_atual < 0):
            print("Passamos da última posição da matriz. Encerrando o loop.")
            break
        
        if linha_atual % 2 == 1 and not posicoes_ocupadas[linha_atual][coluna_atual].ocupado:
            # Verifica se a linha sucessora está disponível
            if linha_atual + 1 <= m and not posicoes_ocupadas[linha_atual + 1][coluna_atual].ocupado:
                # Tenta alocar a carga nas duas linhas
                if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga,volume) and \
                   posicoes_ocupadas[linha_atual + 1][coluna_atual].alocar_carga(carga,volume):

                    prob += C[linha_atual][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual}_{coluna_atual}"
                    prob += C[linha_atual + 1][coluna_atual] == 1, f"Carga_na_posicao_{linha_atual + 1}_{coluna_atual}"
                    carga.alocada = True
                    return carga,prob, linha_atual, coluna_atual, True
                
        # Verifica se a linha atual é a última        
        ultima_linha = linha_atual == m - 1        
        # Avança para a próxima linha
        linha_atual,coluna_atual =  mover_linha(not ultima_linha ,linha_atual, coluna_atual, m )
    return carga,prob, linha_atual, coluna_atual, False


def alocar_cargas(m, n, cargas, posicoes_iniciais_ocupadas=None,volume=5,volume_box_duplo = 5):
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

    linha_atual, coluna_atual = 0, n - 1
    primeira_carga_alocada = False 
    teste = False
    qtd_carga_alocada = 0

    for carga in cargas:
        while not carga.alocada:
           
            if linha_atual >= m or (linha_atual == m - 1 and coluna_atual < 0):
                print("Passamos da última posição da matriz. Encerrando o loop.")
                break
            posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado

            if ( linha_atual < m and coluna_atual >= 0 and not posicao_atual_ocupada ) : 
              
                if not posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga,volume_box_duplo) :

                    carga, prob, linha_atual, coluna_atual, sucesso = alocar_em_linhas_impares(
                        carga, 0, n - 1, m, posicoes_ocupadas, prob, C,volume
                    )
                    
                    if sucesso:
                        qtd_carga_alocada += 1
                        break  # Sai do loop se a alocação foi bem-sucedida
                else: 
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
                            if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga,volume):
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
                            if( not primeira_carga_alocada or not verificar_carga_alocada(cargas)):
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

    # Coletar as posições específicas das cargas recebidas no parâmetro
    carga_positions = []
    for i in range(m):
        for j in range(n):
            # Filtrar apenas as cargas recebidas como parâmetro
            for carga in posicoes_ocupadas[i][j].cargas:
                if carga in cargas:
                    carga_positions.append(posicoes_ocupadas[i][j])
                    posicoes_ocupadas[i][j].ocupado = True  # Marca como ocupado

    cargas_nao_alocadas = [carga for carga in cargas if not carga.alocada]
    return carga_positions, posicoes_ocupadas, qtd_carga_alocada,cargas_nao_alocadas


def iniciar_alocacao(m,n):
    criar_tabelas()
    matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
    inserir_boxes(matriz_inicial)

def alocar(m,n, cargas,volume, volume_box_duplo):    
    matriz = recuperar_matriz(m, n)
    cargas_filtradas = verificar_cargas_gravadas(cargas)
    carga_positions, posicoes_ocupadas ,qtd_carga_alocada,cargas_nao_alocadas  = alocar_cargas(m, n, cargas_filtradas, matriz,volume,volume_box_duplo)
    
    print(f"cargas_nao_alocadas:{cargas_nao_alocadas} cargas_filtradas:{(not len(cargas_filtradas) == 0)}")
    gravou = (( qtd_carga_alocada <= contar_boxes_desocupados()) ) and (not len(cargas_filtradas) == 0) and len(cargas_nao_alocadas) == 0
    return gravou ,carga_positions,posicoes_ocupadas,cargas_nao_alocadas,matriz 

