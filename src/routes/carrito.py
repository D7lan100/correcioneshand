from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import json

carrito_bp = Blueprint('carrito_bp', __name__, template_folder="../templates/navbar")

def get_db_cursor():
    db = current_app.db
    # 🚨 VERIFICACIÓN AGREGADA
    if not db or not db.connection:
        # Si la conexión no existe, forzamos un error que el try/except puede manejar
        raise ConnectionError("La conexión a la base de datos (current_app.db) no está disponible.")
    
    # Si la conexión existe, intentamos obtener el cursor
    cur = db.connection.cursor()
    
    # Doble verificación por si el cursor es None (raro, pero posible)
    if cur is None:
        raise RuntimeError("El cursor devuelto por la conexión es None.")
        
    return cur

def obtener_pedido_pendiente(id_usuario):
    cur = get_db_cursor()
    cur.execute("""
        SELECT id_pedido FROM pedidos
        WHERE id_usuario = %s AND estado = 'pendiente'
        ORDER BY fecha_pedido DESC LIMIT 1
    """, (id_usuario,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None

def crear_pedido_pendiente(id_usuario):
    cur = get_db_cursor()
    cur.execute("""
        INSERT INTO pedidos (id_usuario, fecha_pedido, estado, metodo_pago)
        VALUES (%s, NOW(), 'pendiente', 'No definido')
    """, (id_usuario,))
    current_app.db.connection.commit()
    cur.execute("SELECT LAST_INSERT_ID()")
    id_pedido = cur.fetchone()[0]
    cur.close()
    return id_pedido

def obtener_id_vendedor(id_producto):
    cur = None
    try:
        cur = get_db_cursor()
        # Selecciona el id_vendedor de la tabla productos
        cur.execute("SELECT id_vendedor FROM productos WHERE id_producto = %s", (id_producto,))
        resultado = cur.fetchone()
        
        if resultado and resultado[0]:
            return resultado[0] # Retorna el ID del vendedor
        return None
    except Exception as e:
        print(f"Error al obtener ID de vendedor: {e}")
        return None
    finally:
        if cur:
            cur.close()


# ----------------------------
# Ver carrito (lee detalle_pedido en BD)
# ----------------------------
@carrito_bp.route('/') 
@login_required
def ver():
    id_usuario = current_user.id 
    id_pedido = obtener_pedido_pendiente(id_usuario)

    items = []
    total = 0.0

    if id_pedido:
        cur = get_db_cursor()
        
        # Incluimos los datos necesarios para la lógica de cotización en el HTML
        cur.execute("""
            SELECT 
                dp.id_detalle, dp.id_producto, p.nombre, p.precio, dp.cantidad,
                dp.precio_total, dp.texto_personalizado, dp.imagen_personalizada, 
                dp.plantilla_seleccionada, p.imagen AS imagen_producto,
                dp.estado_vendedor, 
                s.feedback_vendedor, 
                dp.formulario_seleccionado,
                dp.precio_propuesto,
                dp.aceptado_usuario
            FROM detalle_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            LEFT JOIN solicitudes s ON dp.id_detalle = s.id_detalle
            WHERE dp.id_pedido = %s
            ORDER BY dp.id_detalle
        """, (id_pedido,))
        rows = cur.fetchall()
        cur.close()

        if not rows:
            print(f"Info: Pedido {id_pedido} está 'pendiente' pero no tiene detalles.")

        for r in rows:
            id_detalle = r[0]
            id_producto = r[1]
            nombre = r[2]
            precio_unit = float(r[3]) if r[3] is not None else 0.0
            cantidad = int(r[4]) if r[4] is not None else 1
            precio_total_bd = float(r[5]) if r[5] is not None else None
            texto = r[6]
            imagen_personalizada = r[7]
            plantilla = r[8]
            imagen_producto = r[9]
            
            estado_vendedor = r[10]
            feedback_vendedor = r[11]
            formulario = r[12]
            precio_propuesto = float(r[13]) if r[13] is not None else None
            aceptado_usuario = r[14]

            # --- LÓGICA DE PRECIOS PARA EL HTML ---

            precio_base = precio_unit 
            precio_actualizado_unit = 0.0
            subtotal = 0.0
            
            # 1. Si el usuario ACEPTÓ la cotización
            if aceptado_usuario and precio_propuesto and precio_propuesto > 0:
                precio_actualizado_unit = precio_propuesto 
                subtotal = precio_actualizado_unit * cantidad 
            # 2. Si hay una COTIZACIÓN PENDIENTE de aceptación (muestra el precio original en el subtotal)
            elif estado_vendedor == 'cotizado' and precio_propuesto and precio_propuesto > 0:
                 precio_actualizado_unit = precio_propuesto # Se usa para mostrarlo
                 subtotal = precio_base * cantidad # Mantiene el subtotal original hasta que se acepte
            # 3. Item Base, Aprobado, Rechazado, o Pendiente sin cotización
            else:
                precio_actualizado_unit = 0.0 # No hay precio actualizado que mostrar
                subtotal = precio_base * cantidad

            total += subtotal
            
            es_personalizado = bool(texto or imagen_personalizada or plantilla or formulario)

            items.append({
                'id_detalle': id_detalle,
                'id_producto': id_producto,
                'nombre': nombre,
                'precio': precio_base, # Precio unitario base
                'cantidad': cantidad,
                'subtotal': subtotal, 
                'texto_personalizado': texto,
                'imagen_personalizada': imagen_personalizada,
                'plantilla_seleccionada': plantilla,
                'formulario_seleccionado': formulario,
                'imagen_producto': imagen_producto,
                'es_personalizado': es_personalizado,
                'estado_vendedor': estado_vendedor,
                'mensaje_vendedor': feedback_vendedor, 
                'precio_actualizado': precio_actualizado_unit, # Precio cotizado o aceptado (0 si no aplica)
                'precio_propuesto': precio_propuesto, 
                'aceptado_usuario': aceptado_usuario 
            })
        
        total = round(total, 2)
        
        for item in items:

            # ---- PLANTILLA ----
            plantilla_raw = item.get('plantilla_seleccionada')
            if isinstance(plantilla_raw, str):
                try:
                    data = json.loads(plantilla_raw)
                    # permite JSON como {"plantilla": {...}} ó {...}
                    item['plantilla_dict'] = data.get('plantilla', data)
                except:
                    item['plantilla_dict'] = None
            else:
                item['plantilla_dict'] = None

            # ---- FORMULARIO ----
            formulario_raw = item.get('formulario_seleccionado')
            if isinstance(formulario_raw, str):
                try:
                    data = json.loads(formulario_raw)
                    # permite JSON como {"formulario": {...}} ó {...}
                    item['formulario_dict'] = data.get('formulario', data)
                except:
                    item['formulario_dict'] = None
            else:
                item['formulario_dict'] = None
        
    return render_template('navbar/carrito.html', items=items, total=total)


# ----------------------------
# Agregar producto (NO PERSONALIZADO) al carrito
# ----------------------------
@carrito_bp.route('/agregar/<int:id_producto>', methods=['POST'])
@login_required
def agregar(id_producto):
    try:
        cantidad = int(request.form.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1

        db = current_app.db
        cur = db.connection.cursor()

        cur.execute("SELECT precio FROM productos WHERE id_producto = %s", (id_producto,))
        prod = cur.fetchone()
        if not prod:
            flash("❌ Producto no encontrado.", "danger")
            cur.close()
            return redirect(url_for('productos_bp.productos'))
        precio_unit = float(prod[0]) if prod[0] is not None else 0.0

        id_usuario = current_user.id
        id_pedido = obtener_pedido_pendiente(id_usuario)
        if not id_pedido:
            id_pedido = crear_pedido_pendiente(id_usuario)

        cur = db.connection.cursor()
        cur.execute("""
            SELECT id_detalle, cantidad FROM detalle_pedido
            WHERE id_pedido = %s AND id_producto = %s
            AND texto_personalizado IS NULL AND imagen_personalizada IS NULL AND plantilla_seleccionada IS NULL AND formulario_seleccionado IS NULL
            LIMIT 1
        """, (id_pedido, id_producto))
        detalle = cur.fetchone()

        if detalle:
            id_detalle = detalle[0]
            nueva_cantidad = int(detalle[1]) + cantidad
            precio_total = precio_unit * nueva_cantidad
            
            cur.execute("""
                UPDATE detalle_pedido
                SET cantidad = %s,
                    precio_total = %s,
                    estado_vendedor = 'aprobado'
                WHERE id_detalle = %s
            """, (nueva_cantidad, precio_total, id_detalle))
        else:
            precio_total = precio_unit * cantidad
            
            cur.execute("""
                INSERT INTO detalle_pedido 
                    (id_pedido, id_producto, cantidad, precio_total, estado_vendedor)
                VALUES (%s, %s, %s, %s, 'aprobado')
            """, (id_pedido, id_producto, cantidad, precio_total))

        db.connection.commit()
        cur.close()
        flash("✅ Producto agregado al carrito.", "success")
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"❌ Error agregar carrito: {e}") 
        flash("No se pudo agregar el producto al carrito.", "danger")

    return redirect(url_for('carrito_bp.ver'))

# ----------------------------
# Eliminar producto del carrito (por id_detalle)
# ----------------------------
@carrito_bp.route('/eliminar/<int:id_detalle>', methods=['POST'])
@login_required
def eliminar(id_detalle):
    try:
        db = current_app.db
        cur = db.connection.cursor()
        id_pedido = obtener_pedido_pendiente(current_user.id)
        if not id_pedido:
            flash("⚠ No hay carrito activo.", "warning")
            cur.close()
            return redirect(url_for('carrito_bp.ver'))
        
        # Eliminar primero las solicitudes relacionadas
        cur.execute("""
            DELETE FROM solicitudes
            WHERE id_detalle = %s
        """, (id_detalle,))

        cur.execute("""
            DELETE FROM detalle_pedido
            WHERE id_detalle = %s AND id_pedido = %s
        """, (id_detalle, id_pedido))
        
        db.connection.commit()
        cur.close()
        flash("🗑 Producto eliminado del carrito.", "info")
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"❌ Error eliminar carrito: {e}")
        flash("No se pudo eliminar el producto.", "danger")

    return redirect(url_for('carrito_bp.ver'))


# ----------------------------
# Vaciar carrito
# ----------------------------
@carrito_bp.route('/vaciar', methods=['POST'])
@login_required
def vaciar():
    try:
        db = current_app.db
        cur = db.connection.cursor()
        id_pedido = obtener_pedido_pendiente(current_user.id)
        if id_pedido:
            # Eliminar primero los registros en 'solicitudes' que dependen de 'detalle_pedido'
            cur.execute("""
                DELETE FROM solicitudes
                WHERE id_detalle IN (SELECT id_detalle FROM detalle_pedido WHERE id_pedido = %s)
            """, (id_pedido,))
            
            cur.execute("DELETE FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
            cur.execute("UPDATE pedidos SET estado = 'cancelado' WHERE id_pedido = %s", (id_pedido,))
            db.connection.commit()
        cur.close()
        flash("🧹 Carrito vaciado correctamente.", "info")
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"❌ Error vaciar carrito: {e}")
        flash("No se pudo vaciar el carrito.", "danger")

    return redirect(url_for('carrito_bp.ver'))

# ----------------------------
# Aceptar cotización
# ----------------------------
@carrito_bp.route('/aceptar/<int:id_detalle>', methods=['POST'])
@login_required
def aceptar_cotizacion(id_detalle):
    id_usuario = current_user.id
    
    try:
        cur = get_db_cursor()
        id_pedido_activo = obtener_pedido_pendiente(id_usuario)
        
        if not id_pedido_activo:
            flash("No tienes un pedido activo.", "warning")
            return redirect(url_for('carrito_bp.ver'))

        # Obtener datos para validar y calcular
        cur.execute("""
            SELECT precio_propuesto, cantidad, p.precio 
            FROM detalle_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE id_detalle = %s AND id_pedido = %s
        """, (id_detalle, id_pedido_activo))
        
        item = cur.fetchone()
        
        if not item:
            flash("Error: El ítem no se encontró en tu carrito.", "danger")
            return redirect(url_for('carrito_bp.ver'))

        precio_nuevo_unitario = item[0]
        cantidad = item[1]
        
        if precio_nuevo_unitario is None or precio_nuevo_unitario <= 0:
            flash("Error: No hay una cotización válida para aceptar.", "warning")
            return redirect(url_for('carrito_bp.ver'))
        
        # Calcular el nuevo precio total
        precio_nuevo_total = precio_nuevo_unitario * cantidad

        # Actualizar el ítem: aceptado_usuario = 1, precio_total = nuevo total, estado_vendedor = 'aprobado'
        cur.execute("""
            UPDATE detalle_pedido SET
                aceptado_usuario = 1,
                precio_total = %s,
                estado_vendedor = 'aprobado'
            WHERE id_detalle = %s
        """, (precio_nuevo_total, id_detalle))
        
        # Opcional: Actualizar la solicitud asociada
        cur.execute("""
            UPDATE solicitudes SET
                estado = 'aceptado'
            WHERE id_detalle = %s
        """, (id_detalle,))
        
        current_app.db.connection.commit()
        cur.close()
        
        flash("Cotización aceptada. El precio de tu carrito ha sido actualizado.", "success")
        
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"Error al aceptar cotización: {e}")
        flash("Error al procesar la aceptación.", "danger")

    return redirect(url_for('carrito_bp.ver'))


