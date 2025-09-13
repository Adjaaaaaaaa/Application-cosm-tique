# 🎯 BeautyScan - Assistant Beauté IA

## 📋 Description

**BeautyScan** est une application web intelligente qui révolutionne l'expérience cosmétique en proposant des conseils personnalisés basés sur l'intelligence artificielle. L'application utilise Azure OpenAI GPT-4 pour analyser les ingrédients cosmétiques, générer des routines personnalisées et fournir des recommandations adaptées au profil unique de chaque utilisateur.

Architecture API:
- **API Django (REST v1)**: endpoints principaux sous `http://127.0.0.1:8000/api/v1/...`
- **Service FastAPI (profils)**: récupération des profils sous `http://127.0.0.1:8002/...`

### 🎯 Objectifs du Projet
- **Transparence cosmétique** : Décrypter les listes d'ingrédients complexes
- **Personnalisation avancée** : Routines adaptées au type de peau, allergies et objectifs
- **Intelligence artificielle** : Conseils experts via Azure OpenAI GPT-4
- **Expérience utilisateur** : Interface intuitive et design élégant

## ⚙️ Prérequis

### Logiciels Requis
- **Python** : Version 3.8 ou supérieure
- **pip** : Gestionnaire de paquets Python
- **Git** : Contrôle de version
- **Navigateur web** : Chrome, Firefox, Safari ou Edge

### Comptes et Services
- **Azure OpenAI** : Compte avec accès GPT-4 (optionnel)
- **Stripe** : Compte pour les paiements (optionnel)
- **Compte GitHub** : Pour contribuer au projet

### Configuration Système
- **RAM** : Minimum 4GB (recommandé 8GB+)
- **Espace disque** : 2GB minimum
- **Réseau** : Connexion internet stable

## 🚀 Installation

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/cosmetic-scan-application.git
cd cosmetic-scan-application
```

### 2. Créer l'Environnement Virtuel
```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement (Linux/Mac)
source .venv/bin/activate

# Activer l'environnement (Windows)
.venv\Scripts\activate
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration des Variables d'Environnement
```bash
# Copier le template
cp .env.example .env

# Éditer le fichier .env avec vos clés
nano .env  # Linux/Mac
# ou
notepad .env  # Windows
```

**Variables obligatoires :**
```env
SECRET_KEY=votre-clé-secrète-django
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True
```

**Variables Azure OpenAI (obligatoires pour l'IA):**
```env
AZURE_OPENAI_API_KEY=votre-clé-azure-openai
AZURE_OPENAI_ENDPOINT=https://votre-ressource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
OPENAI_MODEL=gpt-4.1  # ou le nom du déploiement Azure (ex: gpt-4o)
```

**Paiements (optionnel):**
```env
STRIPE_PUBLISHABLE_KEY=votre-clé-stripe-publique
STRIPE_SECRET_KEY=votre-clé-stripe-secrète
```

### 5. Initialiser la Base de Données
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Vérifier l'Installation
```bash
python manage.py check
python manage.py runserver 8000
```

## 🎮 Utilisation

### Démarrage Rapide
```bash
# Méthode recommandée
python start_server.py

# Méthode manuelle
python manage.py runserver 8000
```

### Guide technique détaillé (étapes pas à pas)

1) Prérequis système
- Installer Python 3.10+ et pip
- Installer Git
- Windows: PowerShell; Linux/Mac: bash/zsh

2) Clonage et environnement
```bash
git clone https://github.com/votre-username/cosmetic-scan-application.git
cd cosmetic-scan-application
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3) Dépendances
```bash
pip install -r requirements.txt
```

4) Configuration .env (minimum fonctionnel)
```env
SECRET_KEY=generez-une-cle
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True

# Azure OpenAI (obligatoire pour IA)
AZURE_OPENAI_API_KEY=votre-cle
AZURE_OPENAI_ENDPOINT=https://votre-ressource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
OPENAI_MODEL=gpt-4.1

# Optionnel paiements
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
```

5) Base de données (SQLite dev par défaut)
```bash
python manage.py migrate
python manage.py createsuperuser
```

6) Lancer le serveur (dev)
```bash
python start_server.py
# ou
python manage.py runserver 8000
```

7) Vérifications rapides
- Interface: http://127.0.0.1:8000/
- Assistant IA: http://127.0.0.1:8000/ai-routines/beauty-assistant/
- API health: `curl http://127.0.0.1:8000/api/v1/health/`

8) Test IA (cURL)
```bash
curl -X POST http://127.0.0.1:8000/ai-routines/assistant-api/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bienfaits de la vaseline ?",
    "routine_type": "general",
    "budget": 50
  }'
```

