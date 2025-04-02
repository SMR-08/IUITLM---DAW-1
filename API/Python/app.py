# file: app.py
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import os
import hashlib
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Union
from urllib.parse import unquote

# --- Importaciones de Lógica de Negocio ---
# EJ04: Clases del Banco
try:
    from ejercicios_python.EJ04.EJ4 import Cuenta, CuentaJoven
    logging.info("Módulos EJ04 (Cuenta, CuentaJoven) importados correctamente.")
except ImportError as e:
    logging.error(f"Error CRÍTICO importando módulos de EJ04: {e}. La funcionalidad del banco NO estará disponible.")
    # Definir stubs si fuera estrictamente necesario para que el linter no falle,
    # aunque es mejor que falle si no se pueden importar.
    class Cuenta: pass
    class CuentaJoven(Cuenta): pass

# --- Importación de Base de Datos ---
try:
    from db import (
        obtener_todos_los_elementos,
        insertar_elemento,
        actualizar_elemento,
        eliminar_elemento,
        ErrorBaseDatos # Importar la excepción real
    )
    logging.info("Módulo db.py importado correctamente.")
except ImportError:
    logging.error("Error CRÍTICO importando 'db.py'. Las operaciones de base de datos fallarán.")
    # Define stubs para que el resto del código no falle en el análisis estático
    class ErrorBaseDatos(Exception): pass
    def obtener_todos_los_elementos(*args: Any, **kwargs: Any) -> List[Dict[str, Any]]: raise ImportError("Módulo DB no cargado")
    def insertar_elemento(*args: Any, **kwargs: Any) -> Union[int, None]: raise ImportError("Módulo DB no cargado")
    def actualizar_elemento(*args: Any, **kwargs: Any) -> bool: raise ImportError("Módulo DB no cargado")
    def eliminar_elemento(*args: Any, **kwargs: Any) -> bool: raise ImportError("Módulo DB no cargado")



# --- Inicialización de Flask y CORS ---
app = Flask(__name__)
CORS(app)

# --- Configuración del Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
log = logging.getLogger(__name__)

# --- Nombres de Bases de Datos desde Variables de Entorno ---
# Usamos valores por defecto por si no están definidas, aunque deberían estarlo por docker-compose
DB_HOST = os.environ.get("DB_HOST") # Requerido

BANCO_DB_CONFIG = {
    "host": DB_HOST,
    "name": os.environ.get("DB_BANCO_NAME"),
    "user": os.environ.get("DB_BANCO_USER"),
    "pass": os.environ.get("DB_BANCO_PASSWORD")
}

INVENTARIO_DB_CONFIG = {
    "host": DB_HOST,
    "name": os.environ.get("DB_INVENTARIO_NAME"),
    "user": os.environ.get("DB_INVENTARIO_USER"),
    "pass": os.environ.get("DB_INVENTARIO_PASSWORD")
}
# Validar que las configuraciones esenciales están presentes
if not all(BANCO_DB_CONFIG.values()) or not all(INVENTARIO_DB_CONFIG.values()) or not DB_HOST:
    log.critical("¡Faltan variables de entorno críticas para la configuración de la base de datos!")
    # Podrías lanzar una excepción aquí para evitar que la app inicie incorrectamente
    # raise EnvironmentError("Faltan variables de entorno de BD")
    # O simplemente loguearlo y esperar fallos posteriores
    log.warning(f"Banco Config Check: {BANCO_DB_CONFIG}")
    log.warning(f"Inventario Config Check: {INVENTARIO_DB_CONFIG}")


log.info(f"Configuración BD Banco: Host={BANCO_DB_CONFIG['host']}, DB={BANCO_DB_CONFIG['name']}, User={BANCO_DB_CONFIG['user']}")
log.info(f"Configuración BD Inventario: Host={INVENTARIO_DB_CONFIG['host']}, DB={INVENTARIO_DB_CONFIG['name']}, User={INVENTARIO_DB_CONFIG['user']}")