# ----------------------------
# 🚨 NUEVA FUNCIÓN: Rechazar cotización
# ----------------------------
@carrito_bp.route('/rechazar/<int:id_detalle>', methods=['POST'])
@login_required
def rechazar_cotizacion(id_detalle):
    id_usuario = current_user.id
    
    try:
        cur = get_db_cursor()
        id_pedido_activo = obtener_pedido_pendiente(id_usuario)
        
        if not id_pedido_activo:
            flash("No tienes un pedido activo.", "warning")
            return redirect(url_for('carrito_bp.ver'))

        # Obtener el precio base del producto y la cantidad
        cur.execute("""
            SELECT p.precio, dp.cantidad
            FROM detalle_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE id_detalle = %s AND id_pedido = %s
        """, (id_detalle, id_pedido_activo))
        
        item = cur.fetchone()
        
        if not item:
            flash("Error: El ítem no se encontró en tu carrito.", "danger")
            return redirect(url_for('carrito_bp.ver'))

        precio_base_unitario = item[0]
        cantidad = item[1]
        
        # Calcular el nuevo precio total (restablece al precio base)
        precio_base_total = precio_base_unitario * cantidad

        # Actualizar el ítem: aceptado_usuario = 0, precio_total = precio base, estado_vendedor = 'rechazado' (para el HTML)
        cur.execute("""
            UPDATE detalle_pedido SET
                aceptado_usuario = 0,
                precio_total = %s,
                precio_propuesto = NULL, -- Limpiamos el precio propuesto
                estado_vendedor = 'rechazado' -- Marcamos como rechazado
            WHERE id_detalle = %s
        """, (precio_base_total, id_detalle))
        
        # Opcional: Actualizar la solicitud asociada
        cur.execute("""
            UPDATE solicitudes SET
                estado = 'rechazado'
            WHERE id_detalle = %s
        """, (id_detalle,))
        
        current_app.db.connection.commit()
        cur.close()
        
        flash("❌ Cotización rechazada. El ítem se ha restablecido a su precio base original.", "info")
        
    except Exception as e:
        current_app.db.connection.rollback()
        print(f"Error al rechazar cotización: {e}")
        flash("Error al procesar el rechazo.", "danger")

    return redirect(url_for('carrito_bp.ver'))