# Étape 1: Construction
FROM python:3.8-alpine AS builder

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendance
COPY Pipfile Pipfile.lock ./

# Installer pipenv et les dépendances de l'application
RUN pip install --no-cache-dir pipenv \
    && pipenv install --deploy --ignore-pipfile

# Copier le contenu de l'application
COPY . .

# Étape 2: Final
FROM python:3.8-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances installées du builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Définir le PATH pour inclure les binaires installés par pipenv
ENV PATH=/root/.local/bin:$PATH

# Installer pipenv dans l'image finale
RUN pip install --no-cache-dir pipenv

# Définir la commande par défaut pour exécuter l'application
CMD ["pipenv", "run", "start"]
