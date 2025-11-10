from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, timedelta
from src.models.ModelUser import ModelUser
from src.models.entities.User import User
from src.models.ModelSugerencia import ModelSugerencia
from src.database.db import get_connection
import os
import pymysql

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='../../templates/admin')


# ---------------------------
# Decorador: solo administradores
# ---------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for('auth_bp.login'))
        # Ajusta el id_rol según tu sistema (en tu app habías usado 1 o 2)
        if getattr(current_user, 'id_rol', None) not in (1, 2):  # permisos admin: 1 ó 2
            flash("No tienes permisos para acceder al panel de administración.", "danger")
            return redirect(url_for('home_bp.home'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------
# Helpers para convertir resultados a dicts
# ---------------------------
def fetchall_dict(cursor):
    cols = [d[0] for d in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    result = []
    for r in rows:
        # r may be tuple or dict depending on driver; handle both
        if isinstance(r, dict):
            result.append(r)
        else:
            result.append({cols[i]: r[i] for i in range(len(cols))})
    return result

def fetchone_dict(cursor):
    cols = [d[0] for d in cursor.description] if cursor.description else []
    r = cursor.fetchone()
    if not r:
        return None
    if isinstance(r, dict):
        return r
    return {cols[i]: r[i] for i in range(len(cols))}


# ---------------------------
# Dashboard principal
# ---------------------------
@admin_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    db = current_app.db  # tu MySQL(app) guardado como app.db
    estadisticas = {
        "total_usuarios": 0,
        "total_productos": 0,
        "total_pedidos": 0,
        "pedidos_pendientes": 0,
        "ingresos_mes": 0,
        "productos_populares": [],
        "actividad_reciente": []
    }

    try:
        cursor = db.connection.cursor()
        # Total usuarios
        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            estadisticas["total_usuarios"] = cursor.fetchone()[0] or 0
        except Exception:
            estadisticas["total_usuarios"] = 0

        # Total productos (intenta columnas comunes)
        try:
            cursor.execute("SELECT COUNT(*) FROM producto")
            estadisticas["total_productos"] = cursor.fetchone()[0] or 0
        except Exception:
            try:
                cursor.execute("SELECT COUNT(*) FROM productos")
                estadisticas["total_productos"] = cursor.fetchone()[0] or 0
            except Exception:
                estadisticas["total_productos"] = 0

        # Total pedidos
        try:
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            estadisticas["total_pedidos"] = cursor.fetchone()[0] or 0
        except Exception:
            estadisticas["total_pedidos"] = 0

        # Pedidos pendientes
        try:
            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'pendiente'")
            estadisticas["pedidos_pendientes"] = cursor.fetchone()[0] or 0
        except Exception:
            estadisticas["pedidos_pendientes"] = 0

        # Ingresos del mes (ejemplo sencillo usando columna total si existe)
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(total),0) 
                FROM pedidos 
                WHERE MONTH(fecha_pedido)=MONTH(CURDATE()) AND YEAR(fecha_pedido)=YEAR(CURDATE())
            """)
            val = cursor.fetchone()[0]
            estadisticas["ingresos_mes"] = float(val or 0)
        except Exception:
            estadisticas["ingresos_mes"] = 0

        # Productos populares (intenta una consulta genérica)
        try:
            cursor.execute("""
                SELECT p.nombre AS nombre, SUM(dp.cantidad) AS ventas
                FROM detalle_pedido dp
                JOIN productos p ON dp.id_producto = p.id_producto
                JOIN pedidos pe ON dp.id_pedido = pe.id_pedido
                WHERE pe.fecha_pedido >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY p.id_producto, p.nombre
                ORDER BY ventas DESC
                LIMIT 5
            """)
            estadisticas["productos_populares"] = fetchall_dict(cursor)
        except Exception:
            estadisticas["productos_populares"] = []

        # Actividad reciente (pedidos y usuarios recientes)
        actividad = []
        try:
            cursor.execute("""
                SELECT 'pedido' AS tipo, CONCAT('Pedido #', id_pedido) AS descripcion, fecha_pedido AS fecha
                FROM pedidos
                WHERE fecha_pedido >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY fecha_pedido DESC
                LIMIT 5
            """)
            actividad += fetchall_dict(cursor)
        except Exception:
            pass

        try:
            cursor.execute("""
                SELECT 'usuario' AS tipo, CONCAT('Nuevo usuario: ', nombre_completo) AS descripcion, fecha_registro AS fecha
                FROM usuarios
                WHERE fecha_registro >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY fecha_registro DESC
                LIMIT 5
            """)
            actividad += fetchall_dict(cursor)
        except Exception:
            pass

        # Ordenar por fecha descendente y recortar a 10
        try:
            actividad = sorted(actividad, key=lambda x: x.get('fecha') or '', reverse=True)[:10]
            estadisticas["actividad_reciente"] = actividad
        except Exception:
            estadisticas["actividad_reciente"] = []

        cursor.close()
    except Exception as e:
        # Si algo falla, devolvemos estadisticas por defecto (no None)
        current_app.logger.exception("Error cargando estadísticas admin: %s", e)
        estadisticas = estadisticas

    return render_template('admin/dashboard.html', estadisticas=estadisticas, user=current_user)


# ---------------------------
# Usuarios list (admin)
# ---------------------------
@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    db = get_connection()
    usuarios = ModelUser.listar_todos(db)
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuario/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(id):
    from src.database.db import get_connection

    connection = get_connection()
    if not connection:
        flash("❌ Error al conectar con la base de datos", "danger")
        return redirect(url_for('admin_bp.usuarios'))

    try:
        with connection.cursor() as cursor:
            # 1️⃣ Productos del usuario
            cursor.execute("SELECT id_producto FROM productos WHERE id_vendedor = %s", (id,))
            productos = cursor.fetchall()
            if productos:
                producto_ids = tuple(prod['id_producto'] for prod in productos)
                if len(producto_ids) == 1:
                    producto_ids = (producto_ids[0],)
                placeholders = ','.join(['%s'] * len(producto_ids))
                cursor.execute(f"DELETE FROM calificaciones WHERE id_producto IN ({placeholders})", producto_ids)
                cursor.execute(f"DELETE FROM detalle_pedido WHERE id_producto IN ({placeholders})", producto_ids)
                cursor.execute(f"DELETE FROM material_audiovisual WHERE id_producto IN ({placeholders})", producto_ids)
                cursor.execute(f"DELETE FROM producto_relacion WHERE id_producto_padre IN ({placeholders}) OR id_producto_hijo IN ({placeholders})", producto_ids*2)
                cursor.execute(f"DELETE FROM productos WHERE id_producto IN ({placeholders})", producto_ids)

            # 2️⃣ Pedidos del usuario
            cursor.execute("SELECT id_pedido FROM pedidos WHERE id_usuario = %s", (id,))
            pedidos = cursor.fetchall()
            pedido_ids = tuple(p['id_pedido'] for p in pedidos) if pedidos else ()

            if pedido_ids:
                placeholders = ','.join(['%s'] * len(pedido_ids))
                cursor.execute(f"DELETE FROM detalle_pedido WHERE id_pedido IN ({placeholders})", pedido_ids)
                cursor.execute(f"DELETE FROM domicilio WHERE id_pedido IN ({placeholders})", pedido_ids)
                cursor.execute(f"DELETE FROM pedidos WHERE id_pedido IN ({placeholders})", pedido_ids)

            # 3️⃣ Calendario
            cursor.execute("DELETE FROM calendario WHERE id_usuario = %s", (id,))

            # 4️⃣ Suscripciones
            cursor.execute("DELETE FROM suscripciones WHERE id_usuario = %s", (id,))

            # 5️⃣ Usuario
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))

            connection.commit()
            flash("✅ Usuario y todos sus datos relacionados eliminados correctamente", "success")

    except Exception as e:
        connection.rollback()
        flash("❌ Error inesperado al eliminar usuario. Revisa la consola para detalles.", "danger")
        import traceback
        print(traceback.format_exc())

    finally:
        connection.close()

    return redirect(url_for('admin_bp.usuarios'))



@admin_bp.route('/usuario/<int:id_usuario>/editar', methods=['POST'])
@login_required
def admin_editar_usuario(id_usuario):
    """Editar usuario existente desde el panel admin"""
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')

    if not nombre or not correo:
        flash('❌ Nombre y correo son obligatorios.', 'warning')
        return redirect(url_for('admin_bp.usuarios'))

    conn = get_connection()
    if not conn:
        flash("❌ Error al conectar con la base de datos", "danger")
        return redirect(url_for('admin_bp.usuarios'))

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE usuarios
                SET nombre_completo = %s,
                    correo_electronico = %s,
                    telefono = %s,
                    direccion = %s
                WHERE id_usuario = %s
            """, (nombre, correo, telefono, direccion, id_usuario))
            conn.commit()

        flash("✅ Usuario actualizado correctamente.", "success")
    except Exception as e:
        flash(f"❌ Error inesperado al editar usuario: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('admin_bp.usuarios'))

# ---------------------------
# Productos list (admin)
# ---------------------------
@admin_bp.route('/productos')
@login_required
@admin_required
def productos():
    db = current_app.db
    try:
        cursor = db.connection.cursor()
        # prueba con nombres tablas posibles
        try:
            cursor.execute("SELECT id_producto AS id, nombre, precio FROM productos ORDER BY nombre")
        except Exception:
            cursor.execute("SELECT id_producto AS id, nombre, precio FROM producto ORDER BY nombre")
        productos = fetchall_dict(cursor)
        cursor.close()
    except Exception as e:
        productos = []
        current_app.logger.exception("Error obteniendo productos: %s", e)
        flash("Error al cargar productos.", "danger")
    return render_template('admin/productos.html', productos=productos, user=current_user)

@admin_bp.route('/productos/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_producto():
    db = current_app.db
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    descripcion = request.form.get('descripcion', '')

    if not nombre or not precio:
        flash("❌ El nombre y el precio son obligatorios", "warning")
        return redirect(url_for('admin_bp.productos'))

    try:
        cursor = db.connection.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, precio, descripcion) VALUES (%s, %s, %s)",
            (nombre, precio, descripcion)
        )
        db.connection.commit()
        cursor.close()
        flash("✅ Producto agregado correctamente", "success")
    except Exception as e:
        db.connection.rollback()
        current_app.logger.exception("Error agregando producto: %s", e)
        flash("❌ Error al agregar el producto", "danger")

    return redirect(url_for('admin_bp.productos'))

# -----------------------------
# Sugerencias
# -----------------------------
@admin_bp.route('/sugerencias', endpoint='admin_sugerencias')
@login_required
@admin_required
def admin_sugerencias():
    try:
        db = current_app.db
        sugerencias = ModelSugerencia.obtener_todas(db)
        return render_template('admin/sugerencias.html', sugerencias=sugerencias, user=current_user)
    except Exception as e:
        print(f"❌ Error al cargar sugerencias: {e}")
        flash(f"Error al cargar sugerencias: {str(e)}", "danger")
        return render_template('admin/sugerencias.html', sugerencias=[], user=current_user)


# -----------------------------
# ✅ Aprobar / Rechazar sugerencias con retroalimentación
# -----------------------------
@admin_bp.route('/sugerencia/<int:id_sugerencia>/aprobar', methods=['POST'], endpoint='admin_aprobar_sugerencia')
@login_required
@admin_required
def admin_aprobar_sugerencia(id_sugerencia):
    try:
        retroalimentacion = request.form.get('retroalimentacion', '').strip()
        db = current_app.db
        ok = ModelSugerencia.cambiar_estado(db, id_sugerencia, 'aceptada', retroalimentacion)
        if ok:
            flash("✅ Sugerencia aprobada con retroalimentación enviada al usuario.", "success")
        else:
            flash("Error al aprobar sugerencia.", "danger")
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"❌ Error al aprobar sugerencia: {e}")
        flash(f"Error al aprobar sugerencia: {str(e)}", "danger")
    return redirect(url_for('admin_bp.admin_sugerencias'))


