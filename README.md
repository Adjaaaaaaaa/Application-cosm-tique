# 🎯 BeautyScan - Assistant Beauté IA
**Projet réalisé dans le cadre de la formation Simplon**

## 📋 Description

**BeautyScan** est une application web intelligente qui révolutionne l'expérience cosmétique en proposant des conseils personnalisés basés sur l'intelligence artificielle. L'application utilise Azure OpenAI GPT-4 pour analyser les ingrédients cosmétiques, générer des routines personnalisées et fournir des recommandations adaptées au profil unique de chaque utilisateur.

### 🏫 Contexte Simplon
Ce projet a été développé dans le cadre de la formation **Développeur Full Stack** de Simplon, démontrant l'application des technologies modernes de développement web, d'intelligence artificielle et de gestion de projets.

Architecture API:
- **API Django (REST v1)**: endpoints principaux sous `http://127.0.0.1:8000/api/v1/...`
- **Service FastAPI (profils)**: récupération des profils sous `http://127.0.0.1:8002/...`

### 🎯 Objectifs du Projet
- **Transparence cosmétique** : Décrypter les listes d'ingrédients complexes
- **Personnalisation avancée** : Routines adaptées au type de peau, allergies et objectifs
- **Intelligence artificielle** : Conseils experts via Azure OpenAI GPT-4
- **Expérience utilisateur** : Interface intuitive et design élégant

### 🛠️ Technologies Utilisées (Formation Simplon)

#### **Backend**
- **Django 5.0.2** : Framework web Python principal
- **Django REST Framework** : API REST pour les endpoints
- **SQLite/PostgreSQL** : Base de données
- **Azure OpenAI GPT-4** : Intelligence artificielle
- **Stripe** : Système de paiement

#### **Frontend**
- **HTML5/CSS3** : Structure et style
- **Bootstrap 5** : Framework CSS responsive
- **JavaScript** : Interactivité côté client
- **AJAX** : Communication asynchrone

#### **Services Externes**
- **OpenBeautyFacts API** : Base de données produits cosmétiques
- **PubChem API** : Informations sur les ingrédients
- **Azure OpenAI** : Génération de contenu IA
- **Stripe API** : Paiements sécurisés

#### **Outils de Développement**
- **Git** : Contrôle de version
- **Python Virtual Environment** : Isolation des dépendances
- **Django Admin** : Interface d'administration
- **Cache système** : Optimisation des performances

#### **Compétences Développées**
- **Architecture MVC** : Séparation des responsabilités
- **API REST** : Conception d'endpoints
- **Intégration IA** : Utilisation d'APIs externes
- **Gestion de projet** : Structure modulaire et documentation

## ⚙️ Prérequis pour Tester l'Application

