<?php
session_start();

if (!isset($_SESSION['numero_secreto'])) {
    $_SESSION['numero_secreto'] = rand(0, 100);
    $_SESSION['intentos'] = 0;
}

$mensaje = "";
$numero_usuario = isset($_POST['numero']) ? (int)$_POST['numero'] : null;

if ($numero_usuario !== null) {
    $_SESSION['intentos']++;

    if ($numero_usuario > $_SESSION['numero_secreto']) {
        $mensaje = "El número es menor.";
    } elseif ($numero_usuario < $_SESSION['numero_secreto']) {
        $mensaje = "El número es mayor.";
    } else {
        $mensaje = "¡Enhorabuena! Has acertado en " . $_SESSION['intentos'] . " intentos.";
        unset($_SESSION['numero_secreto']);
        unset($_SESSION['intentos']);
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Adivina el número</title>
</head>
<body>
    <h1>Adivina el número (0-100)</h1>

    <?php if ($mensaje): ?>
        <p><?php echo $mensaje; ?></p>
    <?php endif; ?>

    <form method="post">
        <label for="numero">Introduce un número:</label>
        <input type="number" name="numero" id="numero" min="0" max="100" required>
        <button type="submit">Adivinar</button>
    </form>
    <?php if (isset($_SESSION['intentos']) && $numero_usuario !== null && $numero_usuario != $_SESSION['numero_secreto']): ?>
        <p>Intentos: <?php echo $_SESSION['intentos']; ?></p>
    <?php endif; ?>
</body>
</html>