@admin_bp.route('/sugerencia/<int:id_sugerencia>/rechazar', methods=['POST'], endpoint='admin_rechazar_sugerencia')
@login_required
@admin_required
def admin_rechazar_sugerencia(id_sugerencia):
    try:
        retroalimentacion = request.form.get('retroalimentacion', '').strip()
        db = current_app.db
        ok = ModelSugerencia.cambiar_estado(db, id_sugerencia, 'rechazada', retroalimentacion)
        if ok:
            flash("❌ Sugerencia rechazada y retroalimentación enviada al usuario.", "warning")
        else:
            flash("Error al rechazar sugerencia.", "danger")
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"❌ Error al rechazar sugerencia: {e}")
        flash(f"Error al rechazar sugerencia: {str(e)}", "danger")
    return redirect(url_for('admin_bp.admin_sugerencias'))

# ---------------------------
# Suscripciones list (admin)
# ---------------------------
@admin_bp.route('/suscripciones')
@login_required
@admin_required
def suscripciones():
    db = current_app.db
    try:
        cursor = db.connection.cursor()
        # Intenta seleccionar campos comunes
        try:
            cursor.execute("""
                SELECT s.id_suscripcion, u.nombre_completo AS usuario, ts.nombre AS tipo, s.fecha_inicio, s.fecha_fin, s.comprobante, s.estado
                FROM suscripciones s
                LEFT JOIN usuarios u ON s.id_usuario = u.id_usuario
                LEFT JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
                ORDER BY s.fecha_inicio DESC
            """)
        except Exception:
            cursor.execute("""
                SELECT s.id_suscripcion, u.nombre_completo AS usuario, s.id_tipo_suscripcion AS tipo, s.fecha_inicio, s.fecha_fin, s.comprobante, s.estado
                FROM suscripciones s
                LEFT JOIN usuarios u ON s.id_usuario = u.id_usuario
                ORDER BY s.fecha_inicio DESC
            """)
        suscripciones = fetchall_dict(cursor)
        cursor.close()
    except Exception as e:
        suscripciones = []
        current_app.logger.exception("Error obteniendo suscripciones: %s", e)
        flash("Error al cargar suscripciones.", "danger")
    return render_template('admin/suscripciones.html', suscripciones=suscripciones, user=current_user)


