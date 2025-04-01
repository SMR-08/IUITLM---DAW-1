<?php
// file: php/acceso.php
session_start();

$servidor = "mariadb"; // O la IP/hostname de tu servidor MariaDB si no es 'mariadb'
$usuario_bd = "root"; // Cambia si usas otro usuario
$contrasena_bd = "mht85"; // Cambia por tu contraseña real
$nombre_bd = "Banco"; // Nombre de tu base de datos
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT); // Lanza excepciones en errores SQL

$conexion = null;
$error_acceso = "";
$dni_simple_formulario = isset($_POST["dni"]) ? trim($_POST["dni"]) : '';

try {
    $conexion = new mysqli($servidor, $usuario_bd, $contrasena_bd, $nombre_bd);
    $conexion->set_charset("utf8mb4"); // Buena práctica para manejar caracteres especiales

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $contrasena_formulario = isset($_POST["contrasena"]) ? $_POST["contrasena"] : '';

        if (empty($dni_simple_formulario) || empty($contrasena_formulario)) {
             $error_acceso = "El DNI y la contraseña son obligatorios.";
        } else {
            // Hashear el DNI y la contraseña introducidos para compararlos con la BD
            $dni_hasheado_formulario = hash('sha256', $dni_simple_formulario);
            $contrasena_hasheada_formulario = hash('sha256', $contrasena_formulario);

            // --- Consulta para obtener usuario, contraseña y fk_id_cuenta ---
            // Modificamos la consulta para obtener también fk_id_cuenta en el primer paso
            $sql_usuario = "SELECT dni_usuario, contraseña, fk_id_cuenta FROM Usuarios WHERE dni_usuario = ?";
            $sentencia_usuario = $conexion->prepare($sql_usuario);

            if ($sentencia_usuario) {
                $sentencia_usuario->bind_param("s", $dni_hasheado_formulario);
                $sentencia_usuario->execute();
                $resultado_usuario = $sentencia_usuario->get_result();

                if ($resultado_usuario->num_rows === 1) {
                    $usuario = $resultado_usuario->fetch_assoc();

                    // Verificar la contraseña hasheada
                    if ($contrasena_hasheada_formulario === $usuario['contraseña']) {
                        // ¡Contraseña correcta! Ahora buscamos el saldo

                        $id_cuenta = $usuario['fk_id_cuenta']; // Obtenemos el ID de la cuenta asociada

                        // --- Consulta para obtener los datos de la cuenta ---
                        $sql_cuenta = "SELECT datos_objeto FROM CuentasAlmacenadas WHERE id = ?";
                        $sentencia_cuenta = $conexion->prepare($sql_cuenta);

                        if ($sentencia_cuenta) {
                            $sentencia_cuenta->bind_param("i", $id_cuenta);
                            $sentencia_cuenta->execute();
                            $resultado_cuenta = $sentencia_cuenta->get_result();

                            if ($resultado_cuenta->num_rows === 1) {
                                $cuenta_data = $resultado_cuenta->fetch_assoc();
                                $datos_objeto_json = $cuenta_data['datos_objeto'];

                                // Decodificar el JSON para obtener los atributos de la cuenta
                                $datos_cuenta = json_decode($datos_objeto_json, true); // true para obtener un array asociativo

                                $saldo_cuenta = null; // Inicializar saldo
                                if (json_last_error() === JSON_ERROR_NONE && isset($datos_cuenta['cantidad'])) {
                                     // Si el JSON es válido y contiene la clave 'cantidad'
                                    $saldo_cuenta = (float) $datos_cuenta['cantidad'];
                                } else {
                                    // Loggear error si el JSON está mal formado o no tiene 'cantidad'
                                    error_log("Error al decodificar JSON o falta 'cantidad' para cuenta ID: " . $id_cuenta);
                                    $error_acceso = "No se pudo obtener la información del saldo de la cuenta.";
                                    // Considera si quieres detener el login aquí o continuar sin saldo
                                }

                            } else {
                                // La cuenta referenciada por fk_id_cuenta no existe en CuentasAlmacenadas
                                error_log("Error: No se encontró la cuenta con ID " . $id_cuenta . " en CuentasAlmacenadas para el usuario DNI hash: " . $dni_hasheado_formulario);
                                $error_acceso = "Error al encontrar los detalles de la cuenta asociada.";
                                // Considera detener el login
                            }
                            $sentencia_cuenta->close(); // Cerrar sentencia de cuenta

                        } else {
                             // Error preparando la consulta de cuenta
                             $error_acceso = "Error al preparar la consulta de detalles de cuenta.";
                             error_log("Error al preparar la consulta SQL para CuentasAlmacenadas: " . $conexion->error);
                        }


                        // --- Si no hubo errores graves al obtener el saldo, iniciar sesión ---
                        if (empty($error_acceso)) { // Solo proceder si no se establecieron errores críticos arriba
                            session_regenerate_id(true); // Regenerar ID de sesión por seguridad
                            $_SESSION["loggedin"] = true;
                            // Guardamos el DNI SIN hashear para mostrarlo (ya lo hacías)
                            $_SESSION["dni_usuario_plain"] = $dni_simple_formulario;
                             // --- Guardamos el ID de la cuenta y el saldo en la sesión ---
                            $_SESSION["id_cuenta"] = $id_cuenta;
                            $_SESSION["saldo_cuenta"] = $saldo_cuenta; // Guardará el float o null si hubo error

                            $sentencia_usuario->close(); // Cerrar sentencia de usuario ANTES de redirigir
                            $conexion->close();        // Cerrar conexión ANTES de redirigir
                            header("Location: ../banco.php"); // Redirigir a la página principal del banco
                            exit(); // ¡Importante! Terminar el script después de redirigir
                        }
                        // Si hubo error obteniendo saldo, el script continuará y mostrará el $error_acceso más abajo

                    } else {
                        // Contraseña inválida
                        $error_acceso = "Contraseña inválida.";
                    }
                } else {
                    // No se encontró usuario con ese DNI (hasheado)
                    $error_acceso = "No se encontró ningún usuario con ese DNI.";
                }
                $sentencia_usuario->close(); // Cerrar sentencia si se abrió
            } else {
                // Error preparando la consulta de usuario
                $error_acceso = "Error en la preparación de la consulta de usuario.";
                 error_log("Error al preparar la consulta SQL para Usuarios: " . $conexion->error);
            }
        }
    }
} catch (mysqli_sql_exception $e) {
    // Captura errores de conexión o ejecución SQL
    $error_acceso = "Error de Base de Datos. Por favor, inténtelo más tarde."; // Mensaje genérico para el usuario
    error_log("Error de Base de Datos en acceso.php: " . $e->getMessage()); // Log detallado del error
} finally {
    // Asegurarse de cerrar la conexión si sigue abierta (por ejemplo, si no hubo POST)
    if ($conexion instanceof mysqli && $conexion->thread_id) {
        $conexion->close();
    }
}