9) Utiliser FastAPI pour les profils (obligatoire)
- Définir: `PROFILE_API_URL=http://127.0.0.1:8002`
- Lancer: `uvicorn backend.fastapi_app:app --host 127.0.0.1 --port 8002 --reload`
- L’app récupère le profil UNIQUEMENT via FastAPI (`GET /user/profile?user_id=...`). Aucune bascule ORM.

9) Logs et debug
- Activer logs: `export DJANGO_LOG_LEVEL=DEBUG` (Linux/Mac) / `set DJANGO_LOG_LEVEL=DEBUG` (Windows)
- Surveiller le terminal pour les appels Azure/erreurs

10) Optimisation production (résumé)
- `DEBUG=False`, `ALLOWED_HOSTS` configurés
- `python manage.py collectstatic --noinput`
- Gunicorn: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4`
- Serveur statique (nginx) avec cache (Cache-Control, ETag)

### Accès à l'Application
- **Interface principale** : http://127.0.0.1:8000/
- **Assistant IA** : http://127.0.0.1:8000/ai-routines/beauty-assistant/
- **Profil utilisateur** : http://127.0.0.1:8000/accounts/profile/
- **Paiements Premium** : http://127.0.0.1:8000/payments/upgrade/
  
Notes ports: l'application tourne sur le port 8000 (frontend+API). Si vous utilisez un backend séparé sur 8002, adaptez les URLs d'API en conséquence.

### Exemples d'Utilisation

#### 1. Créer un Compte et Profil
```bash
# Accéder à l'inscription
http://127.0.0.1:8000/accounts/signup/

# Remplir le profil avec :
# - Type de peau : Normal, sèche, grasse, mixte
# - Âge : 18-25, 26-35, 36-45, 46-60, 60+
# - Allergies : Parfums, huiles essentielles, conservateurs
# - Objectifs : Anti-âge, hydratation, éclat, acné
```

#### 2. Générer une Routine Personnalisée
```bash
# Via l'interface web
1. Aller sur l'Assistant IA
2. Sélectionner "Routine personnalisée"
3. Choisir le type : Matin, Soir, Cheveux, Corps
4. Définir le budget (ex: 80€)
5. Ajouter une question spécifique (optionnel)
6. Cliquer sur "Générer ma routine"
```

#### 3. Analyser un Ingrédient
```bash
# Via l'interface web
1. Sélectionner "Analyse d'ingrédient"
2. Entrer le nom : "rétinol", "vitamine C", "zinc"
3. Obtenir l'analyse complète avec :
   - Bienfaits généraux
   - Effets selon votre type de peau
   - Produits recommandés
   - Précautions et conseils
```

#### 5. Poser une Question Générale (API)
```bash
curl -X POST http://127.0.0.1:8000/ai-routines/assistant-api/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bienfaits de la vaseline ?",
    "routine_type": "general",
    "budget": 50
  }'
```

#### 4. Utiliser l'API Django (REST v1)
```bash
# Health Check
curl http://127.0.0.1:8000/api/v1/health/

# Générer une routine
curl -X POST http://127.0.0.1:8000/api/v1/enhanced-ai/comprehensive-routine/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "routine_type": "morning",
    "user_question": "Routine anti-âge pour peau sèche",
    "budget": 100
  }'

# Analyser un ingrédient
curl -X POST http://127.0.0.1:8000/api/v1/ai/analyze-product/ \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_name": "rétinol",
    "user_id": 1
  }'
```

## ✨ Fonctionnalités

### 🔐 Gestion des Comptes
- **Inscription/Connexion** : Système d'authentification sécurisé
- **Profils personnalisés** : Sauvegarde complète des préférences
- **Gestion des allergies** : Suivi des intolérances et restrictions
- **Historique des routines** : Suivi des recommandations précédentes

### 🤖 Assistant Beauté IA
- **Routines personnalisées** : Génération automatique selon le profil
- **Analyse d'ingrédients** : Décryptage des composants cosmétiques
- **Questions générales** : Conseils personnalisés sur la beauté
- **Adaptation en temps réel** : Mise à jour des recommandations

### 💳 Système Premium
- **Paiements sécurisés** : Intégration Stripe et PayPal
- **Fonctionnalités avancées** : Routines détaillées et analyses approfondies
- **Gestion des abonnements** : Activation/désactivation Premium
- **Support prioritaire** : Assistance dédiée aux utilisateurs Premium

### 🔧 API Django (REST v1)
- **Endpoints standardisés** : Architecture RESTful
- **Authentification** : Gestion des sessions utilisateur
- **Documentation** : Endpoints documentés et testables
- **Performance** : Optimisation des requêtes et cache

## ⚙️ Configuration

### Configuration de Base
```python
# config/settings/dev.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Configuration Azure OpenAI
```python
# backend/core/config.py
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("OPENAI_MODEL", "gpt-4")
```

