# file: db.py
import mysql.connector
import os
import logging

# Configuración del logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos."""
    pass

def obtener_conexion_bd():
    """
    Establece la conexión a la base de datos, usando variables de entorno.
    Lanza DatabaseError si falla la conexión.
    """
    try:
        mi_bd = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
        )
        return mi_bd
    except mysql.connector.Error as err:
        logging.error(f"Error de conexión a la BD: {err}")  # Log detallado
        raise DatabaseError(f"No se pudo conectar a la base de datos: {err}")

def obtener_todos_los_elementos(nombre_tabla, filtro=None, orden=None, limite=None, offset=None):
    """
    Obtiene registros de una tabla, con opciones de filtrado, orden y paginación.

    Args:
        nombre_tabla: Nombre de la tabla.
        filtro: Diccionario con condiciones WHERE (e.g., {'edad': 25, 'ciudad': 'Madrid'}).
        orden: Lista de tuplas para ordenar (e.g., [('edad', 'ASC'), ('nombre', 'DESC')]).
        limite: Número máximo de registros a devolver (para paginación).
        offset:  Desplazamiento para la paginación (comenzar desde el registro N).

    Returns:
        Lista de diccionarios (cada diccionario es una fila).
        Lanza DatabaseError si hay problemas.
    """
    conexion = obtener_conexion_bd()
    try:
        cursor = conexion.cursor(dictionary=True) # Usamos el cursor de diccionarios

        sql = f"SELECT * FROM {nombre_tabla}"  # Consulta base

        parametros = []
        # Añadir WHERE (si hay filtro)
        if filtro:
            condiciones = []
            for columna, valor in filtro.items():
                condiciones.append(f"`{columna}` = %s")  # Usamos `backticks` para nombres de columnas
                parametros.append(valor)
            sql += " WHERE " + " AND ".join(condiciones)

        # Añadir ORDER BY (si hay orden)
        if orden:
            orden_sql = ", ".join([f"`{columna}` {direccion}" for columna, direccion in orden])
            sql += " ORDER BY " + orden_sql

        # Añadir LIMIT y OFFSET (si hay paginación)
        if limite is not None:
            sql += " LIMIT %s"
            parametros.append(int(limite))  # Convertir a entero
            if offset is not None:
                sql += " OFFSET %s"
                parametros.append(int(offset))

        cursor.execute(sql, tuple(parametros))  # Ejecutar con parámetros
        resultados = cursor.fetchall()
        return resultados

    except mysql.connector.Error as err:
        logging.error(f"Error al obtener datos de {nombre_tabla}: {err}")
        raise DatabaseError(f"Error al obtener datos: {err}")
    finally:
        if conexion:
            conexion.close()



def insertar_elemento(nombre_tabla, datos):
    """
    Inserta un nuevo registro y devuelve el ID del registro insertado.
    """
    conexion = obtener_conexion_bd()
    try:
        cursor = conexion.cursor()
        columnas = ', '.join([f"`{col}`" for col in datos.keys()])  # Backticks
        marcadores = ', '.join(['%s'] * len(datos))
        valores = tuple(datos.values())

        sql = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({marcadores})"
        cursor.execute(sql, valores)
        conexion.commit()
        return cursor.lastrowid  # Devuelve el ID del nuevo registro

    except mysql.connector.Error as err:
        conexion.rollback()
        logging.error(f"Error al insertar en {nombre_tabla}: {err}")
        raise DatabaseError(f"Error al insertar: {err}")
    finally:
        if conexion:
            conexion.close()


def actualizar_elemento(nombre_tabla, id_columna, id_valor, datos):
    """
    Actualiza un registro, permitiendo especificar la columna ID.
    """
    conexion = obtener_conexion_bd()
    try:
        cursor = conexion.cursor()
        sets = ', '.join([f"`{col}` = %s" for col in datos.keys()]) # Backticks
        valores = list(datos.values())
        valores.append(id_valor)

        sql = f"UPDATE {nombre_tabla} SET {sets} WHERE `{id_columna}` = %s"  # Backticks
        cursor.execute(sql, tuple(valores))
        conexion.commit()
        return cursor.rowcount > 0  # Devuelve True si se actualizó alguna fila

    except mysql.connector.Error as err:
        conexion.rollback()
        logging.error(f"Error al actualizar {nombre_tabla}: {err}")
        raise DatabaseError(f"Error al actualizar: {err}")
    finally:
        if conexion:
            conexion.close()


def eliminar_elemento(nombre_tabla, id_columna, id_valor):
    """
    Elimina un registro, permitiendo especificar la columna ID.
    """
    conexion = obtener_conexion_bd()
    try:
        cursor = conexion.cursor()
        sql = f"DELETE FROM {nombre_tabla} WHERE `{id_columna}` = %s" # Backticks
        cursor.execute(sql, (id_valor,))
        conexion.commit()
        return cursor.rowcount > 0 # Devuelve True si se eliminó alguna fila

    except mysql.connector.Error as err:
        conexion.rollback()
        logging.error(f"Error al eliminar de {nombre_tabla}: {err}")
        raise DatabaseError(f"Error al eliminar: {err}")
    finally:
        if conexion:
            conexion.close()
