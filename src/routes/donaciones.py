from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import json

donaciones_bp = Blueprint('donaciones_bp', __name__)

def get_db_cursor():
    db = current_app.db
    return db.connection.cursor()

@donaciones_bp.route('/donar', methods=['GET'])
@login_required
def mostrar_formulario_donacion():
    return render_template("navbar/donaciones.html")


@donaciones_bp.route('/procesar_donacion', methods=['POST'])
@login_required
def procesar_donacion():
    try:
        monto = request.form.get("monto")
        metodo_pago = request.form.get("metodo_pago")

        # capturar resto de datos del formulario
        detalles_pago = json.dumps(request.form.to_dict())

        cur = get_db_cursor()
        sql = """
            INSERT INTO donaciones (id_usuario, monto, metodo_pago, detalles_pago)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(sql, (current_user.id, monto, metodo_pago, detalles_pago))
        current_app.db.connection.commit()

        return redirect(url_for("donaciones_bp.donacion_exitosa"))
        

    except Exception as e:
        print("ERROR DONACIÓN:", e)
        flash("Error al procesar la donación", "danger")
        return redirect(url_for("donaciones_bp.mostrar_formulario_donacion"))


@donaciones_bp.route('/donacion_exitosa')
@login_required
def donacion_exitosa():
    return render_template("navbar/gracias.html")