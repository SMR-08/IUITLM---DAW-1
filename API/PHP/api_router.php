<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *'); 
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$action = $_GET['action'] ?? null; 

/**
 * Controlador para generar la tabla de multiplicación (EJ1).
 */
function handleGenerarTabla() {
    
    require_once __DIR__ . '/ejercicios_php/EJ1.php';

    
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        echo json_encode(['error' => 'Método no permitido para esta acción. Se requiere POST.']);
        exit;
    }

    
    $json_data = file_get_contents('php://input');
    $data = json_decode($json_data, true);

    if ($data === null || !isset($data['numero'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Datos JSON inválidos o falta el campo "numero".']);
        exit;
    }
    $numero_input = $data['numero'];

    
    $tabla_resultados = tablamulti($numero_input);

    
    if ($tabla_resultados !== null) {
        http_response_code(200);
        echo json_encode([
            'mensaje' => 'Tabla de multiplicación generada correctamente (vía router).',
            'numero_base' => $numero_input,
            'tabla' => $tabla_resultados
        ]);
    } else {
        http_response_code(400);
        echo json_encode(['error' => 'Entrada inválida. Proporciona un número válido.']);
    }
    exit;
}

switch ($action) {
    case 'generar_tabla':
        handleGenerarTabla();
        break;
    default:     
        http_response_code(404); 
        echo json_encode(['error' => 'Acción no válida o no especificada. Usa ?action=...']);
        exit;
}

?>