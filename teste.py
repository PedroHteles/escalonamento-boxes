from pulp import LpProblem, LpVariable, LpMinimize
from carga import verificar_carga_alocada,verificar_se_alguma_carga_alocada,verificar_se_todos_volumes_e_superior
from box import Box,desocupar_boxes
from dbUtils import criar_tabelas,contar_boxes_desocupados,inserir_boxes,inserir_boxes_reais,recuperar_matriz,verificar_cargas_gravadas

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
                    carga.alocar_box(posicoes_ocupadas[linha_atual][coluna_atual])
                    carga.alocar_box(posicoes_ocupadas[linha_atual + 1][coluna_atual])
                    return carga,prob, linha_atual, coluna_atual, True
                
        # Verifica se a linha atual é a última        
        ultima_linha = linha_atual == m - 1        
        # Avança para a próxima linha
        linha_atual,coluna_atual =  mover_linha(not ultima_linha ,linha_atual, coluna_atual, m )
    return carga,prob, linha_atual, coluna_atual, False


def alocar_carga(carga, posicoes_ocupadas, linha_atual, coluna_atual, m, n, prob, C, volume, volume_box_duplo, cargas, primeira_carga_alocada, qtd_carga_alocada):
    teste = False

    while not carga.alocada:
        if linha_atual >= m or (linha_atual == m - 1 and coluna_atual < 0):
            print("Passamos da última posição da matriz. Encerrando o loop.")
            break

        posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado
        print(f"teste carga:{carga} :{not posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga, volume_box_duplo)}")
        if linha_atual < m and coluna_atual >= 0 and not posicao_atual_ocupada:
            if not posicoes_ocupadas[linha_atual][coluna_atual].verificar_volume(carga, volume_box_duplo) and not carga.forcar_escala_box_veiculo:
                carga, prob, linha_atual, coluna_atual, sucesso = alocar_em_linhas_impares(
                    carga, 0, n - 1, m, posicoes_ocupadas, prob, C, volume
                )

                if sucesso:
                    coluna_atual = n - 1
                    linha_atual = 0
                    qtd_carga_alocada += 1
                    break  # Sai do loop se a alocação foi bem-sucedida

            else:
                if (
                    (not primeira_carga_alocada and verificar_se_alguma_carga_alocada(cargas))
                    or primeira_carga_alocada
                    or not primeira_carga_alocada
                ):

                    
                    if (
                        not primeira_carga_alocada
                        and verificar_se_alguma_carga_alocada(cargas)
                        and teste == False
                    ):
                        coluna_atual = n - 1
                        linha_atual = 0
                        posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado
                        teste = True

                    if (
                        linha_atual < m
                        and coluna_atual >= 0
                        and (
                            not verificar_se_alguma_carga_alocada(cargas)
                            or (
                                verificar_se_alguma_carga_alocada(cargas)
                                and (
                                    (not primeira_carga_alocada and linha_atual == 0)
                                    or (primeira_carga_alocada and linha_atual >= 0)
                                )
                            )
                        )
                        and not posicao_atual_ocupada
                    ):
                        if posicoes_ocupadas[linha_atual][coluna_atual].alocar_carga(carga, volume):
                            
                            print(f"entrou aq carga:{carga} linha_atual:{linha_atual} coluna_atual:{coluna_atual}")
                            
                            prob += C[linha_atual][coluna_atual] == 1, f"Carga{carga.carga}_na_posicao_{linha_atual}_{coluna_atual}"
                            posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado

                            carga.alocada = True
                            carga.alocar_box(posicoes_ocupadas[linha_atual][coluna_atual])
                            qtd_carga_alocada += 1

                            if (
                                primeira_carga_alocada
                                and posicao_atual_ocupada
                                and not posicoes_ocupadas[linha_atual][coluna_atual - 1].ocupado
                            ):  
                                coluna_atual = n - 1
                                linha_atual = 0
                                posicao_atual_ocupada = posicoes_ocupadas[linha_atual][coluna_atual].ocupado

                            if (
                                not primeira_carga_alocada
                                and (
                                    posicao_atual_ocupada
                                    or posicoes_ocupadas[linha_atual][coluna_atual].verificar_carga()
                                )
                            ):  
                                primeira_carga_alocada = True
                        else:
                            linha_atual, coluna_atual = mover_linha(
                                verificar_carga_alocada(cargas), linha_atual, coluna_atual, m
                            )
                    else:
                        if not primeira_carga_alocada or not verificar_carga_alocada(cargas):
                            coluna_atual -= 1
                            linha_atual = 0
                        else:
                            if linha_atual == m - 1:
                                coluna_atual -= 1
                                linha_atual = 1
                            else:
                                linha_atual += 1
                else:
                    linha_atual, coluna_atual = mover_linha(
                        verificar_carga_alocada(cargas), linha_atual, coluna_atual, m
                    )
        else:
            linha_atual, coluna_atual = mover_linha(
                verificar_carga_alocada(cargas), linha_atual, coluna_atual, m
            )

    return carga, linha_atual, coluna_atual, qtd_carga_alocada, primeira_carga_alocada, prob


