# truco_o_trato.py
import random
def generar_sustos():
    """Genera un susto aleatorio."""
    sustos = ["🎃", "👻", "💀", "🕷", "🕸", "🦇"]
    return random.choice(sustos)

def generar_dulces():
    """Genera un dulce aleatorio."""
    dulces = ["🍰", "🍬", "🍡", "🍭", "🍪", "🍫", "🧁", "🍩"]
    return random.choice(dulces)

def calcular_sustos(personas):
    """Calcula el número de sustos para cada persona y en total."""
    total_sustos = []
    for persona in personas:
        sustos_nombre = len(persona.nombre) // 2
        total_sustos.extend([generar_sustos() for _ in range(sustos_nombre)])

        sustos_edad = 2 if persona.edad % 2 == 0 else 0
        total_sustos.extend([generar_sustos() for _ in range(sustos_edad)])

    altura_total = sum(persona.altura for persona in personas)
    sustos_altura = (altura_total // 100) * 3
    total_sustos.extend([generar_sustos() for _ in range(sustos_altura)])

    return total_sustos

def calcular_dulces(personas):
    """Calcula el número de dulces para cada persona y en total."""
    total_dulces = []
    for persona in personas:
        dulces_nombre = len(persona.nombre)
        total_dulces.extend([generar_dulces() for _ in range(dulces_nombre)])

        dulces_edad = min(persona.edad // 3, 10)  # Maximo 10 dulces por edad.
        total_dulces.extend([generar_dulces() for _ in range(dulces_edad)])

        dulces_altura = min(persona.altura // 50, 3) * 2  # Maximo 150, que son 3 * 2 = 6 dulces.
        total_dulces.extend([generar_dulces() for _ in range(dulces_altura)]) # Gracias StackOverflow

    return total_dulces

def truco_o_trato(quiere_truco, personas):
    """Realiza truco o trato con un listado de personas."""
    if not isinstance(personas, list):
        return "Error: El listado de personas debe ser una lista."
    
    for persona in personas:
        if not isinstance(persona, object):  # Mejor verificación
            return "Error: Cada elemento de la lista debe ser un objeto Persona."

    if quiere_truco:
        resultado = calcular_sustos(personas)
    else:
        resultado = calcular_dulces(personas)
    return resultado