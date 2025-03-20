# /API/Python/app.py
# Para ejecutar desde Vscode lanzalo desde la Terminal: python app.py

from flask import Flask, jsonify, request
from esPar import es_par  # Importamos la función es_par
from  ejercicios_python import *

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
        return jsonify({"error": f"Error en el formato de los datos. Detalles: {e}"}), 400

    try:
        # Crea una instanacia de Producto con los datos
        producto = Producto(nombre, precio, cantidad)
        # Llama agregar_producto desde la instancia de Inventario, pasandole el producto que creamos arriba.
        inventario.agregar_producto(producto)  # Correct call
        return jsonify({"mensaje": "Producto agregado correctamente", "inventario": str(inventario)}), 201

    except TypeError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

@app.route('/inventario', methods=['GET'])
def obtener_inventario():
    return jsonify({"inventario": str(Inventario)})

@app.route('/coches', methods=['POST'])
def crear_coche():
    """
    Endpoint para crear un nuevo coche.
    Espera un JSON con la información del coche: {"marca", "modelo", "año"}.
    """
    data = request.get_json()  # Obtiene los datos del JSON enviado en la petición

    # Verifica si se proporcionaron los datos 
    if not data:
        return jsonify({"error": "No se proporcionaron datos JSON."}), 400  # Respuesta de error si no hay datos

    # Verifica que el JSON tenga las claves necesarias.
    if not all(key in data for key in ("marca", "modelo", "año")):
        return jsonify({"error": "Faltan datos. Se requiere marca, modelo y año."}), 400

    # Intenta crear la instancia del coche. Puede haber errores en el tipo de datos
    try:
        marca = data['marca']
        modelo = data['modelo']
        año = int(data['año'])  # Se asegura de que el año sea un entero

        coche = Coche(marca, modelo, año) # Crea una instancia de la clase Coche
        return jsonify({"mensaje": "Coche creado correctamente", "coche": {"marca": coche.marca, "modelo": coche.modelo, "año": coche.año}}), 201  # Respuesta exitosa.
    except (ValueError, TypeError) as e:
        # Respuesta con el error si hay un problema con los valores proporcionados
        return jsonify({"error": f"Error en formato de datos: {e}"}), 400

@app.route('/coches', methods=['GET'])
def obtener_coches():
    """
    Endpoint para obtener una lista de coches.  Si no hay coches, devuelve una lista vacía.

    """
    coches = [] #Inicia la lista
    #Crear una lista de diccionarios, cada uno representando un coche
    for coche in coches:
      coches.append({
          "marca": coche.marca,
          "modelo":coche.modelo,
          "año":coche.año
      })
    return jsonify({"coches": coches}) #Devolver la lista como un Json.

@app.route('/animales', methods=['GET'])
def sonido_animales():
    """
    Endpoint para crear una lista de instancias de diferentes animales y ejecuta sus sonidos unicos.
    """
    perro1 = Perro()
    gato1 = Gato()
    perro2 = Perro()
    gato2 = Gato()
    animales = [perro1, gato1, perro2, gato2]
    sonidos = []
    for animal in animales:
        if isinstance(animal, Perro):
            sonidos.append({"animal":"perro", "sonido":"Guau..."})
        elif isinstance(animal, Gato):
            sonidos.append({"animal":"gato", "sonido":"Miau..."})
    return jsonify(sonidos)

if __name__ == '__main__':
    app.run(debug=True)