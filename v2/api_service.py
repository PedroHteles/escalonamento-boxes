from flask  import Flask, request, jsonify,g
from carga import Carga,separar_cargas,carga_com_menor_sequencia
from box import calcular_boxes
from box_allocation import update_box,check_carga,update_grupo
import sqlite3

app = Flask(__name__)


def get_db_connection():
    """
    Função para conectar ao banco de dados SQLite.
    """
    return sqlite3.connect('box_allocation.db')

@app.before_request
def start_transaction():
    print("iniciou")
    """
    Antes de cada requisição, iniciar a transação.
    """
    g.db = get_db_connection()
    g.db.isolation_level = 'DEFERRED'  # Para SQLite, se não quiser definir explicitamente
    # Para bancos de dados que suportam o READ UNCOMMITTED:
    # g.db.execute('SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
    g.db.execute('BEGIN')  # Inicia a transação manual


@app.after_request
def manage_transaction(response):
 
    """
    Após a requisição, decide se faz o COMMIT ou ROLLBACK com base no erro.
    """
    if hasattr(g, 'db'):
        if response.status_code == 200:  # Se a resposta for 200 (sucesso)
            try:
                g.db.execute('COMMIT')  # Confirma as alterações no banco
            except sqlite3.OperationalError:
                pass  # Ignora se não houver transação ativa
        else:  # Se houver erro (não 200), faz o ROLLBACK
            try:
                g.db.execute('ROLLBACK')  # Reverte as alterações no banco
            except sqlite3.OperationalError:
                pass  # Ignora se não houver transação ativa
        g.db.close()  # Fecha a conexão com o banco de dados
    print(f"response={response}")
    return response  # Retorna a resposta ao cliente

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
                    prioridade_carregamento=carga_data['prioridade_carregamento'],
                    grupo=carga_data.get('grupo')
                )
                cargas.append(carga)
            except KeyError as e:
                return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400
         
        # Criando uma nova lista ordenada
        cargas_sorted = sorted(cargas, key=lambda carga: carga.sequencia, reverse=False)
        
        # Separando as cargas por grupo utilizando um dicionário
        cargas_por_grupo = {}

        for carga in cargas_sorted:
            grupo = carga.grupo
            if grupo not in cargas_por_grupo:
                cargas_por_grupo[grupo] = []
            cargas_por_grupo[grupo].append(carga)

        # Exemplo de como acessar as cargas por grupo
        for grupo, grupo_cargas in cargas_por_grupo.items():    
            
            lista_ordenada_escala = []
            quantidade_boxes = calcular_boxes(grupo_cargas, 12, 6)    
            filhos_pares, gp, normal = separar_cargas(grupo_cargas)
            carga_menor_sequencia = carga_com_menor_sequencia(filhos_pares, normal) #CARGA QUE VAI SER ESCALADA NO BOX CARREGAMENTO
            
            for carga_encontrada in  carga_menor_sequencia: #carga que ira para um box de carregamento
                resultado = next((carga for carga in grupo_cargas if carga.carga == carga_encontrada.carga), None)
                
                update_box(carga_encontrada.carga,carga_encontrada.tipo_box, "carregamento")
                
                if check_carga(carga_encontrada.carga):
                    raise ValueError(f"carga: {carga_encontrada.carga} ja foi escalada.") 
                               
                resultado.escalada = True            
            
            for carga_encontrada in  gp:
                resultado = next((carga for carga in grupo_cargas if carga.carga == carga_encontrada.carga), None)
                update_grupo(carga_encontrada.carga,resultado.tipo_box, "normal")
                if check_carga(carga_encontrada.carga):
                    raise ValueError(f"carga: {carga_encontrada.carga} ja foi escalada.") 
                resultado.escalada = True

            for carga_para_escalar in grupo_cargas:
                if(not carga_para_escalar.escalada):
                    update_box(carga_para_escalar.carga,carga_para_escalar.tipo_box, "normal")
                    if check_carga(carga_para_escalar.carga):
                        raise ValueError(f"carga: {carga.carga} ja foi escalada.") 
                    resultado.escalada = True

        return jsonify({
            "carga_pre_alocada":  [carga.to_dict() for carga in cargas_sorted]
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500 
    
    
if __name__ == '__main__':
    app.run(debug=False)