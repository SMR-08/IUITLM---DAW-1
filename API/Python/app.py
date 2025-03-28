# file: app.py
from flask import Flask, request, jsonify
from db import *
from ejercicios_python.EJ04.EJ4 import *
from flask_cors import CORS
import json
import logging
import os

aplicacion = Flask(__name__)
CORS(aplicacion)
# Configuración del registro (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def obtener_instancia_cuenta(id_cuenta: int):
    """
    Recupera los datos de una cuenta almacenada por su ID, deserializa el JSON
    y reconstruye la instancia del objeto Cuenta o CuentaJoven correspondiente.

    Args:
        id_cuenta: El ID (clave primaria) de la fila en la tabla CuentasAlmacenadas.

    Returns:
        Una instancia de Cuenta o CuentaJoven si se encuentra y reconstruye con éxito.
        None si no se encuentra la cuenta con ese ID.
        Lanza ValueError si los datos están corruptos o el tipo es desconocido.
        Lanza ErrorBaseDeDatos si hay un problema con la BD.
    """
    try:
        # Obtener los datos de la BD usando la función genérica.
        resultados = obtener_todos_los_elementos(
            'CuentasAlmacenadas',
            filtro={'id': id_cuenta},
            limite=1 # Solo esperamos un resultado
        )

        # Comprobar si se encontró la cuenta.
        if not resultados:
            logging.info(f"No se encontró cuenta almacenada con id={id_cuenta}")
            return None # Indica que no existe

        # Tomamos el primer elemento ya que usamos limite=1 y filtramos por PK.
        datos_db = resultados[0]
        tipo_cuenta = datos_db.get('tipo_cuenta')
        datos_objeto_str = datos_db.get('datos_objeto')

        # Verificación extra (aunque la BD debería tener NOT NULL).
        if not tipo_cuenta or not datos_objeto_str:
             logging.error(f"Datos incompletos recuperados para id={id_cuenta} desde la BD.")
             raise ValueError("Datos recuperados de la base de datos están incompletos.")
        # Deserializar = Traducir JSON a un objeto Python
        # Deserializar el JSON a un diccionario Python.
        try:
            atributos_dict = json.loads(datos_objeto_str)
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar JSON para id={id_cuenta}. Datos: '{datos_objeto_str}'. Error: {e}")
            raise ValueError(f"Los datos almacenados para la cuenta {id_cuenta} están corruptos (JSON inválido).") from e

        # Reconstruir (instanciar) el objeto correcto basado en 'tipo_cuenta'.
        if tipo_cuenta == 'Cuenta':
            # Usamos **kwargs para pasar el diccionario como argumentos nombrados al constructor.
            instancia = Cuenta(**atributos_dict)
            logging.debug(f"Instancia de Cuenta reconstruida para id={id_cuenta}")
            return instancia
        elif tipo_cuenta == 'CuentaJoven':
            instancia = CuentaJoven(**atributos_dict)
            logging.debug(f"Instancia de CuentaJoven reconstruida para id={id_cuenta}")
            return instancia
        else:
            # Tipo desconocido encontrado en la base de datos.
            logging.error(f"Tipo de cuenta desconocido '{tipo_cuenta}' encontrado en la BD para id={id_cuenta}")
            raise ValueError(f"Tipo de cuenta no soportado encontrado en la base de datos: {tipo_cuenta}")

    except ErrorBaseDeDatos as db_err:
        # Si 'obtener_todos_los_elementos' falla.
        logging.error(f"Error de base de datos al intentar obtener cuenta id={id_cuenta}: {db_err}")
        raise # Re-lanzamos la excepción para que el endpoint la maneje

    # No necesitamos un 'except Exception' general aquí,
    # dejamos que ErrorBaseDeDatos y ValueError (lanzadas explícitamente) suban.
@aplicacion.route('/')
def indice():
    return "Estas llamando al Servidor Python de API, ingresa la ruta correcta y respondere!"

