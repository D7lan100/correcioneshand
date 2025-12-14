from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(
        self,
        id_usuario,
        correo_electronico,
        contraseña=None,
        nombre_completo="",
        id_rol=None,
        telefono=None,
        direccion=None,
        is_active=1
    ):
        self.id_usuario = id_usuario
        self.correo_electronico = correo_electronico
        self.contraseña = contraseña
        self.nombre_completo = nombre_completo
        self.id_rol = id_rol
        self.telefono = telefono
        self.direccion = direccion
        self._is_active = is_active

    def get_id(self):
        return str(self.id_usuario)

    @property
    def id(self):
        return self.id_usuario

    @property
    def is_active(self):
        """Flask-Login usa esta propiedad para permitir el acceso."""
        return self._is_active == 1

    @classmethod
    def check_password(cls, hashed_password, password):
        return check_password_hash(hashed_password, password)
