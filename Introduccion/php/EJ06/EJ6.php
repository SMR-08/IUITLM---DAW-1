<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>funciones</title>
</head>
<body>
    <h1>funciones</h1>
    <?php
        function esPar($num) {
                $a = false;
                if ($num % 2 == 0){$a = true;} else {$a = false;}
                return $a;
        }
        if (esPar(15)) {echo("Es par\n");} else {echo("NO Es par\n");}
        if (esPar(12)) {echo("Es par\n");} else {echo("NO Es par\n");}
        if (esPar(828560)) {echo("Es par\n");} else {echo("NO Es par\n");}
?>
</body>
</html>
