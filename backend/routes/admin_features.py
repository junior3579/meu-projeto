from decimal import Decimal, ROUND_HALF_UP
from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall, executar_query_commit

admin_features_bp = Blueprint('admin_features', __name__)

# --- Categorias ---

@admin_features_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = executar_query_fetchall("SELECT id, nome FROM categorias")
    res = []
    if categorias:
        for c in categorias:
            count = executar_query_fetchall("SELECT COUNT(*) FROM salas WHERE categoria_id = %s", (c[0],))
            res.append({
                'id': c[0],
                'nome': c[1],
                'total_salas': count[0][0] if count else 0
            })
    return jsonify(res)

@admin_features_bp.route('/categorias', methods=['POST'])
def criar_categoria():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
    
    sucesso = executar_query_commit("INSERT INTO categorias (nome) VALUES (%s)", (nome,))
    if sucesso:
        return jsonify({'message': 'Categoria criada com sucesso'})
    return jsonify({'error': 'Erro ao criar categoria ou nome já existe'}), 500

@admin_features_bp.route('/categorias/<int:id>', methods=['PUT'])
def renomear_categoria(id):
    data = request.get_json()
    novo_nome = data.get('nome')
    if not novo_nome:
        return jsonify({'error': 'Novo nome é obrigatório'}), 400
    
    sucesso = executar_query_commit("UPDATE categorias SET nome = %s WHERE id = %s", (novo_nome, id))
    if sucesso:
        return jsonify({'message': 'Categoria renomeada com sucesso'})
    return jsonify({'error': 'Erro ao renomear categoria'}), 500

@admin_features_bp.route('/categorias/<int:id>', methods=['DELETE'])
def remover_categoria(id):
    # Opcional: Desvincular salas antes de remover
    executar_query_commit("UPDATE salas SET categoria_id = NULL WHERE categoria_id = %s", (id,))
    sucesso = executar_query_commit("DELETE FROM categorias WHERE id = %s", (id,))
    if sucesso:
        return jsonify({'message': 'Categoria removida com sucesso'})
    return jsonify({'error': 'Erro ao remover categoria'}), 500

# --- Torneios ---

@admin_features_bp.route('/torneios', methods=['GET'])
def listar_torneios():
    # Buscando todas as colunas explicitamente para garantir consistência
    torneios = executar_query_fetchall("SELECT id, nome, status, vencedor_id, valor_inscricao, premio, fase_atual, data_inicio, data_fim FROM torneios")
    res = []
    if torneios:
        for t in torneios:
            # t[0]=id, t[1]=nome, t[2]=status, t[3]=vencedor_id, t[4]=valor_inscricao, t[5]=premio, t[6]=fase_atual, t[7]=data_inicio, t[8]=data_fim
            participantes = executar_query_fetchall(
                "SELECT u.id, u.nome, tp.status FROM torneio_participantes tp JOIN usuarios u ON tp.usuario_id = u.id WHERE tp.torneio_id = %s",
                (t[0],)
            )
            res.append({
                'id': t[0],
                'nome': t[1],
                'status': t[2],
                'vencedor_id': t[3],
                'valor_inscricao': t[4] if t[4] is not None else 0,
                'premio': t[5] if t[5] is not None else 0,
                'fase_atual': t[6] if t[6] is not None else 'inscricao',
                'data_inicio': t[7] if t[7] is not None else '',
                'data_fim': t[8] if t[8] is not None else '',
                'participantes': [{'id': p[0], 'nome': p[1], 'status': p[2]} for p in participantes] if participantes else []
            })
    return jsonify(res)

@admin_features_bp.route('/torneios', methods=['POST'])
def criar_torneio():
    data = request.get_json()
    nome = data.get('nome')
    data_inicio = data.get('data_inicio')
    data_fim = data.get('data_fim')
    valor_inscricao = Decimal(str(data.get('valor_inscricao', 0)))
    premio = Decimal(str(data.get('premio', 0)))
    
    if not nome:
        return jsonify({'error': 'Nome do torneio é obrigatório'}), 400
    
    sucesso = executar_query_commit(
        "INSERT INTO torneios (nome, data_inicio, data_fim, valor_inscricao, premio) VALUES (%s, %s, %s, %s, %s)", 
        (nome, data_inicio, data_fim, valor_inscricao, premio)
    )
    if sucesso:
        return jsonify({'message': f'Torneio {nome} criado com sucesso'})
    return jsonify({'error': 'Erro ao criar torneio'}), 500

