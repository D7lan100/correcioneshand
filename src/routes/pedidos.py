# src/routes/pedidos.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta
import random
from src.routes.carrito import get_db_cursor

pedidos_bp = Blueprint('pedidos_bp', __name__, template_folder="../templates/navbar")


def parse_detalles(detalles_raw):
    """Recibe el campo detalles_pago de la BD y devuelve un dict usable."""
    if not detalles_raw:
        return {}
    if isinstance(detalles_raw, dict):
        return detalles_raw
    try:
        return json.loads(detalles_raw)
    except Exception:
        try:
            return json.loads(detalles_raw.decode('utf-8'))
        except Exception:
            return {}

def mask_card(number):
    """Devuelve '**** **** **** 1234' si number tiene longitud suficiente."""
    if not number or len(number) < 4:
        return None
    return "**** **** **** " + number[-4:]

@pedidos_bp.route('/mis_pedidos')
@login_required
def mis_pedidos():
    db = current_app.db
    cur = db.connection.cursor()
    try:
        # 🚨 SOLO PEDIDOS PAGADOS (cambio solicitado)
        cur.execute("""
            SELECT id_pedido, fecha_pedido, estado, metodo_pago, direccion_envio,
                   ciudad_envio, telefono_contacto, total_pagado, detalles_pago
            FROM pedidos
            WHERE id_usuario = %s
              AND estado = 'pagado'
            ORDER BY fecha_pedido DESC
        """, (current_user.id_usuario,))

        filas = cur.fetchall()

        pedidos = []
        for f in filas:
            id_pedido, fecha_pedido, estado, metodo_pago, direccion_envio, ciudad_envio, telefono_contacto, total_pagado, detalles_pago_raw = f

            # ---------------------------
            # 🚚 FECHA ESTIMADA DE ENTREGA
            # ---------------------------
            fecha_estimada = None
            if fecha_pedido:
                dias_extra = random.randint(2, 5)   # entre 2 y 5 días hábiles
                fecha_estimada = fecha_pedido + timedelta(days=dias_extra)

            # ---------------------------
            # Procesar detalles JSON
            # ---------------------------
            detalles = parse_detalles(detalles_pago_raw)

            # Asegurar SIEMPRE dict
            if not isinstance(detalles, dict):
                detalles = {}

            datos_pago = detalles.get('datos', {})

            tarjeta = None
            pse = None
            paypal = None

            # Método de pago con fallback
            tipo = detalles.get('metodo') or detalles.get('tipo') or metodo_pago or ""

            # ---- TARJETA ----
            if tipo.lower().startswith("tarjeta") or datos_pago.get("numero") or datos_pago.get("tarjeta_numero"):
                tarjeta = {
                    "titular": datos_pago.get("titular") or datos_pago.get("tarjeta_titular"),
                    "numero_mask": mask_card(datos_pago.get("numero") or datos_pago.get("tarjeta_numero")),
                    "exp": datos_pago.get("exp") or datos_pago.get("expiracion")
                }

            # ---- PSE ----
            elif "pse" in tipo.lower() or datos_pago.get("banco"):
                pse = {
                    "banco": datos_pago.get("banco"),
                    "tipo_doc": datos_pago.get("tipo_doc") or datos_pago.get("tipo_documento"),
                    "identificacion": datos_pago.get("identificacion") or datos_pago.get("numero_documento"),
                    "email": datos_pago.get("email"),
                    "postal": datos_pago.get("postal") or datos_pago.get("codigo_postal")
                }

            # ---- PAYPAL ----
            elif "paypal" in tipo.lower() or datos_pago.get("email"):
                paypal = {
                    "email": datos_pago.get("email"),
                    "pais": datos_pago.get("pais") or detalles.get("pais"),
                    "postal": datos_pago.get("postal")
                }


            pedidos.append({
                "id_pedido": id_pedido,
                "fecha": fecha_pedido,
                "estado": estado,
                "metodo_pago": metodo_pago,
                "direccion_envio": direccion_envio,
                "ciudad_envio": ciudad_envio,
                "telefono_contacto": telefono_contacto,
                "total_pagado": float(total_pagado) if total_pagado is not None else 0.0,
                "detalles_raw": detalles,
                "datos_pago": datos_pago,
                "tarjeta": tarjeta,
                "pse": pse,
                "paypal": paypal,

                # FECHA ESTIMADA AHORA SI FUNCIONA ✔
                "fecha_estimada": fecha_estimada.strftime('%Y-%m-%d') if fecha_estimada else None
            })
        return render_template('mis_pedidos.html', pedidos=pedidos)

    except Exception as e:
        print("ERROR mis_pedidos:", e)
        flash("Ocurrió un error cargando tus pedidos.", "danger")
        return render_template('mis_pedidos.html', pedidos=[])
    finally:
        cur.close()


