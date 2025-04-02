# file: db.py
import mysql.connector
import os
import logging
from typing import Optional # Correcto!

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ErrorBaseDatos(Exception):
    def __init__(self, message, errno=None):
        super().__init__(message)
        self.errno = errno

# --- MODIFICADO ---
def obtener_conexion_bd(
    db_host: str,
    db_name: str,
    db_user: str,
    db_pass: str
):
    """
    Establece la conexión a la base de datos usando credenciales explícitas.
    Lanza ErrorBaseDatos si falla la conexión.
    """
    if not all([db_host, db_name, db_user, db_pass]):
         # db_pass puede ser string vacío, pero los otros no
        if not db_host or not db_name or not db_user:
             missing = [k for k, v in {'host': db_host, 'name': db_name, 'user': db_user}.items() if not v]
             msg = f"Faltan parámetros de conexión requeridos: {', '.join(missing)}"
             logging.error(msg)
             raise ValueError(msg)
        # Permitir contraseña vacía, aunque no recomendado
        logging.warning(f"Intentando conectar a BD '{db_name}' en '{db_host}' con usuario '{db_user}' y contraseña VACÍA.")


    try:
        mi_bd = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            # connection_timeout=10 # Considerar añadir timeout
        )
        logging.debug(f"Conexión a BD '{db_name}' como '{db_user}' establecida.")
        return mi_bd
    except mysql.connector.Error as err:
        logging.error(f"Error conexión BD '{db_name}' como '{db_user}': {err} (Code: {err.errno})")
        # No loguear db_pass en producción
        raise ErrorBaseDatos(f"No se pudo conectar a '{db_name}' como '{db_user}': {err}", errno=err.errno)
    except Exception as ex:
        logging.error(f"Error inesperado configurando conexión a BD '{db_name}' como '{db_user}': {ex}")
        raise ErrorBaseDatos(f"Error inesperado al conectar a BD '{db_name}': {ex}")


# --- MODIFICADO: Eliminar db_name, ahora se pasa en la conexión ---
# --- Pasar explícitamente host, user, password, db_name ---
def _ejecutar_consulta(sql: str, params: tuple = (), db_config: dict = None, fetch_one: bool = False, fetch_all: bool = False, commit: bool = False):
    """Función interna para ejecutar consultas y manejar conexiones/cursores."""
    if not db_config:
        raise ValueError("Se requiere db_config con host, name, user, pass")

    conexion = None
    cursor = None
    resultado = None
    last_row_id = None
    row_count = -1 # Inicializar a -1 para distinguir de 0 filas afectadas

    required_keys = ['host', 'name', 'user', 'pass']
    if not all(key in db_config for key in required_keys):
         missing = [k for k in required_keys if k not in db_config]
         raise ValueError(f"Faltan claves en db_config: {', '.join(missing)}")

    try:
        conexion = obtener_conexion_bd(
            db_host=db_config['host'],
            db_name=db_config['name'],
            db_user=db_config['user'],
            db_pass=db_config['pass']
        )
        # Usar dictionary=True si se espera fetch
        use_dict_cursor = fetch_one or fetch_all
        cursor = conexion.cursor(dictionary=use_dict_cursor)

        logging.debug(f"Ejecutando SQL en '{db_config['name']}': {sql} con params: {params}")
        cursor.execute(sql, params)

        if commit:
            conexion.commit()
            last_row_id = cursor.lastrowid
            row_count = cursor.rowcount
            logging.debug(f"Commit realizado. Lastrowid: {last_row_id}, Rowcount: {row_count}")
        elif fetch_one:
            resultado = cursor.fetchone()
            logging.debug(f"Fetchone realizado. Resultado: {'Encontrado' if resultado else 'No encontrado'}")
        elif fetch_all:
            resultado = cursor.fetchall()
            logging.debug(f"Fetchall realizado. {len(resultado) if resultado else 0} filas encontradas.")
        else:
             row_count = cursor.rowcount # Para UPDATE/DELETE sin commit explícito aquí (aunque commit=True es mejor)

        # Devolver un diccionario con todos los posibles resultados
        return {
            "data": resultado,
            "lastrowid": last_row_id,
            "rowcount": row_count,
            "success": True
        }

    except mysql.connector.Error as err:
        if commit and conexion: # Solo rollback si intentamos hacer commit
            logging.warning(f"Rollback DB '{db_config['name']}' debido a error: {err}")
            conexion.rollback()
        logging.error(f"Error MySQL en '{db_config['name']}': {err} (Code: {err.errno})")
        # No relanzar directamente, devolver estructura de error
        # raise ErrorBaseDatos(f"Error MySQL: {err}", errno=err.errno)
        return {"success": False, "error": f"Error MySQL: {err}", "errno": err.errno}
    except Exception as ex:
        if commit and conexion:
            logging.warning(f"Rollback DB '{db_config['name']}' debido a error inesperado: {ex}")
            conexion.rollback()
        logging.error(f"Error inesperado en '{db_config['name']}': {ex}")
        # raise ErrorBaseDatos(f"Error inesperado: {ex}")
        return {"success": False, "error": f"Error inesperado: {ex}", "errno": None}

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            logging.debug(f"Conexión a BD '{db_config['name']}' cerrada.")

