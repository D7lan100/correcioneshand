from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, timedelta, datetime
from src.models.ModelUser import ModelUser
from src.models.entities.User import User
from src.models.ModelSugerencia import ModelSugerencia
from src.models.ModelEstadisticas import ModelEstadisticas
from src.models.ModelSuscripcion import ModelSuscripcion
from src.database.db import get_connection
import os

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
        # 🚨 CORRECCIÓN: Si el rol 2 es el administrador, solo se permite ese rol.
        if getattr(current_user, 'id_rol', None) != 2:
            flash("No tienes permisos para acceder al panel de administración.", "danger")
            return redirect(url_for('home_bp.home'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Helpers (fetch functions)
# ---------------------------
def fetchall_dict(cursor):
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

def fetchone_dict(cursor):
    cols = [d[0] for d in cursor.description] if cursor.description else []
    row = cursor.fetchone()
    return dict(zip(cols, row)) if row else None

# ---------------------------
# Dashboard principal (Listas funcionales)
# ---------------------------
@admin_bp.route('/')
@login_required
@admin_required
def index():
    db = current_app.db

    estadisticas = {
        "total_ingresos": ModelEstadisticas.total_ingresos(db),
        "total_pedidos": ModelEstadisticas.total_pedidos(db),
        "total_usuarios": ModelEstadisticas.total_usuarios(db),
        "ingresos_mes": ModelEstadisticas.ingresos_por_mes(db),
    }

    return render_template(
        'admin/dashboard_funcional.html',
        user=current_user,
        estadisticas=estadisticas
    )
    
# ---------------------------
# API: Datos para los gráficos 
# ---------------------------
@admin_bp.route('/dashboard/data')
@login_required
@admin_required
def dashboard_data():
    conn = get_connection()
    categoria = request.args.get("categoria")
    
    hoy = date.today()
    hace_30_dias = hoy - timedelta(days=30)
    
    try:
        cur = conn.cursor()

        # 🔹 Estados de pedidos (Dona)
        cur.execute("SELECT estado, COUNT(*) AS cantidad FROM pedidos GROUP BY estado")
        estados = fetchall_dict(cur)

        # 🔹 Productos más vendidos (Gráfico de Barras)
        query_productos = """
            SELECT p.nombre AS nombre, COALESCE(SUM(dp.cantidad), 0) AS ventas
            FROM productos p 
            LEFT JOIN detalle_pedido dp ON dp.id_producto = p.id_producto
        """
        params_productos = []
        if categoria and categoria != "todas":
            query_productos += " WHERE p.id_categoria = %s"
            params_productos.append(categoria)

        query_productos += " GROUP BY p.id_producto, p.nombre ORDER BY ventas DESC LIMIT 5"
        cur.execute(query_productos, params_productos)
        productos = fetchall_dict(cur)
        
        # 🔹 Cantidad de Pedidos Diarios (Gráfico de Línea)
        query_pedidos_diarios = """
            SELECT 
                DATE(fecha_pedido) AS fecha, 
                COUNT(id_pedido) AS cantidad
            FROM pedidos 
            WHERE fecha_pedido >= %s
            GROUP BY DATE(fecha_pedido)
            ORDER BY fecha ASC
        """
        cur.execute(query_pedidos_diarios, (hace_30_dias,))
        pedidos_raw = fetchall_dict(cur)
        
        # Rellenar con días sin pedidos (Corregido para manejar strings y date objects)
        pedidos_dias = {}
        for item in pedidos_raw:
            fecha_data = item['fecha']
            if isinstance(fecha_data, (date, datetime)):
                fecha_key = fecha_data.strftime('%Y-%m-%d')
            else:
                fecha_key = str(fecha_data)
                
            pedidos_dias[fecha_key] = item['cantidad']
            
        pedidos_diarios = []
        for i in range(30):
            dia = hace_30_dias + timedelta(days=i)
            fecha_str = dia.strftime('%Y-%m-%d')
            pedidos_diarios.append({
                'fecha': dia.strftime('%d/%m'),
                'cantidad': pedidos_dias.get(fecha_str, 0)
            })

        cur.close()
        conn.close()

        return jsonify({
            "productos": productos,
            "estados": estados,
            "pedidos_diarios": pedidos_diarios
        })

    except Exception as e:
        print("❌ Error en dashboard/data:", e)
        return jsonify({"error": str(e)}), 500
    
# ---------------------------
# USUARIOS
# ---------------------------
@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    db = get_connection()
    
    # 1. Cargar todos los usuarios usando la función que SÍ FUNCIONA
    try:
        # Esto nos da la lista completa y ya formateada por ModelUser
        usuarios_completos = ModelUser.listar_todos(db)
    except Exception as e:
        print(f"❌ ERROR CRÍTICO al cargar usuarios desde ModelUser: {e}")
        flash("❌ Error al cargar la lista de usuarios. La conexión falló.", "danger")
        usuarios_completos = []

    # 2. Obtener parámetros de filtro
    q = request.args.get('q', '').strip().lower()
    rol_id = request.args.get('rol_id')
    estado = request.args.get('estado')
    
    # 3. Aplicar filtros en Python (la lista se llama 'usuarios')
    usuarios = []
    
    for u in usuarios_completos:
        coincide = True
        
        # 3a. Filtro de Búsqueda (q)
        if q:
            # Buscamos en nombre, correo o teléfono (convertimos a string por seguridad)
            nombre = str(u.get('nombre', '')).lower()
            correo = str(u.get('correo', '')).lower()
            telefono = str(u.get('telefono', '')).lower()
            
            if q not in nombre and q not in correo and q not in telefono:
                coincide = False

        # 3b. Filtro por Rol (rol_id)
        if rol_id:
            # Convertir el nombre del rol a minúsculas para comparar con el ID
            rol_nombre = str(u.get('rol', '')).lower()
            
            # Asumimos que 1='usuario' y 2='administrador'
            if rol_id == '1' and rol_nombre != 'usuario':
                coincide = False
            elif rol_id == '2' and rol_nombre != 'administrador':
                coincide = False

        # 3c. Filtro por Estado (estado)
        if estado:
            # El campo 'estado' viene como 1 o 0 de ModelUser.py (línea: 'estado': row['is_active'])
            estado_usuario = str(u.get('estado'))
            
            if estado != estado_usuario:
                coincide = False
        
        # Si pasó todos los filtros, lo añadimos a la lista final
        if coincide:
            usuarios.append(u)
        
    # 4. Renderizar
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuario/<int:id_usuario>/estado', methods=['POST'])
@login_required
@admin_required
def cambiar_estado_usuario(id_usuario):
    nuevo_estado = request.form.get('estado')

    if nuevo_estado not in ['0', '1']:
        flash("❌ Estado inválido.", "danger")
        return redirect(url_for('admin_bp.usuarios'))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuarios 
            SET is_active = %s
            WHERE id_usuario = %s
        """, (nuevo_estado, id_usuario))
        conn.commit()

        if nuevo_estado == '1':
            flash("✅ Usuario activado correctamente.", "success")
        else:
            flash("⚠️ Usuario desactivado correctamente.", "warning")

    except Exception as e:
        conn.rollback()
        print(e)
        flash("❌ Error al cambiar estado del usuario.", "danger")
    finally:
        conn.close()

    return redirect(url_for('admin_bp.usuarios'))

@admin_bp.route('/usuario/<int:id_usuario>/editar', methods=['POST'])
@login_required
@admin_required
def admin_editar_usuario(id_usuario):
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    id_rol = request.form.get('id_rol')

    if not nombre or not correo:
        flash('❌ Nombre y correo son obligatorios.', 'warning')
        return redirect(url_for('admin_bp.usuarios'))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuarios 
            SET nombre_completo=%s, correo_electronico=%s, telefono=%s, direccion=%s, id_rol=%s 
            WHERE id_usuario=%s
        """, (nombre, correo, telefono, direccion, id_rol, id_usuario))
        conn.commit()
        flash("✅ Usuario actualizado correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash("❌ Error al editar usuario.", "danger")
        print(e)
    finally:
        conn.close()
    return redirect(url_for('admin_bp.usuarios'))

@admin_bp.route('/usuario/<int:id>/eliminar', methods=['POST']) 
@login_required 
@admin_required 
def eliminar_usuario(id): 
    conn = get_connection() 
    try: 
        cur = conn.cursor() 
        cur.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id,)) 
        conn.commit() 
        flash("✅ Usuario eliminado correctamente", "success") 
    except Exception as e: 
        conn.rollback() 
        print(e) 
        flash("❌ Error al eliminar usuario", "danger") 
    finally: 
        conn.close() 
    return redirect(url_for('admin_bp.usuarios'))