# ---------------------------
# Aprobar suscripción (POST)
# ---------------------------
@admin_bp.route('/suscripciones/aprobar/<int:id_suscripcion>', methods=['POST'])
@login_required
@admin_required
def aprobar_suscripcion(id_suscripcion):
    db = current_app.db
    try:
        cursor = db.connection.cursor()
        nueva_fecha_inicio = date.today()
        nueva_fecha_fin = nueva_fecha_inicio + timedelta(days=30)
        cursor.execute(
            "UPDATE suscripciones SET estado = %s, fecha_inicio = %s, fecha_fin = %s WHERE id_suscripcion = %s",
            ('Aprobada', nueva_fecha_inicio, nueva_fecha_fin, id_suscripcion)
        )
        db.connection.commit()
        cursor.close()
        flash("Suscripción aprobada correctamente.", "success")
    except Exception as e:
        current_app.logger.exception("Error aprobando suscripción: %s", e)
        flash("Error al aprobar la suscripción.", "danger")
    return redirect(url_for('admin_bp.suscripciones'))


# ---------------------------
# Rechazar suscripción (POST)
# ---------------------------
@admin_bp.route('/suscripciones/rechazar/<int:id_suscripcion>', methods=['POST'])
@login_required
@admin_required
def rechazar_suscripcion(id_suscripcion):
    db = current_app.db
    try:
        cursor = db.connection.cursor()
        cursor.execute("UPDATE suscripciones SET estado = %s WHERE id_suscripcion = %s", ('Rechazada', id_suscripcion))
        db.connection.commit()
        cursor.close()
        flash("Suscripción rechazada correctamente.", "info")
    except Exception as e:
        current_app.logger.exception("Error rechazando suscripción: %s", e)
        flash("Error al rechazar la suscripción.", "danger")
    return redirect(url_for('admin_bp.suscripciones'))

# ---------------------------
# Ver comprobante de suscripción
# ---------------------------
@admin_bp.route('/suscripciones/comprobante/<path:filename>')
@login_required
@admin_required
def ver_comprobante(filename):
    from flask import send_from_directory
    import os

    # Ruta donde se guardan los comprobantes (ajústala si cambia)
    upload_path = os.path.join(current_app.root_path, 'static', 'comprobantes')

    try:
        return send_from_directory(upload_path, filename, as_attachment=False)
    except Exception as e:
        current_app.logger.exception("Error mostrando comprobante: %s", e)
        flash("No se pudo mostrar el comprobante.", "danger")
        return redirect(url_for('admin_bp.suscripciones'))

# ---------------------------
# Descargar/ver comprobante (si lo guardaste en /static/uploads/comprobantes/)
# ---------------------------
# Nota: habitualmente se usa "url_for('static', filename='uploads/comprobantes/archivo.pdf')"
# No es necesario una ruta especial para servirlo si usas static.
