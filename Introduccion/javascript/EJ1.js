class Estudiante {
    constructor(nombre,edad,curso) {
        this.nombre = nombre
        this.edad = edad
        this.curso = curso
    }
    /**
     * Imprime el nombre y curso del estudiante en forma de saludo.
     */
    presentarse() {
        console.log(this.nombre + " del curso: " + this.curso)
    }
}
let estudiantes = []
for (let i = 0; i < 3; i++) {
    let estudiante = new Estudiante("Estudiante" + i, 20 + i, "Curso" + i)
    estudiantes.push(estudiante)
}
for (let i = 0; i < estudiantes.length; i++) {
    estudiantes[i].presentarse()
}