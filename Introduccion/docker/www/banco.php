<?php
    session_start();

    // --- Variables de Conexión a BD ---
    // (Puedes mover esto a un archivo de configuración separado si prefieres)
    $servidor_bd = "mariadb";
    $usuario_bd = "root";
    $contrasena_bd = "mht85";
    $nombre_bd = "Banco";

    // --- Variables para la página ---
    $usuario_logueado = isset($_SESSION["loggedin"]) && $_SESSION["loggedin"] === true;
    $id_cuenta_sesion = null;
    $saldo_actual = null; // Usaremos esta variable para el saldo fresco
    $error_saldo = null; // Para mensajes de error al obtener saldo

    // --- Si el usuario está logueado, intentar obtener el ID de cuenta y el saldo FRESCO ---
    if ($usuario_logueado) {
        $id_cuenta_sesion = $_SESSION["id_cuenta"] ?? null;

        if ($id_cuenta_sesion !== null) {
            $conexion_bd = null; // Inicializar conexión
            try {
                // Establecer conexión (misma configuración que en acceso.php)
                mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
                $conexion_bd = new mysqli($servidor_bd, $usuario_bd, $contrasena_bd, $nombre_bd);
                $conexion_bd->set_charset("utf8mb4");

                // Preparar consulta para obtener datos_objeto
                $sql_saldo = "SELECT datos_objeto FROM CuentasAlmacenadas WHERE id = ?";
                $sentencia_saldo = $conexion_bd->prepare($sql_saldo);

                if ($sentencia_saldo) {
                    $sentencia_saldo->bind_param("i", $id_cuenta_sesion);
                    $sentencia_saldo->execute();
                    $resultado_saldo = $sentencia_saldo->get_result();

                    if ($resultado_saldo->num_rows === 1) {
                        $cuenta_data = $resultado_saldo->fetch_assoc();
                        $datos_objeto_json = $cuenta_data['datos_objeto'];
                        $datos_cuenta = json_decode($datos_objeto_json, true);

                        // Verificar JSON y extraer saldo ('cantidad')
                        if (json_last_error() === JSON_ERROR_NONE && isset($datos_cuenta['cantidad'])) {
                            $saldo_actual = (float) $datos_cuenta['cantidad'];
                            // Opcional: Actualizar la sesión también, aunque la leeremos fresca en la próxima carga
                            $_SESSION["saldo_cuenta"] = $saldo_actual;
                        } else {
                            $error_saldo = "Error al procesar datos de la cuenta.";
                            error_log("Error JSON o falta 'cantidad' en BD para cuenta ID: " . $id_cuenta_sesion);
                        }
                    } else {
                        // La cuenta asociada al usuario no se encontró en CuentasAlmacenadas
                        $error_saldo = "No se encontraron los detalles de la cuenta.";
                        error_log("Cuenta ID " . $id_cuenta_sesion . " (de sesión) no encontrada en CuentasAlmacenadas.");
                        // Quizás invalidar la sesión aquí si la cuenta no existe?
                        // unset($_SESSION['loggedin'], $_SESSION['id_cuenta'], ...);
                        // $usuario_logueado = false; // Forzar estado no logueado
                    }
                    $sentencia_saldo->close();
                } else {
                    $error_saldo = "Error al preparar la consulta de saldo.";
                     error_log("Error preparando SQL para CuentasAlmacenadas: " . $conexion_bd->error);
                }

            } catch (mysqli_sql_exception $e) {
                $error_saldo = "Error de conexión al obtener saldo.";
                error_log("Error de BD en banco.php al obtener saldo: " . $e->getMessage());
            } finally {
                // Cerrar conexión si se abrió
                if ($conexion_bd instanceof mysqli && $conexion_bd->thread_id) {
                    $conexion_bd->close();
                }
            }
        } else {
             // No debería pasar si está logueado, pero por si acaso
             $error_saldo = "Falta información de la cuenta en la sesión.";
             error_log("Usuario logueado pero sin id_cuenta en sesión.");
        }
    } // fin if ($usuario_logueado)
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Menú Principal del Banco</title>
    <link rel="stylesheet" href="css/estilos.css">
    <style>
        /* Estilos para mensajes de gasto (sin cambios) */
        .mensaje-gasto { padding: 10px; margin-top: 15px; border-radius: 4px; display: none; }
        .mensaje-gasto.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .mensaje-gasto.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .visible { display: block !important; }
        .gasto-form { margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee; }
        .gasto-form .form-group { margin-bottom: 15px; }
    </style>
