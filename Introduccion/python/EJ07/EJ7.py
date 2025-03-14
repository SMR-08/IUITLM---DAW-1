print("==== BONOLOTO ====\n")
combinacion = []
combinacion_ganadora = [7, 13, 21, 37, 46, 49]
regex = ["Primera","Segunda", "Tercera", "Cuarta", "Quinta", "Sexta"]
 
is_ok = False
indice = 0
while is_ok == False:
    prm_lect = int(input(f"Introduce la {regex[indice]} pareja de la combinacion {combinacion}\n"))
    if 0 <= prm_lect < 50:
        combinacion.append(prm_lect)
        indice += 1
    if len(combinacion) == len(combinacion_ganadora):
        is_ok = True

# Itera sobre la lista 'combinacion', convirtiendo cada número a una cadena.
# Si el número es diferente de 0, se elimina cualquier cero a la izquierda ('0' prefijos) usando lstrip('0'). El resultado se convierte de nuevo a un entero.
# Si el número es 0, se mantiene como 0.
# El resultado final es una nueva lista 'combinacion' donde se han eliminado los ceros a la izquierda de los números (excepto si el número original es 0).
combinacion = [int(str(num).lstrip('0')) if num != 0 else 0 for num in combinacion]

if combinacion == combinacion_ganadora:
    print("Ganaste")
else:
    indice = 0
    no_coincidentes = []
    for num in combinacion:
        indice +=1
        if num != combinacion_ganadora[indice -1]:
            no_coincidentes.append(num)
    print(f"Los números que NO coinciden son: {no_coincidentes}")