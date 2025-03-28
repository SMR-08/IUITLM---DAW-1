// file: js/registro.js
document.addEventListener('DOMContentLoaded', function () {
    // Obtener el formulario de registro por su ID.
    const formularioRegistro = document.getElementById('registroForm');
    // Obtener el div para mensajes de éxito por su ID.
    const mensajeDiv = document.getElementById('mensaje');
    // Obtener el div para mensajes de error por su ID.
    const mensajeErrorDiv = document.getElementById('errorMensaje');

    // Añadir un listener para el evento 'submit' del formulario.
    formularioRegistro.addEventListener('submit', async function (event) {
        // Prevenir el envío por defecto del formulario.
        event.preventDefault();

        // Resetear mensajes ocultando los divs de mensaje y error.
        mensajeDiv.classList.add('oculto');
        mensajeErrorDiv.classList.add('oculto');

        // Obtener los valores de los campos del formulario.
        const nombre = document.getElementById('nombre').value;
        const apellidos = document.getElementById('apellidos').value;
        const dni = document.getElementById('dni').value;
        const contraseña = document.getElementById('contraseña').value;

        // 1. Crear Solicitud de Cuenta
        try {
            // Realizar una petición POST a la API para crear una cuenta.
            const respuestaCuenta = await fetch('http://api.localhost/cuentas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                // Enviar el nombre completo del titular en el cuerpo de la petición.
                body: JSON.stringify({
                    titular: nombre + ' ' + apellidos
                })
            });

            // Si la respuesta de la cuenta no es exitosa, lanzar un error.
            if (!respuestaCuenta.ok) {
                const datosError = await respuestaCuenta.json();
                throw new Error(`Error al crear cuenta: ${datosError.error || respuestaCuenta.statusText}`);
            }

            // Convertir la respuesta de la cuenta a JSON.
            const datosCuenta = await respuestaCuenta.json();
            // Obtener el ID de la cuenta creada.
            const idCuenta = datosCuenta.id;

            // 2. Hashear DNI y Contraseña (Lado del Cliente - NO RECOMENDADO para contraseñas en producción).
            const dniHash = sha256(dni);
            const contraseñaHash = sha256(contraseña);

            // 3. Crear Solicitud de Usuario (apiregistro)
            // Realizar una petición POST a la API para registrar un usuario.
            const respuestaUsuario = await fetch('http://api.localhost/apiregistro', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                // Enviar DNI hasheado, contraseña hasheada e ID de cuenta en el cuerpo de la petición.
                body: JSON.stringify({
                    dni_usuario: dniHash,
                    contraseña: contraseñaHash,
                    id_cuenta: idCuenta
                })
            });

            // Si la respuesta del usuario no es exitosa, lanzar un error.
            if (!respuestaUsuario.ok) {
                const datosError = await respuestaUsuario.json();
                throw new Error(`Error al registrar usuario: ${datosError.error || respuestaUsuario.statusText}`);
            }

            // Convertir la respuesta del usuario a JSON.
            const datosUsuario = await respuestaUsuario.json();
            // Mostrar mensaje de éxito con el DNI del usuario y el ID de la cuenta.
            mensajeDiv.textContent = 'Usuario y cuenta creados exitosamente. DNI del Usuario : ' + datosUsuario.dni_usuario + ', Cuenta ID: ' + datosUsuario.cuenta_id;
            // Remover la clase 'oculto' para mostrar el mensaje de éxito.
            mensajeDiv.classList.remove('oculto');

        } catch (error) {
            // Capturar errores durante el proceso de registro.
            console.error('Error en el registro:', error);
            // Mostrar mensaje de error en el div correspondiente.
            mensajeErrorDiv.textContent = 'Error en el registro: ' + error.message;
            // Remover la clase 'oculto' para mostrar el mensaje de error.
            mensajeErrorDiv.classList.remove('oculto');
        }
    });
});