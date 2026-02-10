from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall, executar_query_commit
from backend.socketio_instance import get_socketio

salas_bp = Blueprint('salas', __name__)

def validar_reais(reais):
    try:
        reais_val = float(reais)
        if reais_val < 5:
            return None, "O valor mínimo para criar uma sala é R$ 5,00"
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
        # Tentar buscar por ID (se for número) ou por Nome
        if token.isdigit():
            res = executar_query_fetchall("SELECT nome, whatsapp FROM usuarios WHERE id = %s", (int(token),))
        else:
            res = executar_query_fetchall("SELECT nome, whatsapp FROM usuarios WHERE nome = %s", (token,))
        
        if res:
            nome_jogador, whatsapp = res[0]
            # Sempre incluir o jogador, mesmo que o whatsapp seja "Não cadastrado"
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
            'valor_inicial': valor_inicial,
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
    
    # Verificar se usuário existe e buscar saldo e whatsapp
    usuario_info = executar_query_fetchall("SELECT reais, whatsapp FROM usuarios WHERE nome = %s", (criador,))
    if not usuario_info:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    saldo_usuario, whatsapp = usuario_info[0]
    whatsapp = whatsapp if whatsapp else 'Não cadastrado'
    
    # Validar valor inicial
    valor_inicial_validado, erro = validar_reais(valor_inicial)
    if valor_inicial_validado is None:
        return jsonify({'error': erro}), 400
    
    valor_necessario = round(valor_inicial_validado / 2, 2)
    if saldo_usuario < valor_necessario:
        return jsonify({'error': f'Saldo insuficiente para criar esta sala. Você precisa de pelo menos R$ {valor_necessario:.2f} (metade do valor da sala).'}), 400
    
    # Verificar limite de salas por usuário
    count_salas = executar_query_fetchall("SELECT COUNT(*) FROM salas WHERE criador = %s", (criador,))
    if count_salas and count_salas[0][0] >= 2:
        return jsonify({'error': 'Você já tem 2 salas criadas'}), 400
    
    categoria_id = data.get('categoria_id')
    
    # Criar sala
    sucesso = executar_query_commit(
        "INSERT INTO salas (nome_sala, valor_inicial, criador, jogadores, whatsapp, categoria_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (nome_sala, valor_inicial_validado, criador, criador, whatsapp, categoria_id)
    )
    
    if sucesso:
        # Debitar metade do valor inicial do criador
        novos_reais = round(float(saldo_usuario) - valor_necessario, 2)
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE nome = %s", (novos_reais, criador))
        return jsonify({
            'message': f'Sala {nome_sala} criada com sucesso',
            'novos_reais': novos_reais
        })
    else:
        return jsonify({'error': 'Erro ao criar sala'}), 500

