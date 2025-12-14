from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from src.models.ModelProducto import ModelProducto
from werkzeug.utils import secure_filename
import os
import json 
# ------------------ NUEVAS IMPORTACIONES REQUERIDAS ------------------
# (Asumiendo que tienes una librería de paginación o la vas a simular)
# Si usas MySQL directamente, tendrás que implementar la paginación con LIMIT/OFFSET.
# Por ahora, simularemos la interfaz de un objeto de paginación.
# ----------------------------------------------------------------------
from src.routes.carrito import obtener_id_vendedor

def get_cursor():
    """Devuelve un cursor nuevo asegurando que use la BD correcta"""
    db = current_app.db
    cursor = db.connection.cursor()
    # Descomenta esta línea si es necesaria para tu configuración de MySQL:
    # cursor.execute(f"USE {current_app.config['MYSQL_DB']};")
    return cursor

productos_bp = Blueprint('productos_bp', __name__)

# -----------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA GENERAR URLs DE PAGINACIÓN (CRÍTICA)
# -----------------------------------------------------------------------
def url_for_pagination(page):
    """Genera la URL correcta para una página de paginación, preservando args de búsqueda/categoría."""
    args = request.view_args.copy()
    args.update(request.args.to_dict())
    args['page'] = page
    
    # El nombre de la función de vista actual es request.endpoint
    return url_for(request.endpoint, **args)

# -----------------------------------------------------------------------
# FUNCIÓN AUXILIAR CRÍTICA PARA AGRUPAR SOLICITUDES (UPSERT)
# -----------------------------------------------------------------------
# ... (Función gestionar_solicitud_personalizacion sin cambios) ...
def gestionar_solicitud_personalizacion(cursor, id_usuario, id_vendedor, id_producto, id_detalle, detalles_adicionales):
    """
    Busca una solicitud PENDIENTE para un id_detalle.
    Si la encuentra, la actualiza (resetea el estado y detalles).
    Si no la encuentra, crea una nueva.
    """
    try:
        # 1. Buscar solicitud PENDIENTE existente para este detalle
        cursor.execute("""
            SELECT id_solicitud FROM solicitudes
            WHERE id_detalle = %s AND estado = 'pendiente' 
        """, (id_detalle,))
        solicitud_existente = cursor.fetchone()

        if solicitud_existente:
            # 🔄 2A. Actualizar la solicitud existente
            id_solicitud = solicitud_existente[0]
            cursor.execute("""
                UPDATE solicitudes
                SET detalles_adicionales = %s, fecha_solicitud = NOW()
                WHERE id_solicitud = %s
            """, (detalles_adicionales, id_solicitud))
            print(f"🔄 Solicitud (ID: {id_solicitud}) actualizada para Detalle {id_detalle}")
        else:
            # ➕ 2B. Insertar nueva solicitud
            cursor.execute("""
                INSERT INTO solicitudes 
                    (id_usuario, id_vendedor, id_producto, id_detalle, estado, detalles_adicionales)
                VALUES (%s, %s, %s, %s, 'pendiente', %s)
            """, (id_usuario, id_vendedor, id_producto, id_detalle, detalles_adicionales))
            print(f"✅ Solicitud nueva creada para Detalle {id_detalle}")
    except Exception as e:
        print(f"❌ ERROR al gestionar solicitud: {e}")
        # Relanzamos la excepción para que el 'try/except' principal haga rollback
        raise e 
# -----------------------------------------------------------------------
# RUTAS BÁSICAS (CON PAGINACIÓN)
# -----------------------------------------------------------------------

@productos_bp.route('/productos', endpoint='productos')
def productos():
    # 📌 1. Obtener la página actual y definir el límite
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # 📌 2. Llamar al método del modelo con parámetros de paginación
        # Se asume que ModelProducto.get_all ahora maneja la paginación
        pagination_object = ModelProducto.get_all(current_app.db, page=page, per_page=per_page)
        
        # 📌 3. Pasar el objeto de paginación y la función auxiliar a la plantilla
        return render_template(
            'producto/productos.html', 
            productos=pagination_object.items, # La lista de productos para la página actual
            pagination=pagination_object,      # El objeto de paginación completo
            url_for_pagination=url_for_pagination # Función para generar enlaces
        )
    except Exception as e:
        print(f"Error en ruta /productos: {e}")
        flash(f"Error al cargar los productos: {str(e)}", "danger")
        return render_template('producto/productos.html', productos=[], pagination=None)

