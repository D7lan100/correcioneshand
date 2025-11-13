# 📁 src/routes/chat.py
from flask import Blueprint
from flask_socketio import emit, join_room

chat_bp = Blueprint('chat_bp', __name__)

# ============================================================
# 💬 CHAT EN VIVO (por defecto: sala única "chat_en_vivo")
# ============================================================
@chat_bp.record_once
def configurar_chat(state):
    socketio = state.app.socketio

    # 🟢 Cuando alguien se conecta al chat
    @socketio.on('join_chat')
    def handle_join(data):
        username = data.get('username', 'Invitado')
        join_room('chat_en_vivo')
        emit(
            'server_message',
            {'user': 'Sistema', 'message': f'{username} se unió al chat 💬'},
            room='chat_en_vivo'
        )

    # 🟢 Cuando alguien envía un mensaje
    @socketio.on('send_message')
    def handle_send_message(data):
        """
        data = {'user': 'Usuario' o 'Admin', 'message': 'texto'}
        """
        user = data.get('user', 'Desconocido')
        message = data.get('message', '')
        # Reenviar el mensaje a todos los conectados
        emit('receive_message', {'user': user, 'message': message}, room='chat_en_vivo')



# ============================================================
# ⚙️ OPCIONAL: CHAT PRIVADO (por usuario)
# ============================================================
# Si más adelante quieres que cada usuario tenga su propia sala privada
# puedes reemplazar lo anterior por este bloque alternativo.
# 
# Simplemente descomenta este código y comenta el anterior.
#
# ------------------------------------------------------------
@chat_bp.record_once
def configurar_chat(state):
    socketio = state.app.socketio

    @socketio.on('join_chat')
    def handle_join(data):
        username = data.get('username', 'Invitado')
        room = data.get('room', 'chat_general')  # sala personalizada
        join_room(room)
        emit(
            'server_message',
            {'user': 'Sistema', 'message': f'{username} se unió al chat 💬'},
            room=room
        )

    @socketio.on('send_message')
    def handle_send_message(data):
        user = data.get('user', 'Desconocido')
        message = data.get('message', '')
        room = data.get('room', 'chat_general')
        emit('receive_message', {'user': user, 'message': message}, room=room)
