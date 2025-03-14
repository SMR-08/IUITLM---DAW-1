# python EJ05/EJ5.py
class Libro:
    """
    Representa un libro en una biblioteca.

    Atributos:
        titulo (str): El título del libro.
        autor (str): El autor del libro.
        fech_pub (str): La fecha de publicación del libro.
        num_cop (int): El número de copias disponibles del libro.
    """
    def __init__(self, titulo: str, autor: str, fech_pub: str, num_cop: int):
        from datetime import datetime
        self.titulo = titulo
        self.autor = autor
        # Convertir la fecha de publicación a un objeto datetime
        try:
            self.fech_pub = datetime.strptime(fech_pub, "%d-%m-%Y")
        except ValueError:
            raise ValueError("El formato de fecha debe ser DD-MM-YYYY")
        self.num_cop = num_cop
    def getCopias(self):
        return self.num_cop

class Biblioteca:
    def __init__(self):
        """
        Representa una biblioteca que contiene una colección de libros.

        Atributos:
            biblioteca (list): Una lista de objetos `libro` que representan los libros en la biblioteca.
        """
        self.biblioteca = []

    def agregarLibro(self, libro: Libro):
        """
        Agrega un nuevo libro a la biblioteca.

        Args:
            libro (Libro): El objeto Libro a agregar.

        Returns:
            bool: True si el libro se agregó correctamente, False si el libro ya existe en la biblioteca.
        """
        # Verificar si el libro ya existe (usando el título como identificador único)
        if not self.libro_existe(libro.titulo):
            self.biblioteca.append(libro)
            return True  # Operación exitosa
        else:
            return False  # Operación fallida

    def libro_existe(self, titulo:str):
        """Verifica si un libro existe en la biblioteca por su título.

        Args:
            titulo (str): El título del libro a verificar.

        Returns:
            bool: True si el libro existe, False en caso contrario.
        """
        for libro_actual in self.biblioteca:
            if libro_actual.titulo == titulo:
                return True
        return False

    def eliminarLibro(self, titulo:str):
        """Elimina un libro de la biblioteca por su título.

        Args:
            titulo (str): El título del libro a eliminar.

        Returns:
            bool: True si el libro fue eliminado, False si no se encontró.  Se reemplaza por un raise ValueError
        Raises:
            ValueError: Si no se encuentra el libro en la biblioteca.
        """
        for libro_actual in self.biblioteca:
            if libro_actual.titulo == titulo:
                self.biblioteca.remove(libro_actual)
                return  # Sale de la función después de eliminar el libro

        raise ValueError(f"No se encontró el libro con el título {titulo} en la biblioteca.")

    def consultar(self, autor=None):
        """Consulta los libros de la biblioteca.

        Si se proporciona un autor, lista solo los libros de ese autor.
        Si no se proporciona un autor, lista todos los libros de la biblioteca.

        Args:
            autor (str, optional): El autor de los libros a consultar. Defaults to None.
        """
        libros_a_mostrar = []

        if autor:  # Si se proporcionó un autor
            for libro_actual in self.biblioteca:
                if libro_actual.autor == autor:
                    libros_a_mostrar.append(libro_actual)
        else:  # Si no se proporcionó un autor
            libros_a_mostrar = self.biblioteca

        if not libros_a_mostrar: #No hay libros
            print("No hay libros que mostrar con los parámetros dados.")
        else: #Si hay libros
             for libro_actual in libros_a_mostrar:
                #Formateo de fech_pub a string DD-MM-YYYY
                print(f"Título: {libro_actual.titulo}, Autor: {libro_actual.autor}, Fecha de Publicación: {libro_actual.fech_pub.strftime('%d-%m-%Y')}, Número de Copias: {libro_actual.num_cop}")

    def prestarLibro(self, titulo:str):
        """Presta un libro de la biblioteca si hay copias disponibles.

        Args:
            titulo (str): El título del libro a prestar.

        Returns:
            bool: True si el libro fue prestado, False si no se encontró o no hay copias.
        """
        libro_encontrado = False
        indice = 0
        while indice < len(self.biblioteca) and not libro_encontrado:
            if self.biblioteca[indice].titulo == titulo:
                libro_encontrado = True
                if self.biblioteca[indice].num_cop > 0:
                    self.biblioteca[indice].num_cop -= 1
                    return True  # Operación exitosa
                else:
                    return False  # No hay copias disponibles
            else:
                indice += 1
        return False  # Libro no encontrado

    def devolverLibro(self, titulo:str):
        """Devuelve un libro a la biblioteca, incrementando el número de copias.

        Args:
            titulo (str): El título del libro a devolver.

        Returns:
            bool: True si el libro fue devuelto, False si no se encontró.
        """
        libro_encontrado = False
        indice = 0
        operacion_estado = False
        while indice < len(self.biblioteca) and not libro_encontrado:
            if self.biblioteca[indice].titulo == titulo:
                libro_encontrado = True
                self.biblioteca[indice].num_cop += 1
                operacion_estado = True
            else:
                indice +=1
        return operacion_estado


    def totalCopias(self):
        """Calcula el número total de copias de todos los libros en la biblioteca.

        Returns:
            int: El número total de copias.
        """
        total_copias = 0
        for libro_actual in self.biblioteca:
            total_copias += libro_actual.num_cop
        return total_copias