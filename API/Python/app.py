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
# EJ03: Clases de animales
try:
    # Asumiendo que EJ3.py está en la ruta correcta
    from ejercicios_python.EJ03.EJ3 import Animal, Perro, Gato
    logging.info("Módulos EJ3 (Animal, Perro, Gato) importados correctamente.") # Log va aquí
    EJ3_AVAILABLE = True
except ImportError as e:
    log = logging.getLogger(__name__) # Asegúrate que log existe si la importación falla pronto
    log.error(f"Error importando módulos de EJ3: {e}. La funcionalidad de animales NO estará disponible.")
    class Animal: pass
    class Perro(Animal): pass
    class Gato(Animal): pass
    EJ3_AVAILABLE = False

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
    "host": DB_HOST, "name": os.environ.get("DB_BANCO_NAME"),
    "user": os.environ.get("DB_BANCO_USER"), "pass": os.environ.get("DB_BANCO_PASSWORD")
}
INVENTARIO_DB_CONFIG = {
    "host": DB_HOST, "name": os.environ.get("DB_INVENTARIO_NAME"),
    "user": os.environ.get("DB_INVENTARIO_USER"), "pass": os.environ.get("DB_INVENTARIO_PASSWORD")
}
COCHES_DB_CONFIG = {
    "host": DB_HOST, "name": os.environ.get("DB_COCHES_NAME"),
    "user": os.environ.get("DB_COCHES_USER"), "pass": os.environ.get("DB_COCHES_PASSWORD")
}