@salas_bp.route('/salas/<int:id_sala>/entrar', methods=['POST'])
def entrar_em_sala(id_sala):
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    nome_usuario = data.get('nome_usuario')
    
    if not id_usuario or not nome_usuario:
        return jsonify({'error': 'ID e nome do usuário são obrigatórios'}), 400
    
    # Buscar saldo do usuário
    saldo_usuario = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (id_usuario,))
    if not saldo_usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    saldo_usuario = saldo_usuario[0][0]
    
    # Buscar informações da sala
    sala = executar_query_fetchall("SELECT nome_sala, valor_inicial, jogadores, criador FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    nome_sala, valor_inicial, jogadores, criador = sala[0]
    
    # Verificar se tem saldo suficiente (metade do valor da sala)
    valor_necessario = round(float(valor_inicial) / 2, 2)
    if saldo_usuario < valor_necessario:
        return jsonify({'error': f'Saldo insuficiente. Você precisa de pelo menos R$ {valor_necessario:.2f} (metade do valor da sala) para entrar.'}), 400
    
    # Verificar se já está na sala
    jogadores_lista = jogadores.split(",") if jogadores else []
    if len(jogadores_lista) >= 2:
        return jsonify({'error': 'A sala já está cheia (2 jogadores)'}), 400
    if str(id_usuario) in jogadores_lista or nome_usuario in jogadores_lista:
        return jsonify({'error': 'Você já está na sala'}), 400
    
    # Adicionar jogador à sala
    novos_jogadores = jogadores + f",{id_usuario}" if jogadores else str(id_usuario)
    sucesso = executar_query_commit("UPDATE salas SET jogadores = %s WHERE id_sala = %s", (novos_jogadores, id_sala))
    
    if sucesso:
        # Debitar metade do valor inicial
        novos_reais = round(float(saldo_usuario) - valor_necessario, 2)
        executar_query_commit("UPDATE usuarios SET reais = %s WHERE id = %s", (novos_reais, id_usuario))
        
        # Notificação via Socket.IO removida temporariamente para evitar erro de conexão/timeout
        # O redirecionamento via WhatsApp já cumpre o papel de notificar o criador
        pass

        # Buscar informações do criador ou do administrador para redirecionamento ao WhatsApp
        if criador == 'admin':
            res_admin_wa = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'admin_whatsapp'")
            admin_whatsapp = res_admin_wa[0][0] if res_admin_wa else None
            dados_criador = {
                'nome': 'Administrador',
                'whatsapp': admin_whatsapp
            }
        else:
            criador_info = executar_query_fetchall(
                "SELECT nome, whatsapp FROM usuarios WHERE nome = %s",
                (criador,)
            )
            
            dados_criador = None
            if criador_info:
                dados_criador = {
                    'nome': criador_info[0][0],
                    'whatsapp': criador_info[0][1] if criador_info[0][1] and criador_info[0][1] != 'Não cadastrado' else None
                }
        
        return jsonify({
            'message': f'Você entrou na sala {id_sala}',
            'novos_reais': novos_reais,
            'sala_info': {
                'nome': nome_sala,
                'valor': valor_inicial
            },
            'criador_info': dados_criador
        })
    else:
        return jsonify({'error': 'Erro ao entrar na sala'}), 500

@salas_bp.route('/salas/<int:id_sala>', methods=['DELETE'])
def remover_sala(id_sala):
    # Verificar se sala existe
    sala = executar_query_fetchall("SELECT * FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    sucesso = executar_query_commit("DELETE FROM salas WHERE id_sala = %s", (id_sala,))
    
    if sucesso:
        return jsonify({'message': f'Sala {id_sala} removida com sucesso'})
    else:
        return jsonify({'error': 'Erro ao remover sala'}), 500

@salas_bp.route('/salas/<int:id_sala>/jogadores', methods=['GET'])
def obter_jogadores_sala(id_sala):
    sala = executar_query_fetchall("SELECT jogadores FROM salas WHERE id_sala = %s", (id_sala,))
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    jogadores_dict = obter_jogadores(sala[0][0])
    return jsonify(jogadores_dict)

@salas_bp.route('/salas/<int:id_sala>/definir-ganhador', methods=['POST'])
def definir_ganhador_sala(id_sala):
    data = request.get_json()
    vencedor_id = data.get('vencedor_id')
    
    if not vencedor_id:
        return jsonify({'error': 'ID do vencedor é obrigatório'}), 400
    
    # Buscar informações da sala
    sala = executar_query_fetchall(
        "SELECT valor_inicial, jogadores, criador FROM salas WHERE id_sala = %s",
        (id_sala,)
    )
    
    if not sala:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    valor_inicial, jogadores, criador = sala[0]
    
    # Verificar se o vencedor está na sala
    jogadores_lista = jogadores.split(",") if jogadores else []
    vencedor_str = str(vencedor_id)
    
    # Buscar nome do vencedor
    vencedor_info = executar_query_fetchall("SELECT nome FROM usuarios WHERE id = %s", (vencedor_id,))
    if not vencedor_info:
        return jsonify({'error': 'Vencedor não encontrado'}), 404
    
    vencedor_nome = vencedor_info[0][0]
    
    # Verificar se está na sala (por ID ou nome)
    if vencedor_str not in jogadores_lista and vencedor_nome not in jogadores_lista:
        return jsonify({'error': 'Vencedor não está na sala'}), 400
    
    # Atualizar sala com vencedor e status
    sucesso = executar_query_commit(
        "UPDATE salas SET vencedor_id = %s, status = 'finalizada' WHERE id_sala = %s",
        (vencedor_id, id_sala)
    )
    
    if sucesso:
        # Buscar porcentagem da casa nas configurações
        config_casa = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'porcentagem_casa'")
        porcentagem_casa = int(config_casa[0][0]) if config_casa else 10
        porcentagem_vencedor = (100 - porcentagem_casa) / 100.0

        # Calcular distribuição baseada na configuração (usando float para precisão de centavos)
        premio = round(float(valor_inicial) * porcentagem_vencedor, 2)
        valor_cofre = round(float(valor_inicial) - premio, 2)
        
        # Adicionar prêmio ao vencedor
        executar_query_commit(
            "UPDATE usuarios SET reais = reais + %s WHERE id = %s",
            (premio, vencedor_id)
        )
        
        # Adicionar valor ao cofre total
        executar_query_commit(
            "UPDATE cofre_total SET valor_total = valor_total + %s, ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = 1",
            (valor_cofre,)
        )
        
        # Registrar no histórico do cofre
        executar_query_commit(
            "INSERT INTO cofre_historico (id_sala, valor, descricao) VALUES (%s, %s, %s)",
            (id_sala, valor_cofre, f"{porcentagem_casa}% da sala {id_sala} - Vencedor: {vencedor_nome}")
        )
        
        # Emitir notificação via Socket.IO
        socketio = get_socketio()
        if socketio:
            socketio.emit('sala_finalizada', {
                'id_sala': id_sala,
                'vencedor_id': vencedor_id,
                'vencedor_nome': vencedor_nome,
                'premio': premio,
                'valor_cofre': valor_cofre
            })
        
        # Apagar a sala após confirmar o ganhador
        executar_query_commit("DELETE FROM salas WHERE id_sala = %s", (id_sala,))

        return jsonify({
            'message': 'Ganhador definido com sucesso e sala removida',
            'vencedor_id': vencedor_id,
            'vencedor_nome': vencedor_nome,
            'premio': premio,
            'valor_cofre': valor_cofre
        })
    
    return jsonify({'error': 'Erro ao definir ganhador'}), 500