@admin_features_bp.route('/torneios/<int:id>/inscrever', methods=['POST'])
def inscrever_no_torneio(id):
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    nome_usuario = data.get('nome_usuario') # Opcional para busca manual
    
    if not usuario_id and nome_usuario:
        res = executar_query_fetchall("SELECT id FROM usuarios WHERE nome = %s", (nome_usuario,))
        if res:
            usuario_id = res[0][0]
        else:
            return jsonify({'error': 'Usuário não encontrado pelo nome'}), 404

    if not usuario_id:
        return jsonify({'error': 'ID ou Nome do usuário é obrigatório'}), 400

    # Buscar informações do torneio e do usuário
    torneio = executar_query_fetchall("SELECT status, valor_inscricao FROM torneios WHERE id = %s", (id,))
    if not torneio:
        return jsonify({'error': 'Torneio não encontrado'}), 404
    
    status_torneio, valor_inscricao = torneio[0]
    
    usuario = executar_query_fetchall("SELECT reais FROM usuarios WHERE id = %s", (usuario_id,))
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    saldo_usuario = usuario[0][0]
    
    # Validar se tem saldo suficiente
    if valor_inscricao > 0 and saldo_usuario < valor_inscricao:
        return jsonify({'error': f'Saldo insuficiente. A inscrição custa {valor_inscricao} reais e o usuário tem apenas {saldo_usuario} reais.'}), 400
    
    # Verificar se já está inscrito
    existe = executar_query_fetchall("SELECT id FROM torneio_participantes WHERE torneio_id = %s AND usuario_id = %s", (id, usuario_id))
    if existe:
        return jsonify({'error': 'Usuário já inscrito'}), 400
    
    # Realizar a inscrição
    sucesso = executar_query_commit("INSERT INTO torneio_participantes (torneio_id, usuario_id) VALUES (%s, %s)", (id, usuario_id))
    
    if sucesso:
        # Debitar o saldo automaticamente
        if valor_inscricao > 0:
            executar_query_commit("UPDATE usuarios SET reais = reais - %s WHERE id = %s", (valor_inscricao, usuario_id))
            return jsonify({'message': f'Inscrição realizada com sucesso! O valor de {valor_inscricao} reais foi debitado do saldo.', 'novo_saldo': saldo_usuario - valor_inscricao})
        
        return jsonify({'message': 'Inscrição realizada com sucesso'})
    
    return jsonify({'error': 'Erro ao realizar inscrição'}), 500

@admin_features_bp.route('/torneios/<int:id>/desinscrever', methods=['POST'])
def desinscrever_do_torneio(id):
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    
    if not usuario_id:
        return jsonify({'error': 'ID do usuário é obrigatório'}), 400
    
    sucesso = executar_query_commit("DELETE FROM torneio_participantes WHERE torneio_id = %s AND usuario_id = %s", (id, usuario_id))
    if sucesso:
        return jsonify({'message': 'Usuário removido do torneio com sucesso'})
    return jsonify({'error': 'Erro ao remover usuário do torneio'}), 500

@admin_features_bp.route('/torneios/<int:id>/iniciar', methods=['POST'])
def iniciar_torneio(id):
    # Ao iniciar, gerar os primeiros confrontos automaticamente
    participantes = executar_query_fetchall(
        "SELECT usuario_id FROM torneio_participantes WHERE torneio_id = %s AND status = 'ativo'",
        (id,)
    )
    
    if not participantes or len(participantes) < 2:
        return jsonify({'error': 'Necessário pelo menos 2 participantes para iniciar'}), 400
    
    import random
    lista_ids = [p[0] for p in participantes]
    random.shuffle(lista_ids)
    
    # Criar confrontos
    for i in range(0, len(lista_ids), 2):
        p1 = lista_ids[i]
        p2 = lista_ids[i+1] if i+1 < len(lista_ids) else None
        
        if p2:
            executar_query_commit(
                "INSERT INTO torneio_confrontos (torneio_id, fase_nome, jogador1_id, jogador2_id) VALUES (%s, %s, %s, %s)",
                (id, 'Primeira Fase', p1, p2)
            )
        else:
            # Jogador sem dupla passa automaticamente (BYE)
            executar_query_commit(
                "INSERT INTO torneio_confrontos (torneio_id, fase_nome, jogador1_id, vencedor_id, status) VALUES (%s, %s, %s, %s, %s)",
                (id, 'Primeira Fase', p1, p1, 'finalizado')
            )

    sucesso = executar_query_commit("UPDATE torneios SET status = 'em_andamento', fase_atual = 'Primeira Fase' WHERE id = %s", (id,))
    if sucesso:
        return jsonify({'message': 'Torneio iniciado e confrontos gerados!'})
    return jsonify({'error': 'Erro ao iniciar torneio'}), 500

