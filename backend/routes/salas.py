from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall, executar_query_commit
from backend.socketio_instance import get_socketio
from decimal import Decimal, ROUND_HALF_UP

salas_bp = Blueprint('salas', __name__)

def validar_reais(reais):
    try:
        reais_val = Decimal(str(reais))
        if reais_val <= 0:
            return None, "O valor de reais deve ser maior que 0"
        return reais_val, None
    except:
        return None, "Por favor, insira um valor válido"

def obter_jogadores(jogadores_str):
    jogadores_dict = {}
    tokens = jogadores_str.split(",") if jogadores_str else []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            res = executar_query_fetchall("SELECT nome, whatsapp FROM usuarios WHERE id = %s", (int(token),))
        else:
            res = executar_query_fetchall("SELECT nome, whatsapp FROM usuarios WHERE nome = %s", (token,))
        if res:
            nome_jogador, whatsapp = res[0]
            jogadores_dict[nome_jogador] = whatsapp if whatsapp else "Não cadastrado"
    return jogadores_dict

@salas_bp.route('/salas', methods=['GET'])
def listar_salas():
    salas = executar_query_fetchall("SELECT id_sala, nome_sala, valor_inicial, criador, jogadores, whatsapp, categoria_id FROM salas")
    if not salas:
        return jsonify([])
    salas_list = []
    for sala in salas:
        id_sala, nome_sala, valor_inicial, criador, jogadores, whatsapp, categoria_id = sala
        jogadores_dict = obter_jogadores(jogadores)
        salas_list.append({
            'id_sala': id_sala,
            'nome_sala': nome_sala,
            'valor_inicial': float(valor_inicial) if valor_inicial is not None else 0.0,
            'criador': criador,
            'jogadores': jogadores_dict,
            'whatsapp': whatsapp,
            'categoria_id': categoria_id
        })
    return jsonify(salas_list)

@salas_bp.route('/salas', methods=['POST'])
def criar_sala():
    data = request.get_json()
    nome_sala = data.get('nome_sala')
    valor_inicial = data.get('valor_inicial')
    criador = data.get('criador')
    if not nome_sala or not valor_inicial or not criador:
        return jsonify({'error': 'Nome da sala, valor inicial e criador são obrigatórios'}), 400
    usuario_info = executar_query_fetchall("SELECT reais, whatsapp FROM usuarios WHERE nome = %s", (criador,))
    if not usuario_info:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    saldo_usuario = Decimal(str(usuario_info[0][0]))
    whatsapp = usuario_info[0][1] if usuario_info[0][1] else 'Não cadastrado'
    valor_inicial_validado, erro = validar_reais(valor_inicial)
    if valor_inicial_validado is None:
        return jsonify({'error': erro}), 400
    valor_necessario = (valor_inicial_validado / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if saldo_usuario < valor_necessario:
        return jsonify({'error': f'Saldo insuficiente. Precisa de {float(valor_necessario):.2f}'}), 400
    categoria_id = data.get('categoria_id')
    sucesso = executar_query_commit(
        "INSERT INTO salas (nome_sala, valor_inicial, criador, jogadores, whatsapp, categoria_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (nome_sala, valor_inicial_validado, criador, criador, whatsapp, categoria_id)
    )
    if sucesso:
        novos_reais = saldo_usuario - valor_necessario
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE nome = %s", (novos_reais, criador))
        return jsonify({'message': 'Sala criada', 'novos_reais': float(novos_reais)})
    return jsonify({'error': 'Erro ao criar sala'}), 500

@salas_bp.route('/salas/<int:id_sala>/entrar', methods=['POST'])
def entrar_em_sala(id_sala):
    data = request.get_json()
    id_usuario, nome_usuario = data.get('id_usuario'), data.get('nome_usuario')
    if not id_usuario or not nome_usuario:
        return jsonify({'error': 'ID e nome obrigatórios'}), 400
    usuario_res = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (id_usuario,))
    if not usuario_res:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    saldo_usuario = Decimal(str(usuario_res[0][0]))
    sala = executar_query_fetchall("SELECT nome_sala, valor_inicial, jogadores, criador FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    nome_sala, valor_inicial, jogadores, criador = sala[0]
    valor_inicial = Decimal(str(valor_inicial))
    valor_necessario = (valor_inicial / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if saldo_usuario < valor_necessario:
        return jsonify({'error': f'Saldo insuficiente. Precisa de {float(valor_necessario):.2f}'}), 400
    jogadores_lista = jogadores.split(",") if jogadores else []
    if len(jogadores_lista) >= 2:
        return jsonify({'error': 'Sala cheia'}), 400
    novos_jogadores = jogadores + f",{id_usuario}" if jogadores else str(id_usuario)
    if executar_query_commit("UPDATE salas SET jogadores = %s WHERE id_sala = %s", (novos_jogadores, id_sala)):
        novos_reais = saldo_usuario - valor_necessario
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (novos_reais, id_usuario))
        return jsonify({'message': 'Entrou na sala', 'novos_reais': float(novos_reais)})
    return jsonify({'error': 'Erro ao entrar'}), 500

@salas_bp.route('/salas/<int:id_sala>/definir-ganhador', methods=['POST'])
def definir_ganhador_sala(id_sala):
    data = request.get_json()
    vencedor_id = data.get('vencedor_id')
    sala = executar_query_fetchall("SELECT valor_inicial, jogadores FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    valor_inicial = Decimal(str(sala[0][0]))
    if executar_query_commit("UPDATE salas SET vencedor_id = %s, status = 'finalizada' WHERE id_sala = %s", (vencedor_id, id_sala)):
        config_casa = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'porcentagem_casa'")
        porcentagem_casa = Decimal(str(config_casa[0][0])) if config_casa else Decimal('10')
        porcentagem_vencedor = (Decimal('100') - porcentagem_casa) / Decimal('100')
        premio = (valor_inicial * porcentagem_vencedor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        executar_query_commit("UPDATE usuarios SET reais = reais + %s WHERE id = %s", (premio, vencedor_id))
        executar_query_commit("DELETE FROM salas WHERE id_sala = %s", (id_sala,))
        return jsonify({'message': 'Ganhador definido', 'premio': float(premio)})
    return jsonify({'error': 'Erro ao definir ganhador'}), 500
