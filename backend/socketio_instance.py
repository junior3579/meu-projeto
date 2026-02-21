from flask_socketio import SocketIO, join_room

socketio = None

def init_socketio(app):
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")

    @socketio.on('join')
    def on_join(data):
        room = data.get('room')
        if room:
            join_room(room)
            print(f"Usuário entrou na sala: {room}")

    return socketio

def get_socketio():
    return socketio