@admin_features_bp.route('/torneios/<int:id>/confrontos', methods=['GET'])
def listar_confrontos(id):
    confrontos = executar_query_fetchall(
        """SELECT c.id, c.fase_nome, c.jogador1_id, u1.nome, c.jogador2_id, u2.nome, c.vencedor_id, c.status 
           FROM torneio_confrontos c
           LEFT JOIN usuarios u1 ON c.jogador1_id = u1.id
           LEFT JOIN usuarios u2 ON c.jogador2_id = u2.id
           WHERE c.torneio_id = %s ORDER BY c.id DESC""",
        (id,)
    )
    
    res = []
    for c in confrontos:
        res.append({
            'id': c[0],
            'fase': c[1],
            'p1_id': c[2],
            'p1_nome': c[3],
            'p2_id': c[4],
            'p2_nome': c[5] if c[4] else 'AGUARDANDO',
            'vencedor_id': c[6],
            'status': c[7]
        })
    return jsonify(res)

@admin_features_bp.route('/confrontos/<int:id_confronto>/vencedor', methods=['POST'])
def definir_vencedor_confronto(id_confronto):
    data = request.get_json()
    vencedor_id = data.get('vencedor_id')
    
    # Buscar info do confronto
    confronto = executar_query_fetchall("SELECT torneio_id, fase_nome, jogador1_id, jogador2_id FROM torneio_confrontos WHERE id = %s", (id_confronto,))
    if not confronto: return jsonify({'error': 'Confronto não encontrado'}), 404
    
    torneio_id, fase_atual, p1, p2 = confronto[0]
    
    # Validar se o vencedor_id é um dos jogadores do confronto
    if vencedor_id != p1 and vencedor_id != p2:
        return jsonify({'error': 'O vencedor deve ser um dos jogadores do confronto'}), 400

    # Atualizar o vencedor do confronto
    sucesso = executar_query_commit(
        "UPDATE torneio_confrontos SET vencedor_id = %s, status = 'finalizado' WHERE id = %s",
        (vencedor_id, id_confronto)
    )
    
    if sucesso:
        # Eliminar o perdedor
        perdedor_id = p1 if vencedor_id == p2 else p2
        if perdedor_id:
            executar_query_commit(
                "UPDATE torneio_participantes SET status = 'eliminado' WHERE torneio_id = %s AND usuario_id = %s",
                (torneio_id, perdedor_id)
            )
        return jsonify({'message': 'Vencedor definido com sucesso!'})
    
    return jsonify({'error': 'Erro ao definir vencedor'}), 500