### Configuration Stripe
```python
# config/stripe_config.py
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

### Variables d'Environnement Avancées
```env
# Développement
DJANGO_DEVELOPMENT=True
IS_DEVELOPMENT=True
LOCAL_DEVELOPMENT=True

# Base de données
DB_NAME=db.sqlite3

# Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Production
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com
```

### Documents de configuration détaillée
- Doc complémentaire: `STRIPE_SETUP.md` (paiements Stripe)

## 📁 Structure du Projet

```
cosmetic-scan-application/
├── 📁 apps/                          # Applications Django principales
│   ├── 📁 accounts/                  # Gestion des comptes utilisateurs
│   │   ├── 📁 migrations/            # Migrations de base de données
│   │   ├── 📁 templates/             # Templates HTML des comptes
│   │   ├── models.py                 # Modèles User et UserProfile
│   │   ├── views.py                  # Vues d'authentification et profil
│   │   └── urls.py                   # Routes des comptes
│   ├── 📁 ai_routines/               # Assistant beauté IA
│   │   ├── 📁 services/              # Services métier IA
│   │   ├── 📁 templates/             # Templates de l'assistant
│   │   ├── views.py                  # Vues de l'assistant IA
│   │   └── urls.py                   # Routes de l'assistant
│   ├── 📁 scans/                     # Scan et analyse de produits
│   │   ├── 📁 services/              # Services d'analyse
│   │   ├── 📁 templates/             # Templates de scan
│   │   └── views.py                  # Vues de scan
│   └── 📁 payments/                  # Gestion des paiements Premium
│       ├── 📁 templates/             # Templates de paiement
│       ├── views.py                  # Vues de paiement
│       └── urls.py                   # Routes de paiement
├── 📁 backend/                       # Services backend et configuration
│   ├── 📁 services/                  # Services métier principaux
│   │   ├── ai_service.py             # Service principal IA
│   │   ├── enhanced_routine_service.py # Service de génération de routines
│   │   ├── user_service.py           # Service de gestion utilisateur
│   │   ├── ingredient_service.py     # Service d'analyse d'ingrédients
│   │   └── rag_service.py            # Service RAG pour la recherche
│   └── 📁 core/                      # Configuration core
│       ├── config.py                 # Configuration des services
│       ├── exceptions.py             # Gestion des exceptions
│       └── logging.py                # Configuration des logs
├── 📁 config/                        # Configuration Django
│   ├── 📁 settings/                  # Fichiers de configuration
│   │   ├── base.py                   # Configuration de base
│   │   ├── dev.py                    # Configuration développement
│   │   └── prod.py                   # Configuration production
│   ├── urls.py                       # Routes principales
│   ├── env.py                        # Gestion des variables d'environnement
│   └── stripe_config.py              # Configuration Stripe
├── 📁 common/                        # Utilitaires communs
│   ├── mixins.py                     # Mixins Django
│   ├── premium_utils.py              # Utilitaires Premium
│   └── utils.py                      # Utilitaires généraux
├── 📁 templates/                     # Templates HTML globaux
│   ├── base.html                     # Template de base
│   ├── 📁 layout/                    # Composants de mise en page
│   │   ├── navbar.html               # Barre de navigation
│   │   └── footer.html               # Pied de page
│   └── 📁 partials/                  # Composants partiels
├── 📁 static/                        # Fichiers statiques
│   ├── 📁 css/                       # Feuilles de style
│   ├── 📁 js/                        # Scripts JavaScript
│   └── 📁 images/                    # Images et icônes
├── 📄 requirements.txt                # Dépendances Python
├── 📄 start_server.py                 # Script de démarrage automatique
├── 📄 manage.py                       # Gestionnaire Django
├── 📄 .env.example                    # Template des variables d'environnement
├── 📄 .gitignore                      # Fichiers ignorés par Git
└── 📄 README.md                       # Documentation du projet
```

### Fichiers Clés
- **`start_server.py`** : Point d'entrée principal avec vérifications automatiques
- **`config/env.py`** : Gestion centralisée des variables d'environnement
- **`backend/services/`** : Services métier avec architecture modulaire
- **`apps/ai_routines/`** : Application principale de l'assistant IA
- **`templates/base.html`** : Template de base avec système de notifications

## 🧪 Tests

### Tests Unitaires
```bash
# Lancer tous les tests
python manage.py test

