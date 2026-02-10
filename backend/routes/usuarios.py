from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall, executar_query_commit, obter_proxima_posicao_vaga, reordenar_posicoes, obter_menor_id_vago

usuarios_bp = Blueprint('usuarios', __name__)

def validar_reais(reais):
    try:
        reais_int = int(reais)
        if reais_int < 0:
            return None, "O valor de reais não pode ser negativo"

        return reais_int, None
    except:
        return None, "Por favor, insira um valor válido"

@usuarios_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = executar_query_fetchall("SELECT id, nome, reais, whatsapp, posicao, pix_tipo, pix_chave, senha FROM usuarios ORDER BY posicao ASC")
    if not usuarios:
        return jsonify([])
    
    usuarios_list = []
    for u in usuarios:
        usuarios_list.append({
            'id': u[0],
            'nome': u[1],
            'reais': u[2],
            'whatsapp': u[3] if u[3] else "Não cadastrado",
            'posicao': u[4],
            'pix_tipo': u[5] if u[5] else "",
            'pix_chave': u[6] if u[6] else "",
            'senha': u[7]
        })
    
    return jsonify(usuarios_list)

@usuarios_bp.route('/usuarios', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    senha = data.get('senha')
    reais = data.get('reais')
    whatsapp = data.get('whatsapp', 'Não cadastrado')
    pix_tipo = data.get('pix_tipo', '')
    pix_chave = data.get('pix_chave', '')
    
    if not nome or not senha or reais is None:
        return jsonify({'error': 'Nome, senha e reais são obrigatórios'}), 400
    
    # Verificar se usuário já existe
    existe = executar_query_fetchall("SELECT id FROM usuarios WHERE nome = %s", (nome,))
    if existe:
        return jsonify({'error': 'Usuário já existe'}), 400
    
    # Validar reais
    reais_validos, erro = validar_reais(reais)
    if reais_validos is None:
        return jsonify({'error': erro}), 400
    
    id_vago = obter_menor_id_vago()
    posicao_vaga = id_vago

    sucesso = executar_query_commit(
        "INSERT INTO usuarios (id, nome, senha, reais, whatsapp, posicao, pix_tipo, pix_chave) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (id_vago, nome, senha, reais_validos, whatsapp, posicao_vaga, pix_tipo, pix_chave)
    )
    
    if sucesso:
        return jsonify({'message': f'Usuário {nome} cadastrado com sucesso'})
    else:
        return jsonify({'error': 'Erro ao cadastrar usuário'}), 500

@usuarios_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def editar_usuario(id_usuario):
    data = request.get_json()
    nome = data.get('nome')
    senha = data.get('senha')
    reais = data.get('reais')
    whatsapp = data.get('whatsapp')
    pix_tipo = data.get('pix_tipo')
    pix_chave = data.get('pix_chave')
    
    if not nome or not senha or reais is None:
        return jsonify({'error': 'Nome, senha e reais são obrigatórios'}), 400
    
    reais_validos, erro = validar_reais(reais)
    if reais_validos is None:
        return jsonify({'error': erro}), 400

    sucesso = executar_query_commit(
        "UPDATE usuarios SET nome = %s, senha = %s, reais = %s, whatsapp = %s, pix_tipo = %s, pix_chave = %s WHERE id = %s",
        (nome, senha, reais_validos, whatsapp, pix_tipo, pix_chave, id_usuario)
    )
    
    if sucesso:
        return jsonify({'message': 'Usuário atualizado com sucesso'})
    else:
        return jsonify({'error': 'Erro ao atualizar usuário'}), 500

@usuarios_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def remover_usuario(id_usuario):
    existe = executar_query_fetchall("SELECT * FROM usuarios WHERE id = %s", (id_usuario,))
    if not existe:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Remover referências em outras tabelas para evitar erro de Foreign Key
    try:
        # Remover apostas
        executar_query_commit("DELETE FROM apostas WHERE id_usuario = %s", (id_usuario,))
        # Remover transações
        executar_query_commit("DELETE FROM transacoes WHERE id_usuario = %s", (id_usuario,))
        # Remover participações em torneios
        executar_query_commit("DELETE FROM torneio_participantes WHERE usuario_id = %s", (id_usuario,))
        # Limpar referências em confrontos de torneios
        executar_query_commit("UPDATE torneio_confrontos SET jogador1_id = NULL WHERE jogador1_id = %s", (id_usuario,))
        executar_query_commit("UPDATE torneio_confrontos SET jogador2_id = NULL WHERE jogador2_id = %s", (id_usuario,))
        executar_query_commit("UPDATE torneio_confrontos SET vencedor_id = NULL WHERE vencedor_id = %s", (id_usuario,))
        # Limpar vencedor em torneios
        executar_query_commit("UPDATE torneios SET vencedor_id = NULL WHERE vencedor_id = %s", (id_usuario,))
        # Limpar vencedor em salas
        executar_query_commit("UPDATE salas SET vencedor_id = NULL WHERE vencedor_id = %s", (id_usuario,))
        
        # Remover usuário da lista de jogadores em salas (coluna TEXT com IDs separados por vírgula)
        # Como é uma coluna TEXT, precisamos de uma abordagem mais cuidadosa ou apenas aceitar que salas abertas ficarão inconsistentes
        # Uma solução simples é remover o ID se ele estiver sozinho ou em uma lista
        executar_query_commit("UPDATE salas SET jogadores = NULL WHERE jogadores = %s", (str(id_usuario),))
        # Para casos como "1,2", "2,1", etc, é mais complexo com SQL puro sem REGEX avançado em todas as DBs, 
        # mas como o objetivo é permitir apagar o usuário, as restrições de FK eram o maior problema.
        # A coluna 'jogadores' não tem FK, então não impede o DELETE.
        
        # Finalmente remover o usuário
        sucesso = executar_query_commit("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
        
        if sucesso:
            return jsonify({'message': f'Usuário {id_usuario} removido com sucesso'})
        else:
            return jsonify({'error': 'Erro ao remover usuário do banco de dados'}), 500
    except Exception as e:
        print(f"Erro ao remover usuário {id_usuario}: {str(e)}")
        return jsonify({'error': f'Erro ao remover usuário: {str(e)}'}), 500

@usuarios_bp.route('/usuarios/<int:id_usuario>/saldo', methods=['GET'])
def buscar_saldo_usuario(id_usuario):
    result = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (id_usuario,))
    if result:
        return jsonify({'saldo': result[0][0]})
    return jsonify({'error': 'Usuário não encontrado'}), 404