@admin_features_bp.route('/torneios/<int:id>/avancar-fase', methods=['POST'])
def avancar_fase_torneio(id):
    data = request.get_json()
    proxima_fase_nome = data.get('proxima_fase')
    
    if not proxima_fase_nome:
        return jsonify({'error': 'Nome da próxima fase é obrigatório'}), 400
        
    # Buscar participantes ativos (vencedores da fase anterior)
    participantes = executar_query_fetchall(
        "SELECT usuario_id FROM torneio_participantes WHERE torneio_id = %s AND status = 'ativo'",
        (id,)
    )
    
    if not participantes or len(participantes) < 2:
        # Se restar apenas 1, o torneio deve ser finalizado
        if len(participantes) == 1:
            vencedor_final_id = participantes[0][0]
            # Buscar prêmio do torneio
            torneio_info = executar_query_fetchall("SELECT premio FROM torneios WHERE id = %s", (id,))
            premio = torneio_info[0][0] if torneio_info else 0
            
            # Finalizar torneio e pagar prêmio
            executar_query_commit("UPDATE torneios SET status = 'finalizado', vencedor_id = %s WHERE id = %s", (vencedor_final_id, id))
            if premio > 0:
                executar_query_commit("UPDATE usuarios SET reais = reais + %s WHERE id = %s", (premio, vencedor_final_id))
            
            return jsonify({'message': 'Torneio finalizado! Vencedor definido e prêmio pago.', 'finalizado': True})
            
        return jsonify({'error': 'Não há participantes suficientes para avançar'}), 400
        
    # Gerar novos confrontos
    import random
    lista_ids = [p[0] for p in participantes]
    random.shuffle(lista_ids)
    
    for i in range(0, len(lista_ids), 2):
        p1 = lista_ids[i]
        p2 = lista_ids[i+1] if i+1 < len(lista_ids) else None
        
        if p2:
            executar_query_commit(
                "INSERT INTO torneio_confrontos (torneio_id, fase_nome, jogador1_id, jogador2_id) VALUES (%s, %s, %s, %s)",
                (id, proxima_fase_nome, p1, p2)
            )
        else:
            executar_query_commit(
                "INSERT INTO torneio_confrontos (torneio_id, fase_nome, jogador1_id, vencedor_id, status) VALUES (%s, %s, %s, %s, %s)",
                (id, proxima_fase_nome, p1, p1, 'finalizado')
            )
            
    executar_query_commit("UPDATE torneios SET fase_atual = %s WHERE id = %s", (proxima_fase_nome, id))
    return jsonify({'message': f'Torneio avançou para {proxima_fase_nome}!'})

@admin_features_bp.route('/torneios/<int:id>', methods=['PUT'])
def editar_torneio(id):
    data = request.get_json()
    nome = data.get('nome')
    valor_inscricao = Decimal(str(data.get('valor_inscricao', 0)))
    premio = Decimal(str(data.get('premio', 0)))
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    sucesso = executar_query_commit(
        "UPDATE torneios SET nome = %s, valor_inscricao = %s, premio = %s WHERE id = %s",
        (nome, valor_inscricao, premio, id)
    )
    
    if sucesso:
        return jsonify({'message': 'Torneio atualizado com sucesso'})
    return jsonify({'error': 'Erro ao atualizar torneio'}), 500