@pedidos_bp.route('/detalle/<int:id_pedido>')
@login_required
def detalle(id_pedido):
    cur = get_db_cursor()

    try:
        # 1. Obtener información del pedido
        cur.execute("""
            SELECT id_pedido, fecha_pedido, estado, metodo_pago,
                   direccion_envio, ciudad_envio, telefono_contacto,
                   total_pagado, detalles_pago
            FROM pedidos
            WHERE id_pedido = %s AND id_usuario = %s
        """, (id_pedido, current_user.id_usuario)) # Asegúrate de usar id_usuario o id según tu modelo

        row = cur.fetchone()

        if not row:
            flash("Pedido no encontrado o no tienes permiso para verlo.", "warning")
            return redirect(url_for("pedidos_bp.mis_pedidos"))

        # Parsear JSON de detalles de pago
        detalles_pago_raw = row[8]
        detalles_pago = parse_detalles(detalles_pago_raw)
        
        # Preparar objeto pedido
        pedido = {
            "id_pedido": row[0],
            "fecha_pedido": row[1],
            "estado": row[2],
            "metodo_pago": row[3],
            "direccion": row[4],
            "ciudad": row[5],
            "telefono": row[6],
            "total_pagado": float(row[7] or 0),
        }
        
        # Extraer información de pago formateada para mostrar
        info_pago = {}
        metodo_norm = (pedido["metodo_pago"] or "").lower()
        
        if "tarjeta" in metodo_norm:
            info_pago = {
                "Titular": detalles_pago.get("cardHolder"),
                "Número": mask_card(detalles_pago.get("cardNumber")),
                "Vencimiento": detalles_pago.get("expiryDate")
            }
        elif "pse" in metodo_norm:
            info_pago = {
                "Banco": detalles_pago.get("pseBank"),
                "Tipo Persona": detalles_pago.get("psePersonType"),
                "Identificación": detalles_pago.get("pseIdNumber")
            }
        elif "paypal" in metodo_norm:
            info_pago = {
                "Cuenta PayPal": detalles_pago.get("paypalEmail")
            }

        # 2. Obtener productos del pedido (detalle_pedido)
        # Importante: Incluir información de personalización si existe
        cur.execute("""
            SELECT 
                p.nombre, p.imagen, dp.cantidad, dp.precio_total,
                dp.texto_personalizado, dp.imagen_personalizada, 
                dp.plantilla_seleccionada, dp.formulario_seleccionado
            FROM detalle_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE dp.id_pedido = %s
        """, (id_pedido,))

        items_raw = cur.fetchall()
        carrito = []

        for item in items_raw:
            plantilla_raw = item[6]
            formulario_raw = item[7]

            # ---- PLANTILLA ----
            plantilla_dict = None
            plantilla_clean = None
            if isinstance(plantilla_raw, str) and plantilla_raw.strip():
                try:
                    data = json.loads(plantilla_raw)
                    plantilla_dict = data.get("plantilla", data)
                except:
                    plantilla_clean = plantilla_raw  # texto normal

            # ---- FORMULARIO ----
            formulario_dict = None
            formulario_clean = None
            if isinstance(formulario_raw, str) and formulario_raw.strip():
                try:
                    data = json.loads(formulario_raw)
                    formulario_dict = data.get("formulario", data)
                except:
                    formulario_clean = formulario_raw  # texto normal

            carrito.append({
                "nombre": item[0],
                "imagen_producto": item[1],
                "cantidad": item[2],
                "subtotal": float(item[3] or 0),
                "texto_personalizado": item[4],
                "imagen_personalizada": item[5],

                # Nuevos campos completos como en Carrito.py
                "plantilla_dict": plantilla_dict,
                "plantilla_seleccionada": plantilla_clean,

                "formulario_dict": formulario_dict,
                "formulario_seleccionado": formulario_clean,

                "es_personalizado": any([
                    item[4], item[5], plantilla_dict, formulario_dict, 
                    plantilla_clean, formulario_clean
                ])
            })

        return render_template(
            "navbar/detalle_pedido.html",
            pedido=pedido,
            carrito=carrito,
            detalles_pago=info_pago 
        )

    except Exception as e:
        print(f"Error al ver detalle pedido {id_pedido}: {e}")
        flash("Error al cargar el detalle del pedido.", "danger")
        return redirect(url_for("pedidos_bp.mis_pedidos"))
    finally:
        cur.close()