# ---------------------------
# PRODUCTOS
# ---------------------------
@admin_bp.route('/productos')
@login_required
@admin_required
def productos():
    db = current_app.db
    try:
        cur = db.connection.cursor()
        cur.execute("""
            SELECT 
                p.id_producto,
                p.nombre,
                p.descripcion,
                p.precio,
                p.imagen,
                p.disponible,
                p.es_personalizable,
                p.id_categoria,
                c.nombre AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            ORDER BY p.id_producto DESC
        """)
        productos = fetchall_dict(cur)

        cur.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre ASC")
        categorias = fetchall_dict(cur)

        cur.close()
    except Exception as e:
        productos = []
        categorias = []
        flash("Error al cargar productos.", "danger")
        print(e)
    return render_template('admin/productos.html', productos=productos, categorias=categorias, user=current_user)

@admin_bp.route('/productos/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_producto():
    db = current_app.db
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    descripcion = request.form.get('descripcion', '')
    disponible = request.form.get('disponible', 1)
    es_personalizable = request.form.get('es_personalizable', 0)
    id_categoria = request.form.get('id_categoria') or None
    imagen = request.form.get('imagen', None)

    if not nombre or not precio:
        flash("❌ El nombre y el precio son obligatorios", "warning")
        return redirect(url_for('admin_bp.productos'))

    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, precio, imagen, id_categoria, disponible, es_personalizable)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, imagen, id_categoria, disponible, es_personalizable))

        db.connection.commit()
        cursor.close()
        flash("✅ Producto agregado correctamente", "success")

    except Exception as e:
        db.connection.rollback()
        current_app.logger.exception("Error agregando producto: %s", e)
        flash("❌ Error al agregar el producto", "danger")

    return redirect(url_for('admin_bp.productos'))

