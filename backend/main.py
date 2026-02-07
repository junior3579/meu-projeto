import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.database_config import criar_tabelas_remoto
from backend.socketio_instance import init_socketio
from backend.routes.auth import auth_bp
from backend.routes.usuarios import usuarios_bp
from backend.routes.salas import salas_bp
from backend.routes.apostas import apostas_bp
from backend.routes.transacoes import transacoes_bp
from backend.routes.admin_features import admin_features_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
socketio = init_socketio(app)

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(usuarios_bp, url_prefix='/api')
app.register_blueprint(salas_bp, url_prefix="/api")
app.register_blueprint(apostas_bp, url_prefix="/api")
app.register_blueprint(transacoes_bp, url_prefix='/api')
app.register_blueprint(admin_features_bp, url_prefix='/api')

# Criar tabelas no banco de dados (desabilitado para evitar travamento no boot)
# with app.app_context():
#     criar_tabelas_remoto()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Se a rota começar com 'api', deixa os blueprints lidarem
    if path.startswith('api'):
        return "Not Found", 404
        
    # Tenta servir o arquivo da pasta static
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # Para qualquer outra rota (navegação do React), serve o index.html
    return send_from_directory(app.static_folder, 'index.html')


# Para deploy no Render/Gunicorn
port = int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
