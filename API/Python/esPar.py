# /API/Python/esPar.py

def es_par(numero):
    """
    Comprueba si un número es par.

    Args:
        numero: El número a comprobar (debe ser un entero).

    Returns:
        True si el número es par, False si es impar.
        Devuelve None si la entrada no es un entero.
    """
    try:
        numero = int(numero)  # Intentamos convertir a entero
        return numero % 2 == 0
    except ValueError:
        return None  # Manejo de error: la entrada no es un entero.