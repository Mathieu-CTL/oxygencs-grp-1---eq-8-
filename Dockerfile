# Utiliser une image de base légère avec Python 3.8 Alpine
FROM python:3.8-alpine

# Installer pipenv
RUN pip install pipenv

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de Pipfile et Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Installer les dépendances et nettoyer après l'installation
RUN pipenv install --deploy --ignore-pipfile && \
    find /root/.cache -type f -delete

# Copier le code de l'application
COPY . .

# Exposer le port utilisé par l'application (par défaut HTTP)
EXPOSE 80

# Définir la commande pour démarrer l'application
CMD ["pipenv", "run", "start"]