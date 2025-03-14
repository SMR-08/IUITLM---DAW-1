document.addEventListener("DOMContentLoaded", function() {
    const titulo = document.getElementById("titulo");
    const boton = document.getElementById("miBoton");

    // Define una función que se ejecutará cuando se haga clic en el botón
    function cambiarTitulo() {
        titulo.textContent = "¡Hiciste clic!"; // Cambia el texto del h1
        titulo.style.color = "red";         // Cambia el color del texto del h1
    }

    // Asocia la función cambiarTitulo al evento.
    boton.addEventListener("click", cambiarTitulo);

});