# Validar que las configuraciones esenciales están presentes
# Validación y Logging de Configuración (Sin cambios visuales, pero la comprobación crítica está al final)
log.info(f"Configuración BD Banco: Host={BANCO_DB_CONFIG.get('host')}, DB={BANCO_DB_CONFIG.get('name')}, User={BANCO_DB_CONFIG.get('user')}")
log.info(f"Configuración BD Inventario: Host={INVENTARIO_DB_CONFIG.get('host')}, DB={INVENTARIO_DB_CONFIG.get('name')}, User={INVENTARIO_DB_CONFIG.get('user')}")
log.info(f"Configuración BD Coches: Host={COCHES_DB_CONFIG.get('host')}, DB={COCHES_DB_CONFIG.get('name')}, User={COCHES_DB_CONFIG.get('user')}")

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
    """Obtiene todos los productos del inventario y calcula el valor total."""
    db_name = INVENTARIO_DB_CONFIG.get('name', 'InventarioDB_Desconocido')
    log.info(f"GET /inventario (DB: {db_name})")
    try:
        # 1. Obtener datos de la BD
        productos_bd = obtener_todos_los_elementos(
            'ProductosInventario',
            db_config=INVENTARIO_DB_CONFIG,
            orden=[('nombre', 'ASC')]
        )

        # 2. Procesar datos (calcular total, formatear)
        valor_total = Decimal('0.00')
        productos_respuesta = []
        for p in productos_bd:
            try:
                # Validar y convertir precio y cantidad robustamente
                precio_decimal = Decimal(str(p.get('precio', '0.00')))
                cantidad_int = int(p.get('cantidad', 0))
                if cantidad_int < 0: # Corregir cantidad negativa
                    log.warning(f"Cantidad negativa '{p.get('cantidad')}' en producto ID {p.get('id')} ({db_name}), usando 0.")
                    cantidad_int = 0
                if precio_decimal < Decimal('0.00'): # Corregir precio negativo
                     log.warning(f"Precio negativo '{p.get('precio')}' en producto ID {p.get('id')} ({db_name}), usando 0.00.")
                     precio_decimal = Decimal('0.00')

                valor_total += precio_decimal * Decimal(cantidad_int)
                productos_respuesta.append({
                    'id': p.get('id'),
                    'nombre': p.get('nombre', 'Nombre Desconocido'), # Valor por defecto
                    'precio': str(precio_decimal), # Mantener como string para frontend
                    'cantidad': cantidad_int
                })
            except (InvalidOperation, ValueError, TypeError) as proc_err:
                 # Si un producto individual falla al procesar, loguear y continuar
                 log.error(f"Error procesando producto ID {p.get('id')} ({db_name}): {proc_err}", exc_info=True)
                 # Podrías añadir un producto 'inválido' a la respuesta o simplemente saltarlo
                 continue # Saltar este producto

        # 3. Devolver respuesta exitosa
        return jsonify({
            'productos': productos_respuesta,
            'valor_total': float(valor_total), # Enviar como número JSON
            'mensaje': f'Inventario obtenido de {db_name} correctamente.'
        }), 200

    except ErrorBaseDatos as e_db:
        log.error(f"Error BD ({db_name}) en GET /inventario: {e_db}", exc_info=True)
        return jsonify({'error': f'Error de base de datos al obtener inventario: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado en GET /inventario ({db_name}): {e_gen}")
        return jsonify({'error': 'Error interno inesperado al procesar la solicitud.'}), 500


@app.route('/inventario/productos', methods=['POST'])
def agregar_producto_inventario_bd():
    """Agrega un nuevo producto al inventario."""
    db_name = INVENTARIO_DB_CONFIG.get('name', 'InventarioDB_Desconocido')
    log.info(f"POST /inventario/productos (DB: {db_name})")

    # 1. Validación de Entrada
    try:
        datos = request.get_json()
        if not datos:
            raise ValueError("No se recibieron datos JSON.")

        nombre = datos.get('nombre', '').strip()
        precio_str = str(datos.get('precio', '')) # Obtener como string primero
        cantidad_str = str(datos.get('cantidad', '')) # Obtener como string primero

        if not nombre:
            raise ValueError("El nombre del producto es requerido.")

        # Validar precio (Decimal >= 0)
        try:
            precio = Decimal(precio_str)
            if precio < Decimal('0.00'):
                raise ValueError("El precio no puede ser negativo.")
        except InvalidOperation:
             raise ValueError("El precio debe ser un número válido.")

        # Validar cantidad (entero >= 0)
        try:
            cantidad = int(cantidad_str)
            if cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa.")
        except ValueError:
             raise ValueError("La cantidad debe ser un número entero.")

    except (ValueError, KeyError, TypeError) as verr: # Captura errores de JSON o validación
        log.warning(f"Datos inválidos en POST /inventario/productos ({db_name}): {verr}")
        return jsonify({'error': f'Datos inválidos: {str(verr)}'}), 400
    except Exception as e_val: # Otra excepción inesperada durante validación
        log.exception(f"Error inesperado validando datos en POST /inventario/productos ({db_name}): {e_val}")
        return jsonify({'error': 'Error interno procesando la entrada.'}), 500

    # 2. Interacción con la BD
    datos_producto_bd = {'nombre': nombre, 'precio': precio, 'cantidad': cantidad}
    try:
        id_nuevo = insertar_elemento(
            'ProductosInventario',
            datos_producto_bd,
            db_config=INVENTARIO_DB_CONFIG
        )
        log.info(f"Producto agregado a {db_name}: ID={id_nuevo}, Nombre='{nombre}'")

        # 3. Respuesta Exitosa
        producto_creado = {'id': id_nuevo, **datos_producto_bd, 'precio': str(precio)}
        return jsonify({
            'mensaje': f'Producto "{nombre}" agregado correctamente a {db_name}.',
            'producto': producto_creado
        }), 201 # 201 Created

    except ErrorBaseDatos as e_db:
         if hasattr(e_db, 'errno') and e_db.errno == 1062: # Error de duplicado (UNIQUE constraint en 'nombre')
            log.warning(f"Intento de agregar producto duplicado '{nombre}' en {db_name}.")
            return jsonify({'error': f'El producto "{nombre}" ya existe en el inventario.'}), 409 # 409 Conflict
         else:
            log.error(f"Error BD ({db_name}) insertando producto '{nombre}': {e_db}", exc_info=True)
            return jsonify({'error': f'Error de base de datos al agregar el producto: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado agregando producto '{nombre}' a {db_name}: {e_gen}")
        return jsonify({'error': 'Error interno inesperado al guardar el producto.'}), 500


@app.route('/inventario/productos/<path:nombre_producto>', methods=['DELETE'])
def eliminar_producto_inventario_bd(nombre_producto):
    """Elimina un producto del inventario por su nombre."""
    db_name = INVENTARIO_DB_CONFIG.get('name', 'InventarioDB_Desconocido')
    # 1. Validación de Entrada (Parámetro de Ruta)
    try:
        # Decodificar %20, etc. y quitar espacios extra
        nombre_a_eliminar = unquote(nombre_producto).strip()
        if not nombre_a_eliminar:
            raise ValueError("El nombre del producto a eliminar no puede estar vacío.")
    except ValueError as verr:
         log.warning(f"Nombre inválido en DELETE /inventario/productos/{nombre_producto} ({db_name}): {verr}")
         return jsonify({'error': str(verr)}), 400

    log.info(f"DELETE /inventario/productos/'{nombre_a_eliminar}' (DB: {db_name})")

    # 2. Interacción con la BD
    try:
        eliminado = eliminar_elemento(
            'ProductosInventario',
            'nombre', # Columna para identificar
            nombre_a_eliminar, # Valor a buscar
            db_config=INVENTARIO_DB_CONFIG
        )

        # 3. Respuesta según resultado
        if eliminado:
            log.info(f"Producto '{nombre_a_eliminar}' eliminado de {db_name}.")
            # Devolver 200 con mensaje o 204 sin contenido
            return jsonify({'mensaje': f'Producto "{nombre_a_eliminar}" eliminado correctamente de {db_name}.'}), 200
        else:
            log.warning(f"Intento de eliminar producto no encontrado '{nombre_a_eliminar}' en {db_name}.")
            return jsonify({'error': f'Producto "{nombre_a_eliminar}" no encontrado en el inventario.'}), 404 # 404 Not Found

    except ErrorBaseDatos as e_db:
        log.error(f"Error BD ({db_name}) eliminando producto '{nombre_a_eliminar}': {e_db}", exc_info=True)
        return jsonify({'error': f'Error de base de datos al eliminar el producto: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado eliminando producto '{nombre_a_eliminar}' de {db_name}: {e_gen}")
        return jsonify({'error': 'Error interno inesperado al eliminar el producto.'}), 500

# --- Endpoints EJ2: Coches (Base de Datos)

@app.route('/coches', methods=['GET'])
def obtener_coches():
    """Obtiene todos los coches de la base de datos."""
    db_name = COCHES_DB_CONFIG.get('name', 'CochesDB_Desconocido')
    log.info(f"GET /coches (DB: {db_name})")
    try:
        # 1. Obtener datos de la BD
        coches_bd = obtener_todos_los_elementos(
            'Vehiculos',
            db_config=COCHES_DB_CONFIG,
            orden=[('marca', 'ASC'), ('modelo', 'ASC'), ('año', 'DESC')] # Orden más completo
        )

        # 2. Procesar datos (en este caso, ninguno necesario, la BD ya tiene la estructura)

        # 3. Devolver respuesta exitosa
        return jsonify({
            'coches': coches_bd,
            'mensaje': f'Lista de coches obtenida de {db_name} correctamente.'
        }), 200

    except ErrorBaseDatos as e_db:
        log.error(f"Error BD ({db_name}) en GET /coches: {e_db}", exc_info=True)
        return jsonify({'error': f'Error de base de datos al obtener los coches: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado en GET /coches ({db_name}): {e_gen}")
        return jsonify({'error': 'Error interno inesperado al obtener los coches.'}), 500


@app.route('/coches', methods=['POST'])
def agregar_coche():
    """Agrega un nuevo coche a la base de datos."""
    db_name = COCHES_DB_CONFIG.get('name', 'CochesDB_Desconocido')
    log.info(f"POST /coches (DB: {db_name})")

    # 1. Validación de Entrada
    try:
        datos = request.get_json()
        if not datos:
            raise ValueError("No se recibieron datos JSON.")

        marca = datos.get('marca', '').strip()
        modelo = datos.get('modelo', '').strip()
        año_str = str(datos.get('año', '')) # Obtener como string primero

        if not marca or not modelo:
            raise ValueError("La marca y el modelo del coche son requeridos.")

        # Validar año (entero razonable)
        try:
            año = int(año_str)
            # Ajusta el rango si es necesario, 1886 es el año del primer coche Benz Patent-Motorwagen
            if not (1886 <= año <= 2100):
                raise ValueError("El año debe ser un valor razonable (ej: entre 1886 y 2100).")
        except ValueError:
             raise ValueError("El año debe ser un número entero válido.")

    except (ValueError, KeyError, TypeError) as verr:
        log.warning(f"Datos inválidos en POST /coches ({db_name}): {verr}")
        return jsonify({'error': f'Datos inválidos: {str(verr)}'}), 400
    except Exception as e_val:
        log.exception(f"Error inesperado validando datos en POST /coches ({db_name}): {e_val}")
        return jsonify({'error': 'Error interno procesando la entrada.'}), 500

    # 2. Interacción con la BD
    datos_coche_bd = {'marca': marca, 'modelo': modelo, 'año': año}
    try:
        id_nuevo_coche = insertar_elemento(
            'Vehiculos',
            datos_coche_bd,
            db_config=COCHES_DB_CONFIG
        )
        log.info(f"Coche agregado a {db_name}: ID={id_nuevo_coche}, {marca} {modelo} ({año})")

        # 3. Respuesta Exitosa
        coche_creado = {'id': id_nuevo_coche, **datos_coche_bd}
        return jsonify({
            'mensaje': f'Coche "{marca} {modelo}" agregado correctamente a {db_name}.',
            'coche': coche_creado
            }), 201 # 201 Created

    except ErrorBaseDatos as e_db:
        # Aquí no esperamos duplicados por defecto, pero podrías añadir UNIQUE constraints y manejarlos como en inventario
        log.error(f"Error BD ({db_name}) insertando coche {marca} {modelo}: {e_db}", exc_info=True)
        return jsonify({'error': f'Error de base de datos al agregar el coche: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado agregando coche {marca} {modelo} a {db_name}: {e_gen}")
        return jsonify({'error': 'Error interno inesperado al guardar el coche.'}), 500


@app.route('/coches/<int:id_coche>', methods=['GET'])
def obtener_coche_por_id(id_coche):
    """Obtiene un coche específico por su ID."""
    db_name = COCHES_DB_CONFIG.get('name', 'CochesDB_Desconocido')
    log.info(f"GET /coches/{id_coche} (DB: {db_name})")
    # El decorador de Flask ya valida que id_coche sea un int, si no, Flask devuelve 404

    # 1. Interacción con la BD
    try:
        # Usar obtener_todos con filtro y límite 1
        resultados = obtener_todos_los_elementos(
            'Vehiculos',
            db_config=COCHES_DB_CONFIG,
            filtro={'id': id_coche},
            limite=1
        )

        # 2. Procesar Resultado y Devolver Respuesta
        if resultados:
            log.info(f"Coche encontrado en {db_name}: ID={id_coche}")
            return jsonify({'coche': resultados[0]}), 200
        else:
            log.warning(f"Coche con ID {id_coche} no encontrado en {db_name}.")
            return jsonify({'error': f'Coche con ID {id_coche} no encontrado.'}), 404 # Not Found

    except ErrorBaseDatos as e_db:
        log.error(f"Error BD ({db_name}) en GET /coches/{id_coche}: {e_db}", exc_info=True)
        return jsonify({'error': f'Error de base de datos al obtener el coche: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado en GET /coches/{id_coche} ({db_name}): {e_gen}")
        return jsonify({'error': 'Error interno inesperado al obtener el coche.'}), 500


@app.route('/coches/<int:id_coche>', methods=['DELETE'])
def eliminar_coche(id_coche):
    """Elimina un coche por su ID."""
    db_name = COCHES_DB_CONFIG.get('name', 'CochesDB_Desconocido')
    log.info(f"DELETE /coches/{id_coche} (DB: {db_name})")
    # Validación del ID (entero positivo) implícita por <int:>, pero podemos añadir >0 si queremos
    if id_coche <= 0:
         log.warning(f"ID inválido en DELETE /coches/{id_coche} ({db_name}): debe ser positivo.")
         return jsonify({'error': 'El ID del coche debe ser un número positivo.'}), 400

    # 1. Interacción con la BD
    try:
        eliminado = eliminar_elemento(
            'Vehiculos',
            'id', # Columna para identificar
            id_coche, # Valor para identificar
            db_config=COCHES_DB_CONFIG
        )

        # 2. Respuesta según resultado
        if eliminado:
            log.info(f"Coche eliminado de {db_name}: ID={id_coche}")
            return jsonify({'mensaje': f'Coche con ID {id_coche} eliminado correctamente de {db_name}.'}), 200 # O 204 No Content
        else:
            log.warning(f"Intento de eliminar coche no encontrado ID={id_coche} en {db_name}.")
            return jsonify({'error': f'Coche con ID {id_coche} no encontrado.'}), 404 # Not Found

    except ErrorBaseDatos as e_db:
        log.error(f"Error BD ({db_name}) eliminando coche ID={id_coche}: {e_db}", exc_info=True)
        return jsonify({'error': f'Error de base de datos al eliminar el coche: {str(e_db)}'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado eliminando coche ID={id_coche} de {db_name}: {e_gen}")
        return jsonify({'error': 'Error interno inesperado al eliminar el coche.'}), 500
    
@app.route('/')
def indice_api():
    log.info("Solicitud GET / recibida.")
    banco_db = BANCO_DB_CONFIG.get('name', 'No Configurada')
    inventario_db = INVENTARIO_DB_CONFIG.get('name', 'No Configurada')
    coches_db = COCHES_DB_CONFIG.get('name', 'No Configurada')
    return (f"API de Ejercicios Python - Estado Conexiones: "
            f"Banco({banco_db}), Inventario({inventario_db}), Coches({coches_db})")

# Por que carajo no funciona la API de los animales pisha??
@app.route('/animales/sonidos', methods=['GET'])
def obtener_sonidos_animales():
    """Crea instancias de animales y devuelve sus sonidos."""
    log.info("GET /animales/sonidos")

    if not EJ3_AVAILABLE:
        log.error("Intento de acceso a /animales/sonidos pero EJ3 no está disponible.")
        return jsonify({'error': 'La funcionalidad del Ejercicio 3 (Animales) no está disponible debido a un error de importación.'}), 503 # Service Unavailable

    try:
        # 1. Crear Instancias (Lógica del ejercicio)
        perro1 = Perro()
        gato1 = Gato()
        perro2 = Perro()
        gato2 = Gato()
        animal_generico = Animal() # Añadimos uno genérico para variar

        animales_instanciados = [perro1, gato1, perro2, gato2, animal_generico]

        # 2. Obtener los sonidos (usando el método modificado que retorna string)
        lista_sonidos = []
        for animal in animales_instanciados:
            try:
                # Llamamos al método que ahora devuelve el sonido
                sonido = animal.hacer_sonido()
                # Añadimos el tipo de animal para más claridad en la respuesta
                lista_sonidos.append({
                    "tipo": type(animal).__name__,
                    "sonido": sonido
                 })
            except Exception as e_sonido:
                # Si un animal específico fallara (poco probable aquí)
                log.error(f"Error al obtener sonido para {type(animal).__name__}: {e_sonido}")
                lista_sonidos.append({
                    "tipo": type(animal).__name__,
                    "sonido": f"Error al procesar: {e_sonido}"
                 })

        # 3. Devolver respuesta exitosa
        log.info(f"Sonidos de animales generados: {len(lista_sonidos)} sonidos.")
        return jsonify({
            'sonidos': lista_sonidos,
            'mensaje': 'Sonidos de animales generados correctamente.'
        }), 200

    except NameError as ne:
        # Esto podría pasar si EJ3_AVAILABLE es True pero las clases no se definieron bien
        log.error(f"Error crítico: Clases de EJ3 no definidas correctamente. {ne}", exc_info=True)
        return jsonify({'error': 'Error interno: Las clases de Animales no están disponibles.'}), 500
    except Exception as e_gen:
        log.exception(f"Error inesperado en GET /animales/sonidos: {e_gen}")
        return jsonify({'error': 'Error interno inesperado al generar los sonidos.'}), 500

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
    # --- CORREGIDO: Comprobación crítica de variables de entorno ANTES de correr ---
    # Asegurarse de que TODAS las configuraciones necesarias tienen valores mínimos.
    essential_configs = [BANCO_DB_CONFIG, INVENTARIO_DB_CONFIG, COCHES_DB_CONFIG]
    missing_details = []
    if not DB_HOST:
        missing_details.append("DB_HOST")
    for i, config in enumerate(essential_configs):
        db_type = ["Banco", "Inventario", "Coches"][i]
        if not config.get('name'): missing_details.append(f"{db_type}: Nombre BD")
        if not config.get('user'): missing_details.append(f"{db_type}: Usuario BD")
        # La contraseña puede estar vacía, pero la clave 'pass' debe existir (os.environ.get devuelve None si no existe)
        if 'pass' not in config or config.get('pass') is None:
             if os.environ.get(f"DB_{db_type.upper()}_PASSWORD") is None:
                 log.warning(f"Variable de entorno para contraseña de {db_type} (DB_{db_type.upper()}_PASSWORD) no definida. Asumiendo vacío.")
             if 'pass' not in config: config['pass'] = ''


    if missing_details:
         log.critical(f"La aplicación no puede iniciar debido a variables de entorno de BD esenciales faltantes: {', '.join(missing_details)}")
         exit(1) # Salir si falta configuración esencial

    # --- Configuración de ejecución ---
    is_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    # --- CORREGIDO: Usar API_PORT_CONTAINER ---
    port_str = os.environ.get("API_PORT_CONTAINER", "8000") # Flask escucha en este puerto DENTRO del contenedor
    try:
        port = int(port_str)
    except ValueError:
        log.warning(f"Valor inválido para API_PORT_CONTAINER: '{port_str}'. Usando 8000 por defecto.")
        port = 8000

    # Escuchar en 0.0.0.0 para ser accesible desde fuera del contenedor
    host = "0.0.0.0"
    log.info(f"Iniciando servidor Flask en {host}:{port} (Debug: {is_debug})")
    # El puerto expuesto al HOST (API_PORT_HOST) se configura en docker-compose.yaml
    app.run(debug=is_debug, host=host, port=port)