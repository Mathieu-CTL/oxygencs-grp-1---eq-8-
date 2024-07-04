# Étape de construction
FROM python:3.8-slim as builder

# Installer les dépendances nécessaires pour la compilation et pipenv
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libffi-dev \
        build-essential \
    && pip install --no-cache-dir pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock pour installer les dépendances
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
RUN pipenv install --deploy --ignore-pipfile

# Étape finale
FROM python:3.8-slim

WORKDIR /app

# Copier les dépendances installées depuis l'étape de construction
COPY --from=builder /app /app

# Copier les fichiers de l'application depuis l'étape de construction
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH=/app/.venv/bin:$PATH

CMD ["pipenv", "run", "start"]