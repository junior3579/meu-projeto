from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall, executar_query_commit

apostas_bp = Blueprint('apostas', __name__)

@apostas_bp.route('/apostas', methods=['GET'])
def listar_apostas():
    apostas = executar_query_fetchall('''
        SELECT a.id, a.id_sala, a.id_usuario, u.nome, a.valor_aposta, a.status, a.resultado
        FROM apostas a
        JOIN usuarios u ON a.id_usuario = u.id
    ''')
    
    if not apostas:
        return jsonify([])
    
    apostas_list = []
    for aposta in apostas:
        apostas_list.append({
            'id': aposta[0],
            'id_sala': aposta[1],
            'id_usuario': aposta[2],
            'nome_usuario': aposta[3],
            'valor_aposta': aposta[4],
            'status': aposta[5],
            'resultado': aposta[6]
        })
    
    return jsonify(apostas_list)

@apostas_bp.route('/apostas/confirmar', methods=['POST'])
def confirmar_aposta():
    data = request.get_json()
    id_sala = data.get('id_sala')
    id_ganhador = data.get('id_ganhador')
    
    if not id_sala or not id_ganhador:
        return jsonify({'error': 'ID da sala e ID do ganhador são obrigatórios'}), 400
    
    # Verificar se sala existe
    sala = executar_query_fetchall("SELECT valor_inicial FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    valor_inicial = sala[0][0]
    
    # Verificar se ganhador existe
    saldo = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (id_ganhador,))
    if not saldo:
        return jsonify({'error': 'Ganhador não encontrado'}), 404
    
    saldo_atual = float(saldo[0][0])
    # O ganhador ganha 80% do valor total da sala (ex: sala de 10 reais, ganha 8)
    premio = round(float(valor_inicial) * 0.8, 2)
    novo_saldo = round(saldo_atual + premio, 2)
    
    # Atualizar reais do ganhador
    sucesso = executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (novo_saldo, id_ganhador))
    
    if sucesso:
        # Remover apostas da sala
        executar_query_commit("DELETE FROM apostas WHERE id_sala = %s", (id_sala,))
        
        return jsonify({
            'message': f'Jogador {id_ganhador} ganhou {premio} reais',
            'novo_saldo': novo_saldo
        })
    else:
        return jsonify({'error': 'Erro ao confirmar aposta'}), 500

