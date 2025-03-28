<?php
    session_start(); // Iniciar la sesión.
?>
<!DOCTYPE html>
<html>
<head>
    <title>Menú Principal del Banco</title>
    <link rel="stylesheet" href="/css/estilos.css">
</head>
<body>
    <!-- Contenedor principal de la página con clase común contenedor-pagina -->
    <div class="contenedor-pagina contenedor-banco">
        <!--  Contenedor para los botones de login/registro/logout en la parte superior derecha -->
        <div class="top-botones">
            <?php
                // Verificar si el usuario ha iniciado sesión.
                if (isset($_SESSION["sesion_iniciada"]) && $_SESSION["sesion_iniciada"] === true) {
                    // Usuario ha iniciado sesión, mostrar botón de cerrar sesión.
                    echo "<a href='php/logout.php' class='boton-primario'>Cerrar Sesión</a>";
                } else {
                    // Usuario no ha iniciado sesión, mostrar botones de inicio de sesión/registro.
                    echo "<a href='login.html' class='boton-primario'>Iniciar Sesión</a>";
                    echo "<a href='registro.html' class='boton-primario'>Registrarse</a>";
                }
            ?>
        </div>

        <h2>Bienvenido a Banco (nombre en proceso)!</h2>

        <?php
            // Verificar si el usuario ha iniciado sesión.
            if (isset($_SESSION["sesion_iniciada"]) && $_SESSION["sesion_iniciada"] === true) {
                // Usuario ha iniciado sesión.
                echo "<h3>Tu Información de Cuenta:</h3>";
                // Mostrar información del usuario almacenada en la sesión.
                // Usar htmlspecialchars para prevenir ataques XSS al mostrar datos del usuario.
                if (isset($_SESSION["dni_usuario_plano"])) {
                     echo "<p>DNI: " . htmlspecialchars($_SESSION["dni_usuario_plano"]) . "</p>";
                } else {
                     echo "<p>DNI: No disponible</p>"; // Fallback si el DNI plano no fue almacenado.
                }
                // Añadir marcadores de posición para otra información o acciones potenciales.
                echo "<p><i>Más detalles de la cuenta o acciones pueden ser añadidas aquí.</i></p>";


            } else {
                // Usuario no ha iniciado sesión, mensaje ya no necesario aquí porque los botones estan arriba.
            }
        ?>
    </div>
</body>
</html>