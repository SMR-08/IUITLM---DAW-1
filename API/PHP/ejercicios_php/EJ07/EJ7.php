<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Foreach</title>
</head>
<body>
    <h1>Foreach</h1>
    <?php
    $lista = ["Pepe","Luis","Alberto","Juanjo","Maria"];
    foreach ($lista as $pers) {
        echo("$pers ");
    }
?>
</body>
</html>
