// file: js/script.js (Archivo de ejemplo)

// Espera a que el contenido del DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", function() {
    // Obtiene referencias a los elementos del DOM por su ID
    const titulo = document.getElementById("titulo"); // Asume que existe un <h1 id="titulo">
    const boton = document.getElementById("miBoton"); // Asume que existe un <button id="miBoton">

    // Verifica si los elementos existen antes de añadir listeners
    if (titulo && boton) {
        // Define una función que se ejecutará cuando se haga clic en el botón
        function cambiarTitulo() {
            titulo.textContent = "¡Hiciste clic!"; // Cambia el texto del h1 (Traducido)
            titulo.style.color = "blue";         // Cambia el color del texto del h1 (Cambiado a azul para ejemplo)
            console.log("El título ha sido cambiado."); // Mensaje en consola
        }

        // Asocia la función cambiarTitulo al evento 'click' del botón
        boton.addEventListener("click", cambiarTitulo);
        console.log("Listener de clic añadido al botón.");

    } else {
        // Informa si alguno de los elementos no fue encontrado
        if (!titulo) console.error("Elemento con id 'titulo' no encontrado.");
        if (!boton) console.error("Elemento con id 'miBoton' no encontrado.");
    }
});