@admin_bp.route('/producto/<int:id_producto>/editar', methods=['POST'])
@login_required
@admin_required
def editar_producto(id_producto):
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    imagen = request.form.get('imagen')
    categoria = request.form.get('id_categoria')
    disponible = int(request.form.get('disponible', 0))
    personalizable = int(request.form.get('es_personalizable', 0))

    if not nombre or not precio:
        flash("❌ El nombre y el precio son obligatorios", "warning")
        return redirect(url_for('admin_bp.productos'))

    try:
        cur = current_app.db.connection.cursor()
        cur.execute("""
            UPDATE productos
            SET nombre=%s,
                descripcion=%s,
                precio=%s,
                imagen=%s,
                id_categoria=%s,
                disponible=%s,
                es_personalizable=%s
            WHERE id_producto=%s
        """, (nombre, descripcion, precio, imagen, categoria, disponible, personalizable, id_producto))
        current_app.db.connection.commit()
        cur.close()
        flash("✅ Producto actualizado correctamente", "success")
    except Exception as e:
        current_app.db.connection.rollback()
        current_app.logger.exception("Error al editar producto: %s", e)
        flash("❌ Error al editar el producto", "danger")

    return redirect(url_for('admin_bp.productos'))

@admin_bp.route('/producto/<int:id_producto>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_producto(id_producto):
    try:
        cur = current_app.db.connection.cursor()
        cur.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        current_app.db.connection.commit()
        cur.close()
        flash("🗑️ Producto eliminado correctamente", "info")
    except Exception as e:
        current_app.db.connection.rollback()
        current_app.logger.exception("Error al eliminar producto: %s", e)
        flash("❌ No se pudo eliminar el producto", "danger")

    return redirect(url_for('admin_bp.productos'))

# ---------------------------
# SUGERENCIAS
# ---------------------------
@admin_bp.route('/sugerencias', endpoint='admin_sugerencias')
@login_required
@admin_required
def admin_sugerencias():
    try:
        db = current_app.db
        sugerencias = ModelSugerencia.obtener_todas(db)
    except Exception as e:
        print(f"❌ Error al cargar sugerencias: {e}")
        sugerencias = []
    return render_template('admin/sugerencias.html', sugerencias=sugerencias, user=current_user)

@admin_bp.route('/cambiar_estado_sugerencia/<int:id_sugerencia>', methods=['POST'])
@login_required
@admin_required
def cambiar_estado_sugerencia(id_sugerencia):
    try:
        nuevo_estado = request.form.get('estado')
        retroalimentacion = request.form.get('retroalimentacion', '').strip()

        if nuevo_estado not in ('pendiente', 'aceptada', 'rechazada', 'Pendiente', 'Aprobada', 'Rechazada'):
            flash("❌ Estado inválido.", "danger")
            return redirect(url_for('admin_bp.admin_sugerencias'))

        db = current_app.db  # usar la conexión correcta

        # ⚠ AHORA SÍ SE ENVÍA LA RETROALIMENTACIÓN AL MODELO
        ok = ModelSugerencia.cambiar_estado(db, id_sugerencia, nuevo_estado, retroalimentacion)
        if not ok:
            flash("❌ No se pudo actualizar el estado en la base de datos.", "danger")
            return redirect(url_for('admin_bp.admin_sugerencias'))

        # Obtener la sugerencia
        sugerencia = ModelSugerencia.get_by_id(db, id_sugerencia)
        if sugerencia:
            id_usuario = getattr(sugerencia, 'id_usuario', None)
            titulo = getattr(sugerencia, 'titulo', 'Tu sugerencia')

            # Crear notificación
            if id_usuario:
                from src.models.ModelNotificacion import ModelNotificacion

                mensaje = f"Tu sugerencia '{titulo}' fue marcada como '{nuevo_estado}'."
                if retroalimentacion:
                    mensaje += f" Comentario del administrador: {retroalimentacion}"

                ModelNotificacion.crear(
                    db,
                    id_usuario,
                    f"Sugerencia {nuevo_estado}",
                    mensaje
                )

        flash(f"✅ Sugerencia actualizada a '{nuevo_estado}' correctamente.", "success")

    except Exception as e:
        print(f"❌ Error al cambiar el estado: {e}")
        flash(f"Error al cambiar el estado: {str(e)}", "danger")

    return redirect(url_for('admin_bp.admin_sugerencias'))
# ---------------------------
# APROBAR / RECHAZAR SUGERENCIAS
# ---------------------------
@admin_bp.route('/sugerencias/aprobar/<int:id_sugerencia>', methods=['POST'])
@login_required
@admin_required
def admin_aprobar_sugerencia(id_sugerencia):
    try:
        cur = current_app.db.connection.cursor()
        cur.execute("UPDATE sugerencias SET estado = 'Aprobada' WHERE id_sugerencia = %s", (id_sugerencia,))
        current_app.db.connection.commit()
        cur.close()
        flash("✅ Sugerencia aprobada correctamente", "success")
    except Exception as e:
        current_app.db.connection.rollback()
        flash("❌ Error al aprobar la sugerencia", "danger")
        print(e)
    return redirect(url_for('admin_bp.admin_sugerencias'))


@admin_bp.route('/sugerencias/rechazar/<int:id_sugerencia>', methods=['POST'])
@login_required
@admin_required
def admin_rechazar_sugerencia(id_sugerencia):
    try:
        cur = current_app.db.connection.cursor()
        cur.execute("UPDATE sugerencias SET estado = 'Rechazada' WHERE id_sugerencia = %s", (id_sugerencia,))
        current_app.db.connection.commit()
        cur.close()
        flash("❌ Sugerencia rechazada", "info")
    except Exception as e:
        current_app.db.connection.rollback()
        flash("❌ Error al rechazar la sugerencia", "danger")
        print(e)
    return redirect(url_for('admin_bp.admin_sugerencias'))

# ----------------------------
# ADMIN · VER Y RESPONDER PQRS
# ----------------------------
@admin_bp.route('/pqrs')
@login_required
def pqrs():
    if current_user.id_rol != 2:
        flash("Acceso denegado", "error")
        return redirect(url_for('home_bp.home'))

    # 🔹 Filtros recibidos desde el formulario
    tipo_filtro = request.args.get("tipo", "").strip()
    estado_filtro = request.args.get("estado", "").strip()

    try:
        db = get_connection()
        cursor = db.cursor()

        # Base query
        sql = """
            SELECT p.id_pqr, p.tipo, p.asunto, p.mensaje, p.respuesta, 
                   p.estado, p.fecha, p.es_pregunta, p.visible_faq,
                   u.nombre_completo, u.correo_electronico
            FROM pqr p
            INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE 1=1
        """
        params = []

        # 🔹 Filtro por tipo
        if tipo_filtro:
            sql += " AND p.tipo = %s"
            params.append(tipo_filtro)

        # 🔹 Filtro por estado
        if estado_filtro:
            sql += " AND p.estado = %s"
            params.append(estado_filtro)

        sql += " ORDER BY p.fecha DESC"

        cursor.execute(sql, tuple(params))
        data = cursor.fetchall()

        pqrs_list = []
        for row in data:
            pqrs_list.append({
                "id_pqr": row["id_pqr"],
                "tipo": row["tipo"],
                "asunto": row["asunto"],
                "mensaje": row["mensaje"],
                "respuesta": row["respuesta"],
                "estado": row["estado"],
                "fecha": row["fecha"],
                "es_pregunta": row["es_pregunta"],
                "visible_faq": row["visible_faq"],
                "nombre_completo": row["nombre_completo"],
                "correo": row["correo_electronico"]
            })

        return render_template('admin/pqrs.html',
                               pqrs=pqrs_list,
                               tipo_filtro=tipo_filtro,
                               estado_filtro=estado_filtro)

    except Exception as e:
        print("❌ ERROR PQRS:", e)
        flash("Error cargando PQRS", "error")
        return redirect(url_for('admin_bp.index'))

# ----------------------------
# ADMIN · RESPONDER PQR
# ----------------------------
@admin_bp.route('/pqrs/responder/<int:id_pqr>', methods=['POST'])
@login_required
def responder_pqr(id_pqr):
    if current_user.id_rol != 2:
        flash("Acceso denegado", "error")
        return redirect(url_for('home_bp.home'))

    respuesta = request.form.get("respuesta")

    if not respuesta:
        flash("La respuesta no puede estar vacía", "error")
        return redirect(url_for('admin_bp.pqrs'))

    try:
        db = get_connection()
        cursor = db.cursor()  # ← CORRECTO

        sql = """
            UPDATE pqr
            SET respuesta = %s,
                estado = 'Respondido'
            WHERE id_pqr = %s
        """
        cursor.execute(sql, (respuesta, id_pqr))
        db.commit()  # ← CORRECTO

        flash("Respuesta enviada correctamente", "success")
        return redirect(url_for('admin_bp.pqrs'))

    except Exception as e:
        print("======= ERROR RESPONDER PQR =======")
        print(type(e), e)
        print("==================================")
        flash("Error al responder PQR", "error")
        return redirect(url_for('admin_bp.pqrs'))

@admin_bp.route('/publicar_faq/<int:id_pqr>')
@login_required
def publicar_faq(id_pqr):
    db = get_connection()
    cursor = db.cursor()

    sql = "UPDATE pqr SET visible_faq = 1, es_pregunta = 1 WHERE id_pqr = %s"
    cursor.execute(sql, (id_pqr,))
    db.commit()

    cursor.close()
    flash("La pregunta ahora es visible en FAQ.", "success")
    return redirect(url_for('admin_bp.pqrs'))

@admin_bp.route('/ocultar_faq/<int:id_pqr>')
@login_required
def ocultar_faq(id_pqr):
    db = get_connection()
    cursor = db.cursor()

    sql = "UPDATE pqr SET visible_faq = 0 WHERE id_pqr = %s"
    cursor.execute(sql, (id_pqr,))
    db.commit()

    cursor.close()
    flash("La pregunta fue ocultada de FAQ.", "info")
    return redirect(url_for('admin_bp.pqrs'))

# ---------------------------
# PEDIDOS
# ---------------------------
@admin_bp.route('/pedidos')
@login_required
@admin_required
def pedidos():
    db = current_app.db
    try:
        cur = db.connection.cursor()
        cur.execute("""
            SELECT p.id_pedido, u.nombre_completo AS usuario, p.fecha_pedido,
                   p.metodo_pago, p.estado, p.comprobante_pago,
                   d.empresa_transportadora, d.fecha_envio, d.estado AS envio_estado
            FROM pedidos p
            LEFT JOIN usuarios u ON p.id_usuario=u.id_usuario
            LEFT JOIN domicilio d ON p.id_pedido=d.id_pedido
            ORDER BY p.fecha_pedido DESC
        """)
        pedidos = fetchall_dict(cur)
        cur.close()
    except Exception as e:
        pedidos = []
        flash("Error al cargar pedidos", "danger")
        print(e)
    return render_template('admin/pedidos.html', pedidos=pedidos, user=current_user)


@admin_bp.route('/pedidos/actualizar/<int:id_pedido>', methods=['POST'])
@login_required
@admin_required
def actualizar_pedido(id_pedido):
    estado = request.form.get('estado')
    empresa = request.form.get('empresa_transportadora')
    fecha_envio = request.form.get('fecha_envio')
    try:
        cur = current_app.db.connection.cursor()
        cur.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (estado, id_pedido))
        if estado in ('enviado', 'entregado'):
            cur.execute("""
                INSERT INTO domicilio (id_pedido, empresa_transportadora, fecha_envio, estado)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE empresa_transportadora=%s, fecha_envio=%s, estado=%s
            """, (id_pedido, empresa, fecha_envio, estado, empresa, fecha_envio, estado))
        current_app.db.connection.commit()
        cur.close()
        flash("✅ Pedido actualizado correctamente", "success")
    except Exception as e:
        current_app.db.connection.rollback()
        flash("❌ Error al actualizar pedido", "danger")
        print(e)
    return redirect(url_for('admin_bp.pedidos'))