</head>
<body>
    <header>
        <div class="header-content container">
            <div class="logo">Mi Banco</div>
            <nav>
                <ul>
                    <?php if ($usuario_logueado): ?>
                        <li><a href="php/cerrar_sesion.php">Cerrar Sesión</a></li>
                    <?php else: ?>
                        <li><a href="acceso.html">Acceder</a></li>
                        <li><a href="registro.html">Registrarse</a></li>
                    <?php endif; ?>
                </ul>
            </nav>
        </div>
    </header>

    <main class="container">
        <div class="card">
            <h1>¡Bienvenido a Mi Banco!</h1>

            <?php if ($usuario_logueado): ?>
                <div class="account-info">
                    <h3>Información de tu Cuenta:</h3>

                    <?php if (isset($_SESSION["dni_usuario_plain"])): ?>
                        <p><strong>DNI:</strong> <?php echo htmlspecialchars($_SESSION["dni_usuario_plain"]); ?></p>
                    <?php else: ?>
                        <p><strong>DNI:</strong> No disponible</p>
                    <?php endif; ?>

                    <?php // --- Mostrar Saldo FRESCO ---
                        // Mostrar error si ocurrió al obtener saldo
                        if ($error_saldo):
                    ?>
                            <p><strong>Saldo Disponible:</strong> <span id="saldo-valor" style="color: red;">Error al obtener</span></p>
                            <p style="color: #721c24; font-size: 0.9em;">Detalle: <?php echo htmlspecialchars($error_saldo); ?></p>
                    <?php // Mostrar saldo si se obtuvo correctamente
                        elseif ($saldo_actual !== null):
                            $saldo_formateado = number_format($saldo_actual, 2, ',', '.');
                    ?>
                        <p><strong>Saldo Disponible:</strong> <span id="saldo-valor"><?php echo htmlspecialchars($saldo_formateado); ?></span> €</p>
                    <?php else: // Caso raro: no hubo error pero saldo es null ?>
                        <p><strong>Saldo Disponible:</strong> <span id="saldo-valor">No disponible</span></p>
                    <?php endif; ?>
                    <?php // --- FIN: Mostrar Saldo --- ?>

                </div>

                <?php // --- Formulario para Realizar Gasto ---
                 // Mostrar solo si no hubo error grave al obtener datos y tenemos ID
                 if ($id_cuenta_sesion !== null && $error_saldo === null):
                ?>
                <!-- Añadimos ID y data-id-cuenta a este div contenedor -->
                <div id="gasto-form-container" class="gasto-form" data-id-cuenta="<?php echo htmlspecialchars($id_cuenta_sesion); ?>">
                    <h4>Realizar un Gasto</h4>
                    <div class="form-group">
                         <label for="gasto-cantidad">Cantidad a gastar (€):</label>
                         <input type="number" id="gasto-cantidad" name="gasto_cantidad" step="0.01" min="0.01" required class="form-control" placeholder="Ej: 50.00">
                    </div>
                    <button type="button" id="btn-realizar-gasto" class="btn btn-warning">Confirmar Gasto</button>
                    <div id="mensaje-gasto" class="mensaje-gasto"></div>
                </div>
                <?php elseif ($error_saldo): ?>
                    <p style="margin-top: 20px; color: #dc3545;">No se puede operar debido a un error: <?php echo htmlspecialchars($error_saldo); ?></p>
                <?php endif; ?>
                 <?php // --- FIN: Formulario Gasto --- ?>

                <a href="php/cerrar_sesion.php" class="btn btn-danger" style="margin-top: 25px;">Cerrar Sesión</a>

            <?php else: // Usuario NO logueado ?>
                <p>Por favor, inicia sesión o regístrate para acceder a tu cuenta.</p>
                <div style="display: flex; gap: 20px; justify-content: center; margin-top: 20px;">
                    <a href="acceso.html" class="btn btn-primary">Iniciar Sesión</a>
                    <a href="registro.html" class="btn btn-secondary">Registrarse</a>
                </div>
            <?php endif; ?>
        </div>
    </main>

    <?php // --- Incluir el SCRIPT EXTERNO solo si el usuario está logueado y podemos operar ---
     if ($usuario_logueado && $id_cuenta_sesion !== null && $error_saldo === null):
    ?>
        <script src="js/banco_acciones.js" defer></script>
    <?php endif; ?>
     <?php // --- FIN: Incluir script externo --- ?>

</body>
</html>