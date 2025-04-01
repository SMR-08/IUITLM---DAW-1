# file: db.py
import mysql.connector
import os
import logging

# Configuración del logging
# Keep level as ERROR for production, maybe INFO/DEBUG for development
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ErrorBaseDatos(Exception): # Renamed Exception class
    """Excepción personalizada para errores de base de datos."""
    pass

def obtener_conexion_bd():
    """
    Establece la conexión a la base de datos, usando variables de entorno.
    Lanza ErrorBaseDatos si falla la conexión.
    """
    try:
        # Usa las variables de entorno para la configuración de la BD
        mi_bd = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"), # Default added for safety
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            # Consider adding connection timeout
            # connection_timeout=10
        )
        # Podríamos verificar si la conexión está activa aquí si es necesario
        # if not mi_bd.is_connected():
        #     raise ErrorBaseDatos("La conexión a la BD no está activa después de conectar.")
        logging.debug("Conexión a la base de datos establecida exitosamente.")
        return mi_bd
    except mysql.connector.Error as err:
        logging.error(f"Error de conexión a la BD: {err}")  # Log detallado
        # Raise the custom exception
        raise ErrorBaseDatos(f"No se pudo conectar a la base de datos: {err}")
    except Exception as ex:
        # Catch potential missing environment variables more gracefully
        logging.error(f"Error inesperado al configurar la conexión a la BD: {ex}")
        raise ErrorBaseDatos(f"Error de configuración o inesperado al conectar a la BD: {ex}")


def obtener_todos_los_elementos(nombre_tabla, filtro=None, orden=None, limite=None, desplazamiento=None): # Renamed offset -> desplazamiento
    """
    Obtiene registros de una tabla, con opciones de filtrado, orden y paginación.

    Args:
        nombre_tabla: Nombre de la tabla.
        filtro: Diccionario con condiciones WHERE (e.g., {'edad': 25, 'ciudad': 'Madrid'}).
        orden: Lista de tuplas para ordenar (e.g., [('edad', 'ASC'), ('nombre', 'DESC')]).
        limite: Número máximo de registros a devolver (para paginación).
        desplazamiento: Desplazamiento para la paginación (comenzar desde el registro N).

    Returns:
        Lista de diccionarios (cada diccionario es una fila).
        Lanza ErrorBaseDatos si hay problemas.
    """
    conexion = None # Initialize to None
    try:
        conexion = obtener_conexion_bd()
        # Usamos el cursor de diccionarios para obtener resultados como dict
        cursor = conexion.cursor(dictionary=True)

        # Consulta SQL base
        # Usamos f-string de forma segura ya que nombre_tabla viene de nuestro propio código, no del usuario
        # ¡NUNCA uses f-string para insertar valores de usuario directamente en SQL!
        sql = f"SELECT * FROM `{nombre_tabla}`" # Added backticks for table name safety

        parametros = []
        # Añadir cláusula WHERE si se proporciona un filtro
        if filtro:
            condiciones = []
            for columna, valor in filtro.items():
                # Usamos `backticks` para nombres de columnas por seguridad
                condiciones.append(f"`{columna}` = %s")
                parametros.append(valor)
            sql += " WHERE " + " AND ".join(condiciones)

        # Añadir cláusula ORDER BY si se proporciona orden
        if orden:
            # Asegurarse que 'orden' es una lista de tuplas (columna, direccion)
            clausulas_orden = []
            for columna, direccion in orden:
                # Validar dirección para prevenir inyección si viniera de fuera
                direccion_upper = direccion.upper()
                if direccion_upper not in ('ASC', 'DESC'):
                    logging.warning(f"Dirección de orden inválida '{direccion}', usando ASC por defecto.")
                    direccion_upper = 'ASC'
                # Usamos `backticks` para nombres de columnas
                clausulas_orden.append(f"`{columna}` {direccion_upper}")
            sql += " ORDER BY " + ", ".join(clausulas_orden)

        # Añadir cláusulas LIMIT y OFFSET (desplazamiento) para paginación
        if limite is not None:
            try:
                limite_int = int(limite)
                if limite_int < 0:
                    raise ValueError("El límite no puede ser negativo")
                sql += " LIMIT %s"
                parametros.append(limite_int)
            except (ValueError, TypeError):
                logging.warning(f"Valor de límite inválido '{limite}', ignorando.")

            # OFFSET solo tiene sentido si hay LIMIT
            if desplazamiento is not None and limite is not None: # Check limite again
                 try:
                     desplazamiento_int = int(desplazamiento)
                     if desplazamiento_int < 0:
                         raise ValueError("El desplazamiento no puede ser negativo")
                     sql += " OFFSET %s"
                     parametros.append(desplazamiento_int)
                 except (ValueError, TypeError):
                     logging.warning(f"Valor de desplazamiento inválido '{desplazamiento}', ignorando.")


        logging.debug(f"Ejecutando SQL: {sql} con parámetros: {tuple(parametros)}")
        cursor.execute(sql, tuple(parametros)) # Ejecutar con parámetros seguros
        resultados = cursor.fetchall()
        logging.debug(f"Se obtuvieron {len(resultados)} elementos de {nombre_tabla}.")
        return resultados

    except mysql.connector.Error as err:
        logging.error(f"Error de MySQL al obtener datos de {nombre_tabla}: {err}")
        # Raise the custom exception
        raise ErrorBaseDatos(f"Error de MySQL al obtener datos: {err}")
    except Exception as ex:
        logging.error(f"Error inesperado al obtener datos de {nombre_tabla}: {ex}")
        raise ErrorBaseDatos(f"Error inesperado al obtener datos: {ex}")
    finally:
        # Asegurarse de cerrar el cursor y la conexión
        if 'cursor' in locals() and cursor:
             cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            logging.debug("Conexión a la base de datos cerrada.")