# ===========================================
# 📊 PANEL DE SUSCRIPCIONES (Admin)
# ===========================================

@admin_bp.route('/suscripciones')
@login_required
def admin_suscripciones():
    """Panel de administración de suscripciones"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    db = current_app.db
    cursor = db.connection.cursor()
    
    # Obtener todas las suscripciones
    cursor.execute("""
        SELECT s.id_suscripcion, s.id_usuario, s.fecha_inicio, s.fecha_fin, 
               s.estado, s.comprobante, 
               u.nombre_completo, u.correo_electronico, 
               ts.nombre as tipo_nombre, ts.precio_mensual
        FROM suscripciones s
        INNER JOIN usuarios u ON s.id_usuario = u.id_usuario
        INNER JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
        ORDER BY s.fecha_inicio DESC
    """)
    todas_suscripciones = cursor.fetchall()
    
    # Suscripciones pendientes
    cursor.execute("""
        SELECT s.id_suscripcion, s.id_usuario, s.fecha_inicio, s.fecha_fin, 
               s.estado, s.comprobante, 
               u.nombre_completo, u.correo_electronico, 
               ts.nombre as tipo_nombre, ts.precio_mensual
        FROM suscripciones s
        INNER JOIN usuarios u ON s.id_usuario = u.id_usuario
        INNER JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
        WHERE s.estado = 'pendiente'
        ORDER BY s.fecha_inicio DESC
    """)
    pendientes = cursor.fetchall()
    
    # Estadísticas
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN estado = 'aprobada' AND fecha_fin >= CURDATE() THEN 1 END) as activas,
            COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes,
            COUNT(CASE WHEN estado = 'vencida' THEN 1 END) as vencidas
        FROM suscripciones
    """)
    stats = cursor.fetchone()
    
    cursor.close()
    
    estadisticas = {
        'activas': stats[0] if stats else 0,
        'pendientes': stats[1] if stats else 0,
        'vencidas': stats[2] if stats else 0
    }
    
    return render_template(
        'admin/suscripciones.html',
        todas=todas_suscripciones,
        pendientes=pendientes,
        estadisticas=estadisticas
    )

