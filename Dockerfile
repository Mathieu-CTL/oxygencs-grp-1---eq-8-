# Étape finale
FROM python:3.8-alpine

# Installer pipenv dans l'image finale
RUN pip install --no-cache-dir pipenv

WORKDIR /app

# Copier les dépendances installées depuis l'étape de construction
COPY --from=builder /root/.local /root/.local

# Installer pytz dans l'environnement virtuel final
RUN pipenv install pytz

# Copier les fichiers de l'application depuis l'étape de construction
COPY . .

# Ajouter le dossier des binaires locaux au PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["pipenv", "run", "start"]