# Tests d'une application spécifique
python manage.py test apps.accounts
python manage.py test apps.ai_routines

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Tests d'Intégration
```bash
# Test de l'API
python manage.py test apps.api_views

# Test des services
python manage.py test backend.services

# Test des paiements
python manage.py test apps.payments
```

### Tests Manuels
```bash
# Test de l'API Health Check
curl http://127.0.0.1:8000/api/v1/health/

# Test de génération de routine
curl -X POST http://127.0.0.1:8000/api/v1/enhanced-ai/comprehensive-routine/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "routine_type": "morning", "budget": 50}'

# Test d'analyse d'ingrédient
curl -X POST http://127.0.0.1:8000/api/v1/ai/analyze-product/ \
  -H "Content-Type: application/json" \
  -d '{"ingredient_name": "vitamine C", "user_id": 1}'
```

### Tests de Performance
```bash
# Test de charge simple
ab -n 100 -c 10 http://127.0.0.1:8000/api/v1/health/

# Test de l'API IA
ab -n 50 -c 5 -p test_data.json -T application/json \
  http://127.0.0.1:8000/api/v1/enhanced-ai/comprehensive-routine/
```

## 🚀 Déploiement

### Environnement de Développement
```bash
# Configuration développement
export DJANGO_SETTINGS_MODULE=config.settings.dev
export DEBUG=True
export DJANGO_DEVELOPMENT=True

# Démarrage
python manage.py runserver 8000
```

### Environnement de Production
```bash
# Configuration production
export DJANGO_SETTINGS_MODULE=config.settings.prod
export DEBUG=False
export DJANGO_DEVELOPMENT=False

# Collecte des fichiers statiques
python manage.py collectstatic --noinput

# Démarrage avec Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker (Optionnel)
```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```bash
# Construction et exécution
docker build -t beautyscan .
docker run -p 8000:8000 beautyscan
```

## 🔧 Développement

### Prérequis de Développement
```bash
# Outils de développement
pip install -r requirements-dev.txt

# Pré-commit hooks
pre-commit install

# Linting et formatage
pip install black isort flake8 mypy
```

### Standards de Code
```bash
# Formatage automatique
black .
isort .

# Vérification de qualité
flake8 .
mypy .

# Tests avant commit
python manage.py test
python manage.py check
```

### Architecture de Développement
- **Modèle MVC** : Django avec séparation claire des responsabilités
- **Services modulaires** : Architecture orientée services
- **API Django (REST v1)** : Endpoints standardisés et documentés
- **Tests automatisés** : Couverture de code et tests d'intégration

## 🤝 Contribuer

### Processus de Contribution
1. **Fork** le projet sur GitHub
2. **Clone** votre fork localement
3. **Créez** une branche feature : `git checkout -b feature/NouvelleFonctionnalite`
4. **Développez** votre fonctionnalité
5. **Testez** votre code : `python manage.py test`
6. **Commitez** vos changements : `git commit -m 'Ajout: description'`
7. **Poussez** vers votre fork : `git push origin feature/NouvelleFonctionnalite`
8. **Ouvrez** une Pull Request

### Standards de Contribution
- **Code** : Suivre les standards PEP 8 et Django
- **Tests** : Maintenir une couverture de code > 80%
- **Documentation** : Mettre à jour la documentation si nécessaire
- **Messages de commit** : Utiliser le format conventionnel

### Types de Contributions
- 🐛 **Correction de bugs** : Résolution de problèmes existants
- ✨ **Nouvelles fonctionnalités** : Ajout de capacités
- 📚 **Documentation** : Amélioration de la documentation
- 🧪 **Tests** : Ajout de tests et amélioration de la couverture
- 🎨 **Interface** : Amélioration de l'expérience utilisateur

## 🐛 Résolution des Problèmes

### Problèmes Courants

#### 1. Erreur de Connexion à la Base de Données
```bash
# Symptôme
django.db.utils.OperationalError: no such table

# Solution
python manage.py migrate
python manage.py makemigrations
```

#### 2. Erreur de Variables d'Environnement
```bash
# Symptôme
KeyError: 'SECRET_KEY'

# Solution
# Vérifier le fichier .env
cat .env
# Régénérer SECRET_KEY si nécessaire
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 3. Erreur Azure OpenAI
```bash
# Symptôme
Azure OpenAI not available, using fallback

# Solution
# Vérifier les variables d'environnement
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT
# Redémarrer le serveur après modification
```

#### 4. Erreur de Port Déjà Utilisé
```bash
# Symptôme
Error: That port is already in use

