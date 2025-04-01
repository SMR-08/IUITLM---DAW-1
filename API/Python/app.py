# file: app.py
from flask import Flask, request, jsonify
from db import *
from ejercicios_python.EJ04.EJ4 import Cuenta, CuentaJoven
from ejercicios_python.EJ01.EJ1 import Producto, Inventario
from flask_cors import CORS
import json
import logging
import hashlib 
import os





app = Flask(__name__)
CORS(app)
# Configuración del logging
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
        Lanza ErrorBaseDatos si hay un problema con la BD (assuming db.py uses ErrorBaseDatos).
    """
    try:
        # 1. Obtener los datos de la BD usando la función genérica
        # Filtramos por 'id' que es la clave primaria de CuentasAlmacenadas
        resultados = obtener_todos_los_elementos(
            'CuentasAlmacenadas',
            filtro={'id': id_cuenta},
            limite=1 # Solo esperamos un resultado
        )

        # 2. Comprobar si se encontró la cuenta
        if not resultados:
            logging.info(f"No se encontró cuenta almacenada con id={id_cuenta}")
            return None # Indica que no existe

        # Como usamos limite=1 y filtramos por PK, tomamos el primer elemento
        datos_bd = resultados[0]
        tipo_cuenta = datos_bd.get('tipo_cuenta')
        datos_objeto_str = datos_bd.get('datos_objeto')

        # Verificación extra (aunque la BD debería tener NOT NULL)
        if not tipo_cuenta or not datos_objeto_str:
             logging.error(f"Datos incompletos recuperados para id={id_cuenta} desde la BD.")
             raise ValueError("Los datos recuperados de la base de datos están incompletos.")

        # 3. Deserializar el JSON a un diccionario Python
        try:
            diccionario_atributos = json.loads(datos_objeto_str)
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar JSON para id={id_cuenta}. Datos: '{datos_objeto_str}'. Error: {e}")
            raise ValueError(f"Los datos almacenados para la cuenta {id_cuenta} están corruptos (JSON inválido).") from e

        # 4. Reconstruir (instanciar) el objeto correcto basado en 'tipo_cuenta'
        if tipo_cuenta == 'Cuenta':
            # Usamos **kwargs para pasar el diccionario como argumentos nombrados al constructor
            instancia = Cuenta(**diccionario_atributos)
            logging.debug(f"Instancia de Cuenta reconstruida para id={id_cuenta}")
            return instancia
        elif tipo_cuenta == 'CuentaJoven':
            instancia = CuentaJoven(**diccionario_atributos)
            logging.debug(f"Instancia de CuentaJoven reconstruida para id={id_cuenta}")
            return instancia
        else:
            # Tipo desconocido encontrado en la base de datos
            logging.error(f"Tipo de cuenta desconocido '{tipo_cuenta}' encontrado en la BD para id={id_cuenta}")
            raise ValueError(f"Tipo de cuenta no soportado encontrado en la base de datos: {tipo_cuenta}")

    except ErrorBaseDatos as error_bd: # Use translated exception name
        # Si 'obtener_todos_los_elementos' falla
        logging.error(f"Error de base de datos al intentar obtener cuenta id={id_cuenta}: {error_bd}")
        raise # Re-lanzamos la excepción para que el endpoint la maneje

    # No necesitamos un 'except Exception' general aquí,
    # dejamos que ErrorBaseDatos y ValueError (lanzadas explícitamente) suban.

@app.route('/')
def indice():
    return "Estás llamando al Servidor Python de API, ¡ingresa la ruta correcta y responderé!"

@app.route('/cuentas/<int:id_cuenta>/verificar', methods=['GET'])
def verificar_cuenta_objeto(id_cuenta):
    """Endpoint de ejemplo para probar obtener_instancia_cuenta."""
    try:
        cuenta_temporal = obtener_instancia_cuenta(id_cuenta)

        if cuenta_temporal is None:
            return jsonify({'error': f'Cuenta con id {id_cuenta} no encontrada'}), 404

        # Ahora puedes usar los métodos del objeto
        saldo = cuenta_temporal.consultar_saldo()
        titular = cuenta_temporal.consultar_titular()
        tipo = cuenta_temporal.__class__.__name__ # Obtiene 'Cuenta' o 'CuentaJoven'

        informacion = {
            'id_db': id_cuenta,
            'tipo_objeto': tipo,
            'titular': titular,
            'saldo_actual': saldo,
        }
        # Si es CuentaJoven, podríamos añadir más info
        if isinstance(cuenta_temporal, CuentaJoven):
             informacion['bonificacion'] = cuenta_temporal.get_bonificacion()
             informacion['edad'] = cuenta_temporal.get_edad()
             informacion['es_valido'] = cuenta_temporal.TitularValido() # Assuming method names in CuentaJoven remain

        return jsonify(informacion), 200

    except (ErrorBaseDatos, ValueError) as e: # Capturamos errores específicos
        logging.error(f"Error al verificar cuenta {id_cuenta}: {e}")
        # Devolvemos 500 para errores de BD o datos corruptos/inválidos
        return jsonify({'error': f'Error al procesar la cuenta {id_cuenta}: {str(e)}'}), 500
    except Exception as e:
        logging.exception(f"Error inesperado al verificar cuenta {id_cuenta}: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500


# --- NUEVA ESTRUCTURA DE DATOS ---
# Tabla: CuentasAlmacenadas
# Columnas: id (PK), tipo_cuenta (VARCHAR), datos_objeto (TEXT/JSON)
# ----------------------------------

@app.route('/cuentas', methods=['POST'])
def crear_cuenta_objeto():
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
        # Validaciones
        if not isinstance(titular, str) or not titular.strip():
            return jsonify({'error': 'El titular debe ser una cadena no vacía'}), 400
        if not isinstance(cantidad, (int, float)):
            return jsonify({'error': 'La cantidad debe ser un número'}), 400
        if cantidad < 0:
             return jsonify({'error': 'La cantidad inicial no puede ser negativa'}), 400

        tipo = 'Cuenta' # Tipo de objeto a crear

        # Estado inicial del objeto como diccionario
        estado_objeto = {
            'titular': titular,
            'cantidad': cantidad
        }
        # Convertir a JSON string
        datos_json_str = json.dumps(estado_objeto)

        # Datos para insertar en la base de datos
        datos_bd = {
            'tipo_cuenta': tipo,
            'datos_objeto': datos_json_str
        }

        # Insertar en BD y obtener el ID
        id_cuenta_bd = insertar_elemento('CuentasAlmacenadas', datos_bd)

        logging.info(f"Creada entrada para Cuenta con ID: {id_cuenta_bd}")
        return jsonify({
            'mensaje': 'Entrada de Cuenta creada exitosamente en BD', # User-facing message translated
            'id': id_cuenta_bd
        }), 201 # Código 201: Created

    except ErrorBaseDatos as e: # Use translated exception name
        logging.error(f"Error de BD al crear entrada de cuenta: {e}")
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except json.JSONDecodeError:
         logging.error("Error con el JSON de entrada.")
         return jsonify({'error': 'JSON de entrada inválido'}), 400
    except Exception as e:
        logging.exception(f"Error inesperado al crear entrada de cuenta: {e}")
        return jsonify({'error': 'Error inesperado en el servidor'}), 500

@app.route('/cuentas/<int:id_cuenta>/gasto', methods=['POST'])
def realizar_gasto_objeto(id_cuenta):
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
        # 1. Obtener la cantidad del gasto desde el JSON de la solicitud
        datos_gasto = request.get_json()
        if not datos_gasto or 'cantidad' not in datos_gasto:
            return jsonify({'error': 'Falta el campo "cantidad" en el cuerpo JSON'}), 400

        cantidad = datos_gasto['cantidad']

        # Validar cantidad
        if not isinstance(cantidad, (int, float)):
            return jsonify({'error': 'La cantidad debe ser un número'}), 400
        if cantidad <= 0:
            return jsonify({'error': 'La cantidad del gasto debe ser positiva'}), 400

        # 2. Obtener la instancia del objeto Cuenta/CuentaJoven
        objeto_cuenta = obtener_instancia_cuenta(id_cuenta)

        # Verificar si la cuenta existe
        if objeto_cuenta is None:
            return jsonify({'error': f'Cuenta con id {id_cuenta} no encontrada'}), 404

        # Guardamos el saldo antes por si el método realizar_gasto solo imprime
        # y no modifica en caso de error (como en la clase Cuenta base)
        saldo_antes = objeto_cuenta.consultar_saldo() # Assume method names remain

        # 3. Intentar realizar el gasto usando el método del objeto
        try:
            # NOTA: La clase Cuenta original solo imprime "Saldo insuficiente".
            # La clase CuentaJoven lanza ValueError si el titular no es válido.
            # Assuming method names remain in Cuenta/CuentaJoven
            objeto_cuenta.realizar_gasto(cantidad)
        except ValueError as e:
            # Capturamos el error específico de CuentaJoven si el titular no es válido
            logging.warning(f"Intento de gasto rechazado para cuenta joven {id_cuenta}: {e}")
            return jsonify({'error': f"Gasto no permitido: {e}"}), 403 # Forbidden o 400 Bad Request

        # 4. Verificar si el saldo cambió (importante para la clase Cuenta base)
        saldo_despues = objeto_cuenta.consultar_saldo() # Assume method names remain
        if saldo_antes == saldo_despues and isinstance(objeto_cuenta, Cuenta) and not isinstance(objeto_cuenta, CuentaJoven):
             # Si el saldo no cambió y es una Cuenta normal, asumimos saldo insuficiente
             # (basado en el comportamiento de la clase original que solo imprime)
             logging.warning(f"Gasto no realizado en cuenta {id_cuenta} (probablemente saldo insuficiente).")
             return jsonify({'error': 'Saldo insuficiente para realizar el gasto'}), 400 # Bad Request

        # 5. Preparar el estado actualizado para guardar en la BD
        tipo_cuenta = objeto_cuenta.__class__.__name__ # 'Cuenta' o 'CuentaJoven'

        # Reconstruir el diccionario de atributos desde el objeto MODIFICADO
        # Assuming method names remain in Cuenta/CuentaJoven
        if isinstance(objeto_cuenta, CuentaJoven):
            estado_actualizado = {
                'titular': objeto_cuenta.consultar_titular(),
                'cantidad': objeto_cuenta.consultar_saldo(),
                'bonificacion': objeto_cuenta.get_bonificacion(),
                'edad': objeto_cuenta.get_edad()
            }
        elif isinstance(objeto_cuenta, Cuenta):
             estado_actualizado = {
                'titular': objeto_cuenta.consultar_titular(),
                'cantidad': objeto_cuenta.consultar_saldo()
             }
        else:
             # Esto no debería pasar si obtener_instancia_cuenta funciona bien
             logging.error(f"Tipo de objeto inesperado {tipo_cuenta} después de obtener instancia {id_cuenta}")
             raise TypeError("Tipo de objeto inesperado.")

        datos_json_actualizado = json.dumps(estado_actualizado)

        # Datos para la función actualizar_elemento
        datos_bd_actualizar = {
            'datos_objeto': datos_json_actualizado
        }

        # 6. Actualizar la entrada en la base de datos
        # Usamos 'id' como columna identificadora para la tabla CuentasAlmacenadas
        actualizado = actualizar_elemento('CuentasAlmacenadas', 'id', id_cuenta, datos_bd_actualizar)

        if actualizado:
            logging.info(f"Gasto de {cantidad} procesado y guardado para cuenta id={id_cuenta}. Nuevo saldo: {saldo_despues}")
            return jsonify({
                'mensaje': 'Gasto realizado y estado actualizado exitosamente', # User-facing message translated
                'id': id_cuenta,
                'nuevo_saldo': saldo_despues
            }), 200
        else:
            # Si la actualización falla por alguna razón inesperada
            logging.error(f"Se procesó el gasto para id={id_cuenta}, pero falló la actualización en BD.")
            # Podríamos intentar revertir el cambio en memoria aquí, pero es complejo.
            # Devolver un error 500 es lo más seguro.
            return jsonify({'error': 'El gasto se procesó pero no se pudo guardar el nuevo estado'}), 500

    except (ErrorBaseDatos, ValueError, TypeError) as e: # Capturamos errores de BD, datos inválidos, o tipos
        logging.error(f"Error procesando gasto para cuenta {id_cuenta}: {e}")
        # Devolvemos 500 para DB errors, 400 podría ser para ValueError/TypeError dependiendo del contexto
        # pero 500 es seguro si el error viene de obtener_instancia_cuenta o errores internos.
        return jsonify({'error': f'Error al procesar el gasto: {str(e)}'}), 500
    except Exception as e:
        logging.exception(f"Error inesperado procesando gasto para cuenta {id_cuenta}: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500

@app.route('/Cuenta_joven', methods=['POST']) # Endpoint URL unchanged
def crear_cuenta_joven_objeto():
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
        # 1. Obtener los datos JSON de la solicitud
        datos_iniciales = request.get_json()

        # 2. Validación de la entrada (parámetros para el constructor de CuentaJoven)
        campos_requeridos = ['titular', 'bonificacion', 'edad']
        if not datos_iniciales or any(campo not in datos_iniciales for campo in campos_requeridos):
            faltantes = [campo for campo in campos_requeridos if not datos_iniciales or campo not in datos_iniciales]
            return jsonify({'error': f'Faltan campos obligatorios: {", ".join(faltantes)}'}), 400

        titular = datos_iniciales['titular']
        cantidad = datos_iniciales.get('cantidad', 0.00) # Opcional, default 0.00
        bonificacion = datos_iniciales['bonificacion']
        edad = datos_iniciales['edad']

        # Validaciones adicionales de tipo y valor
        if not isinstance(titular, str) or not titular.strip():
            return jsonify({'error': 'El titular debe ser una cadena no vacía'}), 400
        if not isinstance(cantidad, (int, float)) or cantidad < 0:
            return jsonify({'error': 'La cantidad debe ser un número no negativo'}), 400
        if not isinstance(bonificacion, (int, float)) or bonificacion < 0: # Podríamos validar un rango 0-100
            return jsonify({'error': 'La bonificación debe ser un número no negativo'}), 400
        if not isinstance(edad, int) or edad <= 0: # La edad debería ser un entero positivo
             return jsonify({'error': 'La edad debe ser un número entero positivo'}), 400
        # Nota: NO estamos validando aquí si es TitularValido (18 <= edad < 25),
        # solo que los datos sean correctos. Esa lógica pertenece al objeto.

        # 3. Preparar los datos para almacenar en la BD
        tipo = 'CuentaJoven' # Especificamos el tipo correcto

        # Creamos el diccionario que representa el estado del objeto CuentaJoven
        estado_objeto = {
            'titular': titular,
            'cantidad': cantidad,
            'bonificacion': bonificacion,
            'edad': edad
        }

        # Convertimos a cadena JSON
        datos_json_str = json.dumps(estado_objeto)

        # Datos a insertar en la tabla 'CuentasAlmacenadas'
        datos_bd = {
            'tipo_cuenta': tipo,
            'datos_objeto': datos_json_str
        }

        # 4. Insertar en la base de datos
        id_cuenta_bd = insertar_elemento('CuentasAlmacenadas', datos_bd)

        # 5. Devolver una respuesta de éxito
        logging.info(f"Creada entrada para CuentaJoven con ID: {id_cuenta_bd}")
        return jsonify({
            'mensaje': 'Entrada de CuentaJoven creada exitosamente en BD', # User-facing message translated
            'id': id_cuenta_bd
        }), 201 # Created

    except ErrorBaseDatos as e: # Use translated exception name
        logging.error(f"Error de BD al crear entrada de cuenta joven: {e}")
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except json.JSONDecodeError:
         logging.error("Error al decodificar el JSON de entrada para cuenta joven.")
         return jsonify({'error': 'JSON de entrada inválido'}), 400
    except Exception as e:
        logging.exception(f"Error inesperado al crear entrada de cuenta joven: {e}")
        return jsonify({'error': 'Error inesperado en el servidor'}), 500

@app.route('/apiregistro', methods=['POST'])
def api_registro_usuario():
    """
    Endpoint para registrar un usuario y vincularlo a una cuenta.
    Recibe DNI y contraseña en texto plano, los hashea (SHA256) en el servidor,
    y los inserta junto con el ID de cuenta en la tabla 'Usuarios'.
    """
    try:
        datos_registro = request.get_json()

        # 1. Validar entrada - Esperamos campos en texto plano
        campos_requeridos = ['dni_plain', 'contrasena_plain', 'id_cuenta'] # <--- Nombres de campos esperados
        if not datos_registro or any(campo not in datos_registro for campo in campos_requeridos):
            campos_faltantes = [campo for campo in campos_requeridos if not datos_registro or campo not in datos_registro]
            return jsonify({'error': f'Faltan campos obligatorios: {", ".join(campos_faltantes)}'}), 400

        dni_plain = datos_registro['dni_plain'] # <--- Recibir DNI plano
        contrasena_plain = datos_registro['contrasena_plain'] # <--- Recibir contraseña plana
        id_cuenta_str = datos_registro['id_cuenta']

        # 2. Validar tipos y valores básicos
        if not isinstance(dni_plain, str) or not dni_plain.strip():
            return jsonify({'error': 'El DNI debe ser una cadena no vacía'}), 400
        if not isinstance(contrasena_plain, str) or not contrasena_plain: # Permitir contraseñas con espacios, pero no vacías
            return jsonify({'error': 'La contraseña debe ser una cadena no vacía'}), 400
        # (Validación de id_cuenta sigue igual)
        if not isinstance(id_cuenta_str, (str, int)):
            return jsonify({'error': 'El ID de cuenta debe ser un número entero o cadena convertible'}), 400
        try:
            id_cuenta = int(id_cuenta_str)
            if id_cuenta <= 0:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'El ID de cuenta debe ser un número entero positivo válido'}), 400

        # 3. Verificar que la cuenta existe (sin cambios aquí)
        cuenta = obtener_todos_los_elementos('CuentasAlmacenadas', filtro={'id': id_cuenta}, limite=1)
        if not cuenta:
            return jsonify({'error': f'Cuenta con ID {id_cuenta} no encontrada'}), 404

        # 4. --- Hashear DNI y Contraseña en el Servidor ---
        try:
            # Codificar a bytes antes de hashear
            dni_hasheado = hashlib.sha256(dni_plain.encode('utf-8')).hexdigest()
            contrasena_hasheada = hashlib.sha256(contrasena_plain.encode('utf-8')).hexdigest()
            logging.debug(f"DNI plano recibido: {dni_plain}, Hash generado: {dni_hasheado}")
            # No loguear contraseña plana o hasheada en producción por seguridad
        except Exception as e:
             logging.error(f"Error al hashear DNI o contraseña: {e}")
             return jsonify({'error': 'Error interno al procesar credenciales'}), 500


        # 5. Preparar datos para la BD usando los hashes generados
        datos_usuario_bd = {
            'dni_usuario': dni_hasheado,    # Columna 'dni_usuario' recibe el hash
            'contraseña': contrasena_hasheada, # Columna 'contraseña' recibe el hash
            'fk_id_cuenta': id_cuenta
        }

        # 6. Insertar en la base de datos (sin cambios en la lógica de inserción)
        try:
            insertar_elemento('Usuarios', datos_usuario_bd)
        except ErrorBaseDatos as e:
            # Manejo de error de duplicado DNI (PK)
            # La comprobación exacta del mensaje de error puede depender del SGBD y del driver
            error_str = str(e).lower()
            if ("duplicate entry" in error_str and f"'{dni_hasheado}'" in error_str) or \
               ("unique constraint" in error_str and "dni_usuario" in error_str): # Añadir otras posibles variaciones
                logging.warning(f"Intento de registrar DNI duplicado (hash): {dni_hasheado}")
                return jsonify({'error': f'Ya existe un usuario registrado con este DNI'}), 409 # Conflict
            else:
                logging.error(f"Error de BD al registrar usuario: {e}")
                return jsonify({'error': f'Error de base de datos al registrar usuario: {str(e)}'}), 500

        # 7. Devolver respuesta de éxito
        logging.info(f"Usuario registrado con DNI (hash): {dni_hasheado} y vinculado a cuenta ID: {id_cuenta}")
        # Devolvemos solo el id_cuenta como confirmación, no es necesario devolver el hash del DNI
        return jsonify({
            'mensaje': 'Usuario registrado exitosamente y vinculado a la cuenta',
            'id_cuenta': id_cuenta
        }), 201 # Created

    # --- Bloques catch sin cambios ---
    except ErrorBaseDatos as e:
        logging.error(f"Error de BD general en registro de usuario: {e}")
        return jsonify({'error': f'Error de base de datos al registrar usuario: {str(e)}'}), 500
    except json.JSONDecodeError:
        logging.error("Error al decodificar JSON de entrada para registro de usuario.")
        return jsonify({'error': 'JSON de entrada inválido'}), 400
    except Exception as e:
        logging.exception(f"Error inesperado al registrar usuario: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500
    
if __name__ == '__main__':
    # debug=True es útil para desarrollo, desactivar en producción
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")