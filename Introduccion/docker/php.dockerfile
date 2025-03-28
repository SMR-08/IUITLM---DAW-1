FROM php:8.2-fpm

# Install the mysqli extension
RUN docker-php-ext-install mysqli