# src/juego.py
import pygame
import sys
import time
import pprint

# Importar componentes necesarios
from . import configuracion as conf # Importa configuracion usando el alias conf
from .estado_juego import EstadoJuego
from .pieza import Pieza, obtener_pieza_aleatoria
from .cuadricula import (crear_cuadricula, es_posicion_valida, bloquear_pieza,
                   limpiar_lineas, calcular_posicion_fantasma)
# Se importan las funciones de dibujo necesarias
from .dibujo import (dibujar_lineas_cuadricula, dibujar_borde_campo_juego, dibujar_bloques_cuadricula,
                    dibujar_pieza, dibujar_pieza_fantasma, dibujar_siguiente_pieza, dibujar_ui,
                    dibujar_menu_principal, dibujar_menu_pausa, dibujar_menu_opciones,
                    dibujar_fin_juego)
from .sonido import crear_sonido_colocar

class Juego:
    def __init__(self):
        """Inicializa Pygame, sonido, pantalla, reloj y estado inicial del juego."""
        try:
            # Pre-inicializa el mezclador con configuraciones recomendadas.
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.init()
            pygame.font.init()
            # Inicialización del mezclador (después de pygame.init).
            print("Inicializando mezclador DESPUÉS de pygame.init()...")
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                config_mezclador = pygame.mixer.get_init()
                if config_mezclador: print(f"Mezclador inicializado con config: Freq={config_mezclador[0]}, Formato={config_mezclador[1]}, Canales={config_mezclador[2]}")
                else: print("ERROR: pygame.mixer.get_init() devolvió None!", file=sys.stderr)
            except pygame.error as err_mezclador:
                 print(f"ERROR: Falló la inicialización del mezclador: {err_mezclador}", file=sys.stderr)
                 pygame.quit(); sys.exit(1) # Salir si la inicialización del sonido falla.
        except pygame.error as e:
            print(f"Error inicializando el núcleo de Pygame: {e}", file=sys.stderr)
            sys.exit(1)

        self.pantalla = pygame.display.set_mode((conf.ANCHO_PANTALLA, conf.ALTO_PANTALLA))
        pygame.display.set_caption("PyTetris - Menú Opciones") # Título de la ventana.
        self.reloj = pygame.time.Clock()

        # --- Configuración de Sonido ---
        self.sonido_colocar = crear_sonido_colocar()
        # Flag para controlar si el sonido está activado.
        self.es_sonido_activado = True

        # --- Estado del Juego y Menús ---
        self.estado_juego = EstadoJuego.MENU
        self.en_ejecucion = True
        self.opciones_menu_principal = ["Jugar", "Opciones", "Salir"]
        self.opcion_menu_seleccionada = 0
        self.opciones_menu_pausa = ["Reanudar", "Menú Principal", "Salir del Juego"]
        self.opcion_pausa_seleccionada = 0
        # Opciones disponibles en el menú de configuración.
        self.opciones_menu_opciones = ["Sonidos", "Volver"]
        # Índice de la opción seleccionada en el menú de configuración.
        self.opcion_opciones_seleccionada = 0

        # --- Variables de Jugabilidad ---
        self.posiciones_bloqueadas = {}
        self.cuadricula = crear_cuadricula()
        self.pieza_actual = None
        self.siguiente_pieza = None
        self.puntuacion = 0
        self.total_lineas_limpiadas = 0
        self.nivel = 1
        self.velocidad_caida = conf.VELOCIDAD_CAIDA_INICIAL
        self.tiempo_caida = 0
        pygame.key.set_repeat(conf.RETRASO_REPETICION_TECLA, conf.INTERVALO_REPETICION_TECLA)
        # Inicializa/resetea variables de la partida.
        self._reiniciar_variables_juego()

    def _reiniciar_variables_juego(self):
        """Reinicia las variables específicas de una sesión de juego (puntuación, piezas, cuadrícula)."""
        self.posiciones_bloqueadas = {}
        try:
            # Obtiene la primera pieza y la siguiente.
            self.pieza_actual = obtener_pieza_aleatoria()
            # Asegura que la siguiente no sea igual a la actual inmediatamente.
            self.siguiente_pieza = obtener_pieza_aleatoria(self.pieza_actual.tipo)
        except Exception as e:
            print(f"ERROR: Falló al obtener las piezas iniciales: {e}", file=sys.stderr)
            # TODO: Considerar manejo explícito si falla la generación de piezas.
            self.pieza_actual = None
            self.siguiente_pieza = None
        self.puntuacion = 0
        self.total_lineas_limpiadas = 0
        self.nivel = 1
        self.velocidad_caida = self._calcular_velocidad_caida()
        self.tiempo_caida = 0
        # Crea la cuadrícula basada en las (ahora vacías) posiciones bloqueadas.
        self.cuadricula = crear_cuadricula(self.posiciones_bloqueadas)

    def _calcular_puntuacion(self, lineas_limpiadas):
        """Calcula la puntuación basada en las líneas limpiadas a la vez y el nivel actual."""
        if lineas_limpiadas <= 0 or lineas_limpiadas not in conf.PUNTOS_POR_LINEA: return 0
        puntuacion_base = conf.PUNTOS_POR_LINEA[lineas_limpiadas]
        incremento_puntuacion = puntuacion_base * self.nivel
        return incremento_puntuacion

    def _calcular_nivel(self):
        """Calcula el nivel actual basado en el total de líneas limpiadas."""
        return (self.total_lineas_limpiadas // conf.LINEAS_POR_NIVEL) + 1

    def _calcular_velocidad_caida(self):
        """Calcula la velocidad de caída (tiempo por paso) basado en el nivel actual."""
        # Asegura que la velocidad no sea menor que el mínimo definido.
        velocidad = max(conf.VELOCIDAD_CAIDA_MINIMA, conf.VELOCIDAD_CAIDA_INICIAL - (self.nivel - 1) * conf.DECREMENTO_VELOCIDAD_CAIDA)
        return velocidad

    def _gestionar_entrada(self):
        """Procesa todos los eventos de Pygame y actualiza el estado del juego en consecuencia."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.en_ejecucion = False
                return
            # --- Dirigir entrada según el estado ---
            if self.estado_juego == EstadoJuego.MENU: self._gestionar_entrada_menu(evento)
            elif self.estado_juego == EstadoJuego.OPCIONES: self._gestionar_entrada_opciones(evento)
            elif self.estado_juego == EstadoJuego.PAUSADO: self._gestionar_entrada_pausa(evento)
            elif self.estado_juego == EstadoJuego.FIN_JUEGO: self._gestionar_entrada_fin_juego(evento)
            elif self.estado_juego == EstadoJuego.JUGANDO: self._gestionar_entrada_jugando(evento)

    def _gestionar_entrada_menu(self, evento):
        """Gestiona la entrada específica para el estado MENU."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                # Navega hacia arriba en el menú (circular).
                self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada - 1) % len(self.opciones_menu_principal)
            elif evento.key == pygame.K_DOWN:
                # Navega hacia abajo en el menú (circular).
                self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada + 1) % len(self.opciones_menu_principal)
            elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                # Selecciona la opción actual.
                self._gestionar_seleccion_menu(self.opciones_menu_principal[self.opcion_menu_seleccionada])
            elif evento.key == pygame.K_ESCAPE:
                 # Salir del juego desde el menú.
                 self.en_ejecucion = False

    def _gestionar_entrada_opciones(self, evento):
        """Gestiona la entrada específica para el estado OPCIONES."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.opcion_opciones_seleccionada = (self.opcion_opciones_seleccionada - 1) % len(self.opciones_menu_opciones)
            elif evento.key == pygame.K_DOWN:
                self.opcion_opciones_seleccionada = (self.opcion_opciones_seleccionada + 1) % len(self.opciones_menu_opciones)
            elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                accion_seleccionada = self.opciones_menu_opciones[self.opcion_opciones_seleccionada]
                if accion_seleccionada == "Sonidos":
                    # Cambia el estado del flag de sonido.
                    self.es_sonido_activado = not self.es_sonido_activado
                    print(f"Sonidos Activados: {self.es_sonido_activado}") # Feedback en consola.
                    # Opcional: Reproducir sonido de confirmación de UI.
                elif accion_seleccionada == "Volver":
                    self.estado_juego = EstadoJuego.MENU # Volver al menú principal.
                    # Opcional: Resaltar "Opciones" al volver al menú principal.
                    self.opcion_menu_seleccionada = 1
            elif evento.key == pygame.K_ESCAPE:
                 self.estado_juego = EstadoJuego.MENU # Escape también vuelve atrás.
                 # Opcional: Resaltar "Opciones" al volver al menú principal.
                 self.opcion_menu_seleccionada = 1

    def _gestionar_entrada_pausa(self, evento):
        """Gestiona la entrada específica para el estado PAUSADO."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP: self.opcion_pausa_seleccionada = (self.opcion_pausa_seleccionada - 1) % len(self.opciones_menu_pausa)
            elif evento.key == pygame.K_DOWN: self.opcion_pausa_seleccionada = (self.opcion_pausa_seleccionada + 1) % len(self.opciones_menu_pausa)
            elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER: self._gestionar_seleccion_pausa(self.opciones_menu_pausa[self.opcion_pausa_seleccionada])
            elif evento.key == pygame.K_ESCAPE or evento.key == pygame.K_p: self.estado_juego = EstadoJuego.JUGANDO # Reanudar con Escape o P.

    def _gestionar_entrada_fin_juego(self, evento):
        """Gestiona la entrada específica para el estado FIN_JUEGO."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                # Reinicia el juego.
                self._reiniciar_variables_juego()
                self.estado_juego = EstadoJuego.JUGANDO
            elif evento.key == pygame.K_m or evento.key == pygame.K_ESCAPE:
                 # Vuelve al menú principal.
                 self.estado_juego = EstadoJuego.MENU
                 self.opcion_menu_seleccionada = 0 # Resalta "Jugar".

    def _gestionar_entrada_jugando(self, evento):
        """Gestiona la entrada específica para el estado JUGANDO."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_p:
                # Pausa el juego.
                self.estado_juego = EstadoJuego.PAUSADO
                self.opcion_pausa_seleccionada = 0 # Resalta "Reanudar".
                return # Salir para no procesar más teclas en este frame.
            # Solo procesar movimiento si hay una pieza activa.
            if self.pieza_actual:
                if evento.key == pygame.K_LEFT: self._intentar_mover(-1, 0) # Mover izquierda.
                elif evento.key == pygame.K_RIGHT: self._intentar_mover(1, 0) # Mover derecha.
                elif evento.key == pygame.K_DOWN:
                    # Mover abajo (acelerar caída).
                    movido = self._intentar_mover(0, 1)
                    if movido: self.tiempo_caida = 0 # Reiniciar temporizador de caída por gravedad.
                elif evento.key == pygame.K_UP or evento.key == pygame.K_x: self._intentar_rotar(sentido_horario=True) # Rotar horario.
                elif evento.key == pygame.K_z: self._intentar_rotar(sentido_horario=False) # Rotar antihorario.
                elif evento.key == pygame.K_SPACE: self._caida_fuerte() # Caída instantánea.

    def _gestionar_seleccion_menu(self, seleccion):
        """Ejecuta la acción basada en la selección del menú principal."""
        if seleccion == "Jugar":
            self._reiniciar_variables_juego()
            self.estado_juego = EstadoJuego.JUGANDO
        elif seleccion == "Opciones":
            # --- Transición al Menú de Opciones ---
            self.estado_juego = EstadoJuego.OPCIONES
            self.opcion_opciones_seleccionada = 0 # Reiniciar selección en menú de opciones.
        elif seleccion == "Salir":
            self.en_ejecucion = False

    def _gestionar_seleccion_pausa(self, seleccion):
        """Ejecuta la acción basada en la selección del menú de pausa."""
        if seleccion == "Reanudar": self.estado_juego = EstadoJuego.JUGANDO
        elif seleccion == "Menú Principal":
            self.estado_juego = EstadoJuego.MENU
            self.opcion_menu_seleccionada = 0 # Resalta "Jugar".
        elif seleccion == "Salir del Juego": self.en_ejecucion = False

    def _intentar_mover(self, dx, dy):
        """Intenta mover la pieza actual. Devuelve True si tiene éxito."""
        if not self.pieza_actual: return False
        # La validación usa self.posiciones_bloqueadas directamente.
        if es_posicion_valida(self.pieza_actual, self.posiciones_bloqueadas,
                             verificar_x=self.pieza_actual.x + dx,
                             verificar_y=self.pieza_actual.y + dy):
            # Actualiza la posición de la pieza si el movimiento es válido.
            self.pieza_actual.x += dx
            self.pieza_actual.y += dy
            return True
        return False # Movimiento inválido.

    def _intentar_rotar(self, sentido_horario=True):
        """Intenta rotar la pieza actual, incluyendo 'wall kicks' básicos."""
        if not self.pieza_actual: return
        # Guarda el estado original antes de intentar rotar.
        rotacion_original = self.pieza_actual.rotacion
        x_original = self.pieza_actual.x
        y_original = self.pieza_actual.y
        self.pieza_actual.rotar(sentido_horario)

        # Comprueba si la nueva rotación es válida en la posición actual.
        if es_posicion_valida(self.pieza_actual, self.posiciones_bloqueadas):
            return # Rotación simple funcionó.

        # Si la rotación simple falla, intenta 'wall kicks' (desplazamientos).
        # Desplazamientos comunes para intentar encajar la pieza rotada.
        desplazamientos_kick = [(1, 0), (-1, 0), (2, 0), (-2, 0), (0, -1), (0, -2)] # Desplazamientos de 'wall kick' considerados.
        for dx, dy in desplazamientos_kick:
             x_prueba = x_original + dx
             y_prueba = y_original + dy
             if es_posicion_valida(self.pieza_actual, self.posiciones_bloqueadas, verificar_x=x_prueba, verificar_y=y_prueba):
                 # Si una posición con 'kick' es válida, aplica el desplazamiento.
                 self.pieza_actual.x = x_prueba
                 self.pieza_actual.y = y_prueba
                 return # Kick exitoso.

        # Si la rotación y todos los kicks fallaron, revierte la rotación y posición.
        self.pieza_actual.x = x_original
        self.pieza_actual.y = y_original
        self.pieza_actual.rotacion = rotacion_original
        # Asegura que la forma visual coincida con la rotación revertida.
        self.pieza_actual.forma = self.pieza_actual.formas[rotacion_original]

    def _caida_fuerte(self):
        """Deja caer instantáneamente la pieza y activa el bloqueo."""
        if not self.pieza_actual: return
        # calcular_posicion_fantasma usa self.posiciones_bloqueadas.
        fantasma_y = calcular_posicion_fantasma(self.pieza_actual, self.posiciones_bloqueadas)
        distancia_caida = fantasma_y - self.pieza_actual.y
        if distancia_caida > 0:
            self.pieza_actual.y = fantasma_y
            # Fuerza la comprobación de bloqueo en el siguiente ciclo de actualización.
            self.tiempo_caida = self.velocidad_caida

    def _actualizar(self, dt):
        """Actualiza la lógica del juego (principalmente gravedad y bloqueo)."""
        # Solo actualiza si se está jugando y hay una pieza activa.
        if self.estado_juego != EstadoJuego.JUGANDO or not self.pieza_actual: return

        self.tiempo_caida += dt # Acumula tiempo delta.
        # Si ha pasado suficiente tiempo para un paso de gravedad.
        if self.tiempo_caida >= self.velocidad_caida:
            self.tiempo_caida -= self.velocidad_caida # Resetea para el próximo paso.
            # Intenta mover la pieza hacia abajo por gravedad.
            if not self._intentar_mover(0, 1):
                # Si no se puede mover hacia abajo, bloquea la pieza y genera la siguiente.
                self._bloquear_y_generar()

    def _bloquear_y_generar(self):
        """Bloquea la pieza, limpia líneas, genera la siguiente, comprueba Fin de Juego y reproduce sonido (condicional)."""
        if not self.pieza_actual: return

        # Añade la pieza actual a las posiciones bloqueadas.
        bloquear_pieza(self.pieza_actual, self.posiciones_bloqueadas)
        # Opcional: Actualizar self.cuadricula (visualización basada en bloques).
        self.cuadricula = crear_cuadricula(self.posiciones_bloqueadas)

        # --- REPRODUCIR SONIDO CONDICIONALMENTE ---
        # Solo reproducir si el sonido existe Y el flag está activado.
        if self.sonido_colocar and self.es_sonido_activado:
            try:
                self.sonido_colocar.play()
            except pygame.error as e:
                 # Advierte si no se pudo reproducir el sonido.
                 print(f"Advertencia: No se pudo reproducir sonido_colocar: {e}", file=sys.stderr)
        # --- /REPRODUCIR SONIDO CONDICIONALMENTE ---

        # Limpia líneas completas y obtiene el nuevo diccionario de posiciones bloqueadas.
        lineas_limpiadas, self.posiciones_bloqueadas = limpiar_lineas(self.posiciones_bloqueadas)

        if lineas_limpiadas > 0:
            self.puntuacion += self._calcular_puntuacion(lineas_limpiadas)
            self.total_lineas_limpiadas += lineas_limpiadas
            nuevo_nivel = self._calcular_nivel()
            # Si se sube de nivel.
            if nuevo_nivel > self.nivel:
                self.nivel = nuevo_nivel
                self.velocidad_caida = self._calcular_velocidad_caida()
                print(f"¡Subida de Nivel! Nvl {self.nivel}, Vel {self.velocidad_caida:.3f}s")
            # Opcional: Recrear self.cuadricula tras limpiar líneas.
            self.cuadricula = crear_cuadricula(self.posiciones_bloqueadas)
            # Opcional: Reproducir sonido de limpieza de línea (condicional).

        # Prepara la siguiente pieza.
        tipo_ultima_pieza = self.pieza_actual.tipo # Guarda el tipo para evitar repetición inmediata.
        self.pieza_actual = self.siguiente_pieza
        if self.pieza_actual is None:
             # Error: No hay siguiente pieza. Transición a Fin Juego.
             print("ERROR: siguiente_pieza era None durante la secuencia de generación.", file=sys.stderr)
             self.estado_juego = EstadoJuego.FIN_JUEGO
             return
        # Genera una nueva "siguiente pieza", evitando el tipo de la que acaba de entrar en juego.
        self.siguiente_pieza = obtener_pieza_aleatoria(tipo_ultima_pieza)

        # Comprobación de Fin de Juego: Validez de la posición de generación.
        es_generacion_valida = es_posicion_valida(self.pieza_actual, self.posiciones_bloqueadas)
        if not es_generacion_valida:
            self.estado_juego = EstadoJuego.FIN_JUEGO
            print(f"FIN DEL JUEGO activado! La generación falló debido a solapamiento.")
            # Opcional: Reproducir sonido de fin de juego (condicional).

    def _dibujar(self):
        """Dibuja todos los elementos del juego basados en el estado."""
        self.pantalla.fill(conf.NEGRO) # Limpia la pantalla.

        # --- Dibujar según el Estado del Juego ---
        if self.estado_juego == EstadoJuego.MENU:
            dibujar_menu_principal(self.pantalla, self.opcion_menu_seleccionada, self.opciones_menu_principal)
        elif self.estado_juego == EstadoJuego.OPCIONES:
            # Se pasa el estado de activación del sonido a la función de dibujo.
            dibujar_menu_opciones(self.pantalla, self.opcion_opciones_seleccionada, self.opciones_menu_opciones, self.es_sonido_activado)
        elif self.estado_juego in [EstadoJuego.JUGANDO, EstadoJuego.PAUSADO, EstadoJuego.FIN_JUEGO]:
            # Dibuja elementos de jugabilidad comunes a estos estados.
            dibujar_lineas_cuadricula(self.pantalla)
            dibujar_borde_campo_juego(self.pantalla)
            # Crea la cuadrícula actual para dibujar los bloques bloqueados.
            cuadricula_actual_para_dibujo = crear_cuadricula(self.posiciones_bloqueadas)
            dibujar_bloques_cuadricula(self.pantalla, cuadricula_actual_para_dibujo)
            dibujar_ui(self.pantalla, self.puntuacion, self.nivel, self.total_lineas_limpiadas)
            if self.siguiente_pieza: dibujar_siguiente_pieza(self.pantalla, self.siguiente_pieza)

            # Dibuja la pieza actual y fantasma solo si se está jugando.
            if self.estado_juego == EstadoJuego.JUGANDO and self.pieza_actual:
                # Calcula y dibuja la pieza fantasma.
                fantasma_y = calcular_posicion_fantasma(self.pieza_actual, self.posiciones_bloqueadas)
                dibujar_pieza_fantasma(self.pantalla, self.pieza_actual, fantasma_y)
                # Dibuja la pieza activa.
                dibujar_pieza(self.pantalla, self.pieza_actual)
            elif self.estado_juego == EstadoJuego.FIN_JUEGO and self.pieza_actual:
                 # Muestra la pieza que causó el fin del juego en su posición final.
                 dibujar_pieza(self.pantalla, self.pieza_actual)

            # Dibuja superposiciones si está pausado o es fin de juego.
            if self.estado_juego == EstadoJuego.PAUSADO:
                dibujar_menu_pausa(self.pantalla, self.opcion_pausa_seleccionada, self.opciones_menu_pausa)
            elif self.estado_juego == EstadoJuego.FIN_JUEGO:
                dibujar_fin_juego(self.pantalla) # Superposición de Fin de Juego.

        pygame.display.flip() # Actualiza la pantalla completa.

    def ejecutar(self):
        """Bucle principal del juego."""
        self.en_ejecucion = True
        while self.en_ejecucion:
            # Calcula el tiempo delta (dt) desde el último frame.
            dt = self.reloj.tick(60) / 1000.0
            # Gestiona la entrada del usuario.
            self._gestionar_entrada()
            # Actualiza el estado del juego (movimiento, lógica).
            self._actualizar(dt)
            # Dibuja el frame actual.
            self._dibujar()

        # Al salir del bucle (self.en_ejecucion es False).
        pygame.quit()
        print("Pygame cerrado.")