@aplicacion.route('/cuentas/<int:cuenta_id>/verificar', methods=['GET'])
def verificar_objeto_cuenta(cuenta_id):
    """Endpoint de ejemplo para probar obtener_instancia_cuenta."""
    try:
        cuenta_temporal = obtener_instancia_cuenta(cuenta_id)

        if cuenta_temporal is None:
            return jsonify({'error': f'Cuenta con id {cuenta_id} no encontrada'}), 404

        # Ahora puedes usar los métodos del objeto.
        saldo = cuenta_temporal.consultar_saldo()
        titular = cuenta_temporal.consultar_titular()
        tipo = cuenta_temporal.__class__.__name__ # Obtiene 'Cuenta' o 'CuentaJoven'

        info = {
            'id_db': cuenta_id,
            'tipo_objeto': tipo,
            'titular': titular,
            'saldo_actual': saldo,
        }
        # Si es CuentaJoven, podríamos añadir más info.
        if isinstance(cuenta_temporal, CuentaJoven):
             info['bonificacion'] = cuenta_temporal.get_bonificacion()
             info['edad'] = cuenta_temporal.get_edad()
             info['es_valido'] = cuenta_temporal.TitularValido()

        return jsonify(info), 200

    except (ErrorBaseDeDatos, ValueError) as e: # Capturamos errores específicos.
        logging.error(f"Error al verificar cuenta {cuenta_id}: {e}")
        # Devolvemos 500 para errores de BD o datos corruptos/invalidos.
        return jsonify({'error': f'Error al procesar la cuenta {cuenta_id}: {str(e)}'}), 500
    except Exception as e:
        logging.exception(f"Error inesperado al verificar cuenta {cuenta_id}: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500

@aplicacion.route('/cuentas', methods=['POST'])
def crear_objeto_cuenta():
    """
    Crea una nueva entrada para una Cuenta en la tabla 'CuentasAlmacenadas'.
    Almacena el estado inicial del objeto como una cadena JSON.

    Espera un JSON con los parámetros del constructor de la clase Cuenta:
    - titular: Nombre del titular (obligatorio).
    - cantidad: Saldo inicial (opcional, por defecto 0.00).

    Devuelve:
    - Un JSON con el ID de la entrada creada y un mensaje de éxito.
    - Un JSON con un mensaje de error y el código de estado apropiado si falla.
    """
    try:

        datos_iniciales = request.get_json()
        if not datos_iniciales or 'titular' not in datos_iniciales:
            return jsonify({'error': 'Falta el campo "titular"'}), 400

        titular = datos_iniciales['titular']

        cantidad = datos_iniciales.get('cantidad', 0.00)
        if not isinstance(titular, str) or not titular.strip():
            return jsonify({'error': 'El titular debe ser una cadena no vacía'}), 400
        if not isinstance(cantidad, (int, float)):
            return jsonify({'error': 'La cantidad debe ser un número'}), 400
        if cantidad < 0:
             return jsonify({'error': 'La cantidad inicial no puede ser negativa'}), 400

        tipo = 'Cuenta'

        estado_objeto = {
            'titular': titular,
            'cantidad': cantidad
        }
        datos_json_str = json.dumps(estado_objeto)
        datos_db = {
            'tipo_cuenta': tipo,
            'datos_objeto': datos_json_str
        }
        cuenta_db_id = insertar_elemento('CuentasAlmacenadas', datos_db)
        logging.info(f"Creada entrada para Cuenta con ID: {cuenta_db_id}")
        return jsonify({
            'message': 'Entrada de Cuenta creada exitosamente en BD',
            'id': cuenta_db_id
        }), 201

    except ErrorBaseDeDatos as e:
        logging.error(f"Error de BD al crear entrada de cuenta: {e}")
        return jsonify({'error': str(e)}), 500
    except json.JSONDecodeError:
         logging.error("Error con el JSON de entrada.")
         return jsonify({'error': 'JSON de entrada inválido'}), 400
    except Exception as e:
        logging.exception(f"Error inesperado al crear entrada de cuenta: {e}")
        return jsonify({'error': 'Error inesperado en el servidor'}), 500

@aplicacion.route('/cuentas/<int:cuenta_id>/gasto', methods=['POST'])
def realizar_gasto_objeto(cuenta_id):
    """
    Realiza un gasto en una cuenta recuperando el objeto, usando su método,
    y guardando el estado actualizado.

    Espera un JSON con:
    - cantidad: El monto a gastar (obligatorio, positivo).

    Devuelve:
    - JSON con mensaje de éxito y nuevo saldo, o
    - JSON con error si falla.
    """
    try:
        # Obtener la cantidad del gasto desde el JSON de la solicitud.
        datos_gasto = request.get_json()
        if not datos_gasto or 'cantidad' not in datos_gasto:
            return jsonify({'error': 'Falta el campo "cantidad" en el cuerpo JSON'}), 400

        cantidad = datos_gasto['cantidad']

        # Validar cantidad.
        if not isinstance(cantidad, (int, float)):
            return jsonify({'error': 'La cantidad debe ser un número'}), 400
        if cantidad <= 0:
            return jsonify({'error': 'La cantidad del gasto debe ser positiva'}), 400

        # Obtener la instancia del objeto Cuenta/CuentaJoven.
        cuenta_obj = obtener_instancia_cuenta(cuenta_id)

        # Verificar si la cuenta existe.
        if cuenta_obj is None:
            return jsonify({'error': f'Cuenta con id {cuenta_id} no encontrada'}), 404

        # Guardamos el saldo antes por si el método realizar_gasto solo imprime
        # y no modifica en caso de error (como en la clase Cuenta base).
        saldo_anterior = cuenta_obj.consultar_saldo()

        # Intentar realizar el gasto usando el método del objeto.
        try:
            # NOTA: La clase Cuenta original solo imprime "Saldo insuficiente".
            # La clase CuentaJoven lanza ValueError si el titular no es válido.
            cuenta_obj.realizar_gasto(cantidad)
        except ValueError as e:
            # Capturamos el error específico de CuentaJoven si el titular no es válido.
            logging.warning(f"Intento de gasto rechazado para cuenta joven {cuenta_id}: {e}")
            return jsonify({'error': f"Gasto no permitido: {e}"}), 403 # Forbidden o 400 Bad Request

        # Verificar si el saldo cambió (importante para la clase Cuenta base).
        saldo_despues = cuenta_obj.consultar_saldo()
        if saldo_anterior == saldo_despues and isinstance(cuenta_obj, Cuenta) and not isinstance(cuenta_obj, CuentaJoven):
             # Si el saldo no cambió y es una Cuenta normal, asumimos saldo insuficiente
             # (basado en el comportamiento de la clase original que solo imprime).
             logging.warning(f"Gasto no realizado en cuenta {cuenta_id} (probablemente saldo insuficiente).")
             return jsonify({'error': 'Saldo insuficiente para realizar el gasto'}), 400 # Bad Request

        # Preparar el estado actualizado para guardar en la BD.
        tipo_cuenta = cuenta_obj.__class__.__name__ # 'Cuenta' o 'CuentaJoven'

        # Reconstruir el diccionario de atributos desde el objeto MODIFICADO.
        if isinstance(cuenta_obj, CuentaJoven):
            estado_actualizado = {
                'titular': cuenta_obj.consultar_titular(), # Usamos getters si existen/preferimos.
                'cantidad': cuenta_obj.consultar_saldo(),
                'bonificacion': cuenta_obj.get_bonificacion(),
                'edad': cuenta_obj.get_edad()
            }
        elif isinstance(cuenta_obj, Cuenta):
             estado_actualizado = {
                'titular': cuenta_obj.consultar_titular(),
                'cantidad': cuenta_obj.consultar_saldo()
             }
        else:
             # Esto no debería pasar si obtener_instancia_cuenta funciona bien.
             logging.error(f"Tipo de objeto inesperado {tipo_cuenta} después de obtener instancia {cuenta_id}")
             raise TypeError("Tipo de objeto inesperado.")

        datos_json_actualizado = json.dumps(estado_actualizado)

        # Datos para la función actualizar_elemento.
        datos_db_actualizar = {
            'datos_objeto': datos_json_actualizado
        }

        # Actualizar la entrada en la base de datos.
        # Usamos 'id' como columna identificadora para la tabla CuentasAlmacenadas.
        actualizado = actualizar_elemento('CuentasAlmacenadas', 'id', cuenta_id, datos_db_actualizar)

        if actualizado:
            logging.info(f"Gasto de {cantidad} procesado y guardado para cuenta id={cuenta_id}. Nuevo saldo: {saldo_despues}")
            return jsonify({
                'message': 'Gasto realizado y estado actualizado exitosamente',
                'id': cuenta_id,
                'nuevo_saldo': saldo_despues
            }), 200
        else:
            # Si la actualización falla por alguna razón inesperada.
            logging.error(f"Se procesó el gasto para id={cuenta_id}, pero falló la actualización en BD.")
            # Podríamos intentar revertir el cambio en memoria aquí, pero es complejo.
            # Devolver un error 500 es lo más seguro.
            return jsonify({'error': 'El gasto se procesó pero no se pudo guardar el nuevo estado'}), 500

    except (ErrorBaseDeDatos, ValueError, TypeError) as e: # Capturamos errores de BD, datos inválidos, o tipos.
        logging.error(f"Error procesando gasto para cuenta {cuenta_id}: {e}")
        # Devolvemos 500 para DB errors, 400 podría ser para ValueError/TypeError dependiendo del contexto
        # pero 500 es seguro si el error viene de obtener_instancia_cuenta o errores internos.
        return jsonify({'error': f'Error al procesar el gasto: {str(e)}'}), 500
    except Exception as e:
        logging.exception(f"Error inesperado procesando gasto para cuenta {cuenta_id}: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500

@aplicacion.route('/Cuenta_joven', methods=['POST'])
def crear_objeto_cuenta_joven():
    """
    Crea una nueva entrada para una CuentaJoven en la tabla 'CuentasAlmacenadas'.
    Almacena el estado inicial del objeto (incluyendo bonificación y edad) como JSON.

    Espera un JSON con:
    - titular: Nombre del titular (obligatorio).
    - cantidad: Saldo inicial (opcional, por defecto 0.00).
    - bonificacion: Porcentaje de bonificación (obligatorio).
    - edad: Edad del titular (obligatorio).

    Devuelve:
    - JSON con el ID de la entrada creada y mensaje de éxito.
    - JSON con error si falla.
    """
    try:
        # Obtener los datos JSON de la solicitud.
        datos_iniciales = request.get_json()

        # Validación de la entrada (parámetros para el constructor de CuentaJoven).
        campos_requeridos = ['titular', 'bonificacion', 'edad']
        if not datos_iniciales or any(campo not in datos_iniciales for campo in campos_requeridos):
            campos_faltantes = [campo for campo in campos_requeridos if not datos_iniciales or campo not in datos_iniciales]
            return jsonify({'error': f'Faltan campos obligatorios: {", ".join(campos_faltantes)}'}), 400

        titular = datos_iniciales['titular']
        cantidad = datos_iniciales.get('cantidad', 0.00) # Opcional, default 0.00.
        bonificacion = datos_iniciales['bonificacion']
        edad = datos_iniciales['edad']

        # Validaciones adicionales de tipo y valor.
        if not isinstance(titular, str) or not titular.strip():
            return jsonify({'error': 'El titular debe ser una cadena no vacía'}), 400
        if not isinstance(cantidad, (int, float)) or cantidad < 0:
            return jsonify({'error': 'La cantidad debe ser un número no negativo'}), 400
        if not isinstance(bonificacion, (int, float)) or bonificacion < 0: # Podríamos validar un rango 0-100.
            return jsonify({'error': 'La bonificación debe ser un número no negativo'}), 400
        if not isinstance(edad, int) or edad <= 0: # La edad debería ser un entero positivo.
             return jsonify({'error': 'La edad debe ser un número entero positivo'}), 400
        # Nota: NO estamos validando aquí si es TitularValido (18 <= edad < 25),
        # solo que los datos sean correctos. Esa lógica pertenece al objeto.

        # Preparar los datos para almacenar en la BD.
        tipo = 'CuentaJoven' # Especificamos el tipo correcto.

        # Creamos el diccionario que representa el estado del objeto CuentaJoven.
        estado_objeto = {
            'titular': titular,
            'cantidad': cantidad,
            'bonificacion': bonificacion,
            'edad': edad
        }

        # Convertimos a cadena JSON.
        datos_json_str = json.dumps(estado_objeto)

        # Datos a insertar en la tabla 'CuentasAlmacenadas'.
        datos_db = {
            'tipo_cuenta': tipo,
            'datos_objeto': datos_json_str
        }

        # Insertar en la base de datos.
        cuenta_db_id = insertar_elemento('CuentasAlmacenadas', datos_db)

        # Devolver una respuesta de éxito.
        logging.info(f"Creada entrada para CuentaJoven con ID: {cuenta_db_id}")
        return jsonify({
            'message': 'Entrada de CuentaJoven creada exitosamente en BD',
            'id': cuenta_db_id
        }), 201 # Created

    except ErrorBaseDeDatos as e:
        logging.error(f"Error de BD al crear entrada de cuenta joven: {e}")
        return jsonify({'error': str(e)}), 500
    except json.JSONDecodeError:
         logging.error("Error al decodificar el JSON de entrada para cuenta joven.")
         return jsonify({'error': 'JSON de entrada inválido'}), 400
    except Exception as e:
        logging.exception(f"Error inesperado al crear entrada de cuenta joven: {e}")
        return jsonify({'error': 'Error inesperado en el servidor'}), 500

@aplicacion.route('/apiregistro', methods=['POST'])
def api_registro_usuario():
    """
    Endpoint para registrar un usuario en la tabla 'Usuarios' y vincularlo a una cuenta.
    Recibe DNI (ya hasheado) como PRIMARY KEY, contraseña (ya hasheada), e ID de que cuenta tiene que relacionarse.
    """
    try:
        # Obtener datos JSON de la solicitud.
        datos_registro = request.get_json()

        # Validar la entrada: campos obligatorios y tipos.
        campos_requeridos = ['dni_usuario', 'contraseña', 'id_cuenta']
        if not datos_registro or any(campo not in datos_registro for campo in campos_requeridos):
            campos_faltantes = [campo for campo in campos_requeridos if not datos_registro or campo not in datos_registro]
            return jsonify({'error': f'Faltan campos obligatorios: {", ".join(campos_faltantes)}'}), 400

        dni_usuario = datos_registro['dni_usuario']
        contraseña = datos_registro['contraseña']
        id_cuenta_str = datos_registro['id_cuenta']

        # Validar tipos y formatos.
        if not isinstance(dni_usuario, str) or not dni_usuario.strip():
            return jsonify({'error': 'El DNI de usuario debe ser una cadena no vacía'}), 400
        if not isinstance(contraseña, str) or not contraseña.strip(): # Aunque ya hasheada, debe ser string no vacía.
            return jsonify({'error': 'La contraseña debe ser una cadena no vacía'}), 400
        if not isinstance(id_cuenta_str, (str, int)): # Aceptamos str o int inicialmente, luego convertimos a int.
            return jsonify({'error': 'El ID de cuenta debe ser un número entero'}), 400

        try:
            id_cuenta = int(id_cuenta_str) # Intentar convertir a entero.
            if id_cuenta <= 0:
                raise ValueError # Lanzar error si no es positivo.
        except ValueError:
            return jsonify({'error': 'El ID de cuenta debe ser un número entero positivo válido'}), 400

        # Verifico que tal id existe.
        cuenta = obtener_todos_los_elementos('CuentasAlmacenadas', filtro={'id': id_cuenta})
        if not cuenta:
            return jsonify({'error': 'Cuenta no encontrada'}), 404


        # Preparar datos para la inserción en la tabla Usuarios.
        datos_usuario_db = {
            'dni_usuario': dni_usuario,
            'contraseña': contraseña,
            'fk_id_cuenta': id_cuenta # Usamos el ID de cuenta convertido a entero.
        }

        # Insertar el nuevo usuario en la base de datos.
        try:
            usuario_id = insertar_elemento('Usuarios', datos_usuario_db)
        except ErrorBaseDeDatos as e:
            # Manejar el caso de DNI duplicado al registrar usuario.
            if "Duplicate entry" in str(e) and dni_usuario in str(e):
              return jsonify({'error': f'Ya existe un usuario con este DNI'}), 400
            else:
               return jsonify({'error': f'Error de base de datos al registrar usuario: {str(e)}'}), 500


        # Devolver respuesta de éxito.
        logging.info(f"Usuario registrado con DNI: {dni_usuario} y vinculado a cuenta ID: {id_cuenta}")
        return jsonify({
            'message': 'Usuario registrado exitosamente y vinculado a la cuenta',
            'dni_usuario': dni_usuario,
            'cuenta_id': id_cuenta
        }), 201 # Created

    except ErrorBaseDeDatos as e:
        logging.error(f"Error de BD al registrar usuario: {e}")
        return jsonify({'error': f'Error de base de datos al registrar usuario: {str(e)}'}), 500
    except json.JSONDecodeError:
        logging.error("Error al decodificar JSON de entrada para registro de usuario.")
        return jsonify({'error': 'JSON de entrada inválido'}), 400
    except Exception as e:
        logging.exception(f"Error inesperado al registrar usuario: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500


if __name__ == '__main__':
    aplicacion.run(debug=True)