# ===========================================
# ✅ APROBAR SUSCRIPCIÓN
# ===========================================

@admin_bp.route('/suscripciones/aprobar/<int:id_suscripcion>', methods=['POST'])
@login_required
def aprobar_suscripcion_admin(id_suscripcion):
    """Aprueba una solicitud de suscripción"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    try:
        cursor = current_app.db.connection.cursor()
        cursor.execute("""
            UPDATE suscripciones 
            SET estado = 'aprobada'
            WHERE id_suscripcion = %s
        """, (id_suscripcion,))
        current_app.db.connection.commit()
        cursor.close()
        
        flash('✅ Suscripción aprobada correctamente', 'success')
    except Exception as e:
        current_app.db.connection.rollback()
        flash('❌ Error al aprobar la suscripción', 'danger')
        print(e)
    
    return redirect(url_for('admin_bp.admin_suscripciones'))

# ===========================================
# ❌ RECHAZAR SUSCRIPCIÓN
# ===========================================

@admin_bp.route('/suscripciones/rechazar/<int:id_suscripcion>', methods=['POST'])
@login_required
def rechazar_suscripcion_admin(id_suscripcion):
    """Rechaza una solicitud de suscripción"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    try:
        cursor = current_app.db.connection.cursor()
        cursor.execute("""
            UPDATE suscripciones 
            SET estado = 'rechazada'
            WHERE id_suscripcion = %s
        """, (id_suscripcion,))
        current_app.db.connection.commit()
        cursor.close()
        
        flash('❌ Suscripción rechazada', 'info')
    except Exception as e:
        current_app.db.connection.rollback()
        flash('❌ Error al rechazar la suscripción', 'danger')
        print(e)
    
    return redirect(url_for('admin_bp.admin_suscripciones'))

