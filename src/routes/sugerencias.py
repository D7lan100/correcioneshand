# src/routes/sugerencias.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from src.models.ModelSugerencia import ModelSugerencia

sugerencias_bp = Blueprint('sugerencias_bp', __name__)

# -----------------------------
# 💡 Lista pública (solo aceptadas)
# -----------------------------
@sugerencias_bp.route('/', methods=['GET'])
def listar_sugerencias():
    """
    Muestra solo las sugerencias aceptadas públicamente.
    """
    try:
        db = current_app.db
        sugerencias = ModelSugerencia.obtener_aceptadas(db)
        return render_template('navbar/sugerencias.html', sugerencias=sugerencias)
    except Exception as e:
        print(f"❌ Error al listar sugerencias: {e}")
        flash("Error al cargar las sugerencias.", "danger")
        return render_template('navbar/sugerencias.html', sugerencias=[])


# -----------------------------
# ✉ Enviar sugerencia (usuarios autenticados)
# -----------------------------
@sugerencias_bp.route('/enviar', methods=['POST'])
@login_required
def enviar_sugerencia():
    """
    Permite que un usuario autenticado envíe una nueva sugerencia.
    """
    try:
        db = current_app.db
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not titulo or not descripcion:
            flash("Por favor completa todos los campos.", "warning")
            return redirect(url_for('sugerencias_bp.listar_sugerencias'))

        data = {
            'id_usuario': current_user.id_usuario,
            'titulo': titulo,
            'descripcion': descripcion
        }

        resultado = ModelSugerencia.crear_sugerencia(db, data)

        flash(
            resultado.get("message", "Operación completada."),
            "success" if resultado.get("success") else "danger"
        )
        return redirect(url_for('sugerencias_bp.listar_sugerencias'))

    except Exception as e:
        print(f"❌ Error al enviar sugerencia: {e}")
        flash("Ocurrió un error al enviar tu sugerencia.", "danger")
        return redirect(url_for('sugerencias_bp.listar_sugerencias'))


# -----------------------------
# 👍 Like / 👎 Dislike en sugerencias
# -----------------------------
@sugerencias_bp.route('/like/<int:id_sugerencia>', methods=['POST'])
@login_required
def like_sugerencia(id_sugerencia):
    """
    Registra un 'like' del usuario en una sugerencia.
    """
    try:
        db = current_app.db
        ok = ModelSugerencia.registrar_voto(db, id_sugerencia, current_user.id_usuario, 'like')
        if ok:
            flash("¡Gracias por apoyar esta sugerencia! 👍", "success")
        else:
            flash("Ya habías votado esta sugerencia.", "info")
    except Exception as e:
        print(f"❌ Error al dar like: {e}")
        flash("No se pudo registrar el like.", "danger")
    return redirect(url_for('sugerencias_bp.listar_sugerencias'))


@sugerencias_bp.route('/dislike/<int:id_sugerencia>', methods=['POST'])
@login_required
def dislike_sugerencia(id_sugerencia):
    """
    Registra un 'dislike' del usuario en una sugerencia.
    """
    try:
        db = current_app.db
        ok = ModelSugerencia.registrar_voto(db, id_sugerencia, current_user.id_usuario, 'dislike')
        if ok:
            flash("Tu opinión ha sido registrada 👎", "warning")
        else:
            flash("Ya habías votado esta sugerencia.", "info")
    except Exception as e:
        print(f"❌ Error al dar dislike: {e}")
        flash("No se pudo registrar el dislike.", "danger")
    return redirect(url_for('sugerencias_bp.listar_sugerencias'))