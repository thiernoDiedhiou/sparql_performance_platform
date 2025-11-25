# 🗺️ Roadmap - Prochaines Étapes d'Amélioration

## Vue d'ensemble

Suite aux améliorations de **Semaine 1 (Sécurité + Nettoyage)**, ce document détaille les étapes suivantes pour faire passer le projet de **9.0/10** à **9.5/10** (voire 10/10).

---

## 📊 État Actuel

### Score Qualité Global : 9.0/10

| Dimension | Score | Statut |
|-----------|-------|--------|
| **Architecture** | 9/10 | ✅ Excellente |
| **Sécurité** | 9/10 | ✅ Renforcée (Semaine 1) |
| **Tests** | 7/10 | ⚠️ À améliorer |
| **Documentation** | 9.5/10 | ✅ Excellente |
| **Dette Technique** | 8.5/10 | ✅ Réduite |
| **CI/CD** | 0/10 | ❌ Absent |
| **Type Safety** | 7/10 | ⚠️ Partiel |

---

## 🎯 Objectifs par Phase

### Phase 2 : Tests & CI/CD (1-2 mois)
**Objectif : Passer de 7/10 à 9/10 en Tests**

#### Priorité 1 : Couverture de Tests (2 semaines)

**Problème actuel :**
- Couverture : 52% (objectif : 80%+)
- `tests/test_visualizer.py` est **vide**
- Manque de tests d'intégration complets

**Actions :**

1. **Compléter test_visualizer.py** (3-5 jours)
   ```python
   # tests/test_visualizer.py - TODO
   def test_create_comparison_chart():
       """Test création graphiques comparaison"""
       pass  # ACTUELLEMENT VIDE !

   def test_create_heatmap():
       """Test création heatmaps"""
       pass

   def test_export_results():
       """Test export Excel/CSV"""
       pass
   ```

   **Objectif : 15+ tests**

2. **Tests de sécurité** (2-3 jours)
   ```python
   # tests/test_security.py - NOUVEAU
   def test_injection_detection():
       """Tester détection injections SPARQL"""

   def test_dos_protection():
       """Tester limites DoS"""

   def test_credentials_not_hardcoded():
       """Vérifier aucun credential dans code"""
   ```

   **Objectif : 10+ tests**

3. **Tests d'intégration E2E** (3-5 jours)
   ```python
   # tests/test_integration.py - NOUVEAU
   def test_full_benchmark_workflow():
       """Test workflow complet benchmark"""

   def test_data_synchronization_end_to_end():
       """Test synchro Virtuoso → Fuseki complète"""
   ```

   **Objectif : 5+ tests**

**Livrables :**
- ✅ Couverture : 52% → 80%
- ✅ +30 nouveaux tests
- ✅ test_visualizer.py complété
- ✅ Suite de tests de sécurité

---

#### Priorité 2 : CI/CD Pipeline (1 semaine)

**Problème actuel :**
- Pas de CI/CD configuré
- Tests manuels uniquement
- Pas de validation automatique PR

**Actions :**

1. **GitHub Actions - Tests** (1-2 jours)
   ```yaml
   # .github/workflows/tests.yml - NOUVEAU
   name: Tests
   on: [push, pull_request]

   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: ['3.10', '3.11', '3.12']

       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: ${{ matrix.python-version }}

         - name: Install dependencies
           run: |
             pip install -r requirements.txt
             pip install pytest pytest-cov

         - name: Run tests
           run: pytest tests/ --cov=. --cov-report=xml

         - name: Upload coverage to Codecov
           uses: codecov/codecov-action@v3
   ```

2. **GitHub Actions - Linting** (1 jour)
   ```yaml
   # .github/workflows/lint.yml - NOUVEAU
   name: Lint
   on: [push, pull_request]

   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: setup-python@v4

         - name: Install linters
           run: pip install flake8 black mypy

         - name: Run flake8
           run: flake8 . --count --select=E9,F63,F7,F82 --show-source

         - name: Check formatting (black)
           run: black --check .

         - name: Type check (mypy)
           run: mypy --ignore-missing-imports .
   ```

3. **Codecov Integration** (1 jour)
   - Créer compte Codecov
   - Ajouter badge dans README
   - Configurer seuil 80% minimum

