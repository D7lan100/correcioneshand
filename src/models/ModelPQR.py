# src/models/ModelPQR.py

class ModelPQR:

    @classmethod
    def crear_pqr(cls, db, id_usuario, tipo, asunto, mensaje, es_pregunta):
        try:
            cursor = db.cursor()
            sql = """
                INSERT INTO pqr 
                (id_usuario, tipo, asunto, mensaje, es_pregunta, visible_faq, estado)
                VALUES (%s, %s, %s, %s, %s, 0, 'Pendiente')
            """
            cursor.execute(sql, (id_usuario, tipo, asunto, mensaje, es_pregunta))
            db.commit()
            return True
        except Exception as e:
            print("❌ Error crear PQR/Pregunta:", e)
            return False


    @classmethod
    def obtener_pqr_usuario(cls, db, id_usuario):
        try:
            cursor = db.cursor()
            sql = """
                SELECT id_pqr, tipo, asunto, mensaje, respuesta, estado, fecha, es_pregunta, visible_faq
                FROM pqr
                WHERE id_usuario = %s
                ORDER BY fecha DESC
            """
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchall()
        except Exception as e:
            print("❌ Error obtener PQRs usuario:", e)
            return []


    @classmethod
    def obtener_todos(cls, db):
        try:
            cursor = db.cursor()
            sql = """
                SELECT p.*, u.nombre_completo
                FROM pqr p
                INNER JOIN usuarios u ON u.id_usuario = p.id_usuario
                ORDER BY fecha DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print("❌ Error obtener todos PQR:", e)
            return []


    @classmethod
    def obtener_por_id(cls, db, id_pqr):
        try:
            cursor = db.cursor()
            sql = "SELECT * FROM pqr WHERE id_pqr = %s"
            cursor.execute(sql, (id_pqr,))
            return cursor.fetchone()
        except Exception as e:
            print("❌ Error obtener PQR por ID:", e)
            return None


    @classmethod
    def responder(cls, db, id_pqr, respuesta):
        try:
            cursor = db.cursor()
            sql = """
                UPDATE pqr
                SET respuesta=%s,
                    estado='Respondido'
                WHERE id_pqr=%s
            """
            cursor.execute(sql, (respuesta, id_pqr))
            db.commit()
            return True
        except Exception as e:
            print("❌ Error responder PQR:", e)
            return False


    # ============================================================
    # ACTIVAR / DESACTIVAR PREGUNTA FRECUENTE (FUNCIONAL)
    # ============================================================
    @classmethod
    def cambiar_visibilidad_faq(cls, db, id_pqr, visible):
        try:
            cursor = db.cursor()

            if visible == 1:
                # Publicar como FAQ
                sql = """
                    UPDATE pqr 
                    SET es_pregunta = 1,
                        visible_faq = 1
                    WHERE id_pqr = %s
                """
            else:
                # Ocultar de FAQ
                sql = """
                    UPDATE pqr 
                    SET visible_faq = 0
                    WHERE id_pqr = %s
                """

            cursor.execute(sql, (id_pqr,))
            db.commit()
            return True

        except Exception as e:
            print("❌ Error cambiar visibilidad FAQ:", e)
            return False

    # ============================================================
    #   OBTENER SOLO PREGUNTAS FRECUENTES VISIBLES (ARREGLADO)
    # ============================================================
    @classmethod
    def obtener_faq(cls, db):
        try:
            cursor = db.cursor()

            sql = """
                SELECT asunto, mensaje, respuesta
                FROM pqr
                WHERE visible_faq = 1
                  AND es_pregunta = 1
                  AND respuesta IS NOT NULL
            """

            cursor.execute(sql)
            return cursor.fetchall()

        except Exception as e:
            print("❌ Error obtener FAQs:", e)
            return []