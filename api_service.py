from flask  import Flask, request, jsonify
from carga import Carga
from teste import iniciar_alocacao,iniciar_alocacao_reais,alocar
from utils import plot_boxes,plot_boxes_v1,transformar_matriz,imprimir_tamanho_matriz,definir_pares
from dbUtils import atualizar_banco_com_cargas,atualizar_banco_com_cargas_old
from box import preencher_parametro_box


m, n = 9, 10  # Dimensões da matriz

app = Flask(__name__)

# Rota POST para receber e verificar cargas
@app.route('/verificar_cargas', methods=['POST'])
def verificar_cargas():
    try:
        # Recebendo os dados como JSON
        cargas_data = request.json

        # Validando o formato dos dados
        if not isinstance(cargas_data, list):
            return jsonify({"erro": "O corpo da requisição deve ser uma lista de cargas"}), 400

        # Convertendo os dados para objetos da classe Carga
        cargas = []
        for carga_data in cargas_data:
            try:
                carga = Carga(
                    carga=carga_data['carga'],
                    volume=carga_data['volume'],
                    sequencia=carga_data['sequencia'],
                    grupo=carga_data.get('grupo')
                )
                cargas.append(carga)
            except KeyError as e:
                return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400
         
        # Criando uma nova lista ordenada
        cargas_sorted = sorted(cargas, key=lambda carga: carga.sequencia, reverse=False)
        
        gravou ,carga_positions,posicoes_ocupadas,cargas_nao_alocadas,carga_alocada_box_carregamento,matriz = alocar(m,n, cargas_sorted,5,12)    

        print(f"alocar:{posicoes_ocupadas}")
        # Aplicando a função
        matriz_transformada = transformar_matriz(posicoes_ocupadas)
 
        print(f"matriz_transformada:{matriz_transformada}")
 
        nova_matriz = preencher_parametro_box(matriz_transformada)
    
        imprimir_tamanho_matriz(nova_matriz)
        plot_boxes(5,10, nova_matriz)
            
        ids_a_filtrar = [box.id for box in carga_positions]
        
        objetos_filtrados = [
            box
            for row in nova_matriz
            for box in row
            if box.id in ids_a_filtrar
        ]
        
        if(gravou and carga_alocada_box_carregamento):
            grupo_encontrado = next((carga.grupo for carga in cargas), None)
            atualizar_banco_com_cargas(5, 10, matriz_transformada, idGrupo=grupo_encontrado)
            atualizar_banco_com_cargas_old(m, n, posicoes_ocupadas, idGrupo=grupo_encontrado)
            return jsonify({
            "carga_pre_alocada":  [box.to_dict() for box in objetos_filtrados]
        }), 200
        else:
            plot_boxes_v1(m, n, posicoes_ocupadas)
            if(not carga_alocada_box_carregamento):
                return jsonify({
                "msg": f"Problema ao escalar box carregamento"
                }), 400
            else:
                return jsonify({
                "msg": f"Para alocar necessita de {len(cargas_nao_alocadas)} boxes disponiveis!"
                }), 400

        # Retornando a resposta


    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    print("entrou")
    iniciar_alocacao(m,n)
    iniciar_alocacao_reais(5,10)
    app.run(debug=True)