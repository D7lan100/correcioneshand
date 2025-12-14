# src/models/entities/ModelDonaciones.py

from src.models.entities.Donacion import Donaciones
from datetime import datetime


# src/models/entities/ModelDonaciones.py

class ModelDonaciones:
    
    @staticmethod
    def guardar_donacion(donacion, db):
        """Guarda una donación en la base de datos"""
        try:
            connection = db.connection
            cursor = connection.cursor()
            
            #  Usar fecha_creacion (que ya existe en tu tabla)
            query = """
                INSERT INTO donaciones 
                (id_usuario, monto, metodo_pago, datos_pago, estado, fecha_creacion) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            cursor.execute(query, (
                donacion.id_usuario,
                donacion.monto,
                donacion.metodo_pago,
                donacion.datos_pago,
                donacion.estado
            ))
            
            connection.commit()
            cursor.close()
            
            print(f" Donación guardada: Usuario {donacion.id_usuario}, Monto ${donacion.monto}")
            return True
            
        except Exception as e:
            print(f" Error al guardar donación: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    @staticmethod
    def obtener_historial(id_usuario, db):
        """Obtiene el historial de donaciones"""
        try:
            connection = db.connection
            cursor = connection.cursor()
            
            #  Usar fecha_creacion
            query = """
                SELECT id_donacion, monto, metodo_pago, estado, fecha_creacion 
                FROM donaciones 
                WHERE id_usuario = %s 
                ORDER BY fecha_creacion DESC
            """
            
            cursor.execute(query, (id_usuario,))
            rows = cursor.fetchall()
            cursor.close()
            
            donaciones = []
            for row in rows:
                donaciones.append({
                    "id": row[0],
                    "monto": float(row[1]),
                    "metodo": row[2],
                    "estado": row[3],
                    "fecha": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None
                })
            
            return donaciones
            
        except Exception as e:
            print(f" Error al obtener historial: {e}")
            return []