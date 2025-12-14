"""
📁 ARCHIVO 1: src/models/ModelSuscripcion.py
Sistema completo de gestión de suscripciones para Hand&Genius
"""

from datetime import datetime, timedelta
from functools import wraps
from flask import flash, redirect, url_for, session
from flask_login import current_user

class ModelSuscripcion:
    """Modelo para gestionar suscripciones de usuarios"""

    # ===========================================
    # 📊 OBTENER INFORMACIÓN DE SUSCRIPCIÓN
    # ===========================================
    
    @classmethod
    def obtener_suscripcion_activa(cls, db, id_usuario):
        """
        Obtiene la suscripción activa y vigente de un usuario
        Returns: dict con info completa o None
        """
        try:
            cursor = db.connection.cursor()
            query = """
                SELECT 
                    s.id_suscripcion,
                    s.id_usuario,
                    s.fecha_inicio,
                    s.fecha_fin,
                    s.estado,
                    s.comprobante,
                    ts.id_tipo_suscripcion,
                    ts.nombre as tipo_nombre,
                    ts.descripcion as tipo_descripcion,
                    ts.precio_mensual,
                    DATEDIFF(s.fecha_fin, CURDATE()) as dias_restantes
                FROM suscripciones s
                INNER JOIN tipo_suscripcion ts 
                    ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
                WHERE s.id_usuario = %s 
                    AND s.estado = 'aprobada'
                    AND s.fecha_fin >= CURDATE()
                ORDER BY s.fecha_fin DESC
                LIMIT 1
            """
            cursor.execute(query, (id_usuario,))
            row = cursor.fetchone()
            cursor.close()

            if row:
                return {
                    'id_suscripcion': row[0],
                    'id_usuario': row[1],
                    'fecha_inicio': row[2],
                    'fecha_fin': row[3],
                    'estado': row[4],
                    'comprobante': row[5],
                    'id_tipo': row[6],
                    'tipo_nombre': row[7],
                    'tipo_descripcion': row[8],
                    'precio_mensual': float(row[9]),
                    'dias_restantes': row[10],
                    'es_premium': row[7].lower() == 'premium',
                    'es_basica': 'básica' in row[7].lower() or 'basica' in row[7].lower()
                }
            return None

        except Exception as ex:
            print(f"❌ Error al obtener suscripción: {ex}")
            return None

    @classmethod
    def tiene_suscripcion_activa(cls, db, id_usuario):
        """Verifica si el usuario tiene una suscripción activa"""
        suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
        return suscripcion is not None

    @classmethod
    def es_premium(cls, db, id_usuario):
        """Verifica si el usuario tiene plan Premium activo"""
        suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
        return suscripcion and suscripcion['es_premium']

    @classmethod
    def es_basica(cls, db, id_usuario):
        """Verifica si el usuario tiene plan Básica activo"""
        suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
        return suscripcion and suscripcion['es_basica']

    # ===========================================
    # 📺 CONTROL DE ACCESO A TUTORIALES
    # ===========================================
    
    @classmethod
    def puede_ver_tutorial(cls, db, id_usuario, tipo_video):
        """
        Determina si un usuario puede ver un tutorial según su tipo
        
        Args:
            tipo_video: 'publico', 'privado', 'premium'
        Returns: tuple (puede_ver: bool, razon: str)
        """
        # Videos públicos: todos pueden verlos
        if tipo_video == 'publico':
            return True, "Video público"

        suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
        
        # Sin suscripción: solo públicos
        if not suscripcion:
            return False, "Necesitas una suscripción para ver este contenido"

        # Videos privados: cualquier suscripción
        if tipo_video == 'privado':
            return True, "Acceso con suscripción"

        # Videos premium: solo Premium
        if tipo_video == 'premium':
            if suscripcion['es_premium']:
                return True, "Acceso Premium"
            else:
                return False, "Este video requiere suscripción Premium"

        return False, "Tipo de video no reconocido"

    @classmethod
    def obtener_limite_tutoriales(cls, db, id_usuario):
        """
        Retorna el límite de tutoriales según el plan
        Returns: int (0 = sin límite, 2 = básica, None = sin suscripción)
        """
        suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
        
        if not suscripcion:
            return None  # Sin acceso
        
        if suscripcion['es_premium']:
            return 0  # Ilimitado
        
        if suscripcion['es_basica']:
            return 2  # 2 tutoriales al mes
        
        return None

    @classmethod
    def tutoriales_vistos_este_mes(cls, db, id_usuario):
        """Cuenta cuántos tutoriales ha visto el usuario este mes"""
        try:
            cursor = db.connection.cursor()
            # Aquí deberías tener una tabla de "visualizaciones" o similar
            # Por ahora retornamos 0, pero implementa según tu lógica
            cursor.close()
            return 0
        except Exception as ex:
            print(f"❌ Error contando tutoriales vistos: {ex}")
            return 0

    @classmethod
    def obtener_videotutoriales_premium(cls, db, limite=None):
        """Obtiene videotutoriales premium según el límite especificado"""
        try:
            cursor = db.connection.cursor()
            
            if limite:
                cursor.execute("""
                    SELECT p.id_producto, p.nombre, p.descripcion, p.url_video, 
                        p.duracion, p.nivel_dificultad, p.imagen
                    FROM productos p
                    WHERE p.id_categoria = 4 AND p.tipo_video = 'premium'
                    ORDER BY p.id_producto DESC
                    LIMIT %s
                """, (limite,))
            else:
                cursor.execute("""
                    SELECT p.id_producto, p.nombre, p.descripcion, p.url_video, 
                        p.duracion, p.nivel_dificultad, p.imagen
                    FROM productos p
                    WHERE p.id_categoria = 4 AND p.tipo_video = 'premium'
                    ORDER BY p.id_producto DESC
                """)
            
            tutoriales = cursor.fetchall()
            cursor.close()
            
            print(f"🔍 DEBUG: Se encontraron {len(tutoriales)} videotutoriales premium")
            if tutoriales:
                print(f"🔍 DEBUG: Primer tutorial: {tutoriales[0]}")
            
            return tutoriales
        except Exception as ex:
            print(f"❌ Error al obtener videotutoriales premium: {ex}")
            return []

    # ===========================================
    # 💰 DESCUENTOS Y BENEFICIOS
    # ===========================================
    
    @classmethod
    def obtener_descuento(cls, db, id_usuario):
        """
        Retorna el porcentaje de descuento según el plan
        Returns: float (0.0 - 1.0)
        """
        suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
        
        if not suscripcion:
            return 0.0
        
        if suscripcion['es_premium']:
            return 0.15  # 15% de descuento
        
        if suscripcion['es_basica']:
            return 0.05  # 5% de descuento
        
        return 0.0

    @classmethod
    def aplicar_descuento(cls, db, id_usuario, precio):
        """Aplica el descuento al precio según el plan del usuario"""
        descuento = cls.obtener_descuento(db, id_usuario)
        precio_final = precio * (1 - descuento)
        return round(precio_final, 2)

    # ===========================================
    # 🔄 GESTIÓN DE SUSCRIPCIONES
    # ===========================================
    
    @classmethod
    def crear_suscripcion(cls, db, id_usuario, id_tipo, comprobante):
        """Crea una nueva solicitud de suscripción"""
        try:
            cursor = db.connection.cursor()
            
            # Calcular fechas
            fecha_inicio = datetime.now().date()
            fecha_fin = fecha_inicio + timedelta(days=30)
            
            query = """
                INSERT INTO suscripciones 
                (id_usuario, id_tipo_suscripcion, fecha_inicio, fecha_fin, 
                 comprobante, estado)
                VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """
            cursor.execute(query, (
                id_usuario, id_tipo, fecha_inicio, fecha_fin, comprobante
            ))
            db.connection.commit()
            cursor.close()
            return True
            
        except Exception as ex:
            db.connection.rollback()
            print(f"❌ Error al crear suscripción: {ex}")
            return False

    @classmethod
    def verificar_expiracion(cls, db):
        """Marca como vencidas las suscripciones expiradas"""
        try:
            cursor = db.connection.cursor()
            query = """
                UPDATE suscripciones 
                SET estado = 'vencida'
                WHERE estado = 'aprobada' 
                    AND fecha_fin < CURDATE()
            """
            cursor.execute(query)
            db.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected
            
        except Exception as ex:
            db.connection.rollback()
            print(f"❌ Error verificando expiraciones: {ex}")
            return 0

    @classmethod
    def renovar_suscripcion(cls, db, id_usuario, id_tipo):
        """Renueva una suscripción existente por 30 días más"""
        try:
            cursor = db.connection.cursor()
            
            # Buscar suscripción actual
            suscripcion = cls.obtener_suscripcion_activa(db, id_usuario)
            
            if suscripcion:
                # Renovar desde la fecha de fin actual
                nueva_fecha_fin = suscripcion['fecha_fin'] + timedelta(days=30)
                query = """
                    UPDATE suscripciones 
                    SET fecha_fin = %s
                    WHERE id_suscripcion = %s
                """
                cursor.execute(query, (nueva_fecha_fin, suscripcion['id_suscripcion']))
            else:
                # Crear nueva suscripción
                fecha_inicio = datetime.now().date()
                fecha_fin = fecha_inicio + timedelta(days=30)
                query = """
                    INSERT INTO suscripciones 
                    (id_usuario, id_tipo_suscripcion, fecha_inicio, fecha_fin, estado)
                    VALUES (%s, %s, %s, %s, 'aprobada')
                """
                cursor.execute(query, (id_usuario, id_tipo, fecha_inicio, fecha_fin))
            
            db.connection.commit()
            cursor.close()
            return True
            
        except Exception as ex:
            db.connection.rollback()
            print(f"❌ Error al renovar suscripción: {ex}")
            return False


