<?php
    session_start(); // Iniciar la sesión.
?>
<!DOCTYPE html>
<html>
<head>
    <title>Menú Principal del Banco</title>
</head>
<body>
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

            // Proporcionar un enlace para cerrar sesión.
            echo "<p><a href='php/logout.php'>Cerrar Sesión</a></p>";

        } else {
            // Usuario no ha iniciado sesión, mostrar enlaces de inicio de sesión/registro.
            echo "<p>Por favor, inicia sesión o regístrate para acceder a tu cuenta.</p>";
            // Enlace a la página de inicio de sesión.
            echo "<p><a href='login.html'>Iniciar Sesión</a></p>";
            // Enlace a la página de registro.
            echo "<p><a href='registro.html'>Registrarse</a></p>";
        }
    ?>

</body>
</html>