# --- Funciones Auxiliares ---
def obtener_instancia_cuenta(id_cuenta: int) -> Union[Cuenta, CuentaJoven, None]:
    log.debug(f"Intentando obtener instancia para cuenta ID: {id_cuenta}")
    try:
        # Pasar el diccionario de configuración completo
        resultados = obtener_todos_los_elementos(
            'CuentasAlmacenadas',
            db_config=BANCO_DB_CONFIG,
            filtro={'id': id_cuenta},
            limite=1
        )
        if not resultados: return None
        datos_bd = resultados[0]
        tipo_cuenta = datos_bd.get('tipo_cuenta')
        datos_objeto_str = datos_bd.get('datos_objeto')
        
        if tipo_cuenta == 'Cuenta': return Cuenta(**json.loads(datos_objeto_str))
        if tipo_cuenta == 'CuentaJoven': return CuentaJoven(**json.loads(datos_objeto_str))
        raise ValueError(f"Tipo cuenta no soportado: {tipo_cuenta}")
    except (ErrorBaseDatos, ValueError, RuntimeError, json.JSONDecodeError, NameError) as e:
         # Loguear y relanzar o manejar como antes
        log.error(f"Error obteniendo/instanciando cuenta {id_cuenta} ({BANCO_DB_CONFIG['name']}): {e}", exc_info=True)
        # Relanzar para que el endpoint lo maneje
        raise
    except Exception as e:
        log.exception(f"Error inesperado obteniendo instancia cuenta {id_cuenta} ({BANCO_DB_CONFIG['name']}): {e}")
        raise RuntimeError(f"Error interno inesperado obteniendo cuenta: {e}")