@admin_features_bp.route('/torneios/<int:id>', methods=['DELETE'])
def remover_torneio(id):
    try:
        # 1. Remover confrontos
        executar_query_commit("DELETE FROM torneio_confrontos WHERE torneio_id = %s", (id,))
        # 2. Remover participantes
        executar_query_commit("DELETE FROM torneio_participantes WHERE torneio_id = %s", (id,))
        # 3. Remover torneio
        sucesso = executar_query_commit("DELETE FROM torneios WHERE id = %s", (id,))
        
        if sucesso:
            return jsonify({'message': 'Torneio removido com sucesso'})
        return jsonify({'error': 'Erro ao remover torneio'}), 500
    except Exception as e:
        print(f"Erro ao remover torneio {id}: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# --- Cofre do Site ---

@admin_features_bp.route('/cofre/total', methods=['GET'])
def obter_cofre_total():
    """Retorna o valor total acumulado no cofre do site"""
    cofre = executar_query_fetchall("SELECT valor_total, ultima_atualizacao FROM cofre_total WHERE id = 1")
    if cofre:
        return jsonify({
            'valor_total': cofre[0][0],
            'ultima_atualizacao': str(cofre[0][1]) if cofre[0][1] else None
        })
    return jsonify({'valor_total': 0, 'ultima_atualizacao': None})

@admin_features_bp.route('/cofre/historico', methods=['GET'])
def obter_historico_cofre():
    """Retorna o histórico de recebimentos do cofre (10% das salas finalizadas)"""
    # Parâmetros opcionais para paginação
    limite = request.args.get('limite', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    historico = executar_query_fetchall(
        """SELECT h.id, h.id_sala, h.valor, h.data_registro, h.descricao, s.nome_sala
           FROM cofre_historico h
           LEFT JOIN salas s ON h.id_sala = s.id_sala
           ORDER BY h.data_registro DESC
           LIMIT %s OFFSET %s""",
        (limite, offset)
    )
    
    # Contar total de registros
    total = executar_query_fetchall("SELECT COUNT(*) FROM cofre_historico")
    total_registros = total[0][0] if total else 0
    
    resultado = []
    if historico:
        for h in historico:
            resultado.append({
                'id': h[0],
                'id_sala': h[1],
                'valor': h[2],
                'data_registro': str(h[3]) if h[3] else None,
                'descricao': h[4],
                'nome_sala': h[5] if h[5] else f"Sala #{h[1]}"
            })
    
    return jsonify({
        'historico': resultado,
        'total_registros': total_registros,
        'limite': limite,
        'offset': offset
    })

@admin_features_bp.route('/cofre/estatisticas', methods=['GET'])
def obter_estatisticas_cofre():
    """Retorna estatísticas do cofre do site"""
    # Valor total acumulado
    cofre_total = executar_query_fetchall("SELECT valor_total FROM cofre_total WHERE id = 1")
    valor_total = cofre_total[0][0] if cofre_total else 0
    
    # Total de salas finalizadas
    salas_finalizadas = executar_query_fetchall("SELECT COUNT(*) FROM salas WHERE status = 'finalizada'")
    total_salas = salas_finalizadas[0][0] if salas_finalizadas else 0
    
    # Valor médio recebido por sala
    media = executar_query_fetchall("SELECT AVG(valor) FROM cofre_historico")
    valor_medio = float(media[0][0]) if media and media[0][0] else 0
    
    # Saldo total de todos os jogadores
    saldo_jogadores = executar_query_fetchall("SELECT SUM(reais) FROM usuarios")
    total_saldo_jogadores = float(saldo_jogadores[0][0]) if saldo_jogadores and saldo_jogadores[0][0] else 0
    
    # Contar total de usuários para calcular o investimento inicial (20 reais por jogador)
    total_usuarios_res = executar_query_fetchall("SELECT COUNT(*) FROM usuarios")
    total_usuarios = total_usuarios_res[0][0] if total_usuarios_res else 0
    investimento_inicial = total_usuarios * 20

    # Último recebimento
    ultimo = executar_query_fetchall(
        "SELECT valor, data_registro FROM cofre_historico ORDER BY data_registro DESC LIMIT 1"
    )
    ultimo_recebimento = None
    if ultimo:
        ultimo_recebimento = {
            'valor': ultimo[0][0],
            'data': str(ultimo[0][1]) if ultimo[0][1] else None
        }
    
    return jsonify({
        'valor_total': float(valor_total),
        'total_salas_finalizadas': total_salas,
        'valor_medio_por_sala': round(float(valor_medio), 2),
        'ultimo_recebimento': ultimo_recebimento,
        'total_saldo_jogadores': round(float(total_saldo_jogadores), 2),
        'total_geral_casa': round(float(valor_total) + float(total_saldo_jogadores) - float(investimento_inicial), 2)
    })

# --- Configurações e Gestão de Lucro ---

@admin_features_bp.route('/configuracoes', methods=['GET'])
def obter_configuracoes():
    configs = executar_query_fetchall("SELECT chave, valor FROM configuracoes")
    return jsonify({c[0]: c[1] for c in configs})

@admin_features_bp.route('/configuracoes', methods=['POST'])
def salvar_configuracao():
    data = request.get_json()
    chave = data.get('chave')
    valor = data.get('valor')
    
    if not chave or valor is None:
        return jsonify({'error': 'Chave e valor são obrigatórios'}), 400
        
    sucesso = executar_query_commit(
        "INSERT INTO configuracoes (chave, valor) VALUES (%s, %s) ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor",
        (chave, str(valor))
    )
    
    if sucesso:
        return jsonify({'message': f'Configuração {chave} atualizada com sucesso'})
    return jsonify({'error': 'Erro ao salvar configuração'}), 500

@admin_features_bp.route('/cofre/zerar', methods=['POST'])
def zerar_cofre():
    # Obter valor atual para o histórico
    cofre = executar_query_fetchall("SELECT valor_total FROM cofre_total WHERE id = 1")
    valor_anterior = cofre[0][0] if cofre else 0
    
    if valor_anterior <= 0:
        return jsonify({'error': 'O cofre já está zerado'}), 400
        
    # Zerar o cofre
    sucesso = executar_query_commit("UPDATE cofre_total SET valor_total = 0, ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = 1")
    
    if sucesso:
        # Registrar no histórico
        executar_query_commit(
            "INSERT INTO cofre_historico (id_sala, valor, descricao) VALUES (0, %s, %s)",
            (-valor_anterior, f"Cofre zerado pelo administrador (Valor anterior: R$ {valor_anterior})")
        )
        return jsonify({'message': 'Lucro da casa zerado com sucesso'})
    return jsonify({'error': 'Erro ao zerar lucro da casa'}), 500

@admin_features_bp.route('/cofre/transferir', methods=['POST'])
def transferir_lucro():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    valor_transferir = data.get('valor')
    
    if not usuario_id or not valor_transferir:
        return jsonify({'error': 'ID do usuário e valor são obrigatórios'}), 400
        
    try:
        valor_transferir = Decimal(str(valor_transferir)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if valor_transferir <= 0:
            return jsonify({'error': 'O valor deve ser maior que zero'}), 400
    except ValueError:
        return jsonify({'error': 'Valor inválido'}), 400
        
    # Verificar saldo do cofre
    cofre = executar_query_fetchall("SELECT valor_total FROM cofre_total WHERE id = 1")
    saldo_cofre = Decimal(str(cofre[0][0])) if cofre else Decimal('0')
    
    if saldo_cofre < valor_transferir:
        return jsonify({'error': f'Saldo insuficiente no cofre. Disponível: R$ {saldo_cofre}'}), 400
        
    # Verificar se usuário existe
    usuario = executar_query_fetchall("SELECT nome FROM usuarios WHERE id = %s", (usuario_id,))
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    nome_usuario = usuario[0][0]
    
    # Executar transferência
    # 1. Aumentar saldo do usuário primeiro
    sucesso_usuario = executar_query_commit(
        "UPDATE usuarios SET reais = reais + %s WHERE id = %s",
        (valor_transferir, usuario_id)
    )
    
    if sucesso_usuario:
        # 2. Diminuir do cofre
        sucesso_cofre = executar_query_commit(
            "UPDATE cofre_total SET valor_total = valor_total - %s, ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = 1",
            (valor_transferir,)
        )
        
        if sucesso_cofre:
            # 3. Registrar no histórico
            executar_query_commit(
                "INSERT INTO cofre_historico (id_sala, valor, descricao) VALUES (0, %s, %s)",
                (-valor_transferir, f"Transferência de lucro para {nome_usuario}")
            )
            return jsonify({'message': f'R$ {float(valor_transferir):.2f} transferidos para {nome_usuario} com sucesso'})
        else:
            # Rollback do saldo do usuário se falhar a atualização do cofre
            executar_query_commit(
                "UPDATE usuarios SET reais = reais - %s WHERE id = %s",
                (valor_transferir, usuario_id)
            )
            return jsonify({'error': 'Erro ao atualizar saldo do cofre'}), 500
            
    return jsonify({'error': 'Erro ao processar transferência'}), 500

# --- Configurações do Administrador ---

@admin_features_bp.route('/admin/settings', methods=['GET'])
def obter_admin_settings():
    """Retorna as configurações atuais do administrador"""
    res_senha = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'admin_password'")
    res_whatsapp = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'admin_whatsapp'")
    
    return jsonify({
        'admin_password': res_senha[0][0] if res_senha else "3579",
        'admin_whatsapp': res_whatsapp[0][0] if res_whatsapp else ""
    })

@admin_features_bp.route('/admin/settings', methods=['POST'])
def salvar_admin_settings():
    """Salva as novas configurações do administrador"""
    data = request.get_json()
    nova_senha = data.get('admin_password')
    novo_whatsapp = data.get('admin_whatsapp')
    
    if nova_senha:
        executar_query_commit(
            "INSERT INTO configuracoes (chave, valor) VALUES ('admin_password', %s) ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor",
            (str(nova_senha),)
        )
        
    if novo_whatsapp:
        executar_query_commit(
            "INSERT INTO configuracoes (chave, valor) VALUES ('admin_whatsapp', %s) ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor",
            (str(novo_whatsapp),)
        )
        
    return jsonify({'message': 'Configurações do administrador atualizadas com sucesso'})
