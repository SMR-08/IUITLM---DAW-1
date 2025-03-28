// file: js/registro.js (POTENTIAL CHANGE)
document.addEventListener('DOMContentLoaded', function () {
    const registroForm = document.getElementById('registroForm');
    const mensajeDiv = document.getElementById('mensaje');
    const errorMensajeDiv = document.getElementById('errorMensaje');

    registroForm.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent default form submission

        // Reset messages
        mensajeDiv.classList.add('oculto');
        errorMensajeDiv.classList.add('oculto');

        const nombre = document.getElementById('nombre').value;
        const apellidos = document.getElementById('apellidos').value;
        const dni = document.getElementById('dni').value;
        const contraseña = document.getElementById('contraseña').value;

        // 1. Create Cuenta Request - **UPDATED URL**
        try {
            const cuentaResponse = await fetch('http://api.localhost/cuentas', { // **Added 'http://api.localhost'**
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    titular: nombre + ' ' + apellidos
                })
            });

            if (!cuentaResponse.ok) {
                const errorData = await cuentaResponse.json();
                throw new Error(`Error al crear cuenta: ${errorData.error || cuentaResponse.statusText}`);
            }

            const cuentaData = await cuentaResponse.json();
            const cuentaId = cuentaData.id;

            // 2. Hash DNI and Contraseña (Client-Side - NOT RECOMMENDED for production passwords)
            const dniHash = sha256(dni);
            const contraseñaHash = sha256(contraseña);

            // 3. Create Usuario Request (apiregistro) - **UPDATED URL**
            const usuarioResponse = await fetch('http://api.localhost/apiregistro', { // **Added 'http://api.localhost'**
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dni_usuario: dniHash,
                    contraseña: contraseñaHash,
                    id_cuenta: cuentaId
                })
            });

            if (!usuarioResponse.ok) {
                const errorData = await usuarioResponse.json();
                throw new Error(`Error al registrar usuario: ${errorData.error || usuarioResponse.statusText}`);
            }

            const usuarioData = await usuarioResponse.json();
            mensajeDiv.textContent = 'Usuario y cuenta creados exitosamente. DNI del Usuario : ' + usuarioData.dni_usuario + ', Cuenta ID: ' + usuarioData.cuenta_id;
            mensajeDiv.classList.remove('oculto');

        } catch (error) {
            console.error('Error en el registro:', error);
            errorMensajeDiv.textContent = 'Error en el registro: ' + error.message;
            errorMensajeDiv.classList.remove('oculto');
        }
    });
});