# --- REFACTORIZADO: Usar _ejecutar_consulta ---
def obtener_todos_los_elementos(nombre_tabla, db_config: dict, filtro=None, orden=None, limite=None, desplazamiento=None):
    sql = f"SELECT * FROM `{nombre_tabla}`"
    parametros = []
    # ... (lógica para añadir WHERE, ORDER BY, LIMIT, OFFSET igual que antes, construyendo sql y parametros) ...
    if filtro:
        condiciones = [f"`{col}` = %s" for col in filtro.keys()]
        sql += " WHERE " + " AND ".join(condiciones)
        parametros.extend(filtro.values())
    if orden:
        clausulas_orden = []
        for col, dire in orden:
            dire_upper = dire.upper()
            if dire_upper not in ('ASC', 'DESC'): dire_upper = 'ASC'
            clausulas_orden.append(f"`{col}` {dire_upper}")
        sql += " ORDER BY " + ", ".join(clausulas_orden)
    if limite is not None:
        try:
            limite_int = int(limite); assert limite_int >= 0
            sql += " LIMIT %s"; parametros.append(limite_int)
            if desplazamiento is not None:
                try:
                    despl_int = int(desplazamiento); assert despl_int >= 0
                    sql += " OFFSET %s"; parametros.append(despl_int)
                except: logging.warning("Desplazamiento inválido, ignorado.")
        except: logging.warning("Límite inválido, ignorado.")
    # ---
    result = _ejecutar_consulta(sql, tuple(parametros), db_config=db_config, fetch_all=True)
    if not result["success"]:
        # Relanzar como excepción personalizada para mantener la interfaz anterior
        raise ErrorBaseDatos(result["error"], errno=result["errno"])
    return result["data"]

def insertar_elemento(nombre_tabla, datos, db_config: dict):
    columnas = ', '.join([f"`{col}`" for col in datos.keys()])
    marcadores = ', '.join(['%s'] * len(datos))
    valores = tuple(datos.values())
    sql = f"INSERT INTO `{nombre_tabla}` ({columnas}) VALUES ({marcadores})"
    result = _ejecutar_consulta(sql, valores, db_config=db_config, commit=True)
    if not result["success"]:
         raise ErrorBaseDatos(result["error"], errno=result["errno"])
    # Devolver ID insertado
    return result["lastrowid"]

def actualizar_elemento(nombre_tabla, columna_id, valor_id, datos, db_config: dict):
    asignaciones = ', '.join([f"`{col}` = %s" for col in datos.keys()])
    valores = list(datos.values())
    valores.append(valor_id)
    sql = f"UPDATE `{nombre_tabla}` SET {asignaciones} WHERE `{columna_id}` = %s"
    result = _ejecutar_consulta(sql, tuple(valores), db_config=db_config, commit=True)
    if not result["success"]:
         raise ErrorBaseDatos(result["error"], errno=result["errno"])
    # Devolver True si se afectó alguna fila
    return result["rowcount"] > 0

def eliminar_elemento(nombre_tabla, columna_id, valor_id, db_config: dict):
    sql = f"DELETE FROM `{nombre_tabla}` WHERE `{columna_id}` = %s"
    result = _ejecutar_consulta(sql, (valor_id,), db_config=db_config, commit=True)
    if not result["success"]:
         raise ErrorBaseDatos(result["error"], errno=result["errno"])
    # Devolver True si se afectó alguna fila
    return result["rowcount"] > 0