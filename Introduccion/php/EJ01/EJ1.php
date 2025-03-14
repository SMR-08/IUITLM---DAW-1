<!DOCTYPE html>
<html>
<head>
<title>Tabla de Multiplicacion PHP</title>
<style>
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
th, td {
  padding: 5px;
  text-align: center;
}
</style>
</head>
<body>

<form method="post">
    Introduce un número: <input type="number" name="numero"><br>
    <input type="submit" value="Enviar">
</form>

<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $numero = $_POST["numero"];

    if (is_numeric($numero)) {
        echo "<table>";
        $contador = 1;
        for ($i = 0; $i < 5; $i++) {
            echo "<tr>";
            for ($j = 0; $j < 5; $j++) {
                $resultado = $numero * $contador;
                echo "<td>" . $resultado . "</td>";
                $contador++;
            }
            echo "</tr>";
        }
        echo "</table>";
    } else {
        echo "<p>Por favor, introduce un número válido.</p>";
    }
}

?>

</body>
</html>