def alocar_cargas(m, n, cargas, posicoes_iniciais_ocupadas=None,volume=5,volume_box_duplo = 12):
    prob = LpProblem("Alocacao_de_Boxes", LpMinimize)
    C = LpVariable.dicts("Carga", (range(m), range(n)), cat="Binary")

    prob += 0  # Sem objetivo direto, as restrições determinam alocação
    if verificar_se_todos_volumes_e_superior(cargas,volume_box_duplo):
        for carga in cargas:
            if carga == min(cargas, key=lambda carga: carga.sequencia):
                carga.forcar_escala()  

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
    qtd_carga_alocada = 0

    for carga in cargas:
        carga, linha_atual, coluna_atual, qtd_carga_alocada, primeira_carga_alocada, prob = \
          alocar_carga(carga, posicoes_ocupadas, linha_atual, coluna_atual, m, n, prob, C, volume, volume_box_duplo, cargas, primeira_carga_alocada, qtd_carga_alocada)

    prob.solve()

    # Coletar as posições específicas das cargas recebidas no parâmetro
    carga_positions = []
    carga_alocada_box_carregamento=False
    for i in range(m):
        for j in range(n):
            # Filtrar apenas as cargas recebidas como parâmetro
            for carga in posicoes_ocupadas[i][j].cargas:
                if carga in cargas:
                    if(i == 0):
                        carga_alocada_box_carregamento = True
                    carga_positions.append(posicoes_ocupadas[i][j])
                    posicoes_ocupadas[i][j].ocupado = True  # Marca como ocupado

    cargas_nao_alocadas = [carga for carga in cargas if not carga.alocada]                      
    return carga_positions, posicoes_ocupadas, qtd_carga_alocada,cargas_nao_alocadas ,carga_alocada_box_carregamento


def iniciar_alocacao(m,n):
    criar_tabelas()
    matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
    inserir_boxes(matriz_inicial)

def iniciar_alocacao_reais(m,n):
    criar_tabelas()
    matriz_inicial = [[Box(i, j) for j in range(n)] for i in range(m)]
    inserir_boxes_reais(matriz_inicial)
    
    
def alocar(m,n, cargas,volume, volume_box_duplo):    
    matriz = recuperar_matriz(m, n)
    cargas_filtradas = verificar_cargas_gravadas(cargas)
    qtd_box_disponivel = contar_boxes_desocupados()
    carga_positions, posicoes_ocupadas ,qtd_carga_alocada,cargas_nao_alocadas,carga_alocada_box_carregamento  = alocar_cargas(m, n,cargas_filtradas, matriz,volume,volume_box_duplo)
    gravou = (( qtd_carga_alocada <= qtd_box_disponivel) ) and (not len(cargas_filtradas) == 0) and len(cargas_nao_alocadas) == 0
    return gravou ,carga_positions,posicoes_ocupadas,cargas_nao_alocadas,carga_alocada_box_carregamento,matriz 