# Solution
# Trouver le processus
lsof -i :8000
# Tuer le processus
kill -9 <PID>
# Ou utiliser un autre port
python manage.py runserver 8001
```

#### 5. Erreur de Dépendances
```bash
# Symptôme
ModuleNotFoundError: No module named 'openai'

# Solution
# Réactiver l'environnement virtuel
source .venv/bin/activate
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Logs et Debugging
```bash
# Activer les logs détaillés
export DJANGO_LOG_LEVEL=DEBUG

# Vérifier les logs Django
tail -f logs/django.log

# Vérifier la configuration
python manage.py check --deploy

# Test de connectivité
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES)
>>> print(settings.AZURE_OPENAI_KEY)
```

### Outils de Debugging
- **Django Debug Toolbar** : Interface de debugging intégrée
- **Logs structurés** : Système de logging configurable
- **Tests automatisés** : Détection précoce des problèmes
- **Validation de configuration** : Vérification automatique des paramètres

## 📚 Documentation

### Documentation Technique
- **API Reference** : Endpoints et formats de données
- **Architecture** : Diagrammes et explications techniques
- **Configuration** : Guide de configuration détaillé
- **Déploiement** : Instructions de déploiement

### Documentation Utilisateur
- **Guide d'utilisation** : Tutoriels et exemples
- **FAQ** : Questions fréquemment posées
- **Troubleshooting** : Guide de résolution des problèmes
- **Vidéos** : Tutoriels vidéo (optionnel)

### Maintenance de la Documentation
- **Mise à jour automatique** : Synchronisation avec le code
- **Versioning** : Documentation versionnée avec le code
- **Contribution** : Processus de contribution à la documentation
- **Qualité** : Revue et validation de la documentation

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

### Droits et Restrictions
- ✅ **Utilisation commerciale** : Autorisée
- ✅ **Modification** : Autorisée
- ✅ **Distribution** : Autorisée
- ✅ **Utilisation privée** : Autorisée
- ❌ **Responsabilité** : Aucune garantie fournie
- ❌ **Trademark** : Utilisation du nom BeautyScan soumise à autorisation

## 📞 Contact et Support

### Équipe de Développement
- **Lead Developer** : [Votre Nom](mailto:votre-email@example.com)
- **Product Manager** : [Nom PM](mailto:pm@example.com)
- **Designer** : [Nom Designer](mailto:designer@example.com)

### Canaux de Support
- **Issues GitHub** : [Repository Issues](https://github.com/votre-username/cosmetic-scan-application/issues)
- **Discussions** : [GitHub Discussions](https://github.com/votre-username/cosmetic-scan-application/discussions)
- **Email** : support@beautyscan.com
- **Documentation** : [Wiki du projet](https://github.com/votre-username/cosmetic-scan-application/wiki)

### Communauté
- **Discord** : [Serveur Discord](https://discord.gg/beautyscan)
- **Twitter** : [@BeautyScanApp](https://twitter.com/BeautyScanApp)
- **Blog** : [Blog officiel](https://blog.beautyscan.com)

### Politique de Support
- **Support gratuit** : Questions générales et bugs
- **Support Premium** : Assistance technique avancée
- **Temps de réponse** : 24-48h pour les questions générales
- **Urgences** : Support prioritaire pour les utilisateurs Premium

## 🎉 Remerciements

### Contributeurs
- **Développeurs** : Tous les contributeurs open source
- **Designers** : Équipe de design et UX
- **Testeurs** : Utilisateurs beta et testeurs
- **Communauté** : Utilisateurs et supporters

### Technologies et Bibliothèques
- **Django** : Framework web robuste et flexible
- **Azure OpenAI** : Intelligence artificielle de pointe
- **Bootstrap** : Framework CSS pour l'interface
- **Stripe** : Plateforme de paiement sécurisée

### Ressources
- **Documentation Django** : [docs.djangoproject.com](https://docs.djangoproject.com)
- **Azure OpenAI** : [azure.microsoft.com/openai](https://azure.microsoft.com/openai)
- **Stripe** : [stripe.com/docs](https://stripe.com/docs)

---

## 🚀 Démarrage Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/cosmetic-scan-application.git
cd cosmetic-scan-application

# 2. Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés

# 5. Initialiser la base de données
python manage.py migrate

# 6. Démarrer l'application
python start_server.py

# 7. Ouvrir dans le navigateur
# http://127.0.0.1:8000/
```

**🎯 BeautyScan** - Votre assistant beauté intelligent avec GPT-4 ! ✨

---

*Dernière mise à jour : Septembre 2025*  
*Version : 1.0.0*  
*Django : 5.0.2*  
*Python : 3.8+*
