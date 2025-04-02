# file: app.py
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import os
import hashlib
# Importar Decimal para manejo preciso de moneda
from decimal import Decimal, InvalidOperation
# Importar tipos necesarios para anotaciones
from typing import List, Dict, Any, Union, NoReturn

# --- Importaciones de Lógica de Negocio ---
# EJ04: Clases del Banco
try:
    from ejercicios_python.EJ04.EJ4 import Cuenta, CuentaJoven
    logging.info("Módulos EJ04 (Cuenta, CuentaJoven) importados correctamente.")
except ImportError as e:
    logging.error(f"Error CRÍTICO importando módulos de EJ04: {e}. La funcionalidad del banco NO estará disponible.")
    # No se definen stubs; si faltan, dará NameError al usarlas.

# --- Importación de Base de Datos ---
try:
    from db import (
        obtener_todos_los_elementos,
        insertar_elemento,
        actualizar_elemento,
        eliminar_elemento,
        ErrorBaseDatos # Importar la clase de excepción REAL
    )
    logging.info("Módulo db.py importado correctamente.")
except ImportError:
    logging.error("Error CRÍTICO importando 'db.py'. Las operaciones de base de datos fallarán.")

    # Definir stubs con tipos que coinciden con las funciones reales de db.py
    # para satisfacer a Pylance, aunque lanzarán una excepción si se llaman.
    # *** CORRECCIÓN: Quitar la definición de ErrorBaseDatos STUB ***
    # class ErrorBaseDatos(Exception): pass # ELIMINAR ESTA LÍNEA

    def obtener_todos_los_elementos(*args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        raise ImportError("Módulo DB no cargado") # Usar ImportError o RuntimeError

    # *** CORRECCIÓN: Ajustar tipo de retorno del stub de insertar_elemento ***
    def insertar_elemento(*args: Any, **kwargs: Any) -> Union[int, None]:
        raise ImportError("Módulo DB no cargado")

    def actualizar_elemento(*args: Any, **kwargs: Any) -> bool:
        raise ImportError("Módulo DB no cargado")

    def eliminar_elemento(*args: Any, **kwargs: Any) -> bool:
        raise ImportError("Módulo DB no cargado")

    # Asegurarse que ErrorBaseDatos exista para los except posteriores si la importación falló
    # Si preferimos que falle claramente si db no carga, podemos quitar los stubs y la clase también
    # Pero para que el resto del análisis de Pylance funcione, a veces se deja la clase stub:
    class ErrorBaseDatos(Exception): pass


# --- Inicialización de Flask y CORS ---
app = Flask(__name__)
CORS(app)

# --- Configuración del Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
log = logging.getLogger(__name__)

# --- Funciones Auxiliares ---
def obtener_instancia_cuenta(id_cuenta: int) -> Union[Cuenta, CuentaJoven, None]:
    log.debug(f"Intentando obtener instancia para cuenta ID: {id_cuenta}")
    try:
        resultados = obtener_todos_los_elementos('CuentasAlmacenadas', filtro={'id': id_cuenta}, limite=1)
        if not resultados:
            log.info(f"No se encontró cuenta almacenada con id={id_cuenta}")
            return None
        datos_bd = resultados[0]
        tipo_cuenta = datos_bd.get('tipo_cuenta')
        datos_objeto_str = datos_bd.get('datos_objeto')
        if not tipo_cuenta or not datos_objeto_str:
             log.error(f"Datos incompletos para id={id_cuenta} desde BD.")
             raise ValueError("Datos recuperados incompletos.")
        try:
            diccionario_atributos = json.loads(datos_objeto_str)
        except json.JSONDecodeError as e:
            log.error(f"Error JSON para id={id_cuenta}. Datos: '{datos_objeto_str}'. Error: {e}")
            raise ValueError(f"Datos almacenados corruptos para cuenta {id_cuenta}.") from e

        if tipo_cuenta == 'Cuenta':
            instancia = Cuenta(**diccionario_atributos)
            log.debug(f"Instancia de Cuenta reconstruida para id={id_cuenta}")
            return instancia
        elif tipo_cuenta == 'CuentaJoven':
            instancia = CuentaJoven(**diccionario_atributos)
            log.debug(f"Instancia de CuentaJoven reconstruida para id={id_cuenta}")
            return instancia
        else:
            log.error(f"Tipo de cuenta desconocido '{tipo_cuenta}' en BD para id={id_cuenta}")
            raise ValueError(f"Tipo de cuenta no soportado: {tipo_cuenta}")
    except NameError as ne:
        log.error(f"Error instanciando cuenta ID {id_cuenta}: Clases no definidas. Error: {ne}", exc_info=True)
        raise RuntimeError("Error interno: Clases de cuenta no disponibles.") from ne
    except ErrorBaseDatos as error_bd:
        log.error(f"Error BD obteniendo cuenta id={id_cuenta}: {error_bd}", exc_info=True)
        raise
    except ValueError as ve:
        log.error(f"Error valor/datos obteniendo cuenta id={id_cuenta}: {ve}", exc_info=True)
        raise
    except Exception as e:
        log.exception(f"Error inesperado obteniendo instancia cuenta id={id_cuenta}: {e}")
        raise RuntimeError(f"Error interno inesperado obteniendo cuenta: {e}")


# --- Endpoints EJ1: Inventario (Base de Datos) ---
@app.route('/inventario', methods=['GET'])
def obtener_inventario_bd():
    log.info("Solicitud GET /inventario recibida.")
    try:
        productos_bd = obtener_todos_los_elementos('ProductosInventario', orden=[('nombre', 'ASC')])
        log.debug(f"Productos recuperados de BD: {len(productos_bd)}")
        valor_total = Decimal('0.00')
        productos_respuesta = []
        for prod in productos_bd:
            precio_decimal = prod.get('precio', Decimal('0.00'))
            cantidad_int = prod.get('cantidad', 0)
            valor_total += precio_decimal * Decimal(cantidad_int)
            productos_respuesta.append({
                'id': prod.get('id'), 'nombre': prod.get('nombre'),
                'precio': str(precio_decimal), 'cantidad': cantidad_int
            })
        log.info(f"Inventario BD calculado: {len(productos_respuesta)} productos, valor total: {valor_total}")
        return jsonify({
            'productos': productos_respuesta, 'valor_total': str(valor_total),
            'mensaje': 'Inventario obtenido correctamente desde la BD.'
        }), 200
    except ErrorBaseDatos as e:
        log.error(f"Error de BD en GET /inventario: {e}", exc_info=True)
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado en GET /inventario: {e}")
        return jsonify({'error': 'Error interno al obtener el inventario'}), 500

@app.route('/inventario/productos', methods=['POST'])
def agregar_producto_inventario_bd():
    log.info("Solicitud POST /inventario/productos recibida.")
    try:
        datos = request.get_json()
        if not datos or not all(k in datos for k in ['nombre', 'precio', 'cantidad']):
            log.warning("POST /inventario/productos incompleta.")
            return jsonify({'error': 'Faltan datos: nombre, precio y cantidad requeridos'}), 400
        nombre = datos['nombre']
        try: precio = Decimal(str(datos['precio']).strip()); assert precio >= 0
        except: log.warning(f"Precio inválido: {datos.get('precio')}"); return jsonify({'error': 'Precio inválido'}), 400
        try: cantidad = int(datos['cantidad']); assert cantidad >= 0
        except: log.warning(f"Cantidad inválida: {datos.get('cantidad')}"); return jsonify({'error': 'Cantidad inválida'}), 400
        if not isinstance(nombre, str) or not nombre.strip(): log.warning("Nombre inválido."); return jsonify({'error': 'Nombre inválido'}), 400
        nombre_limpio = nombre.strip()
        datos_producto_bd = {'nombre': nombre_limpio, 'precio': precio, 'cantidad': cantidad}

        try:
             id_nuevo_producto = insertar_elemento('ProductosInventario', datos_producto_bd)
             log.info(f"Producto agregado BD: ID={id_nuevo_producto}, Nombre='{nombre_limpio}'")
             return jsonify({
                 'mensaje': f'Producto "{nombre_limpio}" agregado.',
                 'producto': {'id': id_nuevo_producto, 'nombre': nombre_limpio, 'precio': str(precio), 'cantidad': cantidad}
                 }), 201
        except ErrorBaseDatos as e:
             # *** CORRECCIÓN: Usar getattr para errno ***
             error_errno = getattr(e, 'errno', None)
             if error_errno == 1062: # Error de duplicado MySQL/MariaDB
                log.warning(f"Intento agregar producto duplicado: {nombre_limpio}. Errno: {error_errno}")
                return jsonify({'error': f'Ya existe producto "{nombre_limpio}".'}), 409
             else:
               log.error(f"Error BD insertando producto '{nombre_limpio}': {e} (errno: {error_errno})", exc_info=True)
               return jsonify({'error': f'Error BD al agregar: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado POST /inventario/productos: {e}")
        return jsonify({'error': 'Error interno procesando solicitud'}), 500

@app.route('/inventario/productos/<path:nombre_producto>', methods=['DELETE'])
def eliminar_producto_inventario_bd(nombre_producto):
    log.info(f"Solicitud DELETE /inventario/productos/{nombre_producto} recibida.")
    if not nombre_producto: log.warning("DELETE sin nombre."); return jsonify({'error': 'Nombre producto requerido'}), 400
    from urllib.parse import unquote
    nombre_a_eliminar = unquote(nombre_producto).strip()
    if not nombre_a_eliminar: log.warning("DELETE nombre vacío."); return jsonify({'error': 'Nombre producto vacío'}), 400

    try:
        eliminado = eliminar_elemento('ProductosInventario', 'nombre', nombre_a_eliminar)
        if eliminado:
            log.info(f"Producto eliminado BD: '{nombre_a_eliminar}'")
            return jsonify({'mensaje': f'Producto "{nombre_a_eliminar}" eliminado.'}), 200
        else:
            log.warning(f"Intento eliminar producto no encontrado BD: '{nombre_a_eliminar}'")
            return jsonify({'error': f'Producto "{nombre_a_eliminar}" no encontrado.'}), 404
    except ErrorBaseDatos as e:
        log.error(f"Error BD eliminando producto '{nombre_a_eliminar}': {e}", exc_info=True)
        return jsonify({'error': f'Error BD al eliminar: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado eliminando producto '{nombre_a_eliminar}': {e}")
        return jsonify({'error': 'Error interno al eliminar producto'}), 500


# --- Endpoints EJ4: Banco ---
@app.route('/')
def indice_api():
    log.info("Solicitud GET / recibida.")
    return "API de Ejercicios Python - Hub HTML o endpoints (/inventario, /cuentas)"

@app.route('/cuentas/<int:id_cuenta>/verificar', methods=['GET'])
def verificar_cuenta_objeto(id_cuenta):
    log.info(f"Solicitud GET /cuentas/{id_cuenta}/verificar recibida.")
    try:
        cuenta_temporal = obtener_instancia_cuenta(id_cuenta)
        if cuenta_temporal is None: return jsonify({'error': f'Cuenta {id_cuenta} no encontrada'}), 404

        saldo = cuenta_temporal.consultar_saldo()
        titular = cuenta_temporal.consultar_titular()
        tipo = cuenta_temporal.__class__.__name__
        informacion = {
            'id_db': id_cuenta, 'tipo_objeto': tipo, 'titular': titular, 'saldo_actual': saldo,
        }
        if isinstance(cuenta_temporal, CuentaJoven):
             # *** CORRECCIÓN: Añadir assert para Pylance ***
             assert isinstance(cuenta_temporal, CuentaJoven)
             informacion['bonificacion'] = cuenta_temporal.get_bonificacion()
             informacion['edad'] = cuenta_temporal.get_edad()
             try:
                 # *** CORRECCIÓN: Añadir assert para Pylance ***
                 assert isinstance(cuenta_temporal, CuentaJoven)
                 informacion['es_valido'] = cuenta_temporal.TitularValido()
             except AttributeError:
                 log.warning(f"Método TitularValido no encontrado en CuentaJoven id={id_cuenta}")

        log.info(f"Verificación exitosa cuenta ID: {id_cuenta}")
        return jsonify(informacion), 200
    except (ErrorBaseDatos, ValueError, RuntimeError) as e:
        log.error(f"Error verificando cuenta {id_cuenta}: {e}", exc_info=True)
        status_code = 500 if isinstance(e, (ErrorBaseDatos, RuntimeError)) else 400
        if isinstance(e, ValueError):
            if "no encontrada" in str(e).lower(): status_code = 404
            elif "corruptos" in str(e).lower(): status_code = 500
        return jsonify({'error': f'Error procesando cuenta {id_cuenta}: {str(e)}'}), status_code
    except Exception as e:
        log.exception(f"Error inesperado verificando cuenta {id_cuenta}: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500

@app.route('/cuentas', methods=['POST'])
def crear_cuenta_objeto():
    log.info("Solicitud POST /cuentas recibida.")
    try:
        datos_iniciales = request.get_json()
        if not datos_iniciales or 'titular' not in datos_iniciales: log.warning("POST /cuentas incompleta."); return jsonify({'error': 'Falta titular'}), 400
        titular = datos_iniciales['titular']
        cantidad = datos_iniciales.get('cantidad', 0.00)
        if not isinstance(titular, str) or not titular.strip(): log.warning("Titular inválido."); return jsonify({'error': 'Titular inválido'}), 400
        try: cantidad_decimal = Decimal(str(cantidad)); assert cantidad_decimal >= 0
        except: log.warning(f"Cantidad inválida: {cantidad}"); return jsonify({'error': 'Cantidad inválida'}), 400

        tipo = 'Cuenta'
        estado_objeto = {'titular': titular, 'cantidad': float(cantidad_decimal) }
        datos_json_str = json.dumps(estado_objeto)
        datos_bd = {'tipo_cuenta': tipo, 'datos_objeto': datos_json_str }
        id_cuenta_bd = insertar_elemento('CuentasAlmacenadas', datos_bd)
        log.info(f"Creada entrada BD Cuenta ID: {id_cuenta_bd}")
        return jsonify({ 'mensaje': 'Entrada Cuenta creada.', 'id': id_cuenta_bd }), 201
    except ErrorBaseDatos as e:
        log.error(f"Error BD POST /cuentas: {e}", exc_info=True); return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except json.JSONDecodeError: log.error("JSON inválido POST /cuentas."); return jsonify({'error': 'JSON inválido'}), 400
    except Exception as e: log.exception(f"Error inesperado POST /cuentas: {e}"); return jsonify({'error': 'Error inesperado servidor'}), 500

@app.route('/cuentas/<int:id_cuenta>/gasto', methods=['POST'])
def realizar_gasto_objeto(id_cuenta):
    log.info(f"Solicitud POST /cuentas/{id_cuenta}/gasto recibida.")
    try:
        datos_gasto = request.get_json()
        if not datos_gasto or 'cantidad' not in datos_gasto: log.warning(f"POST gasto {id_cuenta} incompleto."); return jsonify({'error': 'Falta cantidad'}), 400
        try: cantidad_gasto = Decimal(str(datos_gasto['cantidad'])); assert cantidad_gasto > 0
        except: log.warning(f"Cantidad inválida gasto {id_cuenta}: {datos_gasto.get('cantidad')}"); return jsonify({'error': 'Cantidad debe ser número positivo'}), 400

        objeto_cuenta = obtener_instancia_cuenta(id_cuenta)
        if objeto_cuenta is None: return jsonify({'error': f'Cuenta {id_cuenta} no encontrada'}), 404

        cantidad_float_para_objeto = float(cantidad_gasto)
        saldo_antes_float = objeto_cuenta.consultar_saldo()

        try: objeto_cuenta.realizar_gasto(cantidad_float_para_objeto)
        except ValueError as e: log.warning(f"Gasto rechazado cuenta {id_cuenta}: {e}"); return jsonify({'error': f"Gasto no permitido: {e}"}), 400

        saldo_despues_float = objeto_cuenta.consultar_saldo()
        saldo_antes_decimal = Decimal(str(saldo_antes_float))
        saldo_despues_decimal = Decimal(str(saldo_despues_float))

        if saldo_antes_decimal == saldo_despues_decimal:
            if isinstance(objeto_cuenta, Cuenta) and not isinstance(objeto_cuenta, CuentaJoven) and cantidad_gasto > 0:
                log.warning(f"Gasto no realizado cuenta {id_cuenta} (saldo insuficiente). Saldo: {saldo_antes_float}")
                return jsonify({'error': 'Saldo insuficiente'}), 400
            else:
                log.info(f"Gasto procesado cuenta {id_cuenta}, saldo no cambió ({saldo_antes_float}).")
                return jsonify({'mensaje': 'Gasto procesado, saldo sin cambios.', 'id': id_cuenta, 'nuevo_saldo': saldo_despues_float }), 200

        log.info(f"Saldo cambiado cuenta {id_cuenta}: {saldo_antes_float} -> {saldo_despues_float}")
        estado_actualizado = {}
        if isinstance(objeto_cuenta, CuentaJoven):
             # *** CORRECCIÓN: Añadir assert para Pylance ***
             assert isinstance(objeto_cuenta, CuentaJoven)
             estado_actualizado = {
                 'titular': objeto_cuenta.consultar_titular(), 'cantidad': saldo_despues_float,
                 'bonificacion': objeto_cuenta.get_bonificacion(), 'edad': objeto_cuenta.get_edad()
             }
        elif isinstance(objeto_cuenta, Cuenta):
             estado_actualizado = {'titular': objeto_cuenta.consultar_titular(), 'cantidad': saldo_despues_float}
        else: log.error(f"Tipo objeto inesperado {objeto_cuenta.__class__.__name__} tras gasto ID {id_cuenta}"); raise TypeError("Tipo objeto inesperado.")

        datos_json_actualizado = json.dumps(estado_actualizado)
        datos_bd_actualizar = {'datos_objeto': datos_json_actualizado}
        actualizado = actualizar_elemento('CuentasAlmacenadas', 'id', id_cuenta, datos_bd_actualizar)

        if actualizado:
            log.info(f"Gasto {cantidad_gasto} guardado BD cuenta id={id_cuenta}. Nuevo saldo: {saldo_despues_float}")
            return jsonify({'mensaje': 'Gasto realizado y actualizado.', 'id': id_cuenta, 'nuevo_saldo': saldo_despues_float}), 200
        else:
            log.error(f"Gasto procesado id={id_cuenta}, pero falló actualización BD.")
            return jsonify({'error': 'Gasto procesado pero no se pudo guardar estado.'}), 500
    except (ErrorBaseDatos, ValueError, TypeError, RuntimeError) as e:
        log.error(f"Error procesando gasto cuenta {id_cuenta}: {e}", exc_info=True)
        status_code = 500
        if isinstance(e, (ErrorBaseDatos, RuntimeError, TypeError)): status_code = 500
        elif isinstance(e, ValueError): status_code = 400;
        if isinstance(e, ValueError) and "no encontrada" in str(e).lower(): status_code=404
        if isinstance(e, ValueError) and "corruptos" in str(e).lower(): status_code=500
        return jsonify({'error': f'Error procesando gasto: {str(e)}'}), status_code
    except Exception as e:
        log.exception(f"Error inesperado procesando gasto cuenta {id_cuenta}: {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500

@app.route('/Cuenta_joven', methods=['POST'])
def crear_cuenta_joven_objeto():
    log.info("Solicitud POST /Cuenta_joven recibida.")
    try:
        datos = request.get_json(); campos_req = ['titular', 'bonificacion', 'edad']
        if not datos or not all(k in datos for k in campos_req): log.warning("POST /Cuenta_joven incompleta."); return jsonify({'error': f'Faltan campos: {", ".join(k for k in campos_req if not datos or k not in datos)}'}), 400
        titular = datos['titular']; cantidad = datos.get('cantidad', 0.00); bonificacion = datos['bonificacion']; edad = datos['edad']
        if not isinstance(titular, str) or not titular.strip(): log.warning("Titular inválido."); return jsonify({'error': 'Titular inválido'}), 400
        try: cant_val = float(cantidad); assert cant_val >= 0
        except: log.warning("Cantidad inválida"); return jsonify({'error': 'Cantidad inválida'}), 400
        try: bonif_val = float(bonificacion); assert bonif_val >= 0
        except: log.warning("Bonificación inválida"); return jsonify({'error': 'Bonificación inválida'}), 400
        if not isinstance(edad, int) or edad <= 0: log.warning("Edad inválida"); return jsonify({'error': 'Edad inválida'}), 400

        tipo = 'CuentaJoven'; estado = {'titular': titular, 'cantidad': cant_val, 'bonificacion': bonif_val, 'edad': edad}
        datos_json = json.dumps(estado); datos_bd = {'tipo_cuenta': tipo, 'datos_objeto': datos_json}
        id_cuenta_bd = insertar_elemento('CuentasAlmacenadas', datos_bd)
        log.info(f"Creada entrada BD CuentaJoven ID: {id_cuenta_bd}")
        return jsonify({ 'mensaje': 'Entrada CuentaJoven creada.', 'id': id_cuenta_bd }), 201
    except ErrorBaseDatos as e: log.error(f"Error BD POST /Cuenta_joven: {e}", exc_info=True); return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except json.JSONDecodeError: log.error("JSON inválido POST /Cuenta_joven."); return jsonify({'error': 'JSON inválido'}), 400
    except Exception as e: log.exception(f"Error inesperado POST /Cuenta_joven: {e}"); return jsonify({'error': 'Error inesperado servidor'}), 500

@app.route('/apiregistro', methods=['POST'])
def api_registro_usuario():
    log.info("Solicitud POST /apiregistro recibida.")
    try:
        datos = request.get_json(); campos_req = ['dni_plain', 'contrasena_plain', 'id_cuenta']
        if not datos or not all(k in datos for k in campos_req): log.warning("POST /apiregistro incompleto."); return jsonify({'error': f'Faltan campos: {", ".join(k for k in campos_req if not datos or k not in datos)}'}), 400
        dni_plain = datos['dni_plain']; contrasena_plain = datos['contrasena_plain']; id_cuenta_str = datos['id_cuenta']
        if not isinstance(dni_plain, str) or not dni_plain.strip(): log.warning("DNI inválido."); return jsonify({'error': 'DNI inválido'}), 400
        if not isinstance(contrasena_plain, str) or not contrasena_plain: log.warning("Contraseña inválida."); return jsonify({'error': 'Contraseña inválida'}), 400
        try: id_cuenta = int(id_cuenta_str); assert id_cuenta > 0
        except: log.warning("ID cuenta inválido."); return jsonify({'error': 'ID cuenta inválido'}), 400

        cuenta = obtener_todos_los_elementos('CuentasAlmacenadas', filtro={'id': id_cuenta}, limite=1)
        if not cuenta: log.warning(f"Registro con ID cuenta inexistente: {id_cuenta}"); return jsonify({'error': f'Cuenta {id_cuenta} no encontrada'}), 404

        try: dni_has = hashlib.sha256(dni_plain.encode('utf-8')).hexdigest(); contra_has = hashlib.sha256(contrasena_plain.encode('utf-8')).hexdigest()
        except Exception as e: log.error(f"Error hasheando credenciales: {e}", exc_info=True); return jsonify({'error': 'Error interno procesando credenciales'}), 500

        datos_bd = {'dni_usuario': dni_has, 'contraseña': contra_has, 'fk_id_cuenta': id_cuenta}
        try:
            insertar_elemento('Usuarios', datos_bd)
        except ErrorBaseDatos as e:
             # *** CORRECCIÓN: Usar getattr para errno ***
             error_errno = getattr(e, 'errno', None)
             if error_errno == 1062:
                 log.warning(f"Intento registro DNI duplicado (hash): {dni_has}. Errno: {error_errno}")
                 return jsonify({'error': 'Ya existe usuario con este DNI'}), 409
             else:
               log.error(f"Error BD registrando usuario (DNI hash {dni_has}): {e} (errno: {error_errno})", exc_info=True)
               return jsonify({'error': f'Error BD al registrar: {str(e)}'}), 500

        log.info(f"Usuario registrado (hash DNI: {dni_has}), vinculado cuenta ID: {id_cuenta}")
        return jsonify({ 'mensaje': 'Usuario registrado y vinculado.', 'id_cuenta': id_cuenta }), 201
    except ErrorBaseDatos as e: log.error(f"Error BD general /apiregistro: {e}", exc_info=True); return jsonify({'error': f'Error BD general: {str(e)}'}), 500
    except json.JSONDecodeError: log.error("JSON inválido /apiregistro."); return jsonify({'error': 'JSON inválido'}), 400
    except Exception as e: log.exception(f"Error inesperado /apiregistro: {e}"); return jsonify({'error': 'Error interno inesperado'}), 500


# --- Ejecución de la App ---
if __name__ == '__main__':
    is_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    log.info(f"Iniciando servidor Flask en {host}:{port} (Debug: {is_debug})")
    app.run(debug=is_debug, host=host, port=port)