# Étape 1: Construction
FROM python:3.8-alpine AS builder

# Définir le répertoire de travail
WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
COPY . .

# Installer les dépendances de l'application
RUN pip install --no-cache-dir pipenv 
RUN pipenv install --deploy --ignore-pipfile

# Définir le PATH pour inclure les binaires installés par pipenv
ENV PATH=/root/.local/bin:$PATH

# Installer pipenv dans l'image finale
RUN pip install --no-cache-dir pipenv

# Définir la commande par défaut pour exécuter l'application
CMD ["pipenv", "run", "start"]
