# src/estado_juego.py
from enum import Enum, auto

class EstadoJuego(Enum):
    """Representa los posibles estados del juego."""
    MENU = auto()       # Menú principal está activo
    OPCIONES = auto()    # Menú de opciones está activo <--- AÑADIDO
    JUGANDO = auto()     # La jugabilidad está activa
    PAUSADO = auto()     # Menú de pausa está activo sobre la pantalla de juego
    FIN_JUEGO = auto()  # Pantalla de fin de juego se muestra