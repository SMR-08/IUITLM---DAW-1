<?php
// Se ha tenido que refactorizar para poder manejar varias solicitudes dependiendo el ejercicio
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *'); 
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Access-Control-Allow-Credentials: true'); 

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$ejercicio = null;
$accion = null;
$datos_entrada = [];
$response_data = [];
$status_code = 200; // OK por defecto

// Obtener datos
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    if ($input === null && json_last_error() !== JSON_ERROR_NONE) {
        $status_code = 400;
        $response_data = ['error' => 'Cuerpo JSON inválido.'];
    } else {
        $datos_entrada = $input ?? [];
        $ejercicio = $datos_entrada['ejercicio'] ?? null;
        $accion = $datos_entrada['accion'] ?? null;
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $datos_entrada = $_GET;
    $ejercicio = $datos_entrada['ejercicio'] ?? null;
    $accion = $datos_entrada['accion'] ?? null;
} else {
    $status_code = 405;
    $response_data = ['error' => 'Método no permitido. Solo GET y POST.'];
}

if ($status_code === 200) { // Solo si no hubo errores previos
    try {
        // El Switch es para cada ejercicio segun se eliga en el index.html
        switch ($ejercicio) {
            case 'ej1': // Tabla de Multiplicar
                $ruta_ej1 = __DIR__ . '/ejercicios_php/EJ01/EJ1.php';
                if (!file_exists($ruta_ej1)) throw new Exception("Archivo de lógica EJ1 no encontrado.", 500);
                require_once $ruta_ej1;

                if ($accion === 'generar_tabla') {
                    if ($_SERVER['REQUEST_METHOD'] !== 'POST') throw new Exception("Acción 'generar_tabla' requiere POST.", 405);
                    $numero_input = $datos_entrada['numero'] ?? null;
                    if ($numero_input === null) throw new Exception("Falta el parámetro 'numero'.", 400);

                    $tabla_resultados = tablamulti($numero_input);

                    if ($tabla_resultados !== null) {
                        $response_data = [
                            'mensaje' => 'Tabla de multiplicación (EJ1) generada correctamente.',
                            'numero_base' => $numero_input,
                            'tabla' => $tabla_resultados
                        ];
                    } else {
                         throw new Exception("Entrada inválida para 'numero'.", 400);
                    }
                } else {
                    throw new Exception("Acción no válida para EJ1.", 400);
                }
                break;

            case 'ej2': // Adivina el Número
                $ruta_ej2 = __DIR__ . '/ejercicios_php/EJ02/EJ2.php';
                if (!file_exists($ruta_ej2)) throw new Exception("Archivo de lógica EJ2 no encontrado.", 500);
                require_once $ruta_ej2;

                switch ($accion) {
                    case 'iniciar':
                        if ($_SERVER['REQUEST_METHOD'] !== 'POST') throw new Exception("Acción 'iniciar' (EJ2) requiere POST.", 405);
                        $response_data = iniciarJuegoAdivina();
                        break;
                    case 'adivinar':
                        if ($_SERVER['REQUEST_METHOD'] !== 'POST') throw new Exception("Acción 'adivinar' (EJ2) requiere POST.", 405);
                        $numero_intento = $datos_entrada['numero'] ?? null;
                        if ($numero_intento === null || !is_numeric($numero_intento)) {
                             throw new Exception("Falta el parámetro 'numero' o no es numérico.", 400);
                        }
                        $response_data = procesarIntentoAdivina(intval($numero_intento));
                        break;
                    case 'obtener_estado':
                         if ($_SERVER['REQUEST_METHOD'] !== 'GET') throw new Exception("Acción 'obtener_estado' (EJ2) requiere GET.", 405);
                         $response_data = obtenerEstadoJuegoAdivina();
                         break;
                    default:
                        throw new Exception("Acción no válida para EJ2.", 400);
                }
                break;

            default:
                // Casos en que no sea ninguno o este vacio
                if ($ejercicio === null) {
                    throw new Exception("Parámetro 'ejercicio' requerido.", 400);
                } else {
                    throw new Exception("Ejercicio no válido o no implementado.", 404);
                }
        }
    } catch (Exception $e) {
        // Capturar excepciones 
        $status_code = $e->getCode() >= 400 ? $e->getCode() : 500; // Usar código de excepción si es válido, sino 500 de default
        $response_data = ['error' => $e->getMessage()];
    }
}
http_response_code($status_code);
echo json_encode($response_data);
exit;
?>