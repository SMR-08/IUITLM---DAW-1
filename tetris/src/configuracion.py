# src/configuracion.py
import pygame

# Dimensiones de Pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 750

# Dimensiones de la Cuadrícula
ANCHO_CUADRICULA = 10
ALTO_CUADRICULA = 20 # Filas visibles.
TAMANO_BLOQUE = 30

# Cálculos de posición del campo de juego
ANCHO_CAMPO_JUEGO = ANCHO_CUADRICULA * TAMANO_BLOQUE
ALTO_CAMPO_JUEGO = ALTO_CUADRICULA * TAMANO_BLOQUE
# Centra el campo de juego en la pantalla.
X_SUP_IZQ = (ANCHO_PANTALLA - ANCHO_CAMPO_JUEGO) // 2
Y_SUP_IZQ = (ALTO_PANTALLA - ALTO_CAMPO_JUEGO) // 2

# Colores (RGB)
BLANCO = (255, 255, 255)
GRIS = (128, 128, 128)
GRIS_OSCURO = (50, 50, 50)
NEGRO = (0, 0, 0)
CIAN = (0, 255, 255)     # Pieza I.
AZUL = (0, 0, 255)       # Pieza J.
NARANJA = (255, 165, 0)   # Pieza L.
AMARILLO = (255, 255, 0)   # Pieza O.
VERDE = (0, 255, 0)      # Pieza S.
PURPURA = (128, 0, 128)   # Pieza T.
ROJO = (255, 0, 0)        # Pieza Z.
COLOR_SELECCION_MENU = (255, 255, 0) # Amarillo para selección.

# --- Colores de Título ---
COLOR_TITULO_SUP = (60, 120, 255)    # Color superior para gradiente del título.
COLOR_TITULO_INF = (100, 0, 200) # Color inferior para gradiente del título.
COLOR_TITULO_OPCIONES = NARANJA       # Color para el título de Opciones.

# Formas y Colores de Tetrominós (definición central)
TETROMINOS = {
    # Definiciones de forma: lista de matrices de rotación.
    # Cada matriz es una lista de filas. 1 = bloque, 0 = vacío.
    0: {'formas': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]], 'color': CIAN}, # I
    1: {'formas': [[[1, 1], [1, 1]]], 'color': AMARILLO}, # O (Solo una rotación).
    2: {'formas': [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]], 'color': PURPURA}, # T
    3: {'formas': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]], 'color': VERDE}, # S
    4: {'formas': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]], 'color': ROJO}, # Z
    5: {'formas': [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]], 'color': AZUL}, # J
    6: {'formas': [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]], 'color': NARANJA} # L
}

# Puntuación
PUNTOS_POR_LINEA = {1: 40, 2: 100, 3: 300, 4: 1200} # Puntos por líneas limpiadas a la vez.
LINEAS_POR_NIVEL = 10 # Líneas necesarias para avanzar al siguiente nivel.

# Tiempos del Juego
VELOCIDAD_CAIDA_INICIAL = 0.8 # Segundos por paso de cuadrícula en nivel 1.
DECREMENTO_VELOCIDAD_CAIDA = 0.05 # Disminución de velocidad (tiempo) por nivel.
VELOCIDAD_CAIDA_MINIMA = 0.05 # Velocidad de caída más rápida posible (segundos por paso).
RETRASO_REPETICION_TECLA = 200 # Retraso en ms antes de inicio de repetición de tecla.
INTERVALO_REPETICION_TECLA = 40 # Intervalo para acciones de tecla repetidas (ms).

# Configuraciones de Fuente
# Nombres de fuente. Fallback a 'arial' si no se encuentran.
NOMBRE_FUENTE_UI = 'consolas'
TAMANO_FUENTE_UI = 25
NOMBRE_FUENTE_TITULO_MENU = 'impact' # Fuente para el título del menú.
TAMANO_FUENTE_TITULO_MENU = 70
NOMBRE_FUENTE_OPCIONES_MENU = 'consolas'
TAMANO_FUENTE_OPCIONES_MENU = 40
NOMBRE_FUENTE_FIN_JUEGO_GRANDE = 'impact'
TAMANO_FUENTE_FIN_JUEGO_GRANDE = 50
NOMBRE_FUENTE_FIN_JUEGO_PEQUENA = 'consolas'
TAMANO_FUENTE_FIN_JUEGO_PEQUENA = 30
NOMBRE_FUENTE_TITULO_PAUSA = 'impact'
TAMANO_FUENTE_TITULO_PAUSA = 60

# Posiciones de la UI (Relativas a la pantalla o campo de juego)
# Área para mostrar la siguiente pieza.
X_AREA_SIG_PIEZA = X_SUP_IZQ + ANCHO_CAMPO_JUEGO + 50
Y_AREA_SIG_PIEZA = Y_SUP_IZQ + 70
# Área para mostrar puntuación, nivel, líneas (a la izquierda del campo de juego).
X_AREA_PUNTUACION = X_SUP_IZQ - 200 if X_SUP_IZQ - 200 > 20 else 20 # Con margen mínimo.
Y_INICIO_AREA_PUNTUACION = Y_SUP_IZQ + 50

# Transparencia de la pieza fantasma (0=invisible, 255=opaco)
ALFA_FANTASMA = 90