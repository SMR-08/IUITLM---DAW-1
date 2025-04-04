// file: docker/www/js/hub.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Constantes y Variables ---
    const apiUrlBase = 'http://api.localhost'; // O la URL donde corre tu API Flask

    // --- Elementos del DOM para Inventario (EJ1) ---
    const btnVerInventario = document.getElementById('btn-ver-inventario');
    const inventarioOutputDiv = document.getElementById('inventario-output');
    const mensajeInventarioDiv = document.getElementById('mensaje-inventario');

    const formAgregar = document.getElementById('form-agregar-producto');
    const inputNombre = document.getElementById('prod-nombre');
    const inputPrecio = document.getElementById('prod-precio');
    const inputCantidad = document.getElementById('prod-cantidad');
    const mensajeAgregarDiv = document.getElementById('mensaje-agregar');

    const formEliminar = document.getElementById('form-eliminar-producto');
    const inputNombreEliminar = document.getElementById('prod-nombre-eliminar');
    const mensajeEliminarDiv = document.getElementById('mensaje-eliminar');

    const btnVerCoches = document.getElementById('btn-ver-coches');
    const cochesOutputDiv = document.getElementById('coches-output');
    const mensajeCochesDiv = document.getElementById('mensaje-coches');

    const formAgregarCoche = document.getElementById('form-agregar-coche');
    const inputCocheMarca = document.getElementById('coche-marca');
    const inputCocheModelo = document.getElementById('coche-modelo');
    const inputCocheAño = document.getElementById('coche-año');
    const mensajeAgregarCocheDiv = document.getElementById('mensaje-agregar-coche');

    const formEliminarCoche = document.getElementById('form-eliminar-coche');
    const inputCocheIdEliminar = document.getElementById('coche-id-eliminar');
    const mensajeEliminarCocheDiv = document.getElementById('mensaje-eliminar-coche');

    const btnObtenerSonidos = document.getElementById('btn-obtener-sonidos');
    const sonidosOutputDiv = document.getElementById('sonidos-output');
    const mensajeSonidosDiv = document.getElementById('mensaje-sonidos');

    // --- Funciones Auxiliares ---
    function mostrarMensaje(divElement, texto, tipo = 'error') {
        if (divElement) {
            divElement.textContent = texto;
            divElement.className = `mensaje ${tipo} visible`; // Añade clase de tipo y 'visible'
        }
    }

    function ocultarMensajes() {
        mensajeInventarioDiv.classList.remove('visible', 'success', 'error');
        mensajeAgregarDiv.classList.remove('visible', 'success', 'error');
        mensajeEliminarDiv.classList.remove('visible', 'success', 'error');
        mensajeCochesDiv?.classList.remove('visible', 'success', 'error');
        mensajeAgregarCocheDiv?.classList.remove('visible', 'success', 'error');
        mensajeEliminarCocheDiv?.classList.remove('visible', 'success', 'error');
        mensajeSonidosDiv?.classList.remove('visible', 'success', 'error');
    }

    async function fetchApi(endpoint, options = {}) {
        try {
            const response = await fetch(`${apiUrlBase}${endpoint}`, options);
            const data = await response.json(); // Intenta parsear JSON siempre
            if (!response.ok) {
                // Si la respuesta no es OK, lanza un error con el mensaje de la API si existe
                throw new Error(data.error || `Error ${response.status}: ${response.statusText}`);
            }
            return data; // Devuelve los datos si todo OK
        } catch (error) {
            console.error(`Error en fetchApi para ${endpoint}:`, error);
            // Re-lanza el error para que el llamador lo maneje
            throw error;
        }
    }

    function renderizarInventario(data) {
        if (!inventarioOutputDiv) return;

        if (data && data.productos !== undefined && data.valor_total !== undefined) {
            let html = '<h4>Productos Actuales:</h4>';
            if (data.productos.length === 0) {
                html += '<p>El inventario está vacío.</p>';
            } else {
                html += '<ul id="inventario-lista">';
                data.productos.forEach(p => {
                    // Convertimos el precio del producto a número para asegurar, aunque tu código ya lo hace bien
                    const precioProductoNum = parseFloat(p.precio);
                    const precioProductoFormateado = !isNaN(precioProductoNum) ? precioProductoNum.toFixed(2) : 'N/A';
                    html += `<li>${p.nombre} - Precio: ${precioProductoFormateado}€ - Cantidad: ${p.cantidad}</li>`;
               });
                html += '</ul>';
            }
            const valorTotalNumerico = parseFloat(data.valor_total);

            const valorTotalFormateado = !isNaN(valorTotalNumerico) ? valorTotalNumerico.toFixed(2) : '0.00';
            
            html += `<p><strong>Valor Total del Inventario:</strong> <span id="inventario-valor">${valorTotalFormateado}€</span></p>`;
            
            inventarioOutputDiv.innerHTML = html;
            // Mostrar mensaje de éxito si la API lo envió
            if (data.mensaje) {
                mostrarMensaje(mensajeInventarioDiv, data.mensaje, 'success');
            }
        } else {
            inventarioOutputDiv.innerHTML = '<p>No se pudieron cargar los datos del inventario.</p>';
        }
    }

    function renderizarCoches(data) {
        if (!cochesOutputDiv) return;

        if (data && data.coches) {
            let html = '<h4>Lista de Coches:</h4>';
            if (data.coches.length === 0) {
                html += '<p>No hay coches registrados.</p>';
            } else {
                html += '<ul id="coches-lista">';
                // Asumiendo que la API devuelve id, marca, modelo, año
                data.coches.forEach(c => {
                    html += `<li>ID: ${c.id} - ${c.marca} ${c.modelo} (${c.año})</li>`;
                });
                html += '</ul>';
            }
            cochesOutputDiv.innerHTML = html;
            if (data.mensaje) { // Mostrar mensaje de éxito si viene de la API
                mostrarMensaje(mensajeCochesDiv, data.mensaje, 'success');
            }
        } else {
            cochesOutputDiv.innerHTML = '<p>No se pudieron cargar los datos de los coches.</p>';
            mostrarMensaje(mensajeCochesDiv, 'Respuesta inesperada de la API.', 'error');
        }
    }