# ===========================================
# 🔒 DECORADORES PARA PROTEGER RUTAS
# ===========================================

def suscripcion_requerida(f):
    """Decorador: Requiere cualquier suscripción activa"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('auth_bp.login'))
        
        from flask import current_app
        tiene_suscripcion = ModelSuscripcion.tiene_suscripcion_activa(
            current_app.db, current_user.id_usuario
        )
        
        if not tiene_suscripcion:
            flash('Necesitas una suscripción activa para acceder a este contenido', 'warning')
            return redirect(url_for('suscripciones_bp.suscripcion'))
        
        return f(*args, **kwargs)
    return decorated_function


def premium_requerido(f):
    """Decorador: Requiere suscripción Premium"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('auth_bp.login'))
        
        from flask import current_app
        es_premium = ModelSuscripcion.es_premium(
            current_app.db, current_user.id_usuario
        )
        
        if not es_premium:
            flash('Este contenido requiere suscripción Premium', 'warning')
            return redirect(url_for('suscripciones_bp.suscripcion'))
        
        return f(*args, **kwargs)
    return decorated_function


def verificar_acceso_tutorial(tipo_video):
    """Decorador: Verifica acceso a tutorial según su tipo"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión', 'warning')
                return redirect(url_for('auth_bp.login'))
            
            from flask import current_app
            puede_ver, razon = ModelSuscripcion.puede_ver_tutorial(
                current_app.db, current_user.id_usuario, tipo_video
            )
            
            if not puede_ver:
                flash(razon, 'warning')
                return redirect(url_for('suscripciones_bp.suscripcion'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator