# src/pieza.py
import random
from .configuracion import TETROMINOS, ANCHO_CUADRICULA

class Pieza:
    """Representa una única pieza de Tetris (Tetrominó)."""
    def __init__(self, indice_tipo_forma, x, y):
        """
        Inicializa una Pieza.

        Args:
            indice_tipo_forma (int): Índice correspondiente a la clave en configuracion.TETROMINOS.
            x (int): Índice inicial de columna de la cuadrícula (borde izquierdo de la matriz de forma).
            y (int): Índice inicial de fila de la cuadrícula (borde superior de la matriz de forma).
        """
        if indice_tipo_forma not in TETROMINOS:
            raise ValueError(f"Índice de tipo de forma inválido: {indice_tipo_forma}")

        self.tipo = indice_tipo_forma
        self.datos = TETROMINOS[self.tipo]
        self.color = self.datos['color']
        self.formas = self.datos['formas'] # Lista de matrices de rotación.
        self.rotacion = 0 # Índice en self.formas.
        self.forma = self.formas[self.rotacion] # Matriz de rotación actual.

        # La posición se refiere a la esquina superior izquierda de la caja delimitadora de la forma en la cuadrícula.
        self.x = x # Índice de columna de la cuadrícula.
        self.y = y # Índice de fila de la cuadrícula.

    def rotar(self, sentido_horario=True):
        """
        Rota la pieza cambiando el índice de rotación actual.
        Actualiza self.forma a la nueva matriz de rotación.
        La lógica de 'wall kick' se maneja externamente (en la clase Juego).
        """
        num_rotaciones = len(self.formas)
        # No se puede rotar la pieza O o formas con solo una rotación definida.
        if num_rotaciones <= 1:
            return

        if sentido_horario:
            self.rotacion = (self.rotacion + 1) % num_rotaciones
        else:
            # El operador % de Python maneja correctamente los números negativos para envolver.
            self.rotacion = (self.rotacion - 1) % num_rotaciones
        self.forma = self.formas[self.rotacion] # Actualiza la forma activa.

    def obtener_posiciones_bloques(self, cuadricula_x=None, cuadricula_y=None):
        """
        Calcula las posiciones absolutas de la cuadrícula (fila, col) de cada bloque
        que compone la pieza en su rotación y posición actuales.

        Args:
            cuadricula_x (int, optional): Sobrescribe la posición x actual de la pieza. Por defecto, self.x.
            cuadricula_y (int, optional): Sobrescribe la posición y actual de la pieza. Por defecto, self.y.

        Returns:
            list[tuple[int, int]]: Lista de tuplas (fila, col) para cada bloque.
        """
        x_actual = cuadricula_x if cuadricula_x is not None else self.x
        y_actual = cuadricula_y if cuadricula_y is not None else self.y
        forma_a_usar = self.forma

        posiciones = []
        # Itera sobre la matriz de forma actual.
        for idx_f, fila in enumerate(forma_a_usar):
            for idx_c, celda in enumerate(fila):
                # '1' representa un bloque en la matriz de forma.
                if celda == 1:
                    # Calcula la posición absoluta en la cuadrícula.
                    posiciones.append((y_actual + idx_f, x_actual + idx_c))
        return posiciones

    def obtener_dimensiones_forma(self):
        """Devuelve el alto y ancho de la matriz de forma actual."""
        alto = len(self.forma)
        ancho = len(self.forma[0]) if alto > 0 else 0
        return alto, ancho

# --- Función Fábrica ---

def obtener_pieza_aleatoria(tipo_ultima_pieza=None):
    """
    Crea y devuelve un nuevo objeto Pieza aleatorio.

    Args:
        tipo_ultima_pieza (int, optional): El índice de tipo de la pieza generada anteriormente,
                                         para evitar la repetición inmediata. Por defecto, None.

    Returns:
        Pieza: Una instancia de Pieza recién creada.
    """
    # Elige un tipo de forma aleatorio.
    tipo_forma = random.randint(0, len(TETROMINOS) - 1)

    # Asegura que la nueva pieza sea diferente de la última, si se especifica.
    # Implementa un comportamiento simple de "no repetición inmediata".
    while tipo_ultima_pieza is not None and tipo_forma == tipo_ultima_pieza:
         tipo_forma = random.randint(0, len(TETROMINOS) - 1)

    # Calcula la posición inicial para centrar la pieza horizontalmente.
    forma_inicial = TETROMINOS[tipo_forma]['formas'][0] # Usa el primer estado de rotación.
    ancho_forma = len(forma_inicial[0]) if forma_inicial else 0
    # Centra basado en el ancho de la cuadrícula y el ancho de la forma.
    inicio_x = ANCHO_CUADRICULA // 2 - ancho_forma // 2

    # Comienza la pieza por encima de la cuadrícula visible.
    # Ajusta según la altura de la forma para permitir rotación inicial segura.
    alto_forma = len(forma_inicial)
    # Comienza completamente por encima de los límites visibles de la cuadrícula.
    inicio_y = -alto_forma

    return Pieza(tipo_forma, inicio_x, inicio_y)