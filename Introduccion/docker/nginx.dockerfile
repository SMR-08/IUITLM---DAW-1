# Usa la imagen base oficial de Nginx, la versión más reciente.
FROM nginx:latest

# Establece el directorio de trabajo dentro del contenedor en /var/www/html.
# Este es el directorio donde Nginx busca los archivos por defecto.
WORKDIR /var/www/html

# Elimina todos los archivos y directorios existentes dentro del directorio de trabajo.
# Esto asegura que el contenido por defecto de Nginx sea eliminado antes
# de que el volumen con nuestro código sea montado por docker-compose.
RUN rm -rf ./*

# NOTA: No se necesita copiar el contenido de 'www' aquí,
# ya que se monta como un volumen en docker-compose.yaml.
# COPY --chown=www-data:www-data www/. ./  <-- ELIMINADO

# NOTA: No se necesita copiar 'default.conf' aquí si se va a montar
# desde docker-compose.yaml. Si necesitas una configuración base *en la imagen*,
# podrías mantenerla, pero es más flexible gestionarla con volúmenes.
# COPY default.conf /etc/nginx/conf.d/default.conf <-- ELIMINADO (se monta en compose)

# Expone el puerto 80 del contenedor para que sea accesible desde el exterior.
EXPOSE 80