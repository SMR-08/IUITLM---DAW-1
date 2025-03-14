<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Operaciones</title>
</head>
<body>
    <h1>Operaciones</h1>
    <?php
    $num1 = 10;
    $num2 = 5;
    // Operaciones
    $suma = $num1 + $num2;
    $resta = $num1 - $num2;
    $multiplicacion = $num1 * $num2;
    $division = $num1 / $num2;

    echo "<p>Número 1: " . $num1 . "</p>";
    echo "<p>Número 2: " . $num2 . "</p>";
    echo "<p>Suma: " . $suma . "</p>";
    echo "<p>Resta: " . $resta . "</p>";
    echo "<p>Multiplicación: " . $multiplicacion . "</p>";
    echo "<p>División: " . $division . "</p>";
?>
</body>
</html>
