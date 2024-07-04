# Étape de construction
FROM python:3.8-alpine as builder

# Installer les dépendances nécessaires pour la compilation et pipenv
RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        python3-dev \
        build-base \
    && pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock pour installer les dépendances
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
RUN pipenv install --deploy --ignore-pipfile

# Étape finale
FROM python:3.8-alpine

WORKDIR /app

# Installer pip sans cache et nettoyer le cache apk
RUN apk add --no-cache libffi-dev \
    && pip install --no-cache-dir pipenv \
    && rm -rf /var/cache/apk/*

# Copier les dépendances installées depuis l'étape de construction
COPY --from=builder /app /app

# Copier les fichiers de l'application
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH=/app/.venv/bin:$PATH

CMD ["pipenv", "run", "start"]