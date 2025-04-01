// file: js/registro.js
document.addEventListener('DOMContentLoaded', function () {
    const formularioRegistro = document.getElementById('formularioRegistro');
    const divMensaje = document.getElementById('mensaje');
    const divMensajeError = document.getElementById('mensajeError');

    formularioRegistro.addEventListener('submit', async function (evento) {
        evento.preventDefault();

        divMensaje.classList.add('oculto');
        divMensajeError.classList.add('oculto');
        divMensaje.textContent = '';
        divMensajeError.textContent = '';

        const nombre = document.getElementById('nombre').value.trim();
        const apellidos = document.getElementById('apellidos').value.trim();
        const dni = document.getElementById('dni').value.trim(); // DNI en texto plano
        const contrasena = document.getElementById('contrasena').value; // Contraseña en texto plano

        if (!nombre || !apellidos || !dni || !contrasena) {
            divMensajeError.textContent = 'Todos los campos son obligatorios.';
            divMensajeError.classList.remove('oculto');
            return;
        }

        // IMPORTANTE: Asegúrate de que la conexión a tu API sea sobre HTTPS en producción
        // Enviar contraseñas en texto plano sobre HTTP es inseguro.
        const apiUrlBase = 'http://api.localhost'; // O la URL correcta de tu API

        try {
            // 1. Crear Solicitud de Cuenta (sin cambios aquí)
            console.log('Enviando solicitud para crear cuenta...');
            const respuestaCuenta = await fetch(`${apiUrlBase}/cuentas`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    titular: nombre + ' ' + apellidos
                })
            });

            console.log('Respuesta recibida de /cuentas:', respuestaCuenta.status);
            if (!respuestaCuenta.ok) {
                const datosError = await respuestaCuenta.json().catch(() => ({ error: 'Respuesta no JSON del servidor (cuenta)' }));
                throw new Error(`Error al crear cuenta (${respuestaCuenta.status}): ${datosError.error || respuestaCuenta.statusText}`);
            }

            const datosCuenta = await respuestaCuenta.json();
            const idCuenta = datosCuenta.id;
            console.log(`Cuenta creada con ID: ${idCuenta}`);

            // 2. Crear Solicitud de Usuario (apiregistro) - Enviando datos en plano
            //    La API Python se encargará del hashing
            console.log('Enviando solicitud para registrar usuario (datos en plano)...');
            const respuestaUsuario = await fetch(`${apiUrlBase}/apiregistro`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    // Nombres de campo que la API modificada esperará
                    dni_plain: dni,
                    contrasena_plain: contrasena,
                    id_cuenta: idCuenta
                    // Ya no enviamos 'dni_usuario' ni 'contraseña' hasheados desde aquí
                })
            });

            console.log('Respuesta recibida de /apiregistro:', respuestaUsuario.status);
            if (!respuestaUsuario.ok) {
                const datosError = await respuestaUsuario.json().catch(() => ({ error: 'Respuesta no JSON del servidor (usuario)' }));
                throw new Error(`Error al registrar usuario (${respuestaUsuario.status}): ${datosError.error || respuestaUsuario.statusText}`);
            }

            const datosUsuario = await respuestaUsuario.json();
            // Mensaje de éxito (el backend ahora devuelve el ID de cuenta, podemos usarlo)
            divMensaje.textContent = 'Usuario y cuenta creados exitosamente. ID de Cuenta: ' + datosUsuario.id_cuenta;
            divMensaje.classList.remove('oculto');

            formularioRegistro.reset();
            // setTimeout(() => { window.location.href = 'acceso.html'; }, 3000);

        } catch (error) {
            console.error('Error en el proceso de registro:', error);
            divMensajeError.textContent = 'Error en el registro: ' + error.message;
            divMensajeError.classList.remove('oculto');
        }
    });
});