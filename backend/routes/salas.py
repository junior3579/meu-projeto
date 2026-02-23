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
    usuario_info = executar_query_fetchall("SELECT id, reais, whatsapp FROM usuarios WHERE nome = %s", (criador,))
    if not usuario_info:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    id_usuario = usuario_info[0][0]
    saldo_usuario = Decimal(str(usuario_info[0][1]))
    whatsapp = usuario_info[0][2] if usuario_info[0][2] else 'Não cadastrado'
    
    valor_inicial_validado, erro = validar_reais(valor_inicial)
    if valor_inicial_validado is None:
        return jsonify({'error': erro}), 400
    
    valor_necessario = (valor_inicial_validado / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if saldo_usuario < valor_necessario:
        return jsonify({'error': f'Saldo insuficiente. Precisa de {float(valor_necessario):.2f}'}), 400
    
    categoria_id = data.get('categoria_id')
    # Armazenar o ID do usuário na lista de jogadores em vez do nome para consistência
    sucesso = executar_query_commit(
        "INSERT INTO salas (nome_sala, valor_inicial, criador, jogadores, whatsapp, categoria_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (nome_sala, valor_inicial_validado, criador, str(id_usuario), whatsapp, categoria_id)
    )
    if sucesso:
        novos_reais = saldo_usuario - valor_necessario
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (novos_reais, id_usuario))
        
        # Notificar atualização de saldo e nova sala
        socketio = get_socketio()
        if socketio:
            socketio.emit('atualizar_saldo', {'id_usuario': id_usuario, 'novo_saldo': float(novos_reais)}, room=f"user_{id_usuario}")
            socketio.emit('atualizar_salas', {'mensagem': f'Nova sala criada: {nome_sala}'})
            
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
    if str(id_usuario) in jogadores_lista:
        return jsonify({'error': 'Você já está nesta sala'}), 400
    if len(jogadores_lista) >= 2:
        return jsonify({'error': 'Sala cheia'}), 400
        
    novos_jogadores = jogadores + f",{id_usuario}" if jogadores else str(id_usuario)
    if executar_query_commit("UPDATE salas SET jogadores = %s WHERE id_sala = %s", (novos_jogadores, id_sala)):
        novos_reais = saldo_usuario - valor_necessario
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (novos_reais, id_usuario))
        
        # Notificar atualização de saldo e entrada na sala
        socketio = get_socketio()
        if socketio:
            socketio.emit('atualizar_saldo', {'id_usuario': id_usuario, 'novo_saldo': float(novos_reais)}, room=f"user_{id_usuario}")
            socketio.emit('atualizar_salas', {'mensagem': f'Usuário entrou na sala {id_sala}'})
            
        return jsonify({'message': 'Entrou na sala', 'novos_reais': float(novos_reais)})
    return jsonify({'error': 'Erro ao entrar'}), 500

