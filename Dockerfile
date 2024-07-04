# Étape 1: Construction
FROM python:3.8-alpine AS builder

# Installer les dépendances de build et pipenv, définir le répertoire de travail, copier les fichiers de Pipenv, installer les dépendances et copier le reste de l'application
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev \
    && pip install --no-cache-dir pipenv \
    && mkdir /app \
    && cd /app \
    && cp /Pipfile /Pipfile.lock ./ \
    && pipenv install --deploy --ignore-pipfile

# Copier le reste de l'application
COPY . /app

# Étape 2: Exécution
FROM python:3.8-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement les dépendances installées par pipenv depuis l'étape de construction
COPY --from=builder /root/.local /root/.local

# Copier le reste de l'application depuis l'étape de construction
COPY --from=builder /app /app

# Définir le PATH pour inclure les binaires installés par pipenv
ENV PATH=/root/.local/bin:$PATH

# Installer pipenv dans l'image finale
RUN pip install --no-cache-dir pipenv

# Définir la commande par défaut pour exécuter l'application
CMD ["pipenv", "run", "start"]
