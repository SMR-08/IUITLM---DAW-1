<?php
function tablamulti($numero): ?array
{
    if (!is_numeric($numero)) {
        return null;
    }

    $numero = floatval($numero); 
    $tabla = [];
    $contador = 1;

    for ($i = 0; $i < 5; $i++) {
        $fila = []; 
        for ($j = 0; $j < 5; $j++) {
            $resultado = $numero * $contador;
            $fila[] = $resultado; 
            $contador++;
        }
        $tabla[] = $fila;
    }

    return $tabla;
}
?>