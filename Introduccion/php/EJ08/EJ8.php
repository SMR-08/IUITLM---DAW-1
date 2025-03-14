<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>POST</title>
</head>
<body>
    <h1>GET/POST</h1>
        <form action="" method="post">
            <input type="text" name="nombre">
            <input type="submit" value="Enviar">
        </form>
        <?php
            if ($_SERVER["REQUEST_METHOD"] == "POST") {
                $nombre = $_POST["nombre"];
                echo "<h2>Bienvenido, $nombre!</h2>";
            }
        ?>
</body>
</html>