def insertar_elemento(nombre_tabla, datos):
    """
    Inserta un nuevo registro y devuelve el ID del registro insertado (si es autoincremental).

    Args:
        nombre_tabla (str): Nombre de la tabla.
        datos (dict): Diccionario con los datos a insertar {columna: valor}.

    Returns:
        int: El ID de la última fila insertada (lastrowid). Puede ser 0 o no relevante si la PK no es AI.
        Lanza ErrorBaseDatos en caso de fallo.
    """
    conexion = None
    try:
        conexion = obtener_conexion_bd()
        cursor = conexion.cursor()

        # Construir la parte de columnas y marcadores de posición
        # Usar `backticks` para los nombres de las columnas
        columnas = ', '.join([f"`{col}`" for col in datos.keys()])
        marcadores = ', '.join(['%s'] * len(datos))
        valores = tuple(datos.values()) # Convertir los valores a tupla

        # Construir la consulta SQL completa
        sql = f"INSERT INTO `{nombre_tabla}` ({columnas}) VALUES ({marcadores})" # Backticks en tabla también

        logging.debug(f"Ejecutando SQL: {sql} con valores: {valores}")
        cursor.execute(sql, valores)
        conexion.commit() # Confirmar la transacción

        id_insertado = cursor.lastrowid # Obtener el ID del último registro insertado
        logging.info(f"Elemento insertado en '{nombre_tabla}' con éxito. Lastrowid: {id_insertado}")
        return id_insertado

    except mysql.connector.Error as err:
        logging.error(f"Error de MySQL al insertar en {nombre_tabla}: {err}")
        if conexion:
            conexion.rollback() # Revertir cambios en caso de error
            logging.info(f"Rollback realizado para inserción fallida en {nombre_tabla}.")
        raise ErrorBaseDatos(f"Error de MySQL al insertar: {err}") # Re-lanzar como excepción personalizada
    except Exception as ex:
        logging.error(f"Error inesperado al insertar en {nombre_tabla}: {ex}")
        if conexion:
             conexion.rollback()
             logging.info(f"Rollback realizado por error inesperado en {nombre_tabla}.")
        raise ErrorBaseDatos(f"Error inesperado al insertar: {ex}")
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            logging.debug("Conexión a la base de datos cerrada.")


