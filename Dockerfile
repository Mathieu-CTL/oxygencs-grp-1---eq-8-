# Utiliser l'image alpine de Python 3.8
FROM python:3.8-alpine

# Installer les dépendances nécessaires pour l'application
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

# Créer le répertoire de travail pour l'application
WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copier les fichiers de l'application
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH="/root/.local/bin:${PATH}"

# Commande par défaut pour exécuter l'application avec pipenv
CMD ["pipenv", "run", "start"]