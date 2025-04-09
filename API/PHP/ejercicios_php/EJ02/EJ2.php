<?php
// File: /API/PHP/ejercicios_php/EJ02/EJ2.php
// Contiene la lógica del juego Adivina el Número, sin HTML.

/**
 * Inicia o reinicia la partida del juego "Adivina el Número".
 * Guarda el estado en la sesión de PHP.
 *
 * @return array Estado inicial del juego.
 */
function iniciarJuegoAdivina(): array
{
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

    $_SESSION['ej2_numero_secreto'] = rand(0, 100); // Usar prefijo para evitar colisiones
    $_SESSION['ej2_intentos'] = 0;
    $_SESSION['ej2_juego_terminado'] = false;

    return [
        'mensaje' => 'Nueva partida iniciada (EJ2). Adivina un número entre 0 y 100.',
        'intentos' => 0,
        'juego_terminado' => false
    ];
}

/**
 * Procesa un intento del usuario para el Ejercicio 2.
 *
 * @param int $numero_usuario El número introducido por el usuario.
 * @return array El resultado del intento.
 */
function procesarIntentoAdivina(int $numero_usuario): array
{
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

    if (!isset($_SESSION['ej2_numero_secreto']) || ($_SESSION['ej2_juego_terminado'] ?? true)) {
        return [
            'mensaje' => 'No hay partida activa (EJ2) o ya terminó. Inicia una nueva.',
            'intentos' => $_SESSION['ej2_intentos'] ?? 0,
            'juego_terminado' => true,
            'error' => true // Indicar que hubo un problema
        ];
    }

    $_SESSION['ej2_intentos']++;
    $intentos_actuales = $_SESSION['ej2_intentos'];
    $numero_secreto = $_SESSION['ej2_numero_secreto'];
    $mensaje_respuesta = "";
    $juego_terminado_actual = false;
    $error_flag = false; // Para errores de lógica que no terminan el juego

    // Validar rango por si acaso
    if ($numero_usuario < 0 || $numero_usuario > 100) {
        $mensaje_respuesta = "El número debe estar entre 0 y 100.";
        $_SESSION['ej2_intentos']--; // No contar como intento válido
        $intentos_actuales = $_SESSION['ej2_intentos'];
        $error_flag = true;
    } elseif ($numero_usuario > $numero_secreto) {
        $mensaje_respuesta = "El número secreto es menor.";
    } elseif ($numero_usuario < $numero_secreto) {
        $mensaje_respuesta = "El número secreto es mayor.";
    } else {
        $mensaje_respuesta = "¡Enhorabuena (EJ2)! Has acertado en " . $intentos_actuales . " intentos.";
        $_SESSION['ej2_juego_terminado'] = true;
        $juego_terminado_actual = true;
    }

    return [
        'mensaje' => $mensaje_respuesta,
        'intentos' => $intentos_actuales,
        'juego_terminado' => $juego_terminado_actual,
        'error' => $error_flag
    ];
}

/**
 * Obtiene el estado actual del juego del Ejercicio 2.
 *
 * @return array Estado actual.
 */
function obtenerEstadoJuegoAdivina(): array
{
     if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

     $terminado = $_SESSION['ej2_juego_terminado'] ?? true; // Asumir terminado si no hay sesión
     $mensaje = $terminado ? 'No hay partida activa (EJ2). Puedes iniciar una nueva.' : 'Partida (EJ2) en curso.';

     return [
        'mensaje' => $mensaje,
        'intentos' => $_SESSION['ej2_intentos'] ?? 0,
        'juego_terminado' => $terminado
    ];
}

?>