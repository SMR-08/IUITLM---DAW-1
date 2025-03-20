# /API/Python/app.py
# Para ejecutar desde Vscode lanzalo desde la Terminal: python app.py

from flask import Flask, jsonify, request
from esPar import es_par  # Importamos la función es_par
from ejercicios_python.EJ01.EJ1 import Inventario, Producto

app = Flask(__name__)

@app.route('/es_par/<number>', methods=['GET'])
def check_if_even(number):
    """
    Endpoint para comprobar si un número es par.

    Args:
        number: El número a comprobar (pasado como parte de la URL).

    Returns:
        Un JSON con la estructura {"numero": <numero>, "es_par": true/false},
        o un JSON con error y código de estado 400 si el número no es entero.

    """
    resultado = es_par(number)

    if resultado is None:
        return jsonify({"error": "El valor proporcionado no es un número entero."}), 400 # Bad Request

    return jsonify({"numero": int(number), "es_par": resultado})

@app.route('/inventario/agregar', methods=['POST'])
def agregar_producto_endpoint():
    """
    Endpoint to add a product to the inventory.
    Expects JSON: {"nombre": "producto1", "precio": 10.99, "cantidad": 5}
    """
    data = request.get_json()
    inventario = Inventario()

    if not data:
        return jsonify({"error": "No se proporcionaron datos JSON."}), 400

    if not all(key in data for key in ("nombre", "precio", "cantidad")):
        return jsonify({"error": "Faltan datos. Se requiere nombre, precio y cantidad."}), 400

    try:
        nombre = data['nombre']
        precio = float(data['precio'])
        cantidad = int(data['cantidad'])
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Error en formato de datos. Detalle: {e}"}), 400

    try:
        # Create a Producto *instance* with the data.
        producto = Producto(nombre, precio, cantidad)
        # Call agregar_producto on the *inventario instance*, passing the producto.
        inventario.agregar_producto(producto)  # Correct call
        return jsonify({"mensaje": "Producto agregado correctamente", "inventario": str(inventario)}), 201

    except TypeError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

@app.route('/inventario', methods=['GET'])
def obtener_inventario():
    return jsonify({"inventario": str(inventario)})

if __name__ == '__main__':
    app.run(debug=True)