**Livrables :**
- ✅ GitHub Actions configuré
- ✅ Tests automatiques sur push/PR
- ✅ Linting automatique
- ✅ Codecov avec badge

---

### Phase 3 : Refactoring & Type Safety (2-4 semaines)

#### Priorité 1 : Refactoring dataset_manager.py

**Problème :**
- Fichier unique de **50KB** (critique !)
- Faible cohésion
- Difficile à maintenir

**Solution :**

```
utils/dataset_manager/
├── __init__.py
├── loader.py           # DatasetLoader
├── graph_manager.py    # GraphManager
├── metadata.py         # MetadataStore
└── validators.py       # Validators
```

**Actions :**
1. Extraire `DatasetLoader` (chargement fichiers)
2. Extraire `GraphManager` (gestion graphes nommés)
3. Extraire `MetadataStore` (persistence JSON)
4. Créer `Validators` (validation formats)

**Durée : 1 semaine**

---

#### Priorité 2 : Exceptions Personnalisées

**Problème :**
- Utilisation de `Exception` générique
- Pas de hiérarchie d'exceptions
- Difficile de catcher erreurs spécifiques

**Solution :**

```python
# utils/exceptions.py - NOUVEAU

class SPARQLPlatformException(Exception):
    """Exception de base"""
    pass

class SecurityException(SPARQLPlatformException):
    """Erreurs de sécurité"""
    pass

class InjectionDetectedException(SecurityException):
    """Injection SPARQL détectée"""
    pass

class EndpointException(SPARQLPlatformException):
    """Erreurs endpoint"""
    pass

class ConnectionException(EndpointException):
    """Erreur de connexion"""
    pass

class QueryTimeoutException(EndpointException):
    """Timeout requête"""
    pass
```

**Durée : 2-3 jours**

---

#### Priorité 3 : Type Hints Complets

**Problème :**
- Type hints partiels (70% couverture)
- Pas de validation mypy
- Risque de bugs runtime

**Actions :**

1. **Ajouter type hints manquants** (1 semaine)
   ```python
   # AVANT
   def execute_query(endpoint_url, query):
       return results

   # APRÈS
   from typing import Dict, Any, Optional

   def execute_query(
       endpoint_url: str,
       query: str,
       timeout: Optional[int] = None
   ) -> Dict[str, Any]:
       return results
   ```

2. **Configurer mypy** (1 jour)
   ```ini
   # mypy.ini - NOUVEAU
   [mypy]
   python_version = 3.10
   warn_return_any = True
   warn_unused_configs = True
   disallow_untyped_defs = True
   disallow_any_generics = True
   check_untyped_defs = True
   no_implicit_optional = True
   ```

3. **Intégrer mypy dans CI** (1 jour)
   - Ajouter à GitHub Actions
   - Bloquer PR si erreurs mypy

**Durée : 1.5 semaines**

---

### Phase 4 : Features Avancées (3-6 mois)

#### 1. Rate Limiting (1 semaine)

```python
# utils/rate_limiter.py - NOUVEAU
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window  # secondes
        self.requests = defaultdict(list)

    def limit(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implémentation sliding window
            now = time.time()
            ip = self._get_client_ip()

            # Nettoyer anciennes requêtes
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if now - req_time < self.window
            ]

            # Vérifier limite
            if len(self.requests[ip]) >= self.max_requests:
                raise RateLimitExceeded(
                    f"Max {self.max_requests} requêtes/{self.window}s"
                )

            self.requests[ip].append(now)
            return func(*args, **kwargs)

        return wrapper
```

**Usage :**
```python
limiter = RateLimiter(max_requests=100, window=60)

@limiter.limit
def execute_query(endpoint, query):
    # ...
```

---

#### 2. Authentification OAuth2 (2 semaines)

