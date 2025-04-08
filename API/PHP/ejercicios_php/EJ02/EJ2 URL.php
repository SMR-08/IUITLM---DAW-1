<?php

$numero_secreto = isset($_GET['numero_secreto']) ? (int)$_GET['numero_secreto'] : rand(0, 100);
$intentos = isset($_GET['intentos']) ? (int)$_GET['intentos'] : 0;
$mensaje = "";
$numero_usuario = isset($_POST['numero']) ? (int)$_POST['numero'] : null;
$juego_terminado = false;

if ($numero_usuario !== null) {
    $intentos++;

    if ($numero_usuario > $numero_secreto) {
        $mensaje = "El número es menor.";
    } elseif ($numero_usuario < $numero_secreto) {
        $mensaje = "El número es mayor.";
    } else {
        $mensaje = "¡Enhorabuena! Has acertado en " . $intentos . " intentos.";
        $juego_terminado = true;
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

    <form method="post" action="<?php echo $_SERVER['PHP_SELF'];
        if(!$juego_terminado && $numero_usuario!==null) {
          echo '?numero_secreto=' . $numero_secreto . '&intentos=' . $intentos;
        }
         ?>">
        <label for="numero">Introduce un número:</label>
        <input type="number" name="numero" id="numero" min="0" max="100" required>
        <button type="submit">Adivinar</button>
     </form>


    <?php if (!$juego_terminado && $numero_usuario !==null && $intentos >0): ?>
        <p>Intentos: <?php echo $intentos; ?></p>
    <?php endif; ?>

    <?php if(!$juego_terminado && $numero_usuario === null): ?>
    <p>Intentos: 0 </p>
    <?php endif; ?>

    <?php if($juego_terminado):?>
        <form method="get" action="<?php echo $_SERVER['PHP_SELF']?>">
            <button type="submit">Volver a jugar</button>
        </form>
    <?php endif; ?>
</body>
</html>