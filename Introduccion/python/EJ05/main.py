# python EJ05/main.py
from EJ5 import Biblioteca, Libro
import datetime
if __name__ == "__main__":
    biblioteca = Biblioteca()

    libro1 = Libro("Cien años de soledad", "Gabriel García Márquez", "05-06-1967", 5)
    libro2 = Libro("El Quijote", "Miguel de Cervantes", "16-01-1605", 3)
    libro3 = Libro("1984", "Jorge Orwell", "08-06-1949", 7)
    
    biblioteca.agregarLibro(libro1)
    biblioteca.agregarLibro(libro2)
    biblioteca.agregarLibro(libro3)

    print("Consulta inicial:")
    biblioteca.consultar()

    print("\nConsulta por autor (Gabriel García Márquez):")
    biblioteca.consultar("Gabriel García Márquez")

    print("\nPrestar libro 'Cien años de soledad':")
    if biblioteca.prestarLibro("Cien años de soledad"):
        print("Libro prestado con éxito.")
        print(f"Quedan {libro1.getCopias()} copias")
    else:
        print("No se pudo prestar el libro.")

    print("\nConsulta después de prestar:")
    biblioteca.consultar()

    print("\nDevolver libro 'Cien años de soledad':")
    if biblioteca.devolverLibro("Cien años de soledad"):
        print("Libro devuelto con éxito.")
    else:
        print("No se pudo devolver el libro.")

    print("\nConsulta después de devolver:")
    biblioteca.consultar()

    print(f"\nTotal de copias en la biblioteca: {biblioteca.totalCopias()}")
    try:
        biblioteca.eliminarLibro("El Quijote")
        print("\n'El Quijote' eliminado.")
    except ValueError as e:
        print(f"\nError: {e}")

    print("\nConsulta final:")
    biblioteca.consultar()

    try:
        biblioteca.eliminarLibro("Libro Inexistente")
    except ValueError as e:
        print(f"\nError al eliminar: {e}")
    
    print("\nIntentar prestar un libro sin copias")
    biblioteca.prestarLibro("El Quijote")
    biblioteca.prestarLibro("El Quijote")
    biblioteca.prestarLibro("El Quijote")
    if biblioteca.prestarLibro("El Quijote"):
        print("Libro prestado con éxito.")
    else:
        print("No se pudo prestar el libro 'El Quijote' no tiene copias.")

    print("\nConsulta luego de intentar prestar sin copias:")
    biblioteca.consultar()