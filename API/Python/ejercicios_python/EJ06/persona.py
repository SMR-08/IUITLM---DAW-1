class Persona:
    """
    Clase que representa a una persona con nombre, edad y altura.
    """
    def __init__(self, nombre, edad, altura):
        if not isinstance(nombre, str):
            raise TypeError("El nombre debe ser una cadena.")
        if not isinstance(edad, int) or edad < 0:
            raise ValueError("La edad debe ser un entero positivo.")
        if not isinstance(altura, (int, float)) or altura < 0:
            raise ValueError("La altura debe ser un número positivo.")

        self.nombre = nombre
        self.edad = edad
        self.altura = altura

    def __str__(self):
        return f"Nombre: {self.nombre}, Edad: {self.edad}, Altura: {self.altura}"