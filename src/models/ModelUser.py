from .entities.User import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class ModelUser:

    # ----------------------------
    # Login
    # ----------------------------
    @classmethod
    def login(cls, db, user):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_usuario, correo_electronico, contraseña, nombre_completo, 
                            id_rol, telefono, direccion, is_active
                     FROM usuarios 
                     WHERE correo_electronico = %s"""
            cursor.execute(sql, (user.correo_electronico,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                return User(
                    id_usuario=row[0],
                    correo_electronico=row[1],
                    contraseña=row[2],
                    nombre_completo=row[3],
                    id_rol=row[4],
                    telefono=row[5],
                    direccion=row[6],
                    is_active=row[7]
                )
            return None

        except Exception as ex:
            raise Exception(ex)

    # ----------------------------
    # Obtener usuario por ID (Flask-Login)
    # ----------------------------
    @classmethod
    def get_by_id(cls, db, id_usuario):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT id_usuario, correo_electronico, nombre_completo, telefono, 
                       direccion, id_rol, is_active
                FROM usuarios
                WHERE id_usuario = %s
            """
            cursor.execute(sql, (id_usuario,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                return User(
                    id_usuario=row[0],
                    correo_electronico=row[1],
                    contraseña=None,
                    nombre_completo=row[2],
                    telefono=row[3],
                    direccion=row[4],
                    id_rol=row[5],
                    is_active=row[6]
                )
            return None

        except Exception as ex:
            raise Exception(ex)

    # ----------------------------
    # Obtener usuario por email
    # ----------------------------
    @classmethod
    def get_by_email(cls, db, email):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_usuario, correo_electronico, contraseña, nombre_completo, 
                            id_rol, telefono, direccion, is_active
                     FROM usuarios 
                     WHERE correo_electronico = %s"""
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                return User(
                    id_usuario=row[0],
                    correo_electronico=row[1],
                    contraseña=row[2],
                    nombre_completo=row[3],
                    id_rol=row[4],
                    telefono=row[5],
                    direccion=row[6],
                    is_active=row[7]
                )
            return None

        except Exception as ex:
            raise Exception(ex)

    # ----------------------------
    # Registrar nuevo usuario
    # ----------------------------
    @classmethod
    def register(cls, db, user, telefono):
        try:
            cursor = db.connection.cursor()
            hashed_password = generate_password_hash(user.contraseña)
            sql = """INSERT INTO usuarios 
                     (correo_electronico, contraseña, nombre_completo, telefono, 
                      fecha_registro, id_rol) 
                     VALUES (%s, %s, %s, %s, NOW(), 1)"""
            cursor.execute(sql, (user.correo_electronico, hashed_password,
                                 user.nombre_completo, telefono))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            return False

    # ----------------------------
    # Resetear contraseña
    # ----------------------------
    @classmethod
    def reset_password(cls, db, email, new_password):
        try:
            cursor = db.connection.cursor()
            hashed_password = generate_password_hash(new_password)
            sql = "UPDATE usuarios SET contraseña = %s WHERE correo_electronico = %s"
            cursor.execute(sql, (hashed_password, email))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            return False

    # ----------------------------
    # Total de usuarios
    # ----------------------------
    @classmethod
    def total_usuarios(cls, db):
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        result = cursor.fetchone()
        cursor.close()
        return result['total'] if result else 0

    # ----------------------------
    # Usuarios recientes
    # ----------------------------
    @classmethod
    def recientes(cls, db, dias=7):
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT nombre_completo, fecha_registro
            FROM usuarios
            WHERE fecha_registro >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY fecha_registro DESC
        """, (dias,))
        usuarios = cursor.fetchall()
        cursor.close()
        return usuarios

    # ----------------------------
    # Listar administradores
    # ----------------------------
    @classmethod
    def listar_admins(cls, db):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT id_usuario, correo_electronico, nombre_completo, id_rol
                FROM usuarios
                WHERE id_rol = 2
                ORDER BY nombre_completo ASC
            """
            cursor.execute(sql)
            admins = cursor.fetchall()
            cursor.close()
            return admins
        except Exception as ex:
            raise Exception(ex)

    # ----------------------------
    # Registrar administrador
    # ----------------------------
    @classmethod
    def registrar_admin(cls, db, user, telefono):
        try:
            cursor = db.connection.cursor()
            hashed_password = generate_password_hash(user.contraseña)
            sql = """INSERT INTO usuarios 
                     (correo_electronico, contraseña, nombre_completo, telefono, 
                      fecha_registro, id_rol) 
                     VALUES (%s, %s, %s, %s, NOW(), 2)"""
            cursor.execute(sql, (user.correo_electronico, hashed_password,
                                 user.nombre_completo, telefono))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            return False

    # ----------------------------
    # Listar todos los usuarios
    # ----------------------------
    @classmethod
    def listar_todos(cls, db):
        try:
            cursor = db.cursor()
            query = """
            SELECT 
                u.id_usuario,
                u.nombre_completo,
                u.correo_electronico,
                u.telefono,
                u.direccion,
                r.nombre AS rol,
                u.fecha_registro,
                u.is_active
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id_rol
            ORDER BY u.id_usuario ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            usuarios = []
            for row in rows:
                usuarios.append({
                    'id': row['id_usuario'],
                    'nombre': row['nombre_completo'],
                    'correo': row['correo_electronico'],
                    'telefono': row['telefono'],
                    'direccion': row['direccion'],
                    'rol': row['rol'] if row['rol'] else 'Usuario',
                    'fecha_registro': row['fecha_registro'],
                    'estado': row['is_active']   # 🔥 Cambiamos a 'estado'
                })
            return usuarios

        except Exception as ex:
            print("❌ Error al listar usuarios:", ex)
            raise Exception(ex)

@classmethod
def get_plan_activo(cls, db, id_usuario):
    """
    Consulta la base de datos para obtener el tipo de suscripción activa de un usuario.
    Retorna el 'nombre' del plan (ej: 'Básica', 'Premium') o None.
    """
    try:
        cursor = db.connection.cursor(dictionary=True) # Usamos dictionary=True para obtener resultados por nombre de columna
        
        # Consulta: Obtiene el nombre del plan (tipo_suscripcion.nombre) que está 'aprobada'
        # y que se encuentra vigente (fecha_fin >= fecha actual).
        query = """
        SELECT ts.nombre
        FROM suscripciones s
        JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
        WHERE s.id_usuario = %s
          AND s.estado = 'aprobada'
          AND s.fecha_fin >= CURDATE()
        ORDER BY s.fecha_inicio DESC
        LIMIT 1
        """
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            return resultado['nombre']
        return None

    except Exception as ex:
        # Aquí puedes loggear el error
        print(f"Error al obtener plan activo para el usuario {id_usuario}: {ex}")
        return None