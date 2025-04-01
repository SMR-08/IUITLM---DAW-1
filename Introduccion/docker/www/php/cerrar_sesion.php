<?php
    // file: php/cerrar_sesion.php
    session_start(); // Iniciar sesión para poder destruirla

    // Desasigna todas las variables de sesión.
    $_SESSION = array();

    // Si se desea destruir la sesión completamente, borre también la cookie de sesión.
    if (ini_get("session.use_cookies")) {
        $params = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000,
            $params["path"], $params["domain"],
            $params["secure"], $params["httponly"]
        );
    }

    // Finalmente, destruye la sesión.
    session_destroy();

    // --- ACTUALIZAR UBICACIÓN DE REDIRECCIÓN ---
    header("Location: ../banco.php");
    exit();
?>