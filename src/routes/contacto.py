from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.database.db import get_connection
from src.models.ModelPQR import ModelPQR


contacto_bp = Blueprint('contacto_bp', __name__)

# ============================================================
# 📄 PÁGINA DE CONTACTO CON FAQ (CON DEBUG MEJORADO)
# ============================================================
@contacto_bp.route("/contacto")
def contacto():
    print("\n" + "="*60)
    print("🔍 CARGANDO PÁGINA DE CONTACTO CON FAQs")
    print("="*60)
    
    try:
        db = get_connection()
        cursor = db.cursor()
        
        print("\n📊 PASO 1: Verificando registros en la tabla pqr...")
        
        # Contar todos los registros
        cursor.execute("SELECT COUNT(*) as total FROM pqr")
        total = cursor.fetchone()
        print(f"   Total de registros en pqr: {total[0] if total else 0}")
        
        # Contar por condiciones
        cursor.execute("SELECT COUNT(*) as total FROM pqr WHERE es_pregunta = 1")
        con_es_pregunta = cursor.fetchone()
        print(f"   Con es_pregunta = 1: {con_es_pregunta[0] if con_es_pregunta else 0}")
        
        cursor.execute("SELECT COUNT(*) as total FROM pqr WHERE visible_faq = 1")
        con_visible = cursor.fetchone()
        print(f"   Con visible_faq = 1: {con_visible[0] if con_visible else 0}")
        
        cursor.execute("SELECT COUNT(*) as total FROM pqr WHERE respuesta IS NOT NULL AND respuesta != ''")
        con_respuesta = cursor.fetchone()
        print(f"   Con respuesta válida: {con_respuesta[0] if con_respuesta else 0}")
        
        # Contar los que cumplen TODAS las condiciones
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM pqr 
            WHERE es_pregunta = 1 
              AND visible_faq = 1 
              AND respuesta IS NOT NULL 
              AND respuesta != ''
        """)
        cumplen_todo = cursor.fetchone()
        print(f"   ✅ Que cumplen TODAS las condiciones: {cumplen_todo[0] if cumplen_todo else 0}")
        
        print("\n📝 PASO 2: Ejecutando consulta principal de FAQs...")
        
        # Consulta principal SIN el filtro de respuesta vacía para ver qué pasa
        sql_query = """
            SELECT 
                id_pqr,
                asunto, 
                mensaje, 
                respuesta,
                visible_faq,
                es_pregunta,
                estado,
                CHAR_LENGTH(respuesta) as longitud_respuesta
            FROM pqr
            WHERE es_pregunta = 1
              AND visible_faq = 1
              AND respuesta IS NOT NULL
            ORDER BY fecha DESC
        """
        
        cursor.execute(sql_query)
        resultados = cursor.fetchall()
        
        print(f"\n✅ Registros encontrados: {len(resultados)}")
        
        # Filtrar manualmente las respuestas vacías y mostrar detalles
        faq = []
        for idx, row in enumerate(resultados, 1):
            print(f"\n--- Registro #{idx} (ID: {row[0]}) ---")
            print(f"   Asunto: {row[1][:50]}...")
            print(f"   Mensaje: {row[2][:50]}...")
            print(f"   Respuesta: '{row[3][:50] if row[3] else 'NULL'}'...")
            print(f"   visible_faq: {row[4]}")
            print(f"   es_pregunta: {row[5]}")
            print(f"   estado: {row[6]}")
            print(f"   Longitud respuesta: {row[7]}")
            
            # Solo agregar si la respuesta tiene contenido
            if row[3] and len(row[3].strip()) > 0:
                faq.append((row[1], row[2], row[3]))  # asunto, mensaje, respuesta
                print(f"   ✅ AGREGADO a FAQs")
            else:
                print(f"   ❌ RECHAZADO (respuesta vacía o NULL)")
        
        print(f"\n🎯 RESULTADO FINAL: {len(faq)} FAQs válidas para mostrar")
        print("="*60 + "\n")

        cursor.close()
        db.close()

        return render_template("contacto.html", faq=faq)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO al cargar FAQs:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print("\n📋 Stack trace completo:")
        traceback.print_exc()
        print("="*60 + "\n")
        return render_template("contacto.html", faq=[])


# ============================================================
# 📮 ENVIAR PQR (SIN CAMBIOS)
# ============================================================
@contacto_bp.route('/enviar_pqr', methods=['POST'])
@login_required
def enviar_pqr():
    tipo = request.form.get('tipo')
    mensaje = request.form.get('mensaje')
    asunto = request.form.get('asunto')
    es_pregunta = 0

    print("========== DEBUG PQR ==========")
    print("tipo:", tipo)
    print("asunto:", asunto)
    print("mensaje:", mensaje)
    print("usuario:", current_user.id_usuario)
    print("es_pregunta (forzado):", es_pregunta)
    print("================================")

    db = get_connection()

    resultado = ModelPQR.crear_pqr(
        db=db,
        id_usuario=current_user.id_usuario,
        tipo=tipo,
        asunto=asunto,
        mensaje=mensaje,
        es_pregunta=es_pregunta
    )

    print("resultado insertar:", resultado)

    flash("Tu mensaje fue enviado correctamente.", "success")
    return redirect(url_for('contacto_bp.contacto'))


# ============================================================
# 📄 MIS PQRS (SIN CAMBIOS)
# ============================================================
@contacto_bp.route('/mis_pqr')
@login_required
def mis_pqr():
    db = get_connection()
    pqr_list = ModelPQR.obtener_pqr_usuario(db, current_user.id_usuario)
    return render_template('mis_pqr.html', pqr_list=pqr_list)