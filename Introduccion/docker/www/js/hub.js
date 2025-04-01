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
                    html += `<li>${p.nombre} - Precio: ${p.precio.toFixed(2)}€ - Cantidad: ${p.cantidad}</li>`;
                });
                html += '</ul>';
            }
            html += `<p><strong>Valor Total del Inventario:</strong> <span id="inventario-valor">${data.valor_total.toFixed(2)}€</span></p>`;
            inventarioOutputDiv.innerHTML = html;
            // Mostrar mensaje de éxito si la API lo envió
            if (data.mensaje) {
                mostrarMensaje(mensajeInventarioDiv, data.mensaje, 'success');
            }
        } else {
            inventarioOutputDiv.innerHTML = '<p>No se pudieron cargar los datos del inventario.</p>';
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

}); // Fin DOMContentLoaded