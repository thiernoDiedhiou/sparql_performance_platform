# Dockerfile pour la plateforme SPARQL Performance Testing
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="Votre Nom <email@example.com>"
LABEL description="Plateforme d'évaluation de performance SPARQL - Virtuoso vs Jena Fuseki"
LABEL version="2.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs results data

# Exposition du port Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Command de démarrage
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
