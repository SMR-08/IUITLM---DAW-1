class Coche:
    """Clase para representar un coche."""

    def __init__(self, marca, modelo, año):
        """Inicializa los atributos de la clase coche."""
        self.marca = marca
        self.modelo = modelo
        self.año = año

    def mostrar_info(self):
        """Imprime la información del coche."""
        print(f"Marca: {self.marca}, Modelo: {self.modelo}, Año: {self.año}")


if __name__ == '__main__':
    
    # Crear lista de coches
    coches = [
        Coche("Toyota", "Corolla", 2020),
        Coche("Honda", "Civic", 2021),
        Coche("Ford", "Mustang", 2022),
    ]

    # Mostrar información de todos los coches
    for coche in coches:
        coche.mostrar_info()