```python
# auth/oauth2.py - NOUVEAU
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

oauth.register(
    name='google',
    client_id=get_env('GOOGLE_CLIENT_ID'),
    client_secret=get_env('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

**Intégration Streamlit :**
- Session management
- Protected routes
- Role-based access control (RBAC)

---

#### 3. Monitoring Grafana/Prometheus (3 semaines)

**Architecture :**
```
sparql_platform
├── prometheus_exporter.py  # Exporte métriques
├── grafana_dashboards/
│   ├── overview.json
│   ├── security.json
│   └── performance.json
└── docker-compose.monitoring.yml
```

**Métriques exposées :**
- Nombre de requêtes/seconde
- Temps de réponse (P50, P95, P99)
- Requêtes bloquées (injections)
- Erreurs par endpoint
- Consommation CPU/Mémoire

**Dashboard Grafana :**
- Overview (vue d'ensemble)
- Security (tentatives injection, alertes)
- Performance (latence, throughput)
- Capacity (ressources système)

---

## 📅 Timeline Recommandé

### Mois 1-2 : Tests & CI/CD
```
Semaine 1-2: Amélioration tests (couverture 80%)
Semaine 3:   CI/CD GitHub Actions
Semaine 4-5: Refactoring dataset_manager
Semaine 6:   Exceptions personnalisées
Semaine 7-8: Type hints complets + mypy
```

### Mois 3-4 : Features Intermédiaires
```
Semaine 9-10:  Rate limiting
Semaine 11-13: Authentification OAuth2
Semaine 14-16: Monitoring Prometheus/Grafana
```

### Mois 5-6 : Production & Scalabilité
```
Semaine 17-18: REST API (FastAPI)
Semaine 19-20: Multi-user support
Semaine 21-22: Cloud deployment (AWS/GCP)
Semaine 23-24: Load testing & optimizations
```

---

## 🎯 Objectifs de Score

| Phase | Durée | Score Actuel | Score Cible | Gain |
|-------|-------|--------------|-------------|------|
| **Phase 1 (✅ Fait)** | 1 semaine | 8.5/10 | 9.0/10 | +0.5 |
| **Phase 2** | 1-2 mois | 9.0/10 | 9.3/10 | +0.3 |
| **Phase 3** | 2-4 semaines | 9.3/10 | 9.5/10 | +0.2 |
| **Phase 4** | 3-6 mois | 9.5/10 | 9.8/10 | +0.3 |

**Score Final Visé : 9.8/10** (Exceptionnel)

---

## 🚀 Quick Wins (Court Terme)

Actions rapides à fort impact :

1. **Compléter test_visualizer.py** (1 jour)
   - Impact : +0.1 au score Tests
   - Effort : Faible

2. **Ajouter pre-commit hooks** (2 heures)
   ```bash
   pip install pre-commit

   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.3.0
       hooks:
         - id: black
     - repo: https://github.com/pycqa/flake8
       rev: 6.0.0
       hooks:
         - id: flake8
   ```
   - Impact : Code quality automatique
   - Effort : Très faible

3. **GitHub Actions Tests** (4 heures)
   - Impact : +1.0 au score CI/CD
   - Effort : Faible

4. **Codecov Integration** (2 heures)
   - Impact : Visibilité couverture
   - Effort : Très faible

**Total Quick Wins : 2 jours → Impact majeur**

---

## 📚 Ressources

### Documentation à Consulter
- [GitHub Actions](https://docs.github.com/en/actions)
- [Codecov](https://docs.codecov.com/)
- [Mypy](https://mypy.readthedocs.io/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

### Outils Recommandés
- **Tests** : pytest, pytest-cov, pytest-mock
- **Linting** : flake8, black, mypy
- **CI/CD** : GitHub Actions, GitLab CI
- **Monitoring** : Prometheus, Grafana
- **Security** : Bandit, Safety

---

## ✅ Checklist de Démarrage Phase 2

Avant de commencer Phase 2, vérifier :

- [x] Phase 1 complétée (Sécurité + Nettoyage)
- [x] Tous les tests passent (12/12)
- [x] .env configuré avec credentials
- [x] SECURITY.md lu et compris
- [ ] GitHub Actions activé
- [ ] Codecov account créé
- [ ] Branche `develop` créée
- [ ] Roadmap partagée avec l'équipe

---

**Dernière mise à jour** : 22 novembre 2025
**Version** : 3.1.1
**Auteur** : Équipe SPARQL Performance Platform

**Prêt pour Phase 2 !** 🚀
