from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall, executar_query_commit
from decimal import Decimal

transacoes_bp = Blueprint('transacoes', __name__)

# Número do WhatsApp do administrador (configurável)
WHATSAPP_ADMIN = "99985136639"  # Número do administrador padrão

@transacoes_bp.route('/transacoes/solicitar', methods=['POST'])
def solicitar_transacao():
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    tipo = data.get('tipo')  # 'deposito' ou 'saque'
    valor = data.get('valor')
    
    if not id_usuario or not tipo or not valor:
        return jsonify({'error': 'ID do usuário, tipo e valor são obrigatórios'}), 400
    
    if tipo not in ['deposito', 'saque']:
        return jsonify({'error': 'Tipo deve ser "deposito" ou "saque"'}), 400
    
    try:
        valor_val = Decimal(str(valor))
        if valor_val <= 0:
            return jsonify({'error': 'O valor deve ser maior que 0'}), 400
    except:
        return jsonify({'error': 'Valor inválido'}), 400
    
    # Buscar informações do usuário
    usuario = executar_query_fetchall(
        "SELECT nome, whatsapp, reais FROM usuarios WHERE id = %s",
        (id_usuario,)
    )
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    nome_usuario, whatsapp_usuario, reais_usuario = usuario[0]
    reais_usuario = Decimal(str(reais_usuario))
    
    # Verificar se tem saldo suficiente para saque
    if tipo == 'saque' and reais_usuario < valor_val:
        return jsonify({'error': 'Saldo insuficiente para saque'}), 400
    
    # Registrar a solicitação no banco de dados
    sucesso = executar_query_commit(
        "INSERT INTO transacoes (id_usuario, tipo, valor, status) VALUES (%s, %s, %s, %s)",
        (id_usuario, tipo, valor_val, 'pendente')
    )
    
    if not sucesso:
        return jsonify({'error': 'Erro ao registrar solicitação'}), 500
    
    # Preparar mensagem para o admin
    tipo_texto = 'DEPÓSITO' if tipo == 'deposito' else 'SAQUE'
    mensagem = f"🔔 *Nova Solicitação de {tipo_texto}*\n\n"
    mensagem += f"👤 *Usuário:* {nome_usuario}\n"
    mensagem += f"📱 *WhatsApp:* {whatsapp_usuario if whatsapp_usuario and whatsapp_usuario != 'Não cadastrado' else 'Não cadastrado'}\n"
    mensagem += f"💰 *Valor:* {float(valor_val):.2f} reais\n"
    mensagem += f"📋 *Tipo:* {tipo_texto}\n"
    mensagem += f"🆔 *ID do Usuário:* {id_usuario}"
    
    return jsonify({
        'success': True,
        'message': f'Solicitação de {tipo} enviada com sucesso',
        'whatsapp_admin': WHATSAPP_ADMIN,
        'mensagem_admin': mensagem
    })

@transacoes_bp.route('/transacoes/historico/<int:id_usuario>', methods=['GET'])
def historico_transacoes(id_usuario):
    transacoes = executar_query_fetchall(
        "SELECT id, tipo, valor, status, data_criacao FROM transacoes WHERE id_usuario = %s ORDER BY data_criacao DESC",
        (id_usuario,)
    )
    
    if not transacoes:
        return jsonify([])
    
    transacoes_list = []
    for t in transacoes:
        transacoes_list.append({
            'id': t[0],
            'tipo': t[1],
            'valor': float(t[2]) if t[2] is not None else 0.0,
            'status': t[3],
            'data': str(t[4]) if t[4] else None
        })
    
    return jsonify(transacoes_list)
