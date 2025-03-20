print("== LISTA BENEFICIOS ==\n")

anio_ini = int(input("Introduce el año inicial:\n"))
anio_fin = int(input("Introduce el año final:\n"))
años = anio_fin - anio_ini

ingresos = []
gastos = []
anios = []
beneficios = []
beneficios_bool = []

for i in range(años + 1):
    anio_actual = anio_ini + i
    ingr = float(input(f"Introduce los ingresos del año {anio_actual}:\n"))
    gast = float(input(f"Introduce los gastos del año {anio_actual}:\n"))
    ingresos.append(ingr)
    gastos.append(gast)
    anios.append(anio_actual)
    beneficio = ingr - gast
    beneficios.append(beneficio)
    beneficios_bool.append(beneficio > 0)

for i in range(len(anios)):
    print(f"Año: {anios[i]}\nIngresos: {ingresos[i]}\nGastos: {gastos[i]}\nBeneficio: {beneficios[i]}\nHubo Beneficios: {beneficios_bool[i]}\n")

anios_con_beneficios = []
anios_con_perdidas = []

for i in range(len(beneficios_bool)):
    if beneficios_bool[i]:
        anios_con_beneficios.append(anios[i])
    else:
        anios_con_perdidas.append(anios[i])

print(f"Años con beneficios: {anios_con_beneficios}")
print(f"Años con pérdidas: {anios_con_perdidas}")
