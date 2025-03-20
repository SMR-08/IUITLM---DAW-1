class Producto:
    """
    Representa un producto con su nombre, precio y cantidad
    """
    def __init__(self,nombre,precio,cantidad):
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
    def __str__(self):
        return f"Producto: {self.nombre}, Precio: {self.precio} y Cantidad: {self.cantidad}"

class Inventario:
    def __init__(self):
        self.productos = []
    def agregar_producto(self,producto):
        """
        Agrega producto al inventario.
        Args: 
            producto (Producto): Producto a meter.
        Errores:
            TypeError: Si el parametro no es una instancia Producto
            ValueError: Si ya existe un producto igual.
        """
        if not isinstance(producto, Producto):
            raise TypeError ("Solo se pueden agregar productos.")
        
        for i in self.productos:
            if i.nombre == producto.nombre:
                raise ValueError (f"Ya existe un producto con el nombre {i.nombre}")
            
        self.productos.append(producto)
            
    def eliminar_producto(self,nombre):
        estado = False
        """
        Elimina un producto de el inventario por su nombre
        Args:
            nombre (str): El nombre del producto a borrar
        Return:
            estado: (bool) True si lo borra, False si no puede.
        Devuelve:
            TypeError: Si el nombre no es una cadena.
        """
        if not isinstance (nombre, str):
            raise TypeError ("El nombre debe ser una cadena de texto")
        for i, producto in enumerate(self.productos):
            if producto.nombre == nombre:
                del self.productos[i]
                estado = True
            return estado # Devolvera True o False si ha borrado o no el Producto
    def calcular_valor_total(self):
        valor_total = 0
        """
        Calcula el valor total de los productos
        Return:
            valor_total (float): El valor total de el inventario
        """
        for producto in self.productos:
            valor_total += producto.precio * producto.cantidad
            
        return valor_total
    
    def __str__(self):
        salida = "Inventario\n"
        """
        Representacion de el inventario en cadena
        """
        if not self.productos:
            return "El inventario esta vacio."

        for producto in self.productos:
            salida += f"    -{producto}\n"
        salida += f"Productos en el inventario: {len(self.productos)}"
        return salida     
    