// --- HTML para mostrar el formulario de acceso (o re-mostrarlo con errores) ---
// Si la redirección ocurrió, este código no se ejecuta.
// Solo se ejecuta si el método no es POST, o si hubo errores durante el POST.
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso - Mi Banco</title> <!-- Título actualizado -->
    <!-- Asegúrate que la ruta al CSS es correcta desde la carpeta php -->
    <link rel="stylesheet" href="../css/estilos.css">
</head>
<body>
    <header>
        <div class="header-content container">
            <div class="logo">Mi Banco</div>
            <nav>
                <ul>
                    <!-- Enlaces relativos correctos desde la carpeta php -->
                    <li><a href="../banco.php">Inicio</a></li>
                    <li><a href="../registro.html">Registrarse</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main class="container">
        <div class="card">
             <h2>Iniciar Sesión</h2>
            <!-- El action apunta a sí mismo -->
            <form action="acceso.php" method="post">
                <div class="form-group">
                    <label for="dni">DNI:</label>
                    <!-- Rellenar el DNI si ya se envió para comodidad del usuario -->
                    <input type="text" id="dni" name="dni" required value="<?php echo htmlspecialchars($dni_simple_formulario); ?>">
                </div>
                <div class="form-group">
                    <label for="contrasena">Contraseña:</label>
                    <input type="password" id="contrasena" name="contrasena" required>
                </div>
                <button type="submit" class="btn-primary btn-block">Acceder</button>
            </form>

            <!-- Mostrar mensaje de error si existe -->
            <?php if (!empty($error_acceso)): ?>
                <p class="mensaje error" style="display: block;"> <!-- Quitado 'oculto', mostrar si hay error -->
                    <?php echo htmlspecialchars($error_acceso); ?>
                </p>
            <?php endif; ?>

            <p class="text-center" style="margin-top: 20px;">¿No tienes una cuenta? <a href="../registro.html">Regístrate aquí</a></p>
        </div>
    </main>
</body>
</html>