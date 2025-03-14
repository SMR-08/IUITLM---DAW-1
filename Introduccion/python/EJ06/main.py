# main.py
from persona import Persona
from EJ6 import truco_o_trato

if __name__ == "__main__":
    personas_ejemplo = [
        Persona("Juan", 6, 110),
        Persona("Maria", 7, 120),
        Persona("Pedro", 8, 130),
        Persona("Ana", 9, 115)
    ]

    # Ejemplo de Truco
    resultado_truco = truco_o_trato(True, personas_ejemplo)
    print(f"Truco: {resultado_truco}")

    # Ejemplo de Trato
    resultado_trato = truco_o_trato(False, personas_ejemplo)
    print(f"Trato: {resultado_trato}")
