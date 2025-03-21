# IUITLM---DAW-1/Introduccion/angular/app-test/Dockerfile (ORIGINAL)

# Define la imagen base de Node.js versión 18 y la llama "build".  Esta imagen se usará como base para la fase de construcción.
FROM node:18 AS build

# Establece el directorio de trabajo dentro del contenedor.  Todo lo que hagamos a partir de ahora será relativo a este directorio.
# Es como usar "cd /app" en tu terminal.  Creamos (si no existe) y nos movemos a una carpeta llamada "/app" dentro del contenedor.
WORKDIR /app

# Copia los archivos package.json y package-lock.json (si existe) al directorio de trabajo actual (/app) del contenedor.
# Estos archivos contienen la lista de dependencias (bibliotecas de terceros) que necesita la aplicación Angular.
#  Se copian antes que el resto del código para aprovechar el caché de Docker (ver siguiente paso).
COPY package*.json ./

# Ejecuta el comando "npm install" dentro del contenedor.
# Este comando lee el archivo package.json y descarga e instala todas las dependencias listadas en él, dentro de una carpeta "node_modules".
# Al copiar solo los archivos de package primero, y ejecutar "npm install", Docker puede cachear esta capa.
# Acelerando el proceso de construcción en futuras ejecuciones del Dockerfile.
RUN npm install

# Copia el resto del código fuente de la aplicación al directorio de trabajo (/app) del contenedor.
#  El "."  significa "todo el contenido del directorio actual (en tu máquina, donde se encuentra el Dockerfile)"
#  y el segundo "."  representa el directorio actual en el contenedor (que es /app).
COPY . .

# Ejecuta el comando "npm run build" con la configuración de producción.
# Esto compila la aplicación Angular, optimizándola para producción.
# El resultado compilado se genera, por defecto, en una carpeta llamada "dist".  El argumento "--configuration production"
#  especifica que se use la configuración definida para "production" en el archivo angular.json.
RUN npm run build -- --configuration production

# --- SEGUNDA ETAPA:  Aquí empieza una nueva imagen base, basada en nginx ---

# Define una nueva imagen base: nginx:stable-alpine.  Esta imagen ya contiene un servidor web Nginx configurado.
# "stable-alpine" es una versión ligera de Nginx, basada en el sistema operativo Alpine Linux, que es muy pequeño.
#  Esta será la imagen final que se usará para ejecutar la aplicación.  Se elige Nginx porque es un servidor web rápido y eficiente.
FROM nginx:stable-alpine

# Elimina el contenido por defecto del directorio donde Nginx sirve los archivos estáticos.
#  Nginx, por defecto, sirve el contenido que se encuentra en "/usr/share/nginx/html/".  Este comando borra cualquier contenido preexistente.
RUN rm -rf /usr/share/nginx/html/

# Copia los archivos compilados de la aplicación Angular (generados en la etapa "build") al directorio de Nginx.
#  "--from=build" indica que se copien archivos desde la etapa anterior llamada "build".
#  "/app/dist/app-test/browser" es la ruta donde se encuentra la aplicación compilada dentro de la imagen "build".
#  "/usr/share/nginx/html" es el directorio donde Nginx buscará los archivos para servir.
COPY --from=build /app/dist/app-test/browser /usr/share/nginx/html

# Elimina el archivo de configuración por defecto de Nginx.  Esto asegura que se usará nuestra configuración personalizada.
RUN rm /etc/nginx/conf.d/default.conf
# Copia el archivo de configuración personalizada de Nginx (angular-nginx.conf) al directorio de configuración de Nginx en el contenedor.
#  Este archivo contiene las reglas específicas para servir nuestra aplicación Angular, como la configuración del servidor,
#  las rutas, y cómo manejar las solicitudes.
COPY angular-nginx.conf /etc/nginx/conf.d/


# Expone el puerto 80 del contenedor.
#  Esto indica que el contenedor escuchará conexiones en el puerto 80 (el puerto estándar para HTTP).  Es necesario para que
#  se pueda acceder a la aplicación desde fuera del contenedor.
EXPOSE 80