class Animal:
    def hacer_sonido(self) -> str: # Añadido tipo de retorno (opcional pero bueno)
        """Devuelve un sonido genérico."""
        # print("Sonido Genérico...") 
        return "Sonido Genérico..."

class Perro(Animal):
    def hacer_sonido(self) -> str:
        """Devuelve el ladrido del perro."""
        # print("Guau...") 
        return "Guau..."

class Gato(Animal):
    def hacer_sonido(self) -> str:
        """Devuelve el maullido del gato."""
        # print("Miau...") 
        return "Miau..."
    
if __name__ == '__main__':
    # Crear instacias de cada objeto
    perro1 = Perro()
    gato1 = Gato()
    perro2 = Perro()
    gato2 = Gato()
    # Creamos la lista de esas instancias
    animales = [perro1, gato1, perro2, gato2]
    # iteramos hacer sonido
    for animal in animales:
        animal.hacer_sonido()