@productos_bp.route('/productos/categoria/<int:id_categoria>', endpoint='productos_por_categoria')
def productos_por_categoria(id_categoria):
    # 📌 1. Obtener la página actual y definir el límite
    page = request.args.get('page', 1, type=int)
    per_page = 20

    try:
        # 📌 2. Llamar al método del modelo con parámetros de paginación
        pagination_object = ModelProducto.get_by_categoria(current_app.db, id_categoria, page=page, per_page=per_page)
        
        # 📌 3. Pasar el objeto de paginación y la función auxiliar a la plantilla
        return render_template(
            'producto/productos.html', 
            productos=pagination_object.items, 
            categoria_id=id_categoria,
            pagination=pagination_object,
            url_for_pagination=url_for_pagination
        )
    except Exception as e:
        print(f"Error en productos_por_categoria: {e}")
        flash(f"Error al cargar productos de la categoría: {str(e)}", "danger")
        return render_template('producto/productos.html', productos=[], pagination=None)

@productos_bp.route('/productos/buscar', endpoint='buscar_productos')
def buscar_productos():
    # 📌 1. Obtener la página actual, el límite y el término de búsqueda
    page = request.args.get('page', 1, type=int)
    per_page = 20
    termino = request.args.get('q', '').strip()
    
    if not termino:
        flash("Ingresa un término de búsqueda", "info")
        return redirect(url_for('productos_bp.productos'))

    try:
        # 📌 2. Llamar al método del modelo con parámetros de paginación
        pagination_object = ModelProducto.search(current_app.db, termino, page=page, per_page=per_page)
        
        # 📌 3. Pasar el objeto de paginación y la función auxiliar a la plantilla
        return render_template(
            'producto/productos.html', 
            productos=pagination_object.items, 
            termino_busqueda=termino,
            pagination=pagination_object,
            url_for_pagination=url_for_pagination
        )
    except Exception as e:
        print(f"Error en buscar_productos: {e}")
        flash(f"Error al buscar productos: {str(e)}", "danger")
        return render_template('producto/productos.html', productos=[], pagination=None)

# -----------------------------------------------------------------------
# RUTAS RESTANTES (detalle_producto, guardar_texto_personalizado, etc.)
# -----------------------------------------------------------------------

@productos_bp.route('/producto/<int:id_producto>', endpoint='detalle_producto')
def detalle_producto(id_producto):
# ... (Contenido sin cambios) ...
    db = current_app.db
    cur = None
    try:

        producto = ModelProducto.get_by_id(db, id_producto)

        if not producto:
            flash("Producto no encontrado", "error")
            return redirect(url_for('productos_bp.productos'))

        cur = db.connection.cursor()
        
        cur.execute("""
            SELECT 
                c.puntuacion, -- [0]
                c.comentario,  -- [1]
                DATE_FORMAT(c.fecha_calificacion, '%%d-%%m-%%Y %%H:%%i') AS fecha_calificacion, -- [2]
                u.nombre_completo -- [3] <-- ¡CORREGIDO!
            FROM calificaciones c
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE c.id_producto = %s
            ORDER BY c.fecha_calificacion DESC
        """, (id_producto,))
        comentarios_raw = cur.fetchall()

        comentarios_list = []
        for c in comentarios_raw:
            comentarios_list.append({
                'puntuacion': c[0],
                'comentario': c[1],
                'fecha_calificacion': c[2],
                'nombre_usuario': c[3]
            })


        favoritos_usuario = []
        if current_user.is_authenticated:
            cur.execute("""
                SELECT id_producto 
                FROM favoritos 
                WHERE id_usuario = %s
            """, (current_user.id_usuario,))

            favoritos_usuario = [item[0] for item in cur.fetchall()]


        producto.comentarios = comentarios_list
        

        return render_template(
            'producto/detalle_producto.html', 
            producto=producto,
            favoritos_usuario=favoritos_usuario 
        )
        
    except Exception as e:

        print(f"Error en detalle_producto: {e}")
        flash(f"Error al cargar el producto: {str(e)}", "error")
        return redirect(url_for('productos_bp.productos'))
    finally:
        if cur: cur.close()

