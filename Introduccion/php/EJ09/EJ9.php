<!DOCTYPE html>
<html>
<head>
    <title>Fecha y Hora</title>
</head>
<body>
    <?php
    $fecha_hora = date("d-m-Y H:i:s");
    $archivo = fopen("datos.txt", "a");
    fwrite($archivo, $fecha_hora . PHP_EOL);
    fclose($archivo);
?>
</body>
</html>
