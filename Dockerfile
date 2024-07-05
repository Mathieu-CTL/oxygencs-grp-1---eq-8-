# Étape 1: Construction
FROM python:3.8-alpine AS builder

# Installer les dépendances de build
RUN pip install --no-cache-dir pipenv 

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration de Pipenv
COPY Pipfile Pipfile.lock ./

# Installer les dépendances de l'application
RUN pipenv install --deploy --ignore-pipfile

# Copier le reste de l'application
COPY . .

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

