# src/cuadricula.py
from .configuracion import ANCHO_CUADRICULA, ALTO_CUADRICULA, NEGRO
import sys # Para impresión de depuración.

def crear_cuadricula(posiciones_bloqueadas={}):
    """
    Crea la estructura de datos principal de la cuadrícula del juego (lista de listas)
    basada en las posiciones bloqueadas.
    """
    # Inicializa una cuadrícula vacía (llena de color NEGRO).
    cuadricula = [[NEGRO for _ in range(ANCHO_CUADRICULA)] for _ in range(ALTO_CUADRICULA)]
    # Rellena la cuadrícula con los bloques de las posiciones bloqueadas.
    for (f, c), color in posiciones_bloqueadas.items():
        # Asegura que las claves sean válidas y estén dentro de los límites de la cuadrícula antes de asignar.
        if isinstance(f, int) and isinstance(c, int) and 0 <= f < ALTO_CUADRICULA and 0 <= c < ANCHO_CUADRICULA:
             # Comprueba si el color es una tupla válida de 3 elementos (RGB).
             if isinstance(color, tuple) and len(color) == 3:
                cuadricula[f][c] = color
             else:
                 # Advierte si se encuentra un color inválido.
                 print(f"DEBUG: Valor de color inválido {color} para clave ({f},{c}) en crear_cuadricula", file=sys.stderr)
        # Ignora silenciosamente claves/posiciones inválidas fuera de los límites.
    return cuadricula

def es_posicion_valida(pieza, posiciones_bloqueadas, verificar_x=None, verificar_y=None):
    """
    Comprueba si la posición potencial de una pieza es válida.

    Validez significa:
    1. Todos los bloques están dentro de los límites horizontales (0 <= c < ANCHO_CUADRICULA).
    2. Todos los bloques están dentro del límite inferior (f < ALTO_CUADRICULA).
    3. La posición exacta (f, c) de ningún bloque existe como clave en el diccionario posiciones_bloqueadas.

    Args:
        pieza (Pieza): El objeto pieza a comprobar.
        posiciones_bloqueadas (dict): El diccionario que representa todos los bloques bloqueados {(f,c): color}.
        verificar_x (int, optional): La columna a comprobar para el origen de la pieza. Por defecto, pieza.x.
        verificar_y (int, optional): La fila a comprobar para el origen de la pieza. Por defecto, pieza.y.

    Returns:
        bool: True si la posición es válida, False en caso contrario.
    """
    # Determina la posición a comprobar (ya sea la pasada o la actual de la pieza).
    pos_x = verificar_x if verificar_x is not None else pieza.x
    pos_y = verificar_y if verificar_y is not None else pieza.y

    # Obtiene las coordenadas absolutas de la cuadrícula para cada bloque en la posición potencial.
    posiciones_potenciales_bloques = pieza.obtener_posiciones_bloques(cuadricula_x=pos_x, cuadricula_y=pos_y)

    for f, c in posiciones_potenciales_bloques:
        # --- Comprobaciones de Límites ---
        # Comprobar límites horizontales.
        if not (0 <= c < ANCHO_CUADRICULA):
            return False
        # Comprobar límite inferior.
        if f >= ALTO_CUADRICULA:
            return False
        # Nota: No hay comprobación explícita del límite superior (f < 0 está permitido).

        # --- Comprobación de Colisión ---
        # Comprueba directamente si la posición potencial del bloque existe en posiciones_bloqueadas.
        if (f, c) in posiciones_bloqueadas:
            # Colisión detectada: Posición inválida.
            return False

    # Si todos los bloques pasaron las comprobaciones de límites y colisión.
    return True

def bloquear_pieza(pieza, posiciones_bloqueadas):
    """
    Añade los bloques de la pieza que está cayendo actualmente al diccionario posiciones_bloqueadas.
    Incluye bloques potencialmente por encima de la pantalla visible (f < 0).
    """
    for f, c in pieza.obtener_posiciones_bloques():
        # Solo bloquear bloques que no terminen debajo de la cuadrícula visible.
        if f < ALTO_CUADRICULA:
            # Asegura que el color de la pieza sea válido antes de añadirlo.
            if isinstance(pieza.color, tuple) and len(pieza.color) == 3:
                 posiciones_bloqueadas[(f, c)] = pieza.color
            else:
                 # Advierte si se intenta bloquear una pieza con color inválido.
                 print(f"DEBUG: Intento de bloquear pieza con color inválido: {pieza.color}", file=sys.stderr)

