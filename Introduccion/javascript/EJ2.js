class Producto {
    constructor(nombre, precio, cantidad) {
        this.nombre = nombre
        this.precio = precio
        this.cantidad = cantidad
    }
}

class Inventario {
    constructor(longitud) {
        this.lista_producto = [] // Inicializar como un array vacío
    }
    agregar(producto) {
        this.lista_producto.push(producto);
    }
    eliminar(nombre) {
        this.lista_producto = this.lista_producto.filter(producto => producto.nombre !== nombre);
    }
    calcular() {
        return this.lista_producto.reduce((suma, producto) => suma + producto.precio * producto.cantidad, 0);
    }
}
const inventario = new Inventario();
const producto1 = new Producto("Manzana", 2000, 50);
const producto2 = new Producto("Naranja", 1000, 30);
const producto3 = new Producto("Pera", 1500, 40);

inventario.agregar(producto1);
inventario.agregar(producto2);
inventario.agregar(producto3);

console.log(inventario.lista_producto);

inventario.eliminar("Naranja");

console.log(inventario.lista_producto);

console.log(inventario.calcular());