# Étape de construction
FROM python:3.8-alpine as builder

# Installer les dépendances nécessaires pour la compilation et pipenv
RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev && \
    pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock pour installer les dépendances
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
RUN pipenv install --deploy --ignore-pipfile

# Étape finale
FROM python:3.8-alpine

WORKDIR /app

# Installer pipenv dans l'image finale et nettoyer le cache apk
RUN pip install --no-cache-dir pipenv \
    && rm -rf /var/cache/apk/*

# Copier les dépendances installées depuis l'étape de construction
COPY --from=builder /root/.local /root/.local

# Copier les fichiers de l'application depuis l'étape de construction
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["pipenv", "run", "start"]