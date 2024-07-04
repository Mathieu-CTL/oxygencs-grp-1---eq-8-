FROM python:3.8-alpine

# Installer les dépendances de build et les nettoyer après utilisation
RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
        libxslt-dev \
        libxml2-dev \
    && pip install --no-cache-dir pipenv \
    && rm -rf /var/cache/apk/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration de Pipenv
COPY Pipfile Pipfile.lock ./

# Installer les dépendances de l'application
RUN pipenv install --deploy --ignore-pipfile

# Copier le reste de l'application
COPY . .

# Définir le PATH pour inclure les binaires installés par pipenv
ENV PATH=/root/.local/bin:$PATH

# Définir la commande par défaut pour exécuter l'application
CMD ["pipenv", "run", "start"]