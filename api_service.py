from flask  import Flask, request, jsonify
from carga import Carga
from teste import iniciar_alocacao,alocar
from utils import plot_boxes,transformar_matriz,imprimir_tamanho_matriz
from dbUtils import atualizar_banco_com_cargas


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
        # Aplicando a função
        matriz_transformada = transformar_matriz(posicoes_ocupadas)
        plot_boxes(m,n, posicoes_ocupadas)
        plot_boxes(5,10, matriz_transformada)
        
        if(gravou and carga_alocada_box_carregamento):
            return jsonify({
            "carga_alocada":  [box.to_dict() for box in carga_positions]
        }), 200
        else:
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
    app.run(debug=True)