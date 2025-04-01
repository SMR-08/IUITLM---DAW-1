document.addEventListener('DOMContentLoaded', () => {

    // Obtener el contenedor del formulario de gasto (asumimos que tiene el ID o podemos dárselo)
    const gastoFormContainer = document.getElementById('gasto-form-container'); // Necesitaremos añadir este ID en el HTML

    // Solo proceder si el contenedor del formulario existe (significa que el usuario está logueado y el form se renderizó)
    if (gastoFormContainer) {
        // Obtener el id_cuenta del atributo data-*
        const idCuentaUsuario = parseInt(gastoFormContainer.dataset.idCuenta, 10);
        // URL base para la API de Python
        const apiUrlBaseGasto = 'http://api.localhost'; // O la URL de tu API

        // Referencias a elementos del DOM dentro del contenedor
        const btnRealizarGasto = gastoFormContainer.querySelector('#btn-realizar-gasto');
        const inputGastoCantidad = gastoFormContainer.querySelector('#gasto-cantidad');
        const divMensajeGasto = gastoFormContainer.querySelector('#mensaje-gasto');
        // El span del saldo está fuera del form, lo buscamos por su ID global
        const spanSaldoValor = document.getElementById('saldo-valor');

        // Validar que todos los elementos necesarios existen
        if (!idCuentaUsuario || !btnRealizarGasto || !inputGastoCantidad || !divMensajeGasto || !spanSaldoValor) {
            console.error("Error: No se encontraron todos los elementos necesarios para la funcionalidad de gasto.");
            return; // Detener si falta argo
        }


        // Listener para el botón de gasto
        btnRealizarGasto.addEventListener('click', async () => {
            // Ocultar mensajes previos
            divMensajeGasto.classList.remove('visible', 'success', 'error');
            divMensajeGasto.textContent = '';

            // Obtener y validar la cantidad
            const cantidadStr = inputGastoCantidad.value;
            const cantidadNum = parseFloat(cantidadStr);

            if (isNaN(cantidadNum) || cantidadNum <= 0) {
                mostrarMensajeGasto('Por favor, introduce una cantidad válida y positiva.', 'error');
                return;
            }

            // Deshabilitar botón mientras se procesa
            btnRealizarGasto.disabled = true;
            btnRealizarGasto.textContent = 'Procesando...';

            try {
                console.log(`Intentando realizar gasto de ${cantidadNum} en cuenta ID: ${idCuentaUsuario}`);
                const urlGasto = `${apiUrlBaseGasto}/cuentas/${idCuentaUsuario}/gasto`;

                const respuestaGasto = await fetch(urlGasto, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ cantidad: cantidadNum })
                });

                const datosRespuesta = await respuestaGasto.json();

                if (!respuestaGasto.ok) {
                    console.error('Error API gasto:', respuestaGasto.status, datosRespuesta);
                    throw new Error(datosRespuesta.error || `Error ${respuestaGasto.status}: ${respuestaGasto.statusText}`);
                }

                console.log('Gasto realizado:', datosRespuesta);
                mostrarMensajeGasto(datosRespuesta.mensaje || 'Gasto realizado con éxito.', 'success');

                if (datosRespuesta.nuevo_saldo !== undefined) {
                     // Formato
                     const nuevoSaldoSimple = parseFloat(datosRespuesta.nuevo_saldo).toFixed(2).replace('.', ',');
                     spanSaldoValor.textContent = nuevoSaldoSimple;
                }

                inputGastoCantidad.value = '';

            } catch (error) {
                console.error('Error al realizar el gasto:', error);
                mostrarMensajeGasto(`Error: ${error.message}`, 'error');
            } finally {
                btnRealizarGasto.disabled = false;
                btnRealizarGasto.textContent = 'Confirmar Gasto';
            }
        });

        function mostrarMensajeGasto(texto, tipo = 'error') {
            if (divMensajeGasto) {
                divMensajeGasto.textContent = texto;
                divMensajeGasto.className = `mensaje-gasto ${tipo} visible`;
            }
        }
    }
}); 