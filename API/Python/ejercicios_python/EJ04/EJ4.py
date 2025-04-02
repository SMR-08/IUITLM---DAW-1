class Cuenta:
    def __init__(self,titular,cantidad):
        """Inicializa los atributos de la clase Cuenta."""
        self.titular = titular
        self.cantidad = cantidad
    def consultar_saldo(self):
        """Consulta el saldo de la cuenta"""
        return self.cantidad
    def realizar_gasto(self, cantidad):
        """Reduce el saldo si hay suficiente saldo disponible."""
        if self.cantidad >= cantidad:
            self.cantidad -= cantidad
        else:
            print("Saldo insuficiente.")
    def consultar_titular(self):
        """Getter para el atributo titular."""
        return self.titular
    
class CuentaJoven (Cuenta):
    """Inicializa los atributos de la clase CuentaJoven"""
    def __init__(self, titular, cantidad, bonificacion,edad):
        """Inicializa la clase CuentaJoven con titular, cuenta y bonificación."""
        super().__init__(titular, cantidad)
        self.bonificacion = bonificacion
        self.edad = edad
    
    def get_bonificacion(self):
        """Getter para la bonificación."""
        return self.bonificacion

    def set_bonificacion(self, bonificacion):
        """Setter para la bonificación."""
        self.bonificacion = bonificacion
    
    def get_edad(self):
        """Getter para la edad."""
        return self.edad

    def set_edad(self, edad):
        """Setter para la edad."""
        self.edad = edad
        
    def TitularValido(self):
        """El titular debe ser mayor de 18 y menor de 25.
        args: edad
        return booleano
        """
        return 18 <= self.edad < 25
    def realizar_gasto(self, cantidad):
        """Sobrecarga de realizar_gasto para que solo un titular valido pueda efectuar la operacion.
           Comprueba la edad y, si es válida, llama al método realizar_gasto de la clase padre (Cuenta).
        """
        if self.TitularValido():
            cantidad_con_descuento = cantidad * (1 - self.bonificacion / 100)
            super().realizar_gasto(cantidad_con_descuento)
        else:
            raise ValueError("El titular no es válido para realizar esta operación.")
    def mostrar(self):
        """Muestra la información de la cuenta joven."""
        return f"Cuenta Joven {self.bonificacion}"
