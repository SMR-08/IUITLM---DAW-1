# app.py
from flask import Flask, request, jsonify
from db import obtener_conexion_bd, DatabaseError, insertar_elemento, obtener_todos_los_elementos, actualizar_elemento, eliminar_elemento  # Importa las funciones de db.py
import logging

app = Flask(__name__)

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/cuentas', methods=['POST'])
def crear_cuenta():
    """
    Crea una nueva cuenta en la tabla 'Cuenta'.

    Espera un JSON con los siguientes campos:
    - titular: Nombre del titular (obligatorio).
    - cantidad: Saldo inicial (opcional, por defecto 0.00).

    Devuelve:
    - Un JSON con el ID de la cuenta creada y un mensaje de éxito si la operación es correcta.
    - Un JSON con un mensaje de error y el código de estado apropiado si falla.
    """
    try:
        datos = request.get_json()

        # Validación básica de la entrada
        if not datos or 'titular' not in datos:
            return jsonify({'error': 'Falta el campo "titular"'}), 400  # Bad Request

        titular = datos['titular']
        cantidad = datos.get('cantidad', 0.00)  # Valor por defecto si no se proporciona

        # Validacion de datos (más completa, incluyendo tipos)
        if not isinstance(titular, str) or not titular.strip():  # Verifica que sea texto y no esté vacío
            return jsonify({'error': 'El titular debe ser una cadena no vacía'}), 400
        if not isinstance(cantidad, (int, float)):
            return jsonify({'error': 'La cantidad debe ser un número'}), 400


        # Preparar los datos para la inserción
        datos_cuenta = {
            'titular': titular,
            'cantidad': cantidad
        }

        # Insertar en la base de datos
        cuenta_id = insertar_elemento('Cuenta', datos_cuenta)

        # Devolver una respuesta de éxito
        return jsonify({'message': 'Cuenta creada exitosamente', 'cuenta_id': cuenta_id}), 201  # Created

    except DatabaseError as e:
        logging.error(f"Error al crear la cuenta: {e}")
        return jsonify({'error': str(e)}), 500  # Internal Server Error
    except Exception as e:
        logging.exception(f"Error inesperado al crear la cuenta: {e}") # Usamos exception para capturar el traceback
        return jsonify({'error': 'Error inesperado al crear la cuenta'}), 500

@app.route('/cuentas/<int:cuenta_id>/saldo', methods=['GET'])
def consultar_saldo(cuenta_id):
    """
    Consulta el saldo de una cuenta específica.

    Args:
        cuenta_id: El ID de la cuenta a consultar.

    Devuelve:
    - Un JSON con el saldo de la cuenta si la encuentra.
    - Un JSON con un mensaje de error y el código de estado apropiado si no la encuentra o hay un error.
    """
    try:
        # Obtener la cuenta de la base de datos
        cuenta = obtener_todos_los_elementos('Cuenta', filtro={'cuenta_id': cuenta_id})

        # Verificar si la cuenta existe
        if not cuenta:
            return jsonify({'error': 'Cuenta no encontrada'}), 404  # Not Found

        # Como 'obtener_todos_los_elementos' devuelve una lista, tomamos el primer elemento (si existe)
        saldo = cuenta[0]

        # Devolver el saldo
        return jsonify({'cuenta_id': cuenta_id, 'saldo': saldo}), 200  # OK

    except DatabaseError as e:
        logging.error(f"Error al consultar el saldo de la cuenta {cuenta_id}: {e}")
        return jsonify({'error': str(e)}), 500  # Internal Server Error
    except Exception as e:
        logging.exception(f"Error inesperado al consultar saldo: {e}")
        return jsonify({'error': 'Error inesperado al consultar el saldo'}), 500
if __name__ == '__main__':
    app.run(debug=True)  # Modo debug para desarrollo
