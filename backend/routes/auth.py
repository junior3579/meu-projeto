from flask import Blueprint, request, jsonify
from backend.database_config import executar_query_fetchall
from backend.socketio_instance import get_socketio

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nome = data.get('nome')
    senha = data.get('senha')
    
    if not nome or not senha:
        return jsonify({'error': 'Nome e senha são obrigatórios'}), 400
    
    # Verificar se é admin
    if nome == "admin":
        res = executar_query_fetchall("SELECT valor FROM configuracoes WHERE chave = 'admin_password'")
        senha_admin = res[0][0] if res else "3579"
        
        if senha == senha_admin:
            return jsonify({
                'success': True,
                'user': {
                    'id': 0,
                    'nome': 'admin',
                    'tipo': 'admin',
                    'reais': 0.0
                }
            })
    
    # Verificar usuário comum
    result = executar_query_fetchall(
        "SELECT id, reais FROM usuarios WHERE nome = %s AND senha = %s",
        (nome, senha)
    )
    
    if result:
        id_usuario, reais = result[0]
        return jsonify({
            'success': True,
            'user': {
                'id': id_usuario,
                'nome': nome,
                'tipo': 'usuario',
                'reais': float(reais) if reais is not None else 0.0
            }
        })
    
    return jsonify({'error': 'Credenciais inválidas'}), 401