# ===========================================
# 🔄 VERIFICAR EXPIRACIONES (Tarea programada)
# ===========================================

@admin_bp.route('/suscripciones/verificar-expiraciones', methods=['POST'])
@login_required
def verificar_expiraciones_admin():
    """Marca como vencidas las suscripciones expiradas"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    db = current_app.db
    affected = ModelSuscripcion.verificar_expiracion(db)
    
    flash(f'Se actualizaron {affected} suscripciones vencidas', 'info')
    return redirect(url_for('admin_bp.admin_suscripciones'))


# ===========================================
# 📝 EDITAR TIPOS DE SUSCRIPCIÓN
# ===========================================

@admin_bp.route('/tipos-suscripcion/editar/<int:id_tipo>', methods=['POST'])
@login_required
def editar_tipo_suscripcion(id_tipo):
    """Edita los detalles de un tipo de suscripción"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    db = current_app.db
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            UPDATE tipo_suscripcion 
            SET nombre = %s, descripcion = %s, precio_mensual = %s
            WHERE id_tipo_suscripcion = %s
        """, (nombre, descripcion, precio, id_tipo))
        db.connection.commit()
        cursor.close()
        
        flash('Tipo de suscripción actualizado', 'success')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error: {e}', 'danger')
    
    return redirect(url_for('admin_bp.admin_suscripciones'))


# ===========================================
# 📊 REPORTES DE SUSCRIPCIONES
# ===========================================

@admin_bp.route('/suscripciones/reporte')
@login_required
def reporte_suscripciones():
    """Genera un reporte de ingresos por suscripciones"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    db = current_app.db
    cursor = db.connection.cursor()
    
    # Ingresos del mes actual
    cursor.execute("""
        SELECT 
            ts.nombre,
            COUNT(s.id_suscripcion) as cantidad,
            SUM(ts.precio_mensual) as ingresos
        FROM suscripciones s
        INNER JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
        WHERE s.estado = 'aprobada'
            AND MONTH(s.fecha_inicio) = MONTH(CURDATE())
            AND YEAR(s.fecha_inicio) = YEAR(CURDATE())
        GROUP BY ts.id_tipo_suscripcion
    """)
    ingresos_mes = cursor.fetchall()
    
    # Suscripciones activas por tipo
    cursor.execute("""
        SELECT 
            ts.nombre,
            COUNT(s.id_suscripcion) as activas
        FROM suscripciones s
        INNER JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
        WHERE s.estado = 'aprobada' AND s.fecha_fin >= CURDATE()
        GROUP BY ts.id_tipo_suscripcion
    """)
    activas_por_tipo = cursor.fetchall()
    
    cursor.close()
    
    return render_template(
        'admin/reporte_suscripciones.html',
        ingresos_mes=ingresos_mes,
        activas_por_tipo=activas_por_tipo
    )