# --- Endpoints EJ1: Inventario (Base de Datos) ---
@app.route('/inventario', methods=['GET'])
def obtener_inventario_bd():
    log.info(f"GET /inventario (DB: {INVENTARIO_DB_CONFIG['name']})")
    try:
        productos_bd = obtener_todos_los_elementos(
            'ProductosInventario',
            db_config=INVENTARIO_DB_CONFIG, 
            orden=[('nombre', 'ASC')]
        )
        # ... (resto de la lógica igual) ...
        # (Cálculo de valor_total y formateo de productos_respuesta)
        valor_total = sum(Decimal(str(p.get('precio', 0))) * Decimal(p.get('cantidad', 0)) for p in productos_bd)
        productos_respuesta = [
            {'id': p.get('id'), 'nombre': p.get('nombre'), 'precio': str(p.get('precio', '0.00')), 'cantidad': p.get('cantidad', 0)}
            for p in productos_bd
        ]
        return jsonify({'productos': productos_respuesta, 'valor_total': str(valor_total), 'mensaje': 'Inventario OK'}), 200
    except ErrorBaseDatos as e:
        log.error(f"Error BD ({INVENTARIO_DB_CONFIG['name']}) en GET /inventario: {e}", exc_info=True)
        return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado GET /inventario ({INVENTARIO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno'}), 500

@app.route('/inventario/productos', methods=['POST'])
def agregar_producto_inventario_bd():
    log.info(f"POST /inventario/productos (DB: {INVENTARIO_DB_CONFIG['name']})")
    # ... (Validación de datos igual) ...
    try:
        datos = request.get_json()
        # (Validaciones de nombre, precio, cantidad)
        nombre = datos['nombre'].strip(); assert nombre
        precio = Decimal(str(datos['precio'])); assert precio >= 0
        cantidad = int(datos['cantidad']); assert cantidad >= 0
    except Exception as verr:
        log.warning(f"Datos inválidos POST /inventario/productos: {verr}")
        return jsonify({'error': f'Datos inválidos: {verr}'}), 400

    datos_producto_bd = {'nombre': nombre, 'precio': precio, 'cantidad': cantidad}
    try:
        id_nuevo = insertar_elemento(
            'ProductosInventario',
            datos_producto_bd,
            db_config=INVENTARIO_DB_CONFIG 
        )
        return jsonify({'mensaje': 'Producto agregado.', 'producto': {'id': id_nuevo, **datos_producto_bd, 'precio': str(precio)}}), 201
    except ErrorBaseDatos as e:
         if e.errno == 1062: # Duplicado
            return jsonify({'error': f'Producto "{nombre}" ya existe.'}), 409
         else:
            log.error(f"Error BD ({INVENTARIO_DB_CONFIG['name']}) insertando producto: {e}", exc_info=True)
            return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado POST /inventario/productos ({INVENTARIO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno'}), 500

@app.route('/inventario/productos/<path:nombre_producto>', methods=['DELETE'])
def eliminar_producto_inventario_bd(nombre_producto):
    nombre_a_eliminar = unquote(nombre_producto).strip()
    log.info(f"DELETE /inventario/productos/{nombre_a_eliminar} (DB: {INVENTARIO_DB_CONFIG['name']})")
    if not nombre_a_eliminar: return jsonify({'error': 'Nombre producto requerido'}), 400
    try:
        eliminado = eliminar_elemento(
            'ProductosInventario',
            'nombre',
            nombre_a_eliminar,
            db_config=INVENTARIO_DB_CONFIG 
        )
        if eliminado: return jsonify({'mensaje': f'Producto "{nombre_a_eliminar}" eliminado.'}), 200
        else: return jsonify({'error': f'Producto "{nombre_a_eliminar}" no encontrado.'}), 404
    except ErrorBaseDatos as e:
        log.error(f"Error BD ({INVENTARIO_DB_CONFIG['name']}) eliminando producto: {e}", exc_info=True)
        return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado DELETE /inventario/productos ({INVENTARIO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno'}), 500

@app.route('/')
def indice_api():
    log.info("Solicitud GET / recibida.")
    # Podrías añadir info de las BDs aquí si quieres
    return f"API de Ejercicios Python - DB Banco: {DB_NAME_BANCO}, DB Inventario: {DB_NAME_INVENTARIO}"

@app.route('/cuentas/<int:id_cuenta>/verificar', methods=['GET'])
def verificar_cuenta_objeto(id_cuenta):
    log.info(f"GET /cuentas/{id_cuenta}/verificar (DB: {BANCO_DB_CONFIG['name']})")
    try:
        cuenta_temporal = obtener_instancia_cuenta(id_cuenta) # Usa BANCO_DB_CONFIG internamente
        if cuenta_temporal is None: return jsonify({'error': f'Cuenta {id_cuenta} no encontrada'}), 404
        # ... (lógica para extraer info de cuenta_temporal igual) ...
        info = { 'id_db': id_cuenta, 'tipo': type(cuenta_temporal).__name__, 'titular': cuenta_temporal.consultar_titular(), 'saldo': cuenta_temporal.consultar_saldo() }
        # Añadir campos específicos si es CuentaJoven...
        return jsonify(info), 200
    except (ErrorBaseDatos, ValueError, RuntimeError) as e:
        status = 404 if isinstance(e, ValueError) and "no encontrada" in str(e).lower() else 500 if isinstance(e, (ErrorBaseDatos, RuntimeError)) else 400
        log.error(f"Error verificando cuenta {id_cuenta} ({BANCO_DB_CONFIG['name']}): {e}", exc_info=(status==500))
        return jsonify({'error': f'Error procesando cuenta {id_cuenta}: {str(e)}'}), status
    except Exception as e:
        log.exception(f"Error inesperado verificando cuenta {id_cuenta} ({BANCO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500

@app.route('/cuentas', methods=['POST'])
def crear_cuenta_objeto():
    log.info(f"POST /cuentas (DB: {BANCO_DB_CONFIG['name']})")
    # ... (Validación de datos igual) ...
    try:
        datos_iniciales = request.get_json(); assert datos_iniciales and 'titular' in datos_iniciales
        titular = datos_iniciales['titular'].strip(); assert titular
        cantidad = float(datos_iniciales.get('cantidad', 0.0)); assert cantidad >= 0
    except Exception as verr:
         log.warning(f"Datos inválidos POST /cuentas: {verr}")
         return jsonify({'error': f'Datos inválidos: {verr}'}), 400

    tipo = 'Cuenta'; estado_objeto = {'titular': titular, 'cantidad': cantidad }
    datos_json_str = json.dumps(estado_objeto)
    datos_bd = {'tipo_cuenta': tipo, 'datos_objeto': datos_json_str }
    try:
        id_cuenta_bd = insertar_elemento(
            'CuentasAlmacenadas',
            datos_bd,
            db_config=BANCO_DB_CONFIG 
        )
        return jsonify({'mensaje': 'Cuenta creada.', 'id': id_cuenta_bd}), 201
    except ErrorBaseDatos as e:
        log.error(f"Error BD ({BANCO_DB_CONFIG['name']}) POST /cuentas: {e}", exc_info=True)
        return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado POST /cuentas ({BANCO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno'}), 500

@app.route('/cuentas/<int:id_cuenta>/gasto', methods=['POST'])
def realizar_gasto_objeto(id_cuenta):
    log.info(f"POST /cuentas/{id_cuenta}/gasto (DB: {BANCO_DB_CONFIG['name']})")
    # ... (Validación datos gasto igual) ...
    try:
        datos_gasto = request.get_json(); assert datos_gasto and 'cantidad' in datos_gasto
        cantidad_gasto = Decimal(str(datos_gasto['cantidad'])); assert cantidad_gasto > 0
    except Exception as verr:
        log.warning(f"Datos inválidos POST /cuentas/{id_cuenta}/gasto: {verr}")
        return jsonify({'error': f'Datos inválidos: {verr}'}), 400

    try:
        objeto_cuenta = obtener_instancia_cuenta(id_cuenta) # Usa BANCO_DB_CONFIG
        if objeto_cuenta is None: return jsonify({'error': f'Cuenta {id_cuenta} no encontrada'}), 404

        saldo_antes = objeto_cuenta.consultar_saldo()
        objeto_cuenta.realizar_gasto(float(cantidad_gasto)) # Lógica de negocio
        saldo_despues = objeto_cuenta.consultar_saldo()

        # Solo actualizar si el saldo cambió
        if abs(Decimal(str(saldo_antes)) - Decimal(str(saldo_despues))) > Decimal('0.001'):
            log.info(f"Actualizando estado cuenta {id_cuenta} en BD ({BANCO_DB_CONFIG['name']})")
            # ... (Obtener estado_actualizado del objeto igual que antes)
            estado_actualizado = { 'titular': objeto_cuenta.consultar_titular(), 'cantidad': saldo_despues }
            if isinstance(objeto_cuenta, CuentaJoven):
                estado_actualizado['bonificacion'] = objeto_cuenta.get_bonificacion()
                estado_actualizado['edad'] = objeto_cuenta.get_edad()
            # ...
            datos_json_actualizado = json.dumps(estado_actualizado)
            actualizado = actualizar_elemento(
                'CuentasAlmacenadas', 'id', id_cuenta,
                {'datos_objeto': datos_json_actualizado},
                db_config=BANCO_DB_CONFIG 
            )
            if not actualizado:
                log.error(f"Gasto procesado id={id_cuenta}, pero falló actualización BD ({BANCO_DB_CONFIG['name']}).")
                # Considera qué hacer aquí. ¿Devolver error? ¿Advertir?
                return jsonify({'error': 'Gasto procesado pero no se pudo guardar estado.', 'nuevo_saldo': saldo_despues}), 500 # Error servidor
        else:
            log.info(f"Gasto procesado cuenta {id_cuenta}, saldo sin cambios. No se actualiza BD.")

        return jsonify({'mensaje': 'Gasto procesado.', 'id': id_cuenta, 'nuevo_saldo': saldo_despues}), 200

    except (ErrorBaseDatos, ValueError, TypeError, RuntimeError) as e:
        # Manejo de errores similar a verificar_cuenta_objeto
        status = 404 if isinstance(e, ValueError) and "no encontrada" in str(e).lower() else 500 if isinstance(e, (ErrorBaseDatos, RuntimeError, TypeError)) else 400
        log.error(f"Error procesando gasto cuenta {id_cuenta} ({BANCO_DB_CONFIG['name']}): {e}", exc_info=(status==500))
        return jsonify({'error': f'Error procesando gasto: {str(e)}'}), status
    except Exception as e:
        log.exception(f"Error inesperado procesando gasto cuenta {id_cuenta} ({BANCO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno inesperado'}), 500


@app.route('/Cuenta_joven', methods=['POST'])
def crear_cuenta_joven_objeto():
    log.info(f"POST /Cuenta_joven (DB: {BANCO_DB_CONFIG['name']})")
    # ... (Validación datos igual) ...
    try:
         datos = request.get_json(); # Validar campos requeridos...
         titular=datos['titular']; cantidad=float(datos.get('cantidad',0)); bonif=float(datos['bonificacion']); edad=int(datos['edad'])
         # Validar tipos/rangos...
    except Exception as verr:
         log.warning(f"Datos inválidos POST /Cuenta_joven: {verr}")
         return jsonify({'error': f'Datos inválidos: {verr}'}), 400

    tipo = 'CuentaJoven'; estado = {'titular': titular, 'cantidad': cantidad, 'bonificacion': bonif, 'edad': edad}
    datos_json = json.dumps(estado); datos_bd = {'tipo_cuenta': tipo, 'datos_objeto': datos_json}
    try:
        id_cuenta_bd = insertar_elemento(
            'CuentasAlmacenadas',
            datos_bd,
            db_config=BANCO_DB_CONFIG 
        )
        return jsonify({'mensaje': 'CuentaJoven creada.', 'id': id_cuenta_bd}), 201
    except ErrorBaseDatos as e:
        log.error(f"Error BD ({BANCO_DB_CONFIG['name']}) POST /Cuenta_joven: {e}", exc_info=True)
        return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado POST /Cuenta_joven ({BANCO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno'}), 500


@app.route('/apiregistro', methods=['POST'])
def api_registro_usuario():
    log.info(f"POST /apiregistro (DB: {BANCO_DB_CONFIG['name']})")
    # ... (Validación datos igual) ...
    try:
        datos=request.get_json(); # Validar campos...
        dni_plain=datos['dni_plain']; contrasena_plain=datos['contrasena_plain']; id_cuenta=int(datos['id_cuenta'])
        # Validar tipos/rangos...
    except Exception as verr:
         log.warning(f"Datos inválidos POST /apiregistro: {verr}")
         return jsonify({'error': f'Datos inválidos: {verr}'}), 400

    try:
        # 1. Verificar cuenta existe (usa BANCO_DB_CONFIG)
        cuenta = obtener_todos_los_elementos(
            'CuentasAlmacenadas',
            db_config=BANCO_DB_CONFIG, 
            filtro={'id': id_cuenta}, limite=1
        )
        if not cuenta: return jsonify({'error': f'Cuenta {id_cuenta} no encontrada'}), 404

        # 2. Hashear credenciales (igual)
        dni_has = hashlib.sha256(dni_plain.encode()).hexdigest()
        contra_has = hashlib.sha256(contrasena_plain.encode()).hexdigest()

        # 3. Insertar usuario (usa BANCO_DB_CONFIG)
        datos_bd = {'dni_usuario': dni_has, 'contraseña': contra_has, 'fk_id_cuenta': id_cuenta}
        insertar_elemento(
            'Usuarios',
            datos_bd,
            db_config=BANCO_DB_CONFIG 
        )
        return jsonify({'mensaje': 'Usuario registrado y vinculado.'}), 201

    except ErrorBaseDatos as e:
        if e.errno == 1062: # Duplicado DNI
            return jsonify({'error': 'Ya existe usuario con este DNI'}), 409
        elif e.errno == 1452: # FK constraint (cuenta no existe - aunque ya la chequeamos)
             return jsonify({'error': f'Error FK: Cuenta {id_cuenta} no válida.'}), 400
        else:
            log.error(f"Error BD ({BANCO_DB_CONFIG['name']}) /apiregistro: {e}", exc_info=True)
            return jsonify({'error': f'Error BD: {str(e)}'}), 500
    except Exception as e:
        log.exception(f"Error inesperado /apiregistro ({BANCO_DB_CONFIG['name']}): {e}")
        return jsonify({'error': 'Error interno'}), 500


# --- Ejecución App (igual) ---
if __name__ == '__main__':
    # ... (código de inicio igual) ...
    # Comprobación crítica de variables de entorno antes de correr
    if not all(BANCO_DB_CONFIG.values()) or not all(INVENTARIO_DB_CONFIG.values()) or not DB_HOST:
         log.critical("La aplicación no puede iniciar debido a variables de entorno de BD faltantes.")
         exit(1) # Salir si falta configuración esencial

    is_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("API_PORT_HOST", 5000)) # Usar var de .env si existe
    host = os.environ.get("HOST", "0.0.0.0")
    log.info(f"Iniciando servidor Flask en {host}:{port} (Debug: {is_debug})")
    app.run(debug=is_debug, host=host, port=port)