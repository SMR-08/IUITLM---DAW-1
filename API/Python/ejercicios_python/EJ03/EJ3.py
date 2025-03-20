class Animal:
    def hacer_sonido(self):  
        print("Sonido Genérico...")
class Perro(Animal):
    def hacer_sonido(self):  
        print("Guau...")
class Gato(Animal):
    def hacer_sonido(self):  
        print("Miau...")
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
