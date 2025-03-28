<?php
session_start();

// Detalles de conexión a la base de datos
$nombreServidor = "mariadb";
$nombreUsuario = "root"; // Considerar usar un usuario con menos privilegios en producción
$contraseña = "mht85";
$nombreBD = "Banco";    // Usar el nombre de BD definido en docker-compose para la creación inicial

// Reporte de errores para mysqli
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

$conexion = null; // Inicializar variable de conexión
$error_inicio_sesion = ""; // Inicializar mensaje de error
// Mantener registro del DNI plano si el formulario fue enviado
$dni_plano_del_formulario = isset($_POST["dni"]) ? $_POST["dni"] : '';


try {
    // Crear conexión
    $conexion = new mysqli($nombreServidor, $nombreUsuario, $contraseña, $nombreBD);

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // $dni_plano_del_formulario ya está establecido arriba
        $contraseña_del_formulario = $_POST["password"]; // Nombre de variable corregido

        // Hashear el DNI del formulario
        $dni_hasheado_del_formulario = hash('sha256', $dni_plano_del_formulario);

        // Hashear la Contraseña del formulario
        $contraseña_hasheada_del_formulario = hash('sha256', $contraseña_del_formulario);

        // Consulta usando el DNI HASHEADO
        $sql = "SELECT * FROM Usuarios WHERE dni_usuario = ?";
        $stmt = $conexion->prepare($sql);

        if ($stmt) {
            // Vincular el DNI HASHEADO
            $stmt->bind_param("s", $dni_hasheado_del_formulario);
            $stmt->execute();
            $resultado = $stmt->get_result();

            if ($resultado->num_rows > 0) {
                $usuario = $resultado->fetch_assoc();

                // Comparar contraseñas HASHEADAS
                if ($contraseña_hasheada_del_formulario === $usuario['contraseña']) {
                    // Contraseña coincide
                    $_SESSION["sesion_iniciada"] = true;
                    $_SESSION["dni_usuario_plano"] = $dni_plano_del_formulario; // Almacenar DNI plano

                    $stmt->close();
                    $conexion->close();
                    // --- ACTUALIZAR UBICACIÓN DE REDIRECCIÓN ---
                    header("Location: ../banco.php"); // Redirigir a banco.php
                    exit();
                } else {
                    $error_inicio_sesion = "Contraseña inválida.";
                }
            } else {
                $error_inicio_sesion = "No se encontró usuario con ese DNI.";
            }
            $stmt->close();
        } else {
            $error_inicio_sesion = "Error de preparación de consulta a la base de datos.";
        }
    }

} catch (mysqli_sql_exception $e) {
    $error_inicio_sesion = "Error de Base de Datos: " . $e->getMessage();
    // error_log("Database Error: " . $e->getMessage());
    // $error_inicio_sesion = "Ocurrió un error durante el inicio de sesión.";
} finally {
    if ($conexion instanceof mysqli && $conexion->thread_id) {
        $conexion->close();
    }
}

// --- Sección de Salida HTML --- Solo se ejecuta si no se ha redirigido
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Iniciar Sesión</title>
</head>
<body>
    <h2>Iniciar Sesión</h2>
    <!--  Formulario que envía los datos a login.php mediante método POST -->
    <form action="login.php" method="post">
        <label for="dni">DNI:</label><br>
        <!--  Muestra el DNI introducido previamente en caso de error -->
        <input type="text" id="dni" name="dni" required value="<?php echo htmlspecialchars($dni_plano_del_formulario); ?>"><br><br>
        <label for="password">Contraseña:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <input type="submit" value="Iniciar Sesión">
    </form>
    <!--  Parrafo para mostrar mensajes de error en rojo -->
    <p id="error-message" style="color: red;">
        <?php echo htmlspecialchars($error_inicio_sesion); ?>
    </p>

    <p>¿No tienes una cuenta? <a href="../registro.html">Regístrate aquí</a></p>
</body>
</html>