### 🔧 Logiciels Requis
- **Python** : Version 3.8 ou supérieure ([Télécharger Python](https://www.python.org/downloads/))
- **pip** : Gestionnaire de paquets Python (inclus avec Python)
- **Git** : Contrôle de version ([Télécharger Git](https://git-scm.com/downloads))
- **Navigateur web** : Chrome, Firefox, Safari ou Edge
- **Éditeur de code** : VS Code, PyCharm ou équivalent (recommandé)

### 🔑 Comptes et Services Nécessaires
- **Azure OpenAI** : Compte avec accès GPT-4 (**OBLIGATOIRE** pour les fonctionnalités IA)
- **Stripe** : Compte pour les paiements (optionnel - pour tester les fonctionnalités Premium)
- **Compte GitHub** : Pour cloner le projet

### 💻 Configuration Système
- **RAM** : Minimum 4GB (recommandé 8GB+)
- **Espace disque** : 2GB minimum
- **Réseau** : Connexion internet stable
- **OS** : Windows 10+, macOS 10.15+, ou Linux Ubuntu 18.04+

## 🚀 Installation et Configuration Complète

### 1. Cloner le Projet
```bash
# Cloner le repository
git clone https://github.com/votre-username/cosmetic-scan-application.git
cd cosmetic-scan-application

# Vérifier que vous êtes dans le bon dossier
ls -la  # Linux/Mac
# ou
dir     # Windows
```

### 2. Créer l'Environnement Virtuel
```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Linux/Mac :
source .venv/bin/activate

# Windows (PowerShell) :
.venv\Scripts\Activate.ps1

# Windows (CMD) :
.venv\Scripts\activate.bat

# Vérifier que l'environnement est activé (vous devriez voir (.venv) dans votre prompt)
```

### 3. Installer les Dépendances
```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

### 4. Configuration des Variables d'Environnement

#### Créer le fichier .env
```bash
# Copier le template (s'il existe)
cp .env.example .env

# Ou créer un nouveau fichier .env
touch .env  # Linux/Mac
# ou
type nul > .env  # Windows
```

#### Éditer le fichier .env
```bash
# Linux/Mac
nano .env
# ou
code .env

# Windows
notepad .env
# ou
code .env
```

#### Contenu minimum du fichier .env
```env
# Configuration Django de base
SECRET_KEY=django-insecure-votre-clé-secrète-très-longue-et-complexe
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True
DJANGO_DEVELOPMENT=True

# Base de données (SQLite par défaut pour le développement)
DATABASE_URL=sqlite:///db.sqlite3

# Configuration Azure OpenAI (OBLIGATOIRE pour les fonctionnalités IA)
AZURE_OPENAI_API_KEY=votre-clé-api-azure-openai
AZURE_OPENAI_ENDPOINT=https://votre-ressource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
OPENAI_MODEL=gpt-4.1

# Configuration Stripe (optionnel - pour tester les paiements)
STRIPE_PUBLISHABLE_KEY=pk_test_votre-clé-publique-stripe
STRIPE_SECRET_KEY=sk_test_votre-clé-secrète-stripe
STRIPE_WEBHOOK_SECRET=whsec_votre-secret-webhook-stripe

# Configuration email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Logs
DJANGO_LOG_LEVEL=INFO
```

#### Comment obtenir les clés Azure OpenAI
1. Aller sur [Azure Portal](https://portal.azure.com)
2. Créer une ressource "Azure OpenAI"
3. Déployer un modèle GPT-4
4. Récupérer la clé API et l'endpoint dans les paramètres

### 5. Initialiser la Base de Données
```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur pour l'administration
python manage.py createsuperuser
# Suivre les instructions pour créer un compte admin

# Vérifier que tout fonctionne
python manage.py check
```

### 6. Test de l'Installation
```bash
# Démarrer le serveur de développement
python manage.py runserver 8000

# Ou utiliser le script de démarrage automatique
python start_server.py
```

### 7. Vérification dans le Navigateur
1. Ouvrir http://127.0.0.1:8000/
2. Vous devriez voir la page d'accueil de BeautyScan
3. Tester l'inscription/connexion
4. Accéder à l'admin : http://127.0.0.1:8000/admin/

## 🎮 Guide d'Utilisation et Tests

### 🚀 Démarrage de l'Application
```bash
# Méthode recommandée (avec vérifications automatiques)
python start_server.py

# Méthode manuelle
python manage.py runserver 8000

# Avec un port spécifique
python manage.py runserver 8080
```

### 🌐 Accès aux Fonctionnalités

#### 1. **Interface Web Principale**
- **URL** : http://127.0.0.1:8000/
- **Fonctionnalités** : Accueil, navigation, présentation

#### 2. **Authentification**
- **Inscription** : http://127.0.0.1:8000/accounts/signup/
- **Connexion** : http://127.0.0.1:8000/accounts/login/
- **Profil** : http://127.0.0.1:8000/accounts/profile/

#### 3. **Assistant Beauté IA** ⭐
- **Assistant principal** : http://127.0.0.1:8000/ai-routines/beauty-assistant/
- **Routines personnalisées** : http://127.0.0.1:8000/ai-routines/ai-routines/
- **Analyse de produits** : http://127.0.0.1:8000/ai-routines/product-analysis/

#### 4. **Scan de Produits**
- **Scanner un produit** : http://127.0.0.1:8000/scans/create/
- **Historique des scans** : http://127.0.0.1:8000/scans/
- **Dashboard** : http://127.0.0.1:8000/scans/dashboard/

#### 5. **Paiements Premium** (optionnel)
- **Upgrade Premium** : http://127.0.0.1:8000/payments/upgrade/
- **Gestion abonnement** : http://127.0.0.1:8000/payments/manage/

#### 6. **Administration Django**
- **Admin panel** : http://127.0.0.1:8000/admin/
- **Connexion** : Utiliser le superutilisateur créé à l'installation

### 🧪 Tests Complets de l'Application

#### **Test 1 : Vérification de Base**
```bash
# 1. Tester la connexion à la base de données
python manage.py check

# 2. Vérifier les migrations
python manage.py showmigrations

# 3. Tester l'API de santé
curl http://127.0.0.1:8000/api/v1/health/
# Réponse attendue : {"status": "ok", "timestamp": "..."}
```

#### **Test 2 : Authentification et Profils**
```bash
# 1. Créer un compte utilisateur via l'interface web
# Aller sur : http://127.0.0.1:8000/accounts/signup/

# 2. Remplir le profil utilisateur
# - Type de peau : Normal, sèche, grasse, mixte
# - Âge : 18-25, 26-35, 36-45, 46-60, 60+
# - Allergies : Cocher les allergènes pertinents
# - Objectifs : Anti-âge, hydratation, éclat, acné

# 3. Vérifier la sauvegarde
# Aller sur : http://127.0.0.1:8000/accounts/profile/
```

#### **Test 3 : Assistant Beauté IA** ⭐
```bash
# 1. Test de l'assistant principal
# Aller sur : http://127.0.0.1:8000/ai-routines/beauty-assistant/

# 2. Tester une question générale
# Question : "Quels sont les bienfaits de la vitamine C ?"
# Type : "général"
# Budget : 50€

# 3. Tester une routine personnalisée
# Type : "routine_matin"
# Budget : 80€
# Question : "Routine anti-âge pour peau sensible"

# 4. Vérifier les réponses IA (doivent être cohérentes et détaillées)
```

#### **Test 4 : Scan et Analyse de Produits**
```bash
# 1. Tester le scan d'un produit
# Aller sur : http://127.0.0.1:8000/scans/create/

# 2. Utiliser des codes-barres de test :
# - 3600542525770 (Shampooing Garnier)
# - 1234567890123 (Produit généré par IA)
# - 9876543210987 (Autre produit test)

# 3. Vérifier l'analyse complète :
# - Informations produit
# - Liste des ingrédients
# - Score de sécurité
# - Recommandations personnalisées

# 4. Tester le cache (second scan du même produit)
# Le score doit être identique et plus rapide
```

#### **Test 5 : API REST**
```bash
# 1. Test de l'API de santé
curl http://127.0.0.1:8000/api/v1/health/

# 2. Test de génération de routine via API
curl -X POST http://127.0.0.1:8000/api/v1/enhanced-ai/comprehensive-routine/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "routine_type": "morning",
    "user_question": "Routine hydratante pour peau sèche",
    "budget": 100
  }'

# 3. Test d'analyse d'ingrédient via API
curl -X POST http://127.0.0.1:8000/api/v1/ai/analyze-product/ \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_name": "rétinol",
    "user_id": 1
  }'
```

#### **Test 6 : Fonctionnalités Premium** (optionnel)
```bash
# 1. Tester l'upgrade Premium
# Aller sur : http://127.0.0.1:8000/payments/upgrade/

# 2. Utiliser les cartes de test Stripe :
# - Succès : 4242 4242 4242 4242
# - Échec : 4000 0000 0000 0002

# 3. Vérifier l'activation Premium
# Les fonctionnalités avancées doivent être débloquées
```

#### **Test 7 : Cache et Performance**
```bash
# 1. Vérifier les statistiques du cache
python manage.py manage_cache --stats

# 2. Tester la cohérence du cache
# Scanner le même produit plusieurs fois
# Le score doit être identique à chaque fois

# 3. Tester les performances
# Premier scan : ~15-60 secondes
# Scans suivants : <0.1 seconde (cache)
```

### 🔍 Vérifications de Qualité

#### **Logs et Debugging**
```bash
# 1. Activer les logs détaillés
export DJANGO_LOG_LEVEL=DEBUG  # Linux/Mac
set DJANGO_LOG_LEVEL=DEBUG     # Windows

# 2. Surveiller les logs en temps réel
tail -f logs/django.log  # Si configuré
# ou surveiller le terminal du serveur Django

# 3. Vérifier les appels Azure OpenAI
# Les logs doivent montrer les requêtes/réponses IA
```

#### **Tests de Validation**
```bash
# 1. Tests unitaires
python manage.py test

# 2. Tests d'intégration
python manage.py test apps.ai_routines
python manage.py test apps.scans

# 3. Validation de la configuration
python manage.py check --deploy
```

### 📋 Checklist de Test pour Simplon

#### **✅ Tests Obligatoires**
- [ ] **Installation complète** : Application démarre sans erreur
- [ ] **Authentification** : Inscription/connexion fonctionne
- [ ] **Profil utilisateur** : Création et modification du profil
- [ ] **Assistant IA** : Génération de routines personnalisées
- [ ] **Scan de produits** : Analyse de codes-barres avec scores cohérents
- [ ] **Cache** : Performance et cohérence des résultats
- [ ] **API REST** : Endpoints répondent correctement
- [ ] **Interface responsive** : Adaptation mobile/desktop

#### **✅ Tests Avancés**
- [ ] **Fonctionnalités Premium** : Paiements Stripe (optionnel)
- [ ] **Gestion des erreurs** : Messages d'erreur clairs
- [ ] **Performance** : Temps de réponse acceptables
- [ ] **Sécurité** : Validation des données et authentification

#### **🎯 Critères de Validation Simplon**
1. **Fonctionnalité** : Toutes les features principales marchent
2. **Code qualité** : Architecture propre et commentée
3. **Tests** : Couverture de test et validation manuelle
4. **Documentation** : README complet et code documenté
5. **Déploiement** : Application déployable et utilisable

### 🌐 URLs de Test Rapide
- **Interface principale** : http://127.0.0.1:8000/
- **Assistant IA** : http://127.0.0.1:8000/ai-routines/beauty-assistant/
- **Profil utilisateur** : http://127.0.0.1:8000/accounts/profile/
- **Scan produits** : http://127.0.0.1:8000/scans/create/
- **Paiements Premium** : http://127.0.0.1:8000/payments/upgrade/
- **Admin Django** : http://127.0.0.1:8000/admin/

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

## 🐛 Résolution des Problèmes Courants

### ⚠️ Problèmes d'Installation

#### 1. **Erreur Python/Version**
```bash
# Symptôme
python: command not found
# ou
Python version not supported

# Solution
# Installer Python 3.8+ depuis python.org
# Vérifier la version
python --version
# ou
python3 --version
```

#### 2. **Erreur de Variables d'Environnement**
```bash
# Symptôme
KeyError: 'SECRET_KEY'
# ou
Environment variable not found

# Solution
# Vérifier le fichier .env existe
ls -la .env  # Linux/Mac
dir .env     # Windows

# Créer le fichier .env
cp .env.example .env
# ou créer manuellement

# Régénérer SECRET_KEY si nécessaire
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 3. **Erreur de Connexion à la Base de Données**
```bash
# Symptôme
django.db.utils.OperationalError: no such table

# Solution
python manage.py migrate
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### 🔧 Problèmes de Fonctionnement

#### 4. **Erreur Azure OpenAI**
```bash
# Symptôme
Azure OpenAI not available, using fallback
# ou
401 Unauthorized

# Solution
# Vérifier les variables d'environnement
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# Vérifier le fichier .env
grep AZURE_OPENAI .env

# Redémarrer le serveur après modification
python manage.py runserver 8000
```

#### 5. **Erreur de Port Déjà Utilisé**
```bash
# Symptôme
Error: That port is already in use
# ou
Address already in use

# Solution Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Solution Linux/Mac
lsof -i :8000
kill -9 <PID>

# Ou utiliser un autre port
python manage.py runserver 8001
```

#### 6. **Erreur de Dépendances**
```bash
# Symptôme
ModuleNotFoundError: No module named 'django'
# ou
pip: command not found

# Solution
# Réactiver l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Réinstaller les dépendances
pip install -r requirements.txt
pip install --upgrade pip
```

### 🚨 Problèmes Spécifiques à l'Application

#### 7. **Cache ne fonctionne pas**
```bash
# Symptôme
Scores différents à chaque scan
# ou
Cache statistics shows 0 entries

# Solution
# Vérifier les migrations
python manage.py showmigrations scans

# Appliquer les migrations si nécessaire
python manage.py migrate scans

# Vérifier les statistiques du cache
python manage.py manage_cache --stats
```

#### 8. **Assistant IA ne répond pas**
```bash
# Symptôme
No response from AI assistant
# ou
Azure OpenAI timeout

# Solution
# Vérifier la connexion internet
ping azure.microsoft.com

# Vérifier les clés Azure OpenAI
curl -H "api-key: $AZURE_OPENAI_API_KEY" $AZURE_OPENAI_ENDPOINT/openai/models?api-version=2024-02-15-preview

# Tester avec une question simple
curl -X POST http://127.0.0.1:8000/ai-routines/assistant-api/ \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "routine_type": "general", "budget": 50}'
```

#### 9. **Interface ne se charge pas**
```bash
# Symptôme
Page blanche ou erreur 500
# ou
Static files not found

# Solution
# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Vérifier les permissions
chmod -R 755 static/

# Vérifier les logs
python manage.py runserver --verbosity=2
```

### 📞 Support et Aide

#### **Commandes de Diagnostic**
```bash
# Vérification complète du système
python manage.py check --deploy

# Test de tous les composants
python manage.py test

# Vérification de la configuration
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES)
>>> print(settings.AZURE_OPENAI_KEY)
```

#### **Logs et Debugging**
```bash
# Activer les logs détaillés
export DJANGO_LOG_LEVEL=DEBUG  # Linux/Mac
set DJANGO_LOG_LEVEL=DEBUG     # Windows

# Surveiller les logs en temps réel
tail -f logs/django.log  # Si configuré
# ou surveiller le terminal du serveur Django
```

#### **Reset Complet** (en dernier recours)
```bash
# Sauvegarder vos données importantes
cp .env .env.backup

# Supprimer et recréer l'environnement virtuel
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Réinstaller tout
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
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

## 🚀 Démarrage Rapide (Simplon)

### ⚡ Installation Express (5 minutes)

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

# 4. Configurer l'environnement (OBLIGATOIRE)
# Créer le fichier .env avec vos clés Azure OpenAI
echo "SECRET_KEY=django-insecure-$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True
AZURE_OPENAI_API_KEY=votre-clé-azure-openai
AZURE_OPENAI_ENDPOINT=https://votre-ressource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
OPENAI_MODEL=gpt-4.1" > .env

# 5. Initialiser la base de données
python manage.py migrate

# 6. Créer un superutilisateur
python manage.py createsuperuser

# 7. Démarrer l'application
python start_server.py

# 8. Ouvrir dans le navigateur
# http://127.0.0.1:8000/
```

### 🎯 Test Rapide (2 minutes)

1. **Accueil** : http://127.0.0.1:8000/
2. **Inscription** : Créer un compte
3. **Assistant IA** : http://127.0.0.1:8000/ai-routines/beauty-assistant/
4. **Question test** : "Quels sont les bienfaits de la vitamine C ?"
5. **Scan produit** : http://127.0.0.1:8000/scans/create/
6. **Code-barres test** : `3600542525770`

### ✅ Validation Simplon

- [ ] Application démarre sans erreur
- [ ] Interface web accessible
- [ ] Assistant IA répond aux questions
- [ ] Scan de produit fonctionne
- [ ] Cache et performances OK

---

## 📞 Support Simplon

### 🎓 Pour les Formateurs
- **Documentation technique** : Architecture et API détaillées
- **Tests automatisés** : `python manage.py test`
- **Validation qualité** : `python manage.py check --deploy`

### 👨‍🎓 Pour les Apprenants
- **Guide pas à pas** : Instructions détaillées ci-dessus
- **Tests manuels** : Checklist de validation
- **Dépannage** : Section résolution des problèmes

---

**🎯 BeautyScan** - Assistant beauté IA développé dans le cadre de la formation Simplon ! ✨

*Dernière mise à jour : Septembre 2025*  
*Version : 1.0.0*  
*Django : 5.0.2*  
*Python : 3.8+*  
*Formation : Simplon*
