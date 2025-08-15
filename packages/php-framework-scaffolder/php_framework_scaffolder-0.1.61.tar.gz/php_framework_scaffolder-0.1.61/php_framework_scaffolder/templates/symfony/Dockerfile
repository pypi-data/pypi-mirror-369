# syntax=docker/dockerfile:1
FROM php:{{ php_version }}-alpine

RUN apk update

{% for package in apk_packages %}
RUN apk add {{ package }}
{% endfor %}

{% for extension in php_extensions %}
RUN docker-php-ext-install {{ extension }}
{% endfor %}

{% for extension in pecl_extensions %}
RUN pecl install {{ extension }}
RUN docker-php-ext-enable {{ extension }}
{% endfor %}

RUN npm install --global yarn

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer
RUN echo 'memory_limit = 8G' > /usr/local/etc/php/conf.d/docker-php-memlimit.ini

# Install swagger-php globally
RUN --mount=type=cache,target=/tmp/composer/cache \
    COMPOSER_CACHE_DIR=/tmp/composer/cache composer global require zircote/swagger-php:{{ swagger_php_version }}

# Create app directory
WORKDIR /app

# Copy the rest of the application code
COPY ./src ./

# Install composer dependencies with cache mount for faster builds
RUN --mount=type=cache,target=/tmp/composer/cache \
    COMPOSER_CACHE_DIR=/tmp/composer/cache composer install --no-dev --optimize-autoloader --no-scripts

WORKDIR /app/public
ENTRYPOINT [ "php", "-S", "0.0.0.0:80" ]
