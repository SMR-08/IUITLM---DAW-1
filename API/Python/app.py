# /API/Python/app.py
# Para ejecutar desde Vscode lanzalo desde la Terminal: python app.py

from typing import Literal
from flask import Flask, Response, jsonify, request
from esPar import es_par  # Importamos la función es_par
from  ejercicios_python import *

app = Flask(__name__)

@app.route('/es_par/<numero>', methods=['GET'])
# A continuacion iniciamos una funcion llamada 'si_par' que recibe como parametro una variable llamada 'numero'
# Al final con '->' creamos una pista de que devuelve esta funcion.
# Devuelve una tupla (secuencia inmutable y hetereogena) que contiene una clase Response y un tipo Literal con valor 400 O un objeto Response (Si es exitoso)

def si_par(numero) -> tuple[Response, Literal[400]] | Response:
    """
    Endpoint para comprobar si un número es par.

    Args:
        numero: El número a comprobar (pasado como parte de la URL).

    Returns:
        Un JSON con la estructura {"numero": <numero>, "es_par": true/false},
        o un JSON con error y código de estado 400 si el número no es entero.

    """
    resultado = es_par(numero)

    #Si el resultado esta vacio devolvera un error.
    if resultado is None:
        return jsonify({"error": "El valor proporcionado no es un número entero."}), 400 # Error de Bad Request
    
    return jsonify({"numero": int(numero), "es_par": resultado})

@app.route('/cuentas', methods=['POST'])
def crear_cuenta():
    """
    Endpoint para crear una nueva cuenta.
    Espera un JSON: {"titular": "Nombre Apellido", "cantidad": 1000.0}
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se proporcionaron datos JSON."}), 400

    if not all(key in data for key in ("titular", "cantidad")):
        return jsonify({"error": "Faltan datos. Se requiere titular y cantidad."}), 400

    try:
        titular = data['titular']
        cantidad = float(data['cantidad'])
        cuenta = Cuenta(titular, cantidad)
        return jsonify({"mensaje": "Cuenta creada correctamente", "titular": cuenta.titular, "saldo": cuenta.cantidad}), 201

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Error en formato de datos: {e}"}), 400

@app.route('/cuentas/<titular>/saldo', methods=['GET'])
def consultar_saldo(titular):
    """
    Endpoint para consultar el saldo de una cuenta existente.
    El titular se pasa como parte de la URL.
    """
    #Simulamos la base de datos, al no tenerla la cuenta se debe crear en el metodo POST antes de poder utilizar este metodo.
    #Si la cuenta no existe, creamos una "temporal" para que no crashee, ya que no tenemos persistencia.
    cuenta = Cuenta(titular,0)
    saldo = cuenta.consultar_saldo()
    return jsonify({"titular": titular, "saldo": saldo})

@app.route('/cuentas/<titular>/gasto', methods=['POST'])
def realizar_gasto(titular):
    """
    Endpoint para realizar un gasto en una cuenta.
    Espera un JSON con la cantidad a gastar: {"cantidad": 50.0}
    El titular se pasa como parte de la URL.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se proporcionaron datos JSON."}), 400

    if 'cantidad' not in data:
        return jsonify({"error": "Falta la cantidad a gastar."}), 400

    try:
        cantidad_gasto = float(data['cantidad'])
         #Simulamos la base de datos, al no tenerla la cuenta se debe crear en el metodo POST antes de poder utilizar este metodo.
         #Si la cuenta no existe, creamos una "temporal" para que no crashee, ya que no tenemos persistencia.
        cuenta = Cuenta(titular, 1000) #Simulo que ya tiene una cuenta con 1000.
        saldo_anterior = cuenta.consultar_saldo() #Obtenemos el saldo actual.
        cuenta.realizar_gasto(cantidad_gasto)  # Intenta realizar el gasto.
        saldo_actual = cuenta.consultar_saldo() #Obtenemos el saldo despues de la operacion.

        if saldo_actual < saldo_anterior:
            return jsonify({"mensaje": "Gasto realizado correctamente", "titular": titular, "saldo_anterior":saldo_anterior, "saldo": saldo_actual})
        else:
            return jsonify({"error": "Saldo insuficiente", "titular": titular, "saldo": saldo_anterior}), 409 # Conflict

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Error en formato de datos: {e}"}), 400
    
@app.route('/cuentas/<titular>', methods=['GET'])
def obtener_titular(titular):
    """Este Endpoint obtiene el titular, se usa como parte de la URL.
    """
    cuenta = Cuenta(titular,0) #Instanciamos
    return jsonify({"titular":cuenta.consultar_titular()})


if __name__ == '__main__':
    app.run(debug=True)