function renderizarSonidos(data) {
    if (!sonidosOutputDiv) return;

    if (data && data.sonidos) {
        let html = '<h4>Sonidos Generados:</h4>';
        if (data.sonidos.length === 0) {
            html += '<p>No se generaron sonidos.</p>';
        } else {
            html += '<ul id="sonidos-lista">';
            // data.sonidos es ahora una lista de objetos {tipo: ..., sonido: ...}
            data.sonidos.forEach(s => {
                // Escapamos HTML simple por si acaso en tipo/sonido (aunque aquí no debería haber)
                const tipoEscapado = s.tipo.replace(/</g, "<").replace(/>/g, ">");
                const sonidoEscapado = s.sonido.replace(/</g, "<").replace(/>/g, ">");
                html += `<li><strong>${tipoEscapado}:</strong> ${sonidoEscapado}</li>`;
            });
            html += '</ul>';
        }
        sonidosOutputDiv.innerHTML = html;
        if (data.mensaje) { // Mostrar mensaje de éxito si viene de la API
            mostrarMensaje(mensajeSonidosDiv, data.mensaje, 'success');
        }
    } else {
        sonidosOutputDiv.innerHTML = '<p>No se pudieron cargar los datos de los sonidos.</p>';
        mostrarMensaje(mensajeSonidosDiv, 'Respuesta inesperada de la API.', 'error');
    }
}



    // --- Lógica para Ver Inventario ---
    if (btnVerInventario) {
        btnVerInventario.addEventListener('click', async () => {
            ocultarMensajes();
            inventarioOutputDiv.textContent = 'Cargando...';
            try {
                const data = await fetchApi('/inventario');
                renderizarInventario(data);
            } catch (error) {
                inventarioOutputDiv.textContent = 'Error al cargar el inventario.';
                mostrarMensaje(mensajeInventarioDiv, error.message || 'Error desconocido', 'error');
            }
        });
    }

    // --- Lógica para Ver Coches (EJ2) ---
    if (btnVerCoches) {
        btnVerCoches.addEventListener('click', async () => {
            ocultarMensajes();
            cochesOutputDiv.textContent = 'Cargando coches...';
            try {
                const data = await fetchApi('/coches'); // Llama al nuevo endpoint GET /coches
                renderizarCoches(data); // Usa la nueva función de renderizado
            } catch (error) {
                cochesOutputDiv.textContent = 'Error al cargar los coches.';
                mostrarMensaje(mensajeCochesDiv, error.message || 'Error desconocido', 'error');
            }
        });
    }
    
    if (btnObtenerSonidos) {
        btnObtenerSonidos.addEventListener('click', async () => {
            ocultarMensajes();
            sonidosOutputDiv.textContent = 'Generando sonidos...';
            try {
                // Llama al nuevo endpoint GET /animales/sonidos
                const data = await fetchApi('/animales/sonidos');
                renderizarSonidos(data); // Usa la nueva función de renderizado
            } catch (error) {
                sonidosOutputDiv.textContent = 'Error al obtener los sonidos.';
                // Muestra el error específico devuelto por fetchApi o un mensaje genérico
                mostrarMensaje(mensajeSonidosDiv, error.message || 'Error desconocido', 'error');
            }
        });
    }

    // --- Lógica para Agregar Producto ---
    if (formAgregar) {
        formAgregar.addEventListener('submit', async (e) => {
            e.preventDefault(); // Evitar envío tradicional
            ocultarMensajes();

            const nombre = inputNombre.value.trim();
            const precio = parseFloat(inputPrecio.value);
            const cantidad = parseInt(inputCantidad.value, 10);

            // Validación simple en cliente
            if (!nombre || isNaN(precio) || precio < 0 || isNaN(cantidad) || cantidad < 0) {
                mostrarMensaje(mensajeAgregarDiv, 'Datos inválidos. Revisa nombre, precio (>=0) y cantidad (entero >=0).', 'error');
                return;
            }

            const body = JSON.stringify({ nombre, precio, cantidad });

            try {
                const data = await fetchApi('/inventario/productos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: body
                });
                mostrarMensaje(mensajeAgregarDiv, data.mensaje || 'Producto agregado.', 'success');
                formAgregar.reset(); // Limpiar formulario
                // Refrescar inventario automáticamente tras agregar
                btnVerInventario.click();
            } catch (error) {
                mostrarMensaje(mensajeAgregarDiv, error.message || 'Error al agregar producto.', 'error');
            }
        });
    }

    // --- Lógica para Agregar Coche (EJ2) ---
    if (formAgregarCoche) {
        formAgregarCoche.addEventListener('submit', async (e) => {
            e.preventDefault();
            ocultarMensajes();

            const marca = inputCocheMarca.value.trim();
            const modelo = inputCocheModelo.value.trim();
            const año = parseInt(inputCocheAño.value, 10);

            // Validación básica en cliente
            if (!marca || !modelo || isNaN(año) || año < 1886 || año > 2100) {
                mostrarMensaje(mensajeAgregarCocheDiv, 'Datos inválidos. Revisa marca, modelo y año.', 'error');
                return;
            }

            const body = JSON.stringify({ marca, modelo, año });

            try {
                // Llama al nuevo endpoint POST /coches
                const data = await fetchApi('/coches', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: body
                });
                mostrarMensaje(mensajeAgregarCocheDiv, data.mensaje || 'Coche agregado.', 'success');
                formAgregarCoche.reset(); // Limpiar formulario
                // Refrescar lista automáticamente
                if (btnVerCoches) btnVerCoches.click();
            } catch (error) {
                mostrarMensaje(mensajeAgregarCocheDiv, error.message || 'Error al agregar coche.', 'error');
            }
        });
    }

    // --- Lógica para Eliminar Producto ---
    if (formEliminar) {
        formEliminar.addEventListener('submit', async (e) => {
            e.preventDefault();
            ocultarMensajes();

            const nombre = inputNombreEliminar.value.trim();
            if (!nombre) {
                mostrarMensaje(mensajeEliminarDiv, 'Introduce el nombre del producto a eliminar.', 'error');
                return;
            }

            // El nombre va en la URL, necesitamos codificarlo por si tiene caracteres especiales
            const nombreCodificado = encodeURIComponent(nombre);

            try {
                const data = await fetchApi(`/inventario/productos/${nombreCodificado}`, {
                    method: 'DELETE'
                });
                mostrarMensaje(mensajeEliminarDiv, data.mensaje || 'Producto eliminado.', 'success');
                formEliminar.reset(); // Limpiar formulario
                // Refrescar inventario automáticamente tras eliminar
                btnVerInventario.click();
            } catch (error) {
                mostrarMensaje(mensajeEliminarDiv, error.message || 'Error al eliminar producto.', 'error');
            }
        });
    }

    // --- Lógica para Eliminar Coche por ID (EJ2) ---
    if (formEliminarCoche) {
        formEliminarCoche.addEventListener('submit', async (e) => {
            e.preventDefault();
            ocultarMensajes();

            const id = parseInt(inputCocheIdEliminar.value, 10);

            if (isNaN(id) || id <= 0) {
                mostrarMensaje(mensajeEliminarCocheDiv, 'Introduce un ID de coche válido (número entero positivo).', 'error');
                return;
            }

            try {
                 // Llama al nuevo endpoint DELETE /coches/<id>
                const data = await fetchApi(`/coches/${id}`, {
                    method: 'DELETE'
                });
                mostrarMensaje(mensajeEliminarCocheDiv, data.mensaje || 'Coche eliminado.', 'success');
                formEliminarCoche.reset(); // Limpiar formulario
                // Refrescar lista automáticamente
                if (btnVerCoches) btnVerCoches.click();
            } catch (error) {
                 // Manejar el caso 404 (Not Found) específicamente si se desea
                if (error.message && error.message.toLowerCase().includes('no encontrado')) {
                     mostrarMensaje(mensajeEliminarCocheDiv, `Error: ${error.message}`, 'error');
                } else {
                     mostrarMensaje(mensajeEliminarCocheDiv, error.message || 'Error al eliminar coche.', 'error');
                }
            }
        });
    }

}); // Fin DOMContentLoaded