def limpiar_lineas(posiciones_bloqueadas):
    """
    Comprueba y elimina las líneas completadas de las posiciones_bloqueadas.
    Desplaza hacia abajo los bloques por encima de las líneas limpiadas. Incluye comprobaciones defensivas.
    """
    lineas_limpiadas = 0
    filas_completas = []

    # Si no hay bloques bloqueados, no hay nada que limpiar.
    if not posiciones_bloqueadas: return 0, posiciones_bloqueadas

    # --- Encontrar Filas Completas ---
    # Comprueba las filas de la cuadrícula, de abajo hacia arriba.
    for f in range(ALTO_CUADRICULA -1, -1, -1):
        esta_llena = True
        for c in range(ANCHO_CUADRICULA):
            # Usa .get() para un acceso más seguro al diccionario.
            if posiciones_bloqueadas.get((f, c)) is None:
                esta_llena = False
                break # Fila no completa, pasar a la siguiente.
        if esta_llena:
            lineas_limpiadas += 1
            filas_completas.append(f) # Añade el índice de la fila completa.

    # --- Reconstruir Posiciones Bloqueadas si se Limpiaron Líneas ---
    if lineas_limpiadas > 0:
        nuevas_posiciones_bloqueadas = {}
        try:
            # Ordena los índices de las filas completas (ascendente).
            filas_completas.sort()
        except Exception as e:
             # Si falla la ordenación, aborta la limpieza para evitar errores.
             print(f"DEBUG: Error ordenando filas_completas: {filas_completas}. Error: {e}", file=sys.stderr)
             return 0, posiciones_bloqueadas

        # Iterar sobre copia de claves para reconstrucción segura.
        for clave_pos in list(posiciones_bloqueadas.keys()):
            # Validación básica de la clave del diccionario.
            if not (isinstance(clave_pos, tuple) and len(clave_pos) == 2 and
                    isinstance(clave_pos[0], int) and isinstance(clave_pos[1], int)):
                print(f"DEBUG: Clave inválida en posiciones_bloqueadas: {clave_pos}. Omitiendo.", file=sys.stderr)
                continue

            f, c = clave_pos # Desempaqueta fila y columna.

            # Si la fila del bloque no está entre las completadas, se conserva.
            if f not in filas_completas:
                try:
                    # Calcular desplazamiento basado en líneas limpiadas debajo.
                    desplazamiento = sum(1 for f_limpiada in filas_completas if f_limpiada > f)
                except TypeError as e:
                    print(f"DEBUG: TypeError durante cálculo de desplazamiento para f={f}. Error: {e}", file=sys.stderr)
                    desplazamiento = 0 # Por defecto, sin desplazamiento si falla el cálculo.
                    nueva_clave_pos = clave_pos
                else:
                     # Añade el bloque al nuevo diccionario en su posición desplazada.
                     nueva_clave_pos = (f + desplazamiento, c)

                # Valida el valor antes de la asignación.
                valor_a_asignar = posiciones_bloqueadas.get(clave_pos) # Usa get por seguridad.
                if isinstance(valor_a_asignar, tuple) and len(valor_a_asignar) == 3:
                    nuevas_posiciones_bloqueadas[nueva_clave_pos] = valor_a_asignar
                else:
                     # Advierte si se encuentra un valor inválido.
                     print(f"DEBUG: Valor inválido encontrado para clave {clave_pos}: {valor_a_asignar}. Omitiendo asignación.", file=sys.stderr)

        # Devuelve el número de líneas limpiadas y el diccionario reconstruido.
        return lineas_limpiadas, nuevas_posiciones_bloqueadas

    # No se limpiaron líneas, devuelve 0 y el diccionario original.
    return lineas_limpiadas, posiciones_bloqueadas

def calcular_posicion_fantasma(pieza, posiciones_bloqueadas):
    """
    Encuentra la posición y (índice de fila) válida más baja para la pieza
    basándose en las posiciones_bloqueadas.
    """
    fantasma_y = pieza.y
    # Comprueba hacia abajo paso a paso hasta encontrar una posición inválida.
    # La validación usa posiciones_bloqueadas.
    while es_posicion_valida(pieza, posiciones_bloqueadas, verificar_y=fantasma_y + 1):
        fantasma_y += 1
    # La última posición válida es la 'fantasma_y' actual.
    return fantasma_y