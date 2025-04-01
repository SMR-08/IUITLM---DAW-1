# src/dibujo.py
import pygame
# Importa configuracion usando el alias cfg
from . import configuracion as cfg
from .pieza import Pieza

# --- Gestión de Fuentes ---
_fuentes = {} # Caché para objetos de fuente cargados

def obtener_fuente(nombre, tamano):
    """
    Obtiene un objeto pygame.font.Font desde el caché o lo carga.

    Args:
        nombre (str): Nombre de la fuente del sistema.
        tamano (int): Tamaño de la fuente en puntos.

    Returns:
        pygame.font.Font: El objeto de fuente cargado o cacheado.
    """
    clave = (nombre, tamano)
    if clave not in _fuentes:
        try:
            # Intenta cargar la fuente especificada.
            _fuentes[clave] = pygame.font.SysFont(nombre, tamano, bold=True)
        except pygame.error as e:
             # Fallback a fuente 'arial' si la solicitada no se encuentra.
             print(f"Advertencia: Fuente '{nombre}' no encontrada, usando predeterminada. Error: {e}")
             clave_fuente_predet = ('arial', tamano)
             if clave_fuente_predet not in _fuentes:
                 _fuentes[clave_fuente_predet] = pygame.font.SysFont('arial', tamano, bold=True)
             _fuentes[clave] = _fuentes[clave_fuente_predet] # Usa la fuente predeterminada para la clave original.
    return _fuentes[clave]

# --- Ayudantes Básicos de Dibujo ---

def dibujar_texto(superficie, texto, tamano, x, y, color=cfg.BLANCO, nombre_fuente=cfg.NOMBRE_FUENTE_UI):
    """Dibuja texto en una superficie usando fuentes cacheadas."""
    fuente = obtener_fuente(nombre_fuente, tamano)
    etiqueta = fuente.render(texto, 1, color) # 1 habilita anti-aliasing.
    superficie.blit(etiqueta, (x, y))

def _dibujar_superposicion_menu(superficie):
    """Dibuja una superposición semitransparente, usada típicamente detrás de los menús."""
    # pygame.SRCALPHA permite transparencia por píxel.
    superposicion = pygame.Surface((cfg.ANCHO_PANTALLA, cfg.ALTO_PANTALLA), pygame.SRCALPHA)
    superposicion.fill((0, 0, 0, 180)) # Negro con 180/255 alfa (~70% opaco).
    superficie.blit(superposicion, (0, 0))

# --- Elementos del Tablero de Juego ---

def dibujar_lineas_cuadricula(superficie):
    """Dibuja las líneas de la cuadrícula de fondo para el campo de juego."""
    for f in range(cfg.ALTO_CUADRICULA + 1):
        pygame.draw.line(superficie, cfg.GRIS_OSCURO, # Color más oscuro para líneas sutiles.
                         (cfg.X_SUP_IZQ, cfg.Y_SUP_IZQ + f * cfg.TAMANO_BLOQUE),
                         (cfg.X_SUP_IZQ + cfg.ANCHO_CAMPO_JUEGO, cfg.Y_SUP_IZQ + f * cfg.TAMANO_BLOQUE))
    for c in range(cfg.ANCHO_CUADRICULA + 1):
        pygame.draw.line(superficie, cfg.GRIS_OSCURO,
                         (cfg.X_SUP_IZQ + c * cfg.TAMANO_BLOQUE, cfg.Y_SUP_IZQ),
                         (cfg.X_SUP_IZQ + c * cfg.TAMANO_BLOQUE, cfg.Y_SUP_IZQ + cfg.ALTO_CAMPO_JUEGO))

def dibujar_borde_campo_juego(superficie):
    """Dibuja un borde alrededor del área del campo de juego."""
    # Borde de 2px de grosor.
    pygame.draw.rect(superficie, cfg.BLANCO,
                     (cfg.X_SUP_IZQ - 2, cfg.Y_SUP_IZQ - 2, cfg.ANCHO_CAMPO_JUEGO + 4, cfg.ALTO_CAMPO_JUEGO + 4), 2)

def dibujar_bloques_cuadricula(superficie, cuadricula):
    """Dibuja los bloques bloqueados actualmente en la cuadrícula."""
    for f in range(cfg.ALTO_CUADRICULA):
        for c in range(cfg.ANCHO_CUADRICULA):
            color = cuadricula[f][c]
            if color != cfg.NEGRO: # Omite el dibujo de celdas vacías.
                # Calcula coordenadas de pantalla para el bloque.
                pantalla_x = cfg.X_SUP_IZQ + c * cfg.TAMANO_BLOQUE
                pantalla_y = cfg.Y_SUP_IZQ + f * cfg.TAMANO_BLOQUE

                # Dibuja color principal del bloque.
                pygame.draw.rect(superficie, color,
                                 (pantalla_x, pantalla_y, cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), 0) # 0 = relleno.
                # Dibuja borde sutil para definición.
                pygame.draw.rect(superficie, cfg.GRIS,
                                 (pantalla_x, pantalla_y, cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), 1) # 1 = borde de 1px.

# --- Piezas de Tetrominó ---

def dibujar_pieza(superficie, pieza: Pieza):
    """Dibuja la pieza que está cayendo actualmente en su posición."""
    posiciones_bloques = pieza.obtener_posiciones_bloques()

    for f, c in posiciones_bloques:
        # Dibuja solo bloques dentro o por encima del área visible de la cuadrícula verticalmente.
        if f < cfg.ALTO_CUADRICULA:
            # Calcula coordenadas de pantalla.
            pantalla_x = cfg.X_SUP_IZQ + c * cfg.TAMANO_BLOQUE
            pantalla_y = cfg.Y_SUP_IZQ + f * cfg.TAMANO_BLOQUE

            # Renderiza solo si el bloque está en pantalla verticalmente (f >= 0).
            if pantalla_y >= cfg.Y_SUP_IZQ:
                pygame.draw.rect(superficie, pieza.color,
                                (pantalla_x, pantalla_y, cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), 0)
                pygame.draw.rect(superficie, cfg.GRIS, # Añade borde.
                                (pantalla_x, pantalla_y, cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), 1)

def dibujar_pieza_fantasma(superficie, pieza: Pieza, fantasma_y: int):
    """Dibuja un 'fantasma' semitransparente de la pieza donde aterrizaría."""
    # Obtiene posiciones en la Y fantasma calculada.
    posiciones_bloques = pieza.obtener_posiciones_bloques(cuadricula_y=fantasma_y)

    for f, c in posiciones_bloques:
        # Dibuja solo bloques dentro de los límites visibles de la cuadrícula.
        if 0 <= f < cfg.ALTO_CUADRICULA and 0 <= c < cfg.ANCHO_CUADRICULA:
            pantalla_x = cfg.X_SUP_IZQ + c * cfg.TAMANO_BLOQUE
            pantalla_y = cfg.Y_SUP_IZQ + f * cfg.TAMANO_BLOQUE

            # Crea una superficie temporal para el bloque transparente.
            s = pygame.Surface((cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), pygame.SRCALPHA)
            # Usa el color de la pieza pero con el alfa especificado.
            s.fill((*pieza.color, cfg.ALFA_FANTASMA))
            superficie.blit(s, (pantalla_x, pantalla_y))

def dibujar_siguiente_pieza(superficie, pieza: Pieza):
    """Dibuja la vista previa de la siguiente pieza en su área designada."""
    sx = cfg.X_AREA_SIG_PIEZA
    sy = cfg.Y_AREA_SIG_PIEZA

    dibujar_texto(superficie, "Siguiente:", cfg.TAMANO_FUENTE_UI, sx, sy - 40, color=cfg.BLANCO, nombre_fuente=cfg.NOMBRE_FUENTE_UI)

    # Usa la rotación base (índice 0) para una visualización de vista previa consistente.
    forma = pieza.formas[0]
    alto_forma = len(forma)
    ancho_forma = len(forma[0]) if alto_forma > 0 else 0

    # Calcula esquina superior izquierda para centrar la forma de vista previa.
    # Ajusta el centrado basado en las dimensiones reales de la forma.
    ancho_area_previa = 4 * cfg.TAMANO_BLOQUE
    alto_area_previa = 4 * cfg.TAMANO_BLOQUE
    inicio_dibujo_x = sx + (ancho_area_previa - ancho_forma * cfg.TAMANO_BLOQUE) // 2
    inicio_dibujo_y = sy + (alto_area_previa - alto_forma * cfg.TAMANO_BLOQUE) // 2

    # Dibuja los bloques de la forma de vista previa.
    for idx_f, fila in enumerate(forma):
        for idx_c, celda in enumerate(fila):
            if celda == 1: # 1 indica un bloque.
                dibujar_x = inicio_dibujo_x + idx_c * cfg.TAMANO_BLOQUE
                dibujar_y = inicio_dibujo_y + idx_f * cfg.TAMANO_BLOQUE
                pygame.draw.rect(superficie, pieza.color,
                                 (dibujar_x, dibujar_y, cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), 0)
                pygame.draw.rect(superficie, cfg.GRIS, # Añade borde.
                                 (dibujar_x, dibujar_y, cfg.TAMANO_BLOQUE, cfg.TAMANO_BLOQUE), 1)

# --- Elementos de la Interfaz de Usuario (UI) ---

def dibujar_ui(superficie, puntuacion: int, nivel: int, lineas: int):
    """Dibuja los elementos de la UI: puntuación, nivel y líneas limpiadas."""
    ui_x = cfg.X_AREA_PUNTUACION
    ui_y = cfg.Y_INICIO_AREA_PUNTUACION

    # Visualización de Puntuación
    dibujar_texto(superficie, "Puntuación:", cfg.TAMANO_FUENTE_UI, ui_x, ui_y, nombre_fuente=cfg.NOMBRE_FUENTE_UI)
    dibujar_texto(superficie, f"{puntuacion}", cfg.TAMANO_FUENTE_UI, ui_x + 10, ui_y + 30, nombre_fuente=cfg.NOMBRE_FUENTE_UI) # Valor debajo.

    # Visualización de Nivel
    dibujar_texto(superficie, "Nivel:", cfg.TAMANO_FUENTE_UI, ui_x, ui_y + 80, nombre_fuente=cfg.NOMBRE_FUENTE_UI)
    dibujar_texto(superficie, f"{nivel}", cfg.TAMANO_FUENTE_UI, ui_x + 10, ui_y + 110, nombre_fuente=cfg.NOMBRE_FUENTE_UI)

    # Visualización de Líneas Limpiadas
    dibujar_texto(superficie, "Líneas:", cfg.TAMANO_FUENTE_UI, ui_x, ui_y + 160, nombre_fuente=cfg.NOMBRE_FUENTE_UI)
    dibujar_texto(superficie, f"{lineas}", cfg.TAMANO_FUENTE_UI, ui_x + 10, ui_y + 190, nombre_fuente=cfg.NOMBRE_FUENTE_UI)

# --- Pantallas de Menú ---

def dibujar_menu_principal(superficie, opcion_seleccionada: int, opciones: list[str]):
    """Dibuja la pantalla del menú principal con título rediseñado."""
    superficie.fill(cfg.NEGRO)
    texto_titulo = "PyTetris"
    fuente_titulo = obtener_fuente(cfg.NOMBRE_FUENTE_TITULO_MENU, cfg.TAMANO_FUENTE_TITULO_MENU)
    titulo_x = cfg.ANCHO_PANTALLA // 2
    titulo_y = cfg.ALTO_PANTALLA // 3 - fuente_titulo.get_height() // 2 # Centrado vertical.
    desplazamiento_gradiente = 3 # Desplazamiento en píxeles para el efecto gradiente.

    # --- Dibujar Título Principal con Gradiente ---
    # Renderiza color inferior ligeramente desplazado.
    etiqueta_titulo_inf = fuente_titulo.render(texto_titulo, 1, cfg.COLOR_TITULO_INF)
    rect_titulo_inf = etiqueta_titulo_inf.get_rect(center=(titulo_x, titulo_y + desplazamiento_gradiente))
    superficie.blit(etiqueta_titulo_inf, rect_titulo_inf)

    # Renderiza color superior normalmente.
    etiqueta_titulo_sup = fuente_titulo.render(texto_titulo, 1, cfg.COLOR_TITULO_SUP)
    rect_titulo_sup = etiqueta_titulo_sup.get_rect(center=(titulo_x, titulo_y))
    superficie.blit(etiqueta_titulo_sup, rect_titulo_sup)
    # --- Fin Gradiente Título ---

    # Dibujar Opciones
    fuente_opcion = obtener_fuente(cfg.NOMBRE_FUENTE_OPCIONES_MENU, cfg.TAMANO_FUENTE_OPCIONES_MENU)
    opcion_y_inicio = cfg.ALTO_PANTALLA // 2
    espaciado_opcion = 50
    for i, nombre_opcion in enumerate(opciones):
        color = cfg.COLOR_SELECCION_MENU if i == opcion_seleccionada else cfg.BLANCO
        # Nota: La lógica anterior para atenuar "Opciones" ha sido eliminada.

        etiqueta_opcion = fuente_opcion.render(nombre_opcion, 1, color)
        rect_opcion = etiqueta_opcion.get_rect(center=(cfg.ANCHO_PANTALLA // 2, opcion_y_inicio + i * espaciado_opcion))
        superficie.blit(etiqueta_opcion, rect_opcion)

def dibujar_menu_pausa(superficie, opcion_seleccionada: int, opciones: list[str]):
    """Dibuja la superposición del menú de pausa."""
    _dibujar_superposicion_menu(superficie) # Atenúa el juego de fondo.

    # Dibujar Título "Pausado"
    fuente_titulo = obtener_fuente(cfg.NOMBRE_FUENTE_TITULO_PAUSA, cfg.TAMANO_FUENTE_TITULO_PAUSA)
    etiqueta_titulo = fuente_titulo.render("PAUSADO", 1, cfg.AMARILLO)
    titulo_x = cfg.ANCHO_PANTALLA // 2 - etiqueta_titulo.get_width() // 2
    titulo_y = cfg.ALTO_PANTALLA // 3
    superficie.blit(etiqueta_titulo, (titulo_x, titulo_y))

    # Dibujar Opciones de Pausa
    fuente_opcion = obtener_fuente(cfg.NOMBRE_FUENTE_OPCIONES_MENU, cfg.TAMANO_FUENTE_OPCIONES_MENU)
    opcion_y_inicio = cfg.ALTO_PANTALLA // 2 + 30 # Posición debajo del título.
    espaciado_opcion = 50
    for i, opcion in enumerate(opciones):
        color = cfg.COLOR_SELECCION_MENU if i == opcion_seleccionada else cfg.BLANCO
        etiqueta_opcion = fuente_opcion.render(opcion, 1, color)
        opcion_x = cfg.ANCHO_PANTALLA // 2 - etiqueta_opcion.get_width() // 2
        opcion_y = opcion_y_inicio + i * espaciado_opcion
        superficie.blit(etiqueta_opcion, (opcion_x, opcion_y))

def dibujar_fin_juego(superficie):
    """Dibuja la superposición de la pantalla de fin de juego."""
    _dibujar_superposicion_menu(superficie) # Atenúa el juego de fondo.

    # Obtener fuentes.
    fuente_grande = obtener_fuente(cfg.NOMBRE_FUENTE_FIN_JUEGO_GRANDE, cfg.TAMANO_FUENTE_FIN_JUEGO_GRANDE)
    fuente_pequena = obtener_fuente(cfg.NOMBRE_FUENTE_FIN_JUEGO_PEQUENA, cfg.TAMANO_FUENTE_FIN_JUEGO_PEQUENA)

    # Dibujar Texto "FIN DEL JUEGO".
    etiqueta_fin_juego = fuente_grande.render("FIN DEL JUEGO", 1, cfg.ROJO)
    # Posición más alta.
    superficie.blit(etiqueta_fin_juego, (cfg.ANCHO_PANTALLA // 2 - etiqueta_fin_juego.get_width() // 2, cfg.ALTO_PANTALLA // 2 - 60))

    # Dibujar Instrucciones.
    etiqueta_reiniciar = fuente_pequena.render("Pulsa 'R' para Jugar de Nuevo", 1, cfg.BLANCO)
    superficie.blit(etiqueta_reiniciar, (cfg.ANCHO_PANTALLA // 2 - etiqueta_reiniciar.get_width() // 2, cfg.ALTO_PANTALLA // 2 + 20))

    etiqueta_menu = fuente_pequena.render("Pulsa 'M' para Menú Principal", 1, cfg.BLANCO)
    superficie.blit(etiqueta_menu, (cfg.ANCHO_PANTALLA // 2 - etiqueta_menu.get_width() // 2, cfg.ALTO_PANTALLA // 2 + 60))

def dibujar_menu_opciones(superficie, opcion_seleccionada: int, opciones: list[str], estado_sonido_activado: bool):
    """Dibuja la pantalla del menú de opciones con título rediseñado."""
    superficie.fill(cfg.NEGRO)
    texto_titulo = "Opciones"
    fuente_titulo = obtener_fuente(cfg.NOMBRE_FUENTE_TITULO_MENU, cfg.TAMANO_FUENTE_TITULO_MENU)
    fuente_opcion = obtener_fuente(cfg.NOMBRE_FUENTE_OPCIONES_MENU, cfg.TAMANO_FUENTE_OPCIONES_MENU)

    # --- Dibujar Título de Opciones ---
    etiqueta_titulo = fuente_titulo.render(texto_titulo, 1, cfg.COLOR_TITULO_OPCIONES) # Color específico para este título.
    rect_titulo = etiqueta_titulo.get_rect(center=(cfg.ANCHO_PANTALLA // 2, cfg.ALTO_PANTALLA // 4))
    superficie.blit(etiqueta_titulo, rect_titulo)
    # --- Fin Título de Opciones ---

    # Dibujar Elementos de Opción
    opcion_y_inicio = cfg.ALTO_PANTALLA // 2 - 50
    espaciado_opcion = 60
    for i, nombre_opcion in enumerate(opciones):
        color = cfg.COLOR_SELECCION_MENU if i == opcion_seleccionada else cfg.BLANCO
        texto_mostrar = ""
        if nombre_opcion == "Sonidos":
            # Muestra ON/OFF según el estado del flag booleano.
            texto_estado = "ON" if estado_sonido_activado else "OFF"
            texto_mostrar = f"Sonidos: [{texto_estado}]"
        elif nombre_opcion == "Volver":
            texto_mostrar = "Volver al Menú"
        else:
            texto_mostrar = nombre_opcion # Para futuras opciones.

        etiqueta_opcion = fuente_opcion.render(texto_mostrar, 1, color)
        rect_opcion = etiqueta_opcion.get_rect(center=(cfg.ANCHO_PANTALLA // 2, opcion_y_inicio + i * espaciado_opcion))
        superficie.blit(etiqueta_opcion, rect_opcion)