def actualizar_elemento(nombre_tabla, columna_id, valor_id, datos): # Renamed id_columna, id_valor
    """
    Actualiza un registro basado en una columna y valor identificador.

    Args:
        nombre_tabla (str): Nombre de la tabla.
        columna_id (str): Nombre de la columna que identifica la fila (e.g., 'id').
        valor_id: Valor de la columna identificadora.
        datos (dict): Diccionario con las columnas y valores a actualizar.

    Returns:
        bool: True si se actualizó al menos una fila, False en caso contrario.
        Lanza ErrorBaseDatos en caso de fallo.
    """
    conexion = None
    try:
        conexion = obtener_conexion_bd()
        cursor = conexion.cursor()

        # Construir la parte SET de la consulta
        # Usar `backticks` para los nombres de las columnas
        asignaciones = ', '.join([f"`{col}` = %s" for col in datos.keys()])
        # Crear lista de valores para SET y añadir el valor del WHERE al final
        valores = list(datos.values())
        valores.append(valor_id)

        # Construir la consulta SQL completa
        # Usar `backticks` para nombres de tabla y columna ID
        sql = f"UPDATE `{nombre_tabla}` SET {asignaciones} WHERE `{columna_id}` = %s"

        logging.debug(f"Ejecutando SQL: {sql} con valores: {tuple(valores)}")
        cursor.execute(sql, tuple(valores))
        conexion.commit() # Confirmar la transacción

        filas_afectadas = cursor.rowcount # Número de filas afectadas
        logging.info(f"Actualización en '{nombre_tabla}' para {columna_id}={valor_id} afectó a {filas_afectadas} fila(s).")
        return filas_afectadas > 0 # Devuelve True si se actualizó alguna fila

    except mysql.connector.Error as err:
        logging.error(f"Error de MySQL al actualizar {nombre_tabla}: {err}")
        if conexion:
            conexion.rollback() # Revertir cambios en caso de error
            logging.info(f"Rollback realizado para actualización fallida en {nombre_tabla}.")
        raise ErrorBaseDatos(f"Error de MySQL al actualizar: {err}")
    except Exception as ex:
        logging.error(f"Error inesperado al actualizar {nombre_tabla}: {ex}")
        if conexion:
             conexion.rollback()
             logging.info(f"Rollback realizado por error inesperado en {nombre_tabla}.")
        raise ErrorBaseDatos(f"Error inesperado al actualizar: {ex}")
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            logging.debug("Conexión a la base de datos cerrada.")


def eliminar_elemento(nombre_tabla, columna_id, valor_id): # Renamed id_columna, id_valor
    """
    Elimina un registro basado en una columna y valor identificador.

    Args:
        nombre_tabla (str): Nombre de la tabla.
        columna_id (str): Nombre de la columna que identifica la fila (e.g., 'id').
        valor_id: Valor de la columna identificadora.

    Returns:
        bool: True si se eliminó al menos una fila, False en caso contrario.
        Lanza ErrorBaseDatos en caso de fallo.
    """
    conexion = None
    try:
        conexion = obtener_conexion_bd()
        cursor = conexion.cursor()

        # Construir la consulta SQL
        # Usar `backticks` para nombres de tabla y columna
        sql = f"DELETE FROM `{nombre_tabla}` WHERE `{columna_id}` = %s"

        logging.debug(f"Ejecutando SQL: {sql} con valor ID: {(valor_id,)}")
        cursor.execute(sql, (valor_id,)) # Pasar valor ID como tupla
        conexion.commit() # Confirmar la transacción

        filas_afectadas = cursor.rowcount # Número de filas afectadas
        logging.info(f"Eliminación en '{nombre_tabla}' para {columna_id}={valor_id} afectó a {filas_afectadas} fila(s).")
        return filas_afectadas > 0 # Devuelve True si se eliminó alguna fila

    except mysql.connector.Error as err:
        logging.error(f"Error de MySQL al eliminar de {nombre_tabla}: {err}")
        if conexion:
            conexion.rollback() # Revertir cambios en caso de error
            logging.info(f"Rollback realizado para eliminación fallida en {nombre_tabla}.")
        raise ErrorBaseDatos(f"Error de MySQL al eliminar: {err}")
    except Exception as ex:
        logging.error(f"Error inesperado al eliminar de {nombre_tabla}: {ex}")
        if conexion:
             conexion.rollback()
             logging.info(f"Rollback realizado por error inesperado en {nombre_tabla}.")
        raise ErrorBaseDatos(f"Error inesperado al eliminar: {ex}")
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            logging.debug("Conexión a la base de datos cerrada.")

# Note: obtener_valor_columna was not used in app.py, but translating it for completeness
def obtener_valor_columna(nombre_tabla, columna_a_obtener, filtro): # Renamed columna -> columna_a_obtener
    """
    Obtiene el valor de una columna específica de una fila que cumple un filtro.

    Args:
        nombre_tabla (str): Nombre de la tabla.
        columna_a_obtener (str): Nombre de la columna cuyo valor se desea obtener.
        filtro (dict): Diccionario con las condiciones WHERE (e.g., {'id': 5}). Debe idealmente filtrar a una única fila.

    Returns:
        El valor de la columna, o None si no se encuentra la fila o la columna.
        Lanza ErrorBaseDatos si hay problemas de BD.
    """
    conexion = None
    try:
        conexion = obtener_conexion_bd()
        # Usar cursor de diccionarios para acceder por nombre de columna
        cursor = conexion.cursor(dictionary=True)

        # Construir la consulta SQL seleccionando solo la columna deseada
        # Usar `backticks` para nombres de tabla y columna
        sql = f"SELECT `{columna_a_obtener}` FROM `{nombre_tabla}`"

        parametros = []
        # Añadir cláusula WHERE si se proporciona filtro
        if filtro:
            condiciones = []
            for col_filtro, valor_filtro in filtro.items():
                # Usar `backticks` para nombres de columnas
                condiciones.append(f"`{col_filtro}` = %s")
                parametros.append(valor_filtro)
            if condiciones: # Asegurarse de que hay condiciones antes de añadir WHERE
                 sql += " WHERE " + " AND ".join(condiciones)
            else:
                 logging.warning("Se llamó a obtener_valor_columna sin filtro válido, puede devolver un valor inesperado.")
        else:
             # Es peligroso llamar sin filtro, podría devolver el valor de la primera fila
             logging.warning("Se llamó a obtener_valor_columna sin filtro, devolverá el valor de la primera fila encontrada.")
             sql += " LIMIT 1" # Limitar a 1 por seguridad si no hay filtro

        logging.debug(f"Ejecutando SQL: {sql} con parámetros: {tuple(parametros)}")
        cursor.execute(sql, tuple(parametros))
        resultado = cursor.fetchone()  # Usamos fetchone() porque esperamos solo una fila (o la primera)

        if resultado:
            # Verificar si la columna existe en el resultado
            if columna_a_obtener in resultado:
                valor = resultado[columna_a_obtener]
                logging.debug(f"Valor obtenido para '{columna_a_obtener}' en '{nombre_tabla}': {valor}")
                return valor
            else:
                logging.error(f"La columna '{columna_a_obtener}' no se encontró en el resultado de la consulta para la tabla '{nombre_tabla}'.")
                return None
        else:
            logging.info(f"No se encontró ninguna fila en '{nombre_tabla}' que coincida con el filtro: {filtro}")
            return None  # No se encontró la fila que cumpla el filtro

    except mysql.connector.Error as err:
        logging.error(f"Error de MySQL al obtener valor de {columna_a_obtener} en {nombre_tabla}: {err}")
        raise ErrorBaseDatos(f"Error de MySQL al obtener valor: {err}")
    except Exception as ex:
        logging.error(f"Error inesperado al obtener valor de {columna_a_obtener} en {nombre_tabla}: {ex}")
        raise ErrorBaseDatos(f"Error inesperado al obtener valor: {ex}")
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            logging.debug("Conexión a la base de datos cerrada.")