# main.py
import sys
import os
import pygame # Requerido para funcionalidad principal y manejo de errores.

# Bloque opcional para modificar sys.path si se ejecuta main.py directamente
# y las importaciones de 'src' fallan. Es preferible ejecutar como módulo.
# --- INICIO: Modificación opcional de sys.path ---
# directorio_script = os.path.dirname(os.path.abspath(__file__))
# directorio_padre = directorio_script
# if directorio_padre not in sys.path:
#     sys.path.insert(0, directorio_padre)
# --- FIN: Modificación opcional de sys.path ---

# Intenta importar componentes del juego desde el paquete 'src'.
# Requiere ejecución desde el directorio 'tetris' (o que 'tetris' esté en sys.path).
try:
    from src.juego import Juego
    from src.configuracion import ANCHO_PANTALLA, ALTO_PANTALLA # Usado para ventana de error.
except ImportError as e:
     print(f"Error importando módulos del juego: {e}")
     print("Asegúrese de ejecutar este script desde el directorio 'tetris'", file=sys.stderr)
     print(f"o ejecute como módulo: python -m main")
     print(f"sys.path actual: {sys.path}") # Ayuda a depurar problemas de ruta.
     # Intento de mostrar ventana de error básica si pygame se cargó parcialmente.
     try:
         pygame.init()
         pantalla = pygame.display.set_mode((600, 400)) # Tamaño básico de ventana.
         pygame.display.set_caption("Error de Importación")
         fuente = pygame.font.SysFont('arial', 20)
         texto_error1 = fuente.render("Error de Importación. No se encuentran los módulos 'src'.", 1, (255,0,0))
         texto_error2 = fuente.render("Ejecutar desde el directorio 'tetris' o usar 'python -m main'.", 1, (255,0,0))
         pantalla.fill((200, 200, 200))
         pantalla.blit(texto_error1, (20, 50))
         pantalla.blit(texto_error2, (20, 80))
         pygame.display.flip()
         while True: # Mantiene la ventana de error abierta.
             for evento in pygame.event.get():
                 if evento.type == pygame.QUIT: sys.exit(1)
             pygame.time.wait(100)
     except Exception:
         pass # Falla silenciosa si ni siquiera pygame básico puede mostrar el error.
     sys.exit(1) # Salida con código de error.

# Punto de entrada principal si el script se ejecuta directamente.
if __name__ == "__main__":
    # Asegura que Pygame esté inicializado (Juego.__init__ lo hace).
    # Manejo de errores para fallo de inicialización de Pygame.
    try:
        juego_tetris = Juego()
        juego_tetris.ejecutar()
    except pygame.error as error_pg:
        print(f"Ocurrió un error de Pygame: {error_pg}", file=sys.stderr)
        # Intento de mostrar error gráficamente si es posible.
        try:
            # Usa constantes importadas si están disponibles.
            pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
            pygame.display.set_caption("Error de Ejecución")
            fuente = pygame.font.SysFont('arial', 20)
            texto_error1 = fuente.render(f"Error de Pygame: {error_pg}", 1, (255,0,0))
            texto_error2 = fuente.render("El juego encontró un error y debe cerrarse.", 1, (255,0,0))
            pantalla.fill((50, 50, 50))
            pantalla.blit(texto_error1, (20, 50))
            pantalla.blit(texto_error2, (20, 80))
            pygame.display.flip()
            while True: # Mantiene la ventana de error abierta.
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT: break
                pygame.time.wait(100)
        except Exception:
            pass # Fallback a salida por consola.
        pygame.quit()
        sys.exit(1) # Indicar salida con error.
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}", file=sys.stderr)
        pygame.quit()
        sys.exit(1) # Indicar salida con error.