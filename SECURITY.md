# 🔐 Guide de Sécurité - SPARQL Performance Testing Platform

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Configuration Sécurisée](#configuration-sécurisée)
3. [Gestion des Credentials](#gestion-des-credentials)
4. [Protection contre les Injections](#protection-contre-les-injections)
5. [Bonnes Pratiques](#bonnes-pratiques)
6. [Audit et Monitoring](#audit-et-monitoring)
7. [Signalement de Vulnérabilités](#signalement-de-vulnérabilités)

---

## Vue d'ensemble

Cette plateforme implémente plusieurs couches de sécurité pour protéger contre les vulnérabilités courantes :

- ✅ **Gestion sécurisée des credentials** via variables d'environnement
- ✅ **Validation anti-injection SPARQL** pour bloquer les requêtes malveillantes
- ✅ **Protection DoS** avec limites de complexité et de taille de requête
- ✅ **Logging des événements** de sécurité
- ✅ **Séparation des environnements** (dev, staging, production)

---

## Configuration Sécurisée

### 1. Fichier `.env` (OBLIGATOIRE)

**⚠️ CRITIQUE : Ne JAMAIS commiter le fichier `.env` dans Git !**

Le fichier `.env` contient des informations sensibles. Il est automatiquement exclu par `.gitignore`.

#### Création Initiale

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos credentials réels
nano .env  # ou code .env
```

#### Variables Critiques

```bash
# ENDPOINTS
VIRTUOSO_ENDPOINT=http://localhost:8890/sparql
FUSEKI_ENDPOINT=http://localhost:3030/dataset/query

# CREDENTIALS (À CHANGER EN PRODUCTION !)
VIRTUOSO_USERNAME=SPARQL
VIRTUOSO_PASSWORD=VotreMotDePasseSecurise123!

FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=AutreMotDePasseSecurise456!

# SÉCURITÉ APPLICATION
ENABLE_AUTHENTICATION=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=MotDePasseAdminTresSecurise789!
```

### 2. Permissions Fichier

```bash
# Linux/macOS : Restreindre l'accès au fichier .env
chmod 600 .env

# Vérifier les permissions
ls -la .env
# Doit afficher : -rw------- (lecture/écriture propriétaire uniquement)
```

### 3. Environnements Multiples

Utilisez des fichiers `.env` différents par environnement :

```bash
.env                 # Local development (ignoré par git)
.env.development     # Dev partagé (optionnel, ignoré par git)
.env.staging         # Staging (secrets vault)
.env.production      # Production (secrets vault)
.env.example         # Template PUBLIC (committé dans git)
```

---

## Gestion des Credentials

### ❌ MAUVAISE PRATIQUE

```python
# NE JAMAIS FAIRE CECI !
VIRTUOSO_PASSWORD = "admin123"  # Hardcodé dans le code
credentials = {"user": "admin", "pass": "secret"}  # Dangereux
```

### ✅ BONNE PRATIQUE

```python
# Utiliser les variables d'environnement
from config.env_loader import get_env

VIRTUOSO_USERNAME = get_env("VIRTUOSO_USERNAME", "SPARQL")
VIRTUOSO_PASSWORD = get_env("VIRTUOSO_PASSWORD", None)

# Vérifier que le mot de passe est défini
if not VIRTUOSO_PASSWORD:
    raise ValueError("VIRTUOSO_PASSWORD doit être défini dans .env")
```

### Rotation des Mots de Passe

**Fréquence recommandée :**
- Développement : 90 jours
- Staging : 60 jours
- Production : 30 jours

**Procédure :**

1. Générer un nouveau mot de passe fort
   ```bash
   # Générer un mot de passe aléatoire (Linux/macOS)
   openssl rand -base64 32
   ```

2. Mettre à jour `.env`
   ```bash
   VIRTUOSO_PASSWORD=NouveauMotDePasseSecurise
   ```

3. Redémarrer l'application
   ```bash
   docker-compose restart
   ```

---

## Protection contre les Injections

### Validation Automatique

La plateforme valide **automatiquement** toutes les requêtes SPARQL avant exécution.

#### Requêtes Bloquées

Les opérations de **modification** sont interdites :

```sparql
-- ❌ BLOQUÉES
INSERT DATA { ... }
DELETE WHERE { ... }
DROP GRAPH <http://example.org/graph>
LOAD <http://malicious.com/data>
CLEAR GRAPH <http://example.org/graph>
```

#### Requêtes Autorisées

Seules les requêtes de **lecture** sont permises :

```sparql
-- ✅ AUTORISÉES
SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 100
ASK { ?s a <http://example.org/Person> }
CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o } LIMIT 100
DESCRIBE <http://example.org/resource/123>
```

### Limites de Sécurité

```python
# core/executor.py - Configuration par défaut

MAX_QUERY_LENGTH = 50000     # 50KB maximum
MAX_NESTING_LEVEL = 10       # 10 niveaux d'imbrication max
QUERY_TIMEOUT = 60           # 60 secondes max par requête
```

### Contournement (Opérations Internes Uniquement)

Pour les opérations internes légitimes (synchronisation, chargement de données) :

```python
# Utiliser skip_security_check=True (AVEC PRUDENCE)
executor = QueryExecutor()
result = executor.execute_query(
    endpoint_url=VIRTUOSO_ENDPOINT,
    query=insert_query,
    skip_security_check=True  # ⚠️ Réservé aux opérations internes de confiance
)
```

---

## Bonnes Pratiques

### 1. Principe du Moindre Privilège

```python
# ✅ Créer un utilisateur SPARQL en lecture seule
# Sur Virtuoso :
CREATE USER sparql_readonly;
GRANT SPARQL_SELECT TO sparql_readonly;

# Utiliser dans .env
VIRTUOSO_USERNAME=sparql_readonly
VIRTUOSO_PASSWORD=MotDePasseLectureSeule
```

### 2. Endpoints Séparés

```bash
# Lecture (accessible publiquement)
VIRTUOSO_READ_ENDPOINT=http://localhost:8890/sparql

# Écriture (accessible uniquement en interne)
VIRTUOSO_WRITE_ENDPOINT=http://localhost:8890/sparql-auth
```

### 3. Rate Limiting

**TODO** : Implémenter un rate limiter (future release)

```python
# Planifié pour v3.2
from utils.rate_limiter import RateLimiter

limiter = RateLimiter(max_requests=100, window=60)  # 100 req/min

@limiter.limit
def execute_query(endpoint, query):
    # ...
```

### 4. Logging des Événements de Sécurité

Tous les événements de sécurité sont loggés automatiquement :

```python
# Requête bloquée → Logged dans logs/sparql_platform.log
⚠️ [2025-11-22 10:30:45] Requête bloquée pour raison de sécurité:
   Opération 'DELETE' non autorisée
   IP: 192.168.1.100
   User-Agent: Mozilla/5.0
   Endpoint: http://localhost:8890/sparql
```

Vérifier les logs régulièrement :

```bash
# Filtrer les événements de sécurité
grep "sécurité" logs/sparql_platform.log

# Compter les requêtes bloquées
grep -c "bloquée" logs/sparql_platform.log
```

### 5. HTTPS en Production

**⚠️ OBLIGATOIRE pour la production !**

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    environment:
      - SSL_CERTIFICATE=/etc/nginx/ssl/cert.pem
      - SSL_KEY=/etc/nginx/ssl/key.pem
```

Générer un certificat SSL :

```bash
# Self-signed (dev/staging)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Production : Utiliser Let's Encrypt
certbot certonly --standalone -d votredomaine.com
```

---

## Audit et Monitoring

### 1. Checklist de Sécurité

Avant le déploiement en production :

- [ ] `.env` contient des mots de passe forts (≥16 caractères, alphanumériques + symboles)
- [ ] `.env` est exclu de Git (vérifié dans `.gitignore`)
- [ ] Aucun credential hardcodé dans le code source
- [ ] Validation anti-injection activée
- [ ] HTTPS configuré avec certificat valide
- [ ] Logs de sécurité activés
- [ ] Permissions fichiers restreintes (600 pour .env)
- [ ] Endpoints de lecture/écriture séparés
- [ ] Rate limiting configuré (si applicable)
- [ ] Backup automatique des données sensibles

### 2. Tests de Sécurité

Exécuter les tests de sécurité :

```bash
# Tests unitaires incluant validation
pytest tests/test_executor.py::test_security_validation -v

# Test d'injection manuel
python -c "
from core.executor import QueryExecutor
executor = QueryExecutor()

# Tenter une injection
malicious_query = 'SELECT * WHERE { ?s ?p ?o } ; DROP GRAPH <http://example.org/graph>'
result = executor.execute_query('http://localhost:8890/sparql', malicious_query)

assert result['security_blocked'] == True
print('✅ Protection anti-injection fonctionne')
"
```

### 3. Monitoring en Production

**Métriques à surveiller :**

- Nombre de requêtes bloquées par heure
- Tentatives d'injection détectées
- Requêtes dépassant le timeout
- Erreurs d'authentification
- Pics de trafic anormaux

**Alertes recommandées :**

```yaml
# alerts.yml (Prometheus/Grafana)
groups:
  - name: security
    rules:
      - alert: HighRejectedQueries
        expr: rate(security_blocked_queries[5m]) > 10
        annotations:
          summary: "Taux élevé de requêtes bloquées"

      - alert: PossibleInjectionAttack
        expr: increase(injection_attempts[1h]) > 50
        annotations:
          summary: "Possible attaque par injection SPARQL"
```

---

## Signalement de Vulnérabilités

### Politique de Divulgation Responsable

Si vous découvrez une vulnérabilité de sécurité :

1. **NE PAS** divulguer publiquement (GitHub Issues, forums, etc.)
2. **Envoyer un email privé** à : `security@example.com`
3. **Inclure** :
   - Description de la vulnérabilité
   - Étapes de reproduction
   - Impact potentiel
   - Version affectée

### Récompenses

Programme de bug bounty disponible pour les vulnérabilités critiques.

**Niveaux de sévérité :**

| Niveau | Description | Récompense |
|--------|-------------|------------|
| 🔴 Critique | Exécution de code à distance, accès non autorisé aux données | 500€ - 2000€ |
| 🟠 Élevée | Injection SQL/SPARQL, XSS, CSRF | 200€ - 500€ |
| 🟡 Moyenne | Fuite d'informations sensibles, DoS | 50€ - 200€ |
| 🟢 Faible | Problèmes de configuration, warnings | Reconnaissance |

### Contact

- **Email** : security@example.com
- **PGP Key** : [Public Key](https://example.com/pgp.asc)
- **Délai de réponse** : 48h max

---

## Ressources Additionnelles

### Documentation Officielle

- [OWASP SPARQL Injection](https://owasp.org/www-community/vulnerabilities/SPARQL_Injection)
- [Virtuoso Security Guide](http://docs.openlinksw.com/virtuoso/rdfsecurity/)
- [Jena Fuseki Security](https://jena.apache.org/documentation/fuseki2/fuseki-security.html)

### Outils de Test

```bash
# Scanner de vulnérabilités
docker run --rm -v $(pwd):/code trailofbits/echidna /code

# Audit de sécurité Python
pip install bandit
bandit -r . -f html -o security_report.html
```

### Standards de Conformité

Cette plateforme vise à respecter :

- **OWASP Top 10** (Web Application Security)
- **CWE Top 25** (Common Weakness Enumeration)
- **GDPR** (protection des données personnelles)

---

## Changelog de Sécurité

### v3.1 (2025-11-22)

- ✅ Migration des credentials vers `.env`
- ✅ Ajout validation anti-injection SPARQL
- ✅ Création de `.gitignore` complet
- ✅ Protection DoS (limites de longueur/complexité)
- ✅ Logging des événements de sécurité

### v3.0

- Validation basique de syntaxe SPARQL
- Timeout sur requêtes

### Prochaines Versions

- 🔜 Rate limiting par IP
- 🔜 Authentification OAuth2
- 🔜 Audit trail complet
- 🔜 Chiffrement des logs

---

**Dernière mise à jour** : 22 novembre 2025
**Version** : 3.1
**Auteur** : Équipe SPARQL Performance Platform
