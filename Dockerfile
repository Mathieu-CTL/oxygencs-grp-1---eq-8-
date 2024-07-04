# Étape de construction
FROM python:3.8-alpine as builder

# Installer les dépendances nécessaires pour la compilation
RUN apk add --no-cache gcc musl-dev libffi-dev

# Installer pipenv
RUN pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock pour installer les dépendances
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec Pipenv
RUN pipenv install --deploy --ignore-pipfile

# Étape finale
FROM python:3.8-alpine

# Installer les dépendances nécessaires pour l'exécution
RUN apk add --no-cache libffi

WORKDIR /app

# Copier les fichiers de l'application depuis l'étape de construction
COPY . .

# Copier les dépendances installées depuis l'étape de construction
COPY --from=builder /app/.venv /app/.venv

# Ajouter le dossier des binaires locaux au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Commande pour démarrer votre application
CMD ["python", "src/main.py"]