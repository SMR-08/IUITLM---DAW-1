<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Condiciones</title>
</head>
<body>
    <h1>Condiciones</h1>
    <?php
    $nene = 5;
    $joven = 25;
    $mayor = 65;
    // Condiciones
    echo "<p>Edad del Nene: " . $nene . "</p>";
    echo "<p>Edad del Joven: " . $joven . "</p>";
    echo "<p>Edad del Mayor: " . $mayor . "</p>";
    $edad = $nene;
    function clasificarEdad($edad) {
    if ($edad >= 65) {
            echo "<p>Eres Jubilado</p>";
    }
    elseif ($edad > 18) {
            echo "<p>Eres mayor de edad</p>";
    }
    else {
            echo "<p>Eres mu enano</p>";
    }
    }

    clasificarEdad($edad);

    $edad = $joven;
    clasificarEdad($edad);

    $edad = $mayor;
    clasificarEdad($edad);
?>
</body>
</html>
