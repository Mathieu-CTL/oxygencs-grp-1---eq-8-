# Étape de construction
FROM python:3.8-alpine as builder

# Installer les dépendances nécessaires pour la compilation et pipenv
RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        python3-dev \
        build-base \
        openssl-dev \
        libressl-dev \
    && pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock pour installer les dépendances
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
RUN pipenv install --deploy --ignore-pipfile

# Étape finale
FROM python:3.8-alpine

WORKDIR /app

# Installer les dépendances nécessaires pour l'exécution
RUN apk add --no-cache libffi-dev openssl-dev

# Copier l'environnement virtuel créé dans l'étape de construction
COPY --from=builder /app/.venv /app/.venv

# Copier les fichiers de l'application
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["pipenv", "run", "start"]