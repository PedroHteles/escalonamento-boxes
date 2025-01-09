from teste import iniciar_alocacao,alocar
from carga import Carga
from utils import plot_boxes,transformar_matriz,imprimir_tamanho_matriz
from dbUtils import atualizar_banco_com_cargas

# Definindo m e n como variáveis globais
m, n = 9, 10  # Dimensões da matriz

# Quando o script for executado, o método inicial será chamado
if __name__ == "__main__":
    iniciar_alocacao(m,n)

cargas = [ Carga(carga=6, volume=15,grupo=2), Carga(carga=13, volume=15,grupo=2),
           Carga(carga=7, volume=1,grupo=2), Carga(carga=14, volume=1,grupo=2), 
           Carga(carga=8, volume=1,grupo=2), Carga(carga=15, volume=1,grupo=2),
           Carga(carga=9, volume=1,grupo=2), Carga(carga=16, volume=1,grupo=2),
           Carga(carga=10,volume=1,grupo=2), Carga(carga=17,volume=1,grupo=2),
           Carga(carga=10,volume=1,grupo=2), Carga(carga=17,volume=1,grupo=2)]

gravou ,carga_positions,posicoes_ocupadas,cargas_nao_alocadas,matriz  = alocar(m,n, cargas,5,10)    

# if(gravou):
#     print("gravou1")
#     grupo_encontrado = next((carga.grupo for carga in cargas), None)
#     atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
# else:
#     print("nao gravou1")
    
# cargas = [ Carga(carga=20, volume=5,grupo=3), Carga(carga=22, volume=5,grupo=3),
#            Carga(carga=21, volume=1,grupo=3), Carga(carga=23, volume=1,grupo=3), ]

# gravou,posicoes_ocupadas,cargas_nao_alocadas,matriz = alocar(m,n, cargas,5,10)    

# if(gravou):
#     print("gravou2")
#     grupo_encontrado = next((carga.grupo for carga in cargas), None)
#     atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
# else:
#     print("nao gravou")

# cargas = [ Carga(carga=24, volume=12,grupo=4), Carga(carga=55, volume=1,grupo=4),
#            Carga(carga=25, volume=12,grupo=4), Carga(carga=56, volume=1,grupo=4), 
#            Carga(carga=26, volume=12,grupo=4), Carga(carga=57, volume=1,grupo=4),
#            Carga(carga=27, volume=12,grupo=4), Carga(carga=58, volume=1,grupo=4),
#            Carga(carga=28, volume=12,grupo=4), Carga(carga=59, volume=1,grupo=4),
#            Carga(carga=29, volume=12,grupo=4), Carga(carga=60, volume=1,grupo=4),
#            Carga(carga=30, volume=12,grupo=4), Carga(carga=61, volume=1,grupo=4),
#            Carga(carga=31, volume=12,grupo=4), Carga(carga=62, volume=1,grupo=4),
#            Carga(carga=32, volume=12,grupo=4), Carga(carga=63, volume=1,grupo=4),
#            Carga(carga=33, volume=12,grupo=4), Carga(carga=64, volume=1,grupo=4),
#            Carga(carga=34, volume=12,grupo=4), Carga(carga=65, volume=1,grupo=4),
#            Carga(carga=35, volume=12,grupo=4), Carga(carga=66, volume=1,grupo=4),
#            Carga(carga=36, volume=12,grupo=4), Carga(carga=67, volume=1,grupo=4),
#                       Carga(carga=30, volume=12,grupo=4), Carga(carga=61, volume=1,grupo=4),
#            Carga(carga=31, volume=12,grupo=4), Carga(carga=62, volume=1,grupo=4),
#            Carga(carga=32, volume=12,grupo=4), Carga(carga=63, volume=1,grupo=4),
#            Carga(carga=33, volume=12,grupo=4), Carga(carga=64, volume=1,grupo=4),
#            Carga(carga=34, volume=12,grupo=4), Carga(carga=65, volume=1,grupo=4),
#            Carga(carga=35, volume=12,grupo=4), Carga(carga=66, volume=1,grupo=4),
#            Carga(carga=36, volume=12,grupo=4), Carga(carga=67, volume=1,grupo=4),
#                       Carga(carga=30, volume=12,grupo=4), Carga(carga=61, volume=1,grupo=4),
#            Carga(carga=31, volume=12,grupo=4), Carga(carga=62, volume=1,grupo=4),
#            Carga(carga=32, volume=12,grupo=4), Carga(carga=63, volume=1,grupo=4),
#            Carga(carga=33, volume=12,grupo=4), Carga(carga=64, volume=1,grupo=4),
#            Carga(carga=34, volume=12,grupo=4), Carga(carga=65, volume=1,grupo=4),
#            Carga(carga=35, volume=12,grupo=4), Carga(carga=66, volume=1,grupo=4),
#            Carga(carga=36, volume=12,grupo=4), Carga(carga=67, volume=1,grupo=4),
#                       Carga(carga=30, volume=12,grupo=4), Carga(carga=61, volume=1,grupo=4),
#            Carga(carga=31, volume=12,grupo=4), Carga(carga=62, volume=1,grupo=4),
#            Carga(carga=32, volume=12,grupo=4), Carga(carga=63, volume=1,grupo=4),
#            Carga(carga=33, volume=12,grupo=4), Carga(carga=64, volume=1,grupo=4),
#            Carga(carga=34, volume=12,grupo=4), Carga(carga=65, volume=1,grupo=4),
#            Carga(carga=35, volume=12,grupo=4), Carga(carga=66, volume=1,grupo=4),
#            Carga(carga=36, volume=12,grupo=4), Carga(carga=67, volume=1,grupo=4),
#            Carga(carga=37, volume=12,grupo=4), Carga(carga=68, volume=1,grupo=4), 
#            Carga(carga=38, volume=12,grupo=4), Carga(carga=69, volume=1,grupo=4),
#            Carga(carga=39, volume=12,grupo=4), Carga(carga=70, volume=1,grupo=4),
#            Carga(carga=40, volume=12,grupo=4), Carga(carga=71, volume=1,grupo=4),
#            Carga(carga=41, volume=12,grupo=4), Carga(carga=72, volume=1,grupo=4)
#         ]