# ===========================================
# 🎁 OTORGAR SUSCRIPCIÓN MANUAL
# ===========================================

@admin_bp.route('/suscripciones/otorgar', methods=['POST'])
@login_required
def otorgar_suscripcion():
    """Permite al admin otorgar una suscripción manualmente"""
    if current_user.id_rol != 2:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('navbar_bp.home'))
    
    db = current_app.db
    id_usuario = request.form.get('id_usuario')
    id_tipo = request.form.get('id_tipo')
    dias = int(request.form.get('dias', 30))
    
    try:
        from datetime import datetime, timedelta
        cursor = db.connection.cursor()
        
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=dias)
        
        cursor.execute("""
            INSERT INTO suscripciones 
            (id_usuario, id_tipo_suscripcion, fecha_inicio, fecha_fin, 
             estado, comprobante)
            VALUES (%s, %s, %s, %s, 'aprobada', 'OTORGADA_POR_ADMIN')
        """, (id_usuario, id_tipo, fecha_inicio, fecha_fin))
        
        db.connection.commit()
        cursor.close()
        
        flash('Suscripción otorgada exitosamente', 'success')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error: {e}', 'danger')
    
    return redirect(url_for('admin_bp.admin_suscripciones'))

# -----------------------------
# 💬 Chat en vivo (nuevo)
# -----------------------------
@admin_bp.route('/chat', methods=['GET'], endpoint='admin_chat')
@login_required
@admin_required
def admin_chat():
    """
    Vista del chat en vivo para el administrador.
    """
    return render_template('admin/chat_admin.html', user=current_user)