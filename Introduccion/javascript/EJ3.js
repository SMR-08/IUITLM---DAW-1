class Libro {
    constructor(titulo,autor,anio_pub,num_copias) {
        this.titulo = titulo;
        this.autor = autor;
        this.anio_pub = anio_pub;
        this.num_copias = num_copias;
    }

    toString() {
        return `Título: ${this.titulo}, Autor: ${this.autor}, Año: ${this.anio_pub}, Copias: ${this.num_copias}`;
    }
}
class Biblioteca {
    constructor() {
        this.lista_libro = []
    }
    /**
     * Solo agrega un libro
     */
    agregar(libro) {
        this.lista_libro.push(libro);
    }
    /**
     * Solo elimina un libro por titulo dado
     */
    eliminar(titulo) {
        this.lista_libro = this.lista_libro.filter(libro => libro.titulo !== titulo);
    }
    /**
     * Decrementa en uno num_cop de un Libro de titulo dado
     */
    prestar(titulo) {
        const libro = this.lista_libro.find(libro => libro.titulo === titulo);
        if (libro) {
            libro.num_copias--;
        }
    }
    /**
     * Incrementa en uno el num_cop de un Libro de titulo dado
     */
    devolver(titulo) {
        const libro = this.lista_libro.find(libro => libro.titulo === titulo);
        if (libro) {
            libro.num_copias++;
        }
    }
    /**
     * devuelve la suma de todas las copias actuales
     */
    calular() {
        return this.lista_libro.reduce((total, libro) => total + libro.num_copias, 0);
    }
    toString() {
            return this.lista_libro.map(libro => libro.toString()).join('\n');
    }
}
    const libro1 = new Libro("Cien años de soledad","Gabriel García Márquez",1967,5);
    const libro2 = new Libro("El señor de los anillos","J.R.R. Tolkien",1954,3);
    const libro3 = new Libro("1984","George Orwell",1949,7);

    const biblioteca = new Biblioteca();

    biblioteca.agregar(libro1);
    console.log("Biblioteca después de agregar libro1:", biblioteca);
    biblioteca.agregar(libro2);
    console.log("Biblioteca después de agregar libro2:", biblioteca);
    biblioteca.agregar(libro3);
    console.log("Biblioteca después de agregar libro3:", biblioteca);

    biblioteca.prestar("Cien años de soledad");
    console.log("Biblioteca después de prestar 'Cien años de soledad':", biblioteca);
    biblioteca.devolver("El señor de los anillos");
    console.log("Biblioteca después de devolver 'El señor de los anillos':", biblioteca);
    biblioteca.eliminar("1984");
    console.log("Biblioteca después de eliminar '1984':", biblioteca);

    console.log("Número total de copias:", biblioteca.calular());
