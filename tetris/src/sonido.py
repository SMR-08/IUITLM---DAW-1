# src/sonido.py
import numpy as np
import pygame
import sys

# --- Parámetros de Sonido ---
# Parámetros para la generación de sonido.
TASA_MUESTREO = 44100
FRECUENCIA_COLOCAR = 150
DURACION_COLOCAR = 0.08
AMPLITUD_COLOCAR = 5000 # Amplitud del sonido.

# Caché para el sonido de colocar pieza.
_cache_sonido_colocar = None

# --- Generador de Ondas ---
def _generar_onda_cuadrada_decreciente(frec, duracion, amplitud, tasa_muestreo, num_canales):
    """
    Genera muestras de audio para una onda cuadrada decreciente,
    coincidiendo con el número especificado de canales.
    El sonido se coloca en los dos primeros canales (I/D).
    """
    print(f"Generando onda para {num_canales} canales...") # Depuración.
    num_muestras = int(tasa_muestreo * duracion)
    puntos_tiempo = np.linspace(0, duracion, num_muestras, endpoint=False)

    # Generar onda cuadrada mono básica.
    datos_onda_mono = np.sign(np.sin(2 * np.pi * frec * puntos_tiempo))
    # Aplicar decaimiento (lineal al cuadrado para un final más suave).
    decaimiento = np.linspace(1, 0, num_muestras)**2
    datos_onda_mono = amplitud * datos_onda_mono * decaimiento
    # Convertir a array de enteros de 16 bits.
    array_sonido_mono = np.array(datos_onda_mono, dtype=np.int16)

    # Crear array multicanal inicializado a ceros.
    array_sonido_multi = np.zeros((num_muestras, num_canales), dtype=np.int16)

    # Colocar los datos del sonido mono en el primer canal (Izquierda).
    if num_canales >= 1:
        array_sonido_multi[:, 0] = array_sonido_mono

    # Colocar los datos del sonido mono en el segundo canal (Derecha) si está disponible.
    if num_canales >= 2:
        array_sonido_multi[:, 1] = array_sonido_mono

    # Los canales 3 a num_canales permanecen en silencio (ceros).

    print(f"Forma del array generado: {array_sonido_multi.shape}") # Depuración.
    return array_sonido_multi

# --- Creación de Sonido ---
def crear_sonido_colocar():
    """
    Genera y devuelve un objeto pygame.mixer.Sound para el efecto de colocación de pieza.
    Determina los canales reales del mezclador y genera datos de sonido compatibles.
    Cachea el resultado. Asume que pygame.mixer ha sido inicializado previamente.
    """
    global _cache_sonido_colocar
    # Devuelve el sonido cacheado si ya existe.
    if _cache_sonido_colocar is not None:
        return _cache_sonido_colocar

    print("Intentando crear efecto de sonido 'colocar'...")
    try:
        # --- Obtener Configuración Real del Mezclador ---
        config_mezclador = pygame.mixer.get_init()
        if not config_mezclador:
            print("ERROR: ¡El mezclador no está inicializado al intentar crear sonido!", file=sys.stderr)
            return None

        # Desempaqueta la configuración real del mezclador.
        frec_real, formato_real, canales_reales = config_mezclador
        print(f"Mezclador reportó config: Frec={frec_real}, Formato={formato_real}, Canales={canales_reales}")

        # --- Generar Datos de Sonido Coincidentes con Canales Reales ---
        array_sonido = _generar_onda_cuadrada_decreciente(
            frec=FRECUENCIA_COLOCAR,
            duracion=DURACION_COLOCAR,
            amplitud=AMPLITUD_COLOCAR,
            tasa_muestreo=frec_real, # Usa frecuencia real del mezclador.
            num_canales=canales_reales # Usa canales reales del mezclador.
        )

        # Crear el objeto de sonido desde el array numpy potencialmente multicanal.
        sonido = pygame.sndarray.make_sound(array_sonido)
        _cache_sonido_colocar = sonido # Guarda en caché.
        print("Sonido 'Colocar' generado con éxito.")
        return sonido

    except pygame.error as error_pg:
        print(f"ERROR: Error de Pygame generando sonido colocar: {error_pg}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Excepción general generando sonido colocar: {e}", file=sys.stderr)
        return None