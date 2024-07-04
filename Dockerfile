# Étape de construction
FROM python:3.8-alpine as builder

# Installer les dépendances nécessaires pour la compilation
RUN apk add --no-cache gcc musl-dev libffi-dev

# Installer pipenv
RUN pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les fichiers Pipfile et Pipfile.lock pour installer les dépendances
COPY Pipfile Pipfile.lock ./

# Installer les dépendances avec pipenv
RUN pipenv install --deploy --ignore-pipfile

# Étape finale
FROM python:3.8-alpine

# Installer pipenv dans l'image finale
RUN pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les dépendances installées depuis l'étape de construction
# COPY --from=builder /root/.local /root/.local

# Copier les fichiers de l'application depuis l'étape de construction
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH=/root/.local/bin:$PATH

RUN pip list

CMD ["pipenv", "run", "start"]