@salas_bp.route('/salas/<int:id_sala>/definir-ganhador', methods=['POST'])
def definir_ganhador_sala(id_sala):
    data = request.get_json()
    vencedor_id = data.get('vencedor_id')
    if not vencedor_id:
        return jsonify({'error': 'ID do vencedor é obrigatório'}), 400
        
    sala = executar_query_fetchall("SELECT valor_inicial, jogadores, status FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    valor_inicial = Decimal(str(sala[0][0]))
    status_atual = sala[0][2]
    
    if status_atual == 'finalizada':
        return jsonify({'error': 'Esta sala já foi finalizada'}), 400
        
    if executar_query_commit("UPDATE salas SET vencedor_id = %s, status = 'finalizada' WHERE id_sala = %s", (vencedor_id, id_sala)):
        config_casa = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'porcentagem_casa'")
        porcentagem_casa = Decimal(str(config_casa[0][0])) if config_casa else Decimal('10')
        
        # Contabilidade: 10% da casa sobre o valor total (valor_inicial)
        valor_casa = (valor_inicial * (porcentagem_casa / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        premio = valor_inicial - valor_casa
        
        # Buscar saldo atual do vencedor para notificação
        vencedor_res = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (vencedor_id,))
        saldo_vencedor_atual = Decimal(str(vencedor_res[0][0])) if vencedor_res else Decimal('0')
        novo_saldo_vencedor = saldo_vencedor_atual + premio
        
        # Atualizar saldo do vencedor
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (novo_saldo_vencedor, vencedor_id))
        
        # Atualizar cofre da casa
        executar_query_commit("UPDATE cofre_total SET valor_total = valor_total + %s, ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = 1", (valor_casa,))
        
        # Registrar no histórico do cofre
        executar_query_commit(
            "INSERT INTO cofre_historico (id_sala, valor, descricao) VALUES (%s, %s, %s)",
            (id_sala, valor_casa, f"Lucro da sala #{id_sala} ({porcentagem_casa}%)")
        )
        
        # Notificar vencedor e atualizar salas
        socketio = get_socketio()
        if socketio:
            socketio.emit('atualizar_saldo', {'id_usuario': vencedor_id, 'novo_saldo': float(novo_saldo_vencedor)}, room=f"user_{vencedor_id}")
            socketio.emit('atualizar_salas', {'mensagem': f'Ganhador definido na sala {id_sala}'})
        
        return jsonify({'message': 'Ganhador definido', 'premio': float(premio), 'valor_casa': float(valor_casa)})
    return jsonify({'error': 'Erro ao definir ganhador'}), 500

@salas_bp.route('/salas/<int:id_sala>', methods=['DELETE'])
def excluir_sala(id_sala):
    # Buscar informações da sala antes de excluir para realizar o reembolso
    sala = executar_query_fetchall("SELECT valor_inicial, jogadores, status, vencedor_id FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    valor_inicial = Decimal(str(sala[0][0]))
    jogadores_str = sala[0][1]
    status = sala[0][2]
    vencedor_id = sala[0][3]
    
    # Contar o número de jogadores
    jogadores_ids = [j.strip() for j in jogadores_str.split(",") if j.strip()] if jogadores_str else []
    numero_jogadores = len(jogadores_ids)
    
    # Se a sala não foi finalizada (não tem vencedor definido), reembolsar os jogadores
    # AGORA PERMITE EXCLUSÃO COM 2 JOGADORES (ESTORNO PARA AMBOS)
    # IMPORTANTE: O cofre não é afetado durante estorno, apenas quando o ganhador é definido
    if status != 'finalizada' and vencedor_id is None:
        if jogadores_str:
            # Cada jogador pagou metade do valor inicial
            valor_reembolso = (valor_inicial / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            for j_id in jogadores_ids:
                if j_id.isdigit():
                    # Atualizar saldo do jogador (APENAS SALDO, NÃO COFRE)
                    executar_query_commit("UPDATE usuarios SET reais = reais + %s WHERE id = %s", (valor_reembolso, int(j_id)))
                    
                    # Buscar novo saldo para notificar via socket
                    novo_saldo_res = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (int(j_id),))
                    novo_saldo = float(novo_saldo_res[0][0]) if novo_saldo_res else 0.0
                    
                    # Notificar jogador sobre o reembolso
                    socketio = get_socketio()
                    if socketio:
                        socketio.emit('atualizar_saldo', {'id_usuario': int(j_id), 'novo_saldo': novo_saldo}, room=f"user_{int(j_id)}")
                else:
                    # Caso o ID não seja numérico (nome), tenta pelo nome
                    executar_query_commit("UPDATE usuarios SET reais = reais + %s WHERE nome = %s", (valor_reembolso, j_id))
                    
                    # Notificar por nome também se possível
                    user_res = executar_query_fetchall("SELECT id, reais FROM usuarios WHERE nome = %s", (j_id,))
                    if user_res:
                        uid, u_reais = user_res[0]
                        socketio = get_socketio()
                        if socketio:
                            socketio.emit('atualizar_saldo', {'id_usuario': uid, 'novo_saldo': float(u_reais)}, room=f"user_{uid}")
    
    # Excluir a sala
    if executar_query_commit("DELETE FROM salas WHERE id_sala = %s", (id_sala,)):
        # Notificar todos os usuários sobre a atualização de salas
        socketio = get_socketio()
        if socketio:
            socketio.emit('atualizar_salas', {'mensagem': f'Sala {id_sala} foi excluída pelo administrador. Estornos processados.'})
        
        # Registrar a exclusão no histórico do cofre para auditoria (sem afetar o valor)
        if numero_jogadores > 0 and status != 'finalizada' and vencedor_id is None:
            valor_reembolso = (valor_inicial / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            executar_query_commit(
                "INSERT INTO cofre_historico (id_sala, valor, descricao) VALUES (%s, %s, %s)",
                (id_sala, 0, f"Sala #{id_sala} excluída com estorno total para {numero_jogadores} jogadores (R$ {valor_reembolso} cada)")
            )
        
        return jsonify({'message': 'Sala excluída com sucesso e valores reembolsados (se aplicável)'})
    
    return jsonify({'error': 'Erro ao excluir sala'}), 500