# gravou,posicoes_ocupadas,cargas_nao_alocadas,matriz = alocar(m,n, cargas,5,10)    

# if(gravou):
#     print("entrou gravou erro")
#     grupo_encontrado = next((carga.grupo for carga in cargas), None)
#     atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
# else:
#     print("nao gravou")
    
# cargas = [ Carga(carga=101, volume=1,grupo=5), Carga(carga=104, volume=1,grupo=5),
#            Carga(carga=102, volume=1,grupo=5), Carga(carga=105, volume=1,grupo=5),
#            Carga(carga=103, volume=12,grupo=5), Carga(carga=106, volume=1,grupo=5)
#         ]

# gravou,posicoes_ocupadas,cargas_nao_alocadas,matriz = alocar(m,n, cargas,5,10)    

# if(gravou):
#     grupo_encontrado = next((carga.grupo for carga in cargas), None)
#     atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
# else:
#     print("nao gravou")

# cargas = [ Carga(carga=201, volume=1,grupo=6), Carga(carga=204, volume=1,grupo=6),
#            Carga(carga=202, volume=1,grupo=6), Carga(carga=205, volume=1,grupo=6),
#            Carga(carga=203, volume=1,grupo=6), Carga(carga=206, volume=1,grupo=6)
#         ]
# gravou,posicoes_ocupadas,cargas_nao_alocadas,matriz = alocar(m,n, cargas,5,10)    

# if(gravou):
#     grupo_encontrado = next((carga.grupo for carga in cargas), None)
#     atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
# else:
#     print("nao gravou")
    
# cargas = [ Carga(carga=301, volume=1,grupo=7), Carga(carga=307, volume=1,grupo=7),
#            Carga(carga=302, volume=1,grupo=7), Carga(carga=308, volume=1,grupo=7),
#            Carga(carga=303, volume=1,grupo=7), Carga(carga=309, volume=1,grupo=7),
#            Carga(carga=304, volume=1,grupo=7), Carga(carga=310, volume=1,grupo=7),
#            Carga(carga=305, volume=1,grupo=7), Carga(carga=311, volume=1,grupo=7),
#            Carga(carga=306, volume=1,grupo=7), Carga(carga=312, volume=1,grupo=7)
#         ]
# gravou,posicoes_ocupadas,cargas_nao_alocadas,matriz = alocar(m,n, cargas,5,10)    

# if(gravou):
#     grupo_encontrado = next((carga.grupo for carga in cargas), None)
#     atualizar_banco_com_cargas(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
# else:
#     print("nao gravou")
    
# Aplicando a função
matriz_transformada = transformar_matriz(posicoes_ocupadas)
imprimir_tamanho_matriz(matriz_transformada)
plot_boxes(5,10, matriz_transformada)
plot_boxes(m,n, posicoes_ocupadas)

