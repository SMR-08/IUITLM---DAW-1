from EJ1 import Producto, Inventario

inventario = Inventario()

producto1 = Producto("Camisa",20.0,50)

inventario.agregar_producto(producto1)

print(inventario)

inventario.eliminar_producto("Camisa")
numero = inventario.calcular_valor_total()


print (inventario)
print(numero)