# app.py
import os
from flask import Flask
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_session import Session  # ✅ sesiones en servidor

from config import config
from src.models.ModelUser import ModelUser


def create_app():
    # -----------------------------
    # 🚀 Inicialización base
    # -----------------------------
    app = Flask(__name__, template_folder="src/templates", static_folder="src/static")
    app.config.from_object(config['development'])

    # -----------------------------
    # 🔒 Clave secreta
    # -----------------------------
    app.secret_key = (
        os.environ.get('SECRET_KEY')
        or app.config.get('SECRET_KEY')
        or 'dev_fallback_secret_key_!change_me'
    )

    # -----------------------------
    # ⚙️ Configuración de cookies y sesión
    # -----------------------------
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24,
        WTF_CSRF_TIME_LIMIT=60 * 60 * 24,
        WTF_CSRF_ENABLED=False
    )

    # 💾 Sesiones persistentes en servidor (filesystem)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_session')
    app.config['SESSION_PERMANENT'] = False
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    Session(app)

    # -----------------------------
    # 🔌 Inicialización de extensiones
    # -----------------------------
    csrf = CSRFProtect()
    db = MySQL(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    mail = Mail(app)
    socketio = SocketIO(app, cors_allowed_origins="*")

    SECRET_KEY_TOKEN = os.environ.get('SECRET_KEY_TOKEN') or app.secret_key
    s = URLSafeTimedSerializer(SECRET_KEY_TOKEN)

    csrf.init_app(app)
    login_manager.init_app(app)

    app.db = db
    app.csrf = csrf
    app.login_manager = login_manager
    app.mail = mail
    app.s = s
    app.socketio = socketio

    # -----------------------------
    # 👤 Cargar usuario
    # -----------------------------
    @login_manager.user_loader
    def load_user(id_usuario):
        return ModelUser.get_by_id(app.db, id_usuario)

    # -----------------------------
    # 📦 Importar y registrar Blueprints
    # -----------------------------
    from src.routes.auth import auth_bp
    from src.routes.home import home_bp
    from src.routes.productos import productos_bp
    from src.routes.admin import admin_bp
    from src.routes.api import api_bp
    from src.routes.navbar import navbar_bp
    from src.routes.usuarios import usuarios_bp
    from src.routes.carrito import carrito_bp
    from src.routes.suscripciones import suscripciones_bp
    from src.routes.personalizacion import personalizacion_bp
    from src.routes.sugerencias import sugerencias_bp
    from src.routes.fabricacion import fabricacion_bp
    from src.routes.videotutoriales import videotutoriales_bp
    from src.routes.chat import chat_bp
    from src.routes.favoritos import favoritos_bp

    # ⚡ Registrar blueprints
    app.register_blueprint(favoritos_bp, url_prefix="/favoritos")
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(navbar_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(carrito_bp, url_prefix='/carrito')
    app.register_blueprint(suscripciones_bp, url_prefix="/suscripciones")
    app.register_blueprint(personalizacion_bp, url_prefix="/personalizacion")
    app.register_blueprint(sugerencias_bp, url_prefix="/sugerencias")
    app.register_blueprint(fabricacion_bp, url_prefix="/fabricacion")
    app.register_blueprint(videotutoriales_bp, url_prefix="/videotutoriales")
    app.register_blueprint(chat_bp, url_prefix="/chat")

    # -----------------------------
    # 🚫 Exenciones CSRF
    # -----------------------------
    csrf_exempt_endpoints = [
        'auth_bp.logout_redirect',
        'admin_bp.agregar_producto', 'admin_bp.editar_producto',
        'admin_bp.eliminar_producto', 'admin_bp.aprobar_suscripcion',
        'admin_bp.rechazar_suscripcion', 'admin_bp.eliminar_usuario',
        'admin_bp.admin_editar_usuario',
        'usuarios_bp.subir_video',
        'api_bp.api_eventos', 'api_bp.api_productos',
        'productos_bp.guardar_texto_personalizado',
        'productos_bp.subir_boceto', 'productos_bp.guardar_plantilla',
        'productos_bp.registrar_formulario',
        'navbar_bp.calendario', 'suscripciones_bp.subir_comprobante',
        'carrito_bp.agregar', 'carrito_bp.eliminar', 'carrito_bp.vaciar', 'carrito_bp.checkout',
        'videotutoriales_bp.calificar_video',
        'favoritos_bp.agregar_favorito', 'favoritos_bp.eliminar_favorito'
    ]

    with app.app_context():
        for ep in csrf_exempt_endpoints:
            view = app.view_functions.get(ep)
            if view:
                try:
                    csrf.exempt(view)
                    print(f"✅ CSRF exempt: {ep}")
                except Exception as e:
                    print(f"⚠️ No se pudo eximir CSRF de {ep}: {e}")
            else:
                print(f"⚠️ Endpoint no encontrado para CSRF exempt: {ep}")

    # -----------------------------
    # 💬 Chat
    # -----------------------------
    @socketio.on('join_chat')
    def handle_join_chat(data):
        user = data.get('username', 'Usuario')
        socketio.emit('server_message', {'message': f"{user} se unió al chat."})

    @socketio.on('send_message')
    def handle_send_message(data):
        socketio.emit('receive_message', data)

    # -----------------------------
    # 🧭 Listar rutas registradas
    # -----------------------------
    print("\n📌 Rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} -> {rule.rule}")

    return app, socketio


# -----------------------------
# 🧠 Ejecución principal
# -----------------------------
if __name__ == '__main__':
    app, socketio = create_app()
    print("\n🏠 Sitio web: http://localhost:5000")
    print("👑 Panel admin: http://localhost:5000/admin")
    socketio.run(app, debug=True, use_reloader=False, port=5000)