@productos_bp.route('/protected', endpoint='protected')
@login_required
def protected():
    return render_template('usuarios/base.html', user=current_user)

@productos_bp.route('/personalizacion_panel/<int:id_producto>')
def panel_personalizacion(id_producto):
    return render_template('producto/panel_personalizacion.html', id_producto=id_producto)

@productos_bp.route('/personalizar/<int:id_producto>')
def personalizar(id_producto):
    try:
        producto = ModelProducto.get_by_id(current_app.db, id_producto)
        if not producto:
            flash("Producto no encontrado", "error")
            return redirect(url_for('productos_bp.productos'))

        return render_template('producto/personalizar_producto.html', producto=producto)
    except Exception as e:
        print(f"Error en personalizar: {e}")
        flash("Error al cargar la personalización del producto", "danger")
        return redirect(url_for('productos_bp.productos'))

@productos_bp.route('/guardar_texto_personalizado/<int:id_producto>', methods=['POST'])
@login_required
def guardar_texto_personalizado(id_producto):
# ... (Contenido sin cambios) ...
    db = current_app.db
    cursor = None
    try:
        texto = request.form.get('texto_personalizado', '').strip()
        id_usuario = current_user.id_usuario

        if not texto:
            return jsonify(success=False, message="Por favor escribe una descripción antes de enviar."), 400

        cursor = db.connection.cursor()
        id_pedido = None
        id_detalle_creado = None

        # 1. Buscar/Crear Pedido Pendiente
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente' LIMIT 1", (id_usuario,))
        pedido = cursor.fetchone()
        if not pedido:
            cursor.execute("INSERT INTO pedidos (id_usuario, fecha_pedido, estado, metodo_pago) VALUES (%s, NOW(), 'pendiente', 'No definido')", (id_usuario,))
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_pedido = cursor.fetchone()[0]
        else:
            id_pedido = pedido[0]

        # 2. Buscar/Crear Detalle Pedido
        # Busca un detalle para este producto dentro del pedido pendiente
        cursor.execute("SELECT id_detalle FROM detalle_pedido WHERE id_pedido = %s AND id_producto = %s", (id_pedido, id_producto))
        detalle_existente = cursor.fetchone()
        
        if detalle_existente:
            id_detalle_creado = detalle_existente[0]
            # Actualiza el detalle
            cursor.execute("UPDATE detalle_pedido SET texto_personalizado = %s, estado_vendedor = 'pendiente' WHERE id_detalle = %s", (texto, id_detalle_creado))
        else:
            # Crea un nuevo detalle
            cursor.execute("INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, texto_personalizado, estado_vendedor) VALUES (%s, %s, 1, %s, 'pendiente')", (id_pedido, id_producto, texto))
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_detalle_creado = cursor.fetchone()[0]

        # 3. Obtener ID del vendedor
        id_vendedor_asignado = obtener_id_vendedor(id_producto)

        # 4. 🛑 LLAMADA A GESTIONAR SOLICITUD (Asegura que solo haya una solicitud pendiente por detalle)
        if id_vendedor_asignado is not None and id_detalle_creado is not None:
            detalles_adicionales = f"Personalización de texto: {texto[:255]}"
            gestionar_solicitud_personalizacion(cursor, id_usuario, id_vendedor_asignado, id_producto, id_detalle_creado, detalles_adicionales)

        db.connection.commit()
        return jsonify(success=True)

    except Exception as e:
        if db.connection: db.connection.rollback()
        print(f"❌ ERROR SQL TEXTO: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if cursor: cursor.close()

@productos_bp.route('/subir_boceto/<int:id_producto>', methods=['POST'])
@login_required
def subir_boceto(id_producto):
# ... (Contenido sin cambios) ...
    db = current_app.db
    cursor = None
    try:
        archivo = request.files.get('imagen_personalizada')
        if not archivo or archivo.filename == "":
            return jsonify(success=False, message="Por favor selecciona un archivo válido."), 400

        filename_secure = secure_filename(archivo.filename)

        # 🟩 Ruta correcta usando la ubicación real de /src/static/
        ruta_carpeta_fs = os.path.join(
            current_app.static_folder,
            "personalizacion",
            "bocetos_usuarios"
        )
        os.makedirs(ruta_carpeta_fs, exist_ok=True)

        ruta_archivo_fs = os.path.join(ruta_carpeta_fs, filename_secure)
        archivo.save(ruta_archivo_fs)

        # Ruta relativa que usará HTML con url_for('static', filename=...)
        valor_pers_db = f"personalizacion/bocetos_usuarios/{filename_secure}"

        id_usuario = current_user.id_usuario
        cursor = db.connection.cursor()

        # ---------------------------------------------------------
        # 1. Buscar/Crear pedido pendiente
        cursor.execute(
            "SELECT id_pedido FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente' LIMIT 1",
            (id_usuario,)
        )
        pedido = cursor.fetchone()

        if not pedido:
            cursor.execute(
                "INSERT INTO pedidos (id_usuario, fecha_pedido, estado, metodo_pago) VALUES (%s, NOW(), 'pendiente', 'No definido')",
                (id_usuario,)
            )
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_pedido = cursor.fetchone()[0]
        else:
            id_pedido = pedido[0]

        # ---------------------------------------------------------
        # 2. Buscar/Crear detalle
        cursor.execute(
            "SELECT id_detalle FROM detalle_pedido WHERE id_pedido = %s AND id_producto = %s",
            (id_pedido, id_producto)
        )
        detalle_existente = cursor.fetchone()

        if detalle_existente:
            id_detalle = detalle_existente[0]
            cursor.execute(
                "UPDATE detalle_pedido SET imagen_personalizada = %s, estado_vendedor = 'pendiente' WHERE id_detalle = %s",
                (valor_pers_db, id_detalle)
            )
        else:
            cursor.execute(
                "INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, imagen_personalizada, estado_vendedor) VALUES (%s, %s, 1, %s, 'pendiente')",
                (id_pedido, id_producto, valor_pers_db)
            )
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_detalle = cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 3. Obtener vendedor asignado
        id_vendedor_asignado = obtener_id_vendedor(id_producto)

        # 4. Crear/actualizar solicitud de personalización
        if id_vendedor_asignado and id_detalle:
            detalles_adicionales = f"Boceto subido: {filename_secure}"
            gestionar_solicitud_personalizacion(
                cursor, id_usuario, id_vendedor_asignado,
                id_producto, id_detalle, detalles_adicionales
            )

        db.connection.commit()

        print(f"✅ Boceto guardado correctamente en {valor_pers_db}")
        return jsonify(success=True, ruta=valor_pers_db)

    except Exception as e:
        if db.connection:
            db.connection.rollback()
        print(f"❌ ERROR SQL BOCETO: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if cursor:
            cursor.close()
    
@productos_bp.route('/guardar_plantilla/<int:id_producto>', methods=['POST'])
@login_required
def guardar_plantilla(id_producto):
# ... (Contenido sin cambios) ...
    db = current_app.db
    cursor = None
    try:
        data = request.get_json()
        id_usuario = current_user.id_usuario

        if not data:
            return jsonify(success=False, message="No se recibieron datos de la plantilla."), 400

        cursor = db.connection.cursor()
        id_pedido = None
        id_detalle_creado = None

        # 1. Buscar/Crear Pedido Pendiente
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente' LIMIT 1", (id_usuario,))
        pedido = cursor.fetchone()
        if not pedido:
            cursor.execute("INSERT INTO pedidos (id_usuario, fecha_pedido, estado, metodo_pago) VALUES (%s, NOW(), 'pendiente', 'No definido')", (id_usuario,))
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_pedido = cursor.fetchone()[0]
        else:
            id_pedido = pedido[0]

        # 2. Buscar/Crear Detalle Pedido
        cursor.execute("SELECT id_detalle FROM detalle_pedido WHERE id_pedido = %s AND id_producto = %s LIMIT 1", (id_pedido, id_producto))
        detalle = cursor.fetchone()

        # 🛑 CORRECCIÓN: Usar json.dumps() para serializar el objeto JSON
        plantilla_json = json.dumps(data) 
        
        if detalle:
            id_detalle_creado = detalle[0]
            # Actualiza el detalle
            cursor.execute("UPDATE detalle_pedido SET plantilla_seleccionada = %s, estado_vendedor = 'pendiente' WHERE id_detalle = %s", (plantilla_json, id_detalle_creado))
        else:
            # Crea un nuevo detalle
            cursor.execute("INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, plantilla_seleccionada, estado_vendedor) VALUES (%s, %s, 1, %s, 'pendiente')", (id_pedido, id_producto, plantilla_json))
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_detalle_creado = cursor.fetchone()[0]

        
        # 3. Obtener ID del vendedor
        id_vendedor_asignado = obtener_id_vendedor(id_producto) 
        
        # 4. 🛑 LLAMADA A GESTIONAR SOLICITUD (Asegura que solo haya una solicitud pendiente por detalle)
        if id_vendedor_asignado is not None and id_detalle_creado is not None:
            # Usar una representación más informativa que el JSON completo
            detalles_adicionales = f"Personalización de plantilla guardada (Detalle ID: {id_detalle_creado})"
            gestionar_solicitud_personalizacion(cursor, id_usuario, id_vendedor_asignado, id_producto, id_detalle_creado, detalles_adicionales)

        db.connection.commit()
        return jsonify(success=True, message="Plantilla guardada correctamente")

    except Exception as e:
        if db.connection: db.connection.rollback()
        print(f"❌ ERROR SQL PLANTILLA: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if cursor: cursor.close()


@productos_bp.route('/registrar_formulario/<int:id_producto>', methods=['POST'])
@login_required
def registrar_formulario(id_producto):
# ... (Contenido sin cambios) ...
    conn = None
    cursor = None
    try:
        # 1. Obtener los datos JSON enviados desde el frontend
        data = request.get_json()
        if not data:
             return jsonify(success=False, message="No se recibieron datos del formulario (JSON esperado)."), 400

        # Validar campos mínimos (ocasion y detalles son obligatorios en el HTML)
        if not data.get('ocasion'):
             return jsonify(success=False, message="Debes seleccionar una ocasión."), 400

        conn = current_app.db.connection
        cursor = conn.cursor()
        id_usuario = current_user.id_usuario

        id_pedido = None
        id_detalle_creado = None

        # -------------------------------------------------------------------
        # 2. Lógica de Pedido/Detalle (UPSERT)
        # -------------------------------------------------------------------
        
        # A. Buscar/Crear Pedido Pendiente
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente' LIMIT 1", (id_usuario,))
        pedido = cursor.fetchone()
        
        if not pedido:
            cursor.execute("INSERT INTO pedidos (id_usuario, fecha_pedido, estado, metodo_pago) VALUES (%s, NOW(), 'pendiente', 'No definido')", (id_usuario,))
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_pedido = cursor.fetchone()[0]
        else:
            id_pedido = pedido[0]

        # B. Buscar/Crear Detalle Pedido para este producto
        cursor.execute("SELECT id_detalle FROM detalle_pedido WHERE id_pedido = %s AND id_producto = %s LIMIT 1", (id_pedido, id_producto))
        detalle_existente = cursor.fetchone()
        
        # Serializamos el objeto Python (data) a una cadena JSON para guardarlo en la BD
        # ensure_ascii=False permite guardar tildes y ñ correctamente
        formulario_json_str = json.dumps(data, ensure_ascii=False)

        if detalle_existente:
            id_detalle_creado = detalle_existente[0]
            # Actualizamos el registro existente con el nuevo formulario JSON
            cursor.execute("""
                UPDATE detalle_pedido 
                SET formulario_seleccionado = %s, 
                    estado_vendedor = 'pendiente' 
                WHERE id_detalle = %s
            """, (formulario_json_str, id_detalle_creado))
        else:
            # Creamos un nuevo registro
            cursor.execute("""
                INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, formulario_seleccionado, estado_vendedor) 
                VALUES (%s, %s, 1, %s, 'pendiente')
            """, (id_pedido, id_producto, formulario_json_str))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_detalle_creado = cursor.fetchone()[0]

        # -------------------------------------------------------------------
        # 3. Notificar al Vendedor (Tabla Solicitudes)
        # -------------------------------------------------------------------
        id_vendedor_asignado = obtener_id_vendedor(id_producto) 

        if id_vendedor_asignado is not None and id_detalle_creado is not None:
            # Creamos un resumen legible para la notificación rápida
            resumen_info = f"Formulario Completado: {data.get('ocasion', 'N/A')} - {data.get('fecha_limite', 'S/F')}"
            
            gestionar_solicitud_personalizacion(
                cursor, 
                id_usuario, 
                id_vendedor_asignado, 
                id_producto, 
                id_detalle_creado, 
                resumen_info
            )

        conn.commit()
        return jsonify(success=True, message="Formulario registrado correctamente")

    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ Error al registrar formulario JSON: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if cursor: cursor.close()

@productos_bp.route('/fabricacion')
def fabricacion():
    cur = current_app.db.connection.cursor()
    cur.execute("""
        SELECT p.id_producto, p.nombre, p.descripcion, p.imagen, u.nombre_usuario, p.es_personalizable
        FROM productos p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE p.id_categoria = 1
        ORDER BY p.id_producto DESC
    """)
    videos = cur.fetchall()
    cur.close()

    return render_template('navbar/fabricacion.html', videos=videos)

@productos_bp.route('/calificar/<int:id_producto>', methods=['POST'])
@login_required
def calificar_producto(id_producto):
# ... (Contenido sin cambios) ...
    """Permite que un usuario califique un producto a la venta"""
    puntuacion = request.form.get('puntuacion')
    comentario = request.form.get('comentario')

    if not puntuacion:
        flash("Debes seleccionar una puntuación.", "danger")
        # Asegúrate de que 'detalle_producto' sea el nombre de la función de tu ruta de detalle
        return redirect(url_for('productos_bp.detalle_producto', id_producto=id_producto))

    db = current_app.db
    cur = db.connection.cursor()

    try:
        # Verificar si el usuario ya calificó este producto
        cur.execute("""
            SELECT id_calificacion FROM calificaciones
            WHERE id_usuario = %s AND id_producto = %s
        """, (current_user.id_usuario, id_producto))
        existe = cur.fetchone()

        if existe:
            # Si ya calificó, actualiza su calificación
            cur.execute("""
                UPDATE calificaciones
                SET puntuacion = %s, comentario = %s, fecha_calificacion = NOW()
                WHERE id_calificacion = %s
            """, (puntuacion, comentario, existe[0]))
            mensaje = "Tu calificación ha sido actualizada correctamente. ⭐"
        else:
            # Si no existe, inserta una nueva
            cur.execute("""
                INSERT INTO calificaciones (id_usuario, id_producto, puntuacion, comentario)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id_usuario, id_producto, puntuacion, comentario))
            mensaje = "¡Gracias por calificar este producto! 💫"

        # ✅ Recalcular el promedio inmediatamente después
        # Esto asume que tienes la columna calificacion_promedio en la tabla 'productos'
        cur.execute("""
            UPDATE productos
            SET calificacion_promedio = (
                SELECT ROUND(AVG(puntuacion), 2)
                FROM calificaciones
                WHERE id_producto = %s
            )
            WHERE id_producto = %s
        """, (id_producto, id_producto))

        db.connection.commit()
        flash(mensaje, "success")

    except Exception as e:
        db.connection.rollback()
        flash(f"❌ Error al guardar la calificación: {e}", "danger")

    finally:
        cur.close()

    # Redirige al detalle del producto
    return redirect(url_for('productos_bp.detalle_producto', id_producto=id_producto))