from EJ4 import Cuenta, CuentaJoven


cuenta1 = Cuenta("Juan Perez", 1000)
print(f"Titular: {cuenta1.consultar_titular()}")
print(f"Saldo inicial: {cuenta1.consultar_saldo()}")
cuenta1.realizar_gasto(200)
print(f"Saldo después de gasto: {cuenta1.consultar_saldo()}")
cuenta1.realizar_gasto(1500)
print(f"Saldo después de gasto fallido: {cuenta1.consultar_saldo()}")



cuenta_joven1 = CuentaJoven("Maria Gomez", 500, 5,20)
print(f"Titular Cuenta Joven: {cuenta_joven1.consultar_titular()}")
print(f"Saldo inicial Cuenta Joven: {cuenta_joven1.consultar_saldo()}")
print(f"Bonificación Cuenta Joven: {cuenta_joven1.get_bonificacion()}")
print(cuenta_joven1.TitularValido())
cuenta_joven1.realizar_gasto(100)
print(f"Saldo después de gasto Cuenta Joven: {cuenta_joven1.consultar_saldo()}")


cuenta_joven2 = CuentaJoven("Pedro Ramirez", 300, 10,30)
print(cuenta_joven2.TitularValido())
try:
    cuenta_joven2.realizar_gasto(50)
except ValueError as e:
    print(e)
print(f"Saldo después de gasto Cuenta Joven: {cuenta_joven2.consultar_saldo()}")
print(cuenta_joven1.mostrar())
