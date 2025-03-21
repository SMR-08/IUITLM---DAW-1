# IUITLM---DAW-1/API/Python/test_db.py
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Mejor para el rendimiento
db = SQLAlchemy(app)


# --- Modelo de prueba ---
class TestTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_data = db.Column(db.String(255))

    def __repr__(self):
        return f"<TestTable {self.id}: {self.test_data}>"


@app.route('/test_db_connection')
def test_db_connection():
    """Prueba la conexión a la base de datos."""
    try:
        db.session.execute(db.text('SELECT 1'))  # Consulta simple para verificar la conexión
        return jsonify({"message": "Conexión a la base de datos exitosa!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error en la conexión a la base de datos: {e}"}), 500


@app.route('/insert_test_data')
def insert_test_data():
    """Inserta un dato de prueba y verifica que se haya insertado."""
    try:
        # Intenta crear las tablas (si no existen)
        with app.app_context():
          db.create_all()

        # Crea una nueva instancia del modelo de prueba.
        new_data = TestTable(test_data="Dato de prueba")
        db.session.add(new_data)
        db.session.commit()

        # Recupera el dato recién insertado para verificar.
        inserted_data = TestTable.query.filter_by(test_data="Dato de prueba").first()
        if inserted_data:
            return jsonify({"message": f"Dato insertado correctamente. ID: {inserted_data.id}"}), 200
        else:
            return jsonify({"message": "Error: El dato no se encontró después de la inserción."}), 500

    except Exception as e:
        db.session.rollback()  # Deshace cualquier cambio en caso de error
        return jsonify({"message": f"Error al insertar el dato: {e}"}), 500

    finally:
        db.session.close()


if __name__ == '__main__':
    #  app.run(debug=True)  # NO usar app.run con Gunicorn.  Esto es solo para pruebas locales *sin* Docker.
    pass
