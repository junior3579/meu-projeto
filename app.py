import os
from backend.main import app, socketio

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Usar 0.0.0.0 para permitir conexões externas através do proxy
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
