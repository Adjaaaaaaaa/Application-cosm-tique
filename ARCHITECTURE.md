# BeautyScan - Clean Architecture Documentation

## Vue d'ensemble

Ce document décrit la refactorisation de l'application BeautyScan vers une architecture Clean Architecture, en préservant intégralement le comportement existant et l'interface utilisateur.

## Structure de l'architecture

### 1. Couche Domain (`core/`)

**Responsabilité** : Contient la logique métier pure, indépendante de tout framework.

#### Entités (`core/entities/`)
- `user.py` : Entité User avec validation des données
- `profile.py` : Entité UserProfile avec logique métier
- `scan.py` : Entité Scan pour les analyses de produits

#### Objets de valeur (`core/value_objects/`)
- `skin_type.py` : Type de peau avec validation
- `age_range.py` : Tranche d'âge avec validation
- `ingredient.py` : Ingrédient avec validation
- `safety_score.py` : Score de sécurité avec niveaux de risque

#### Exceptions (`core/exceptions.py`)
- Exceptions métier personnalisées pour la gestion d'erreurs

### 2. Couche Use Cases (`usecases/`)

**Responsabilité** : Orchestration de la logique applicative.

#### Use Cases utilisateur (`usecases/user/`)
- `get_user_profile.py` : Récupération du profil utilisateur
- `get_user_allergies.py` : Récupération des allergies
- `format_profile_for_ai.py` : Formatage pour l'IA
- `update_user_profile.py` : Mise à jour du profil

### 3. Couche Interfaces (`interfaces/`)

**Responsabilité** : Définition des contrats (ports) pour l'injection de dépendances.

#### Repositories (`interfaces/repositories/`)
- `user_repository.py` : Interface pour l'accès aux données utilisateur
- `profile_repository.py` : Interface pour l'accès aux profils
- `scan_repository.py` : Interface pour l'accès aux scans

#### Services (`interfaces/services/`)
- `ai_service.py` : Interface pour les services IA
- `product_api_service.py` : Interface pour les APIs produits
- `payment_service.py` : Interface pour les paiements

### 4. Couche Infrastructure (`infrastructure/`)

**Responsabilité** : Implémentation concrète des interfaces avec Django ORM.

#### Repositories Django (`infrastructure/repositories/`)
- `django_user_repository.py` : Implémentation Django du UserRepository
- `django_profile_repository.py` : Implémentation Django du ProfileRepository
- `django_scan_repository.py` : Implémentation Django du ScanRepository

### 5. Couche Adapters (`apps/`)

**Responsabilité** : Adaptation des vues Django pour utiliser Clean Architecture.

#### Apps Django (`apps/`)
- `accounts/` : Gestion des comptes utilisateur
- `scans/` : Analyse des produits cosmétiques
- `payments/` : Gestion des paiements et abonnements
- `ai_routines/` : Routines de soins générées par IA
- `api/` : API interne sécurisée pour les services

#### Adapters de vues (`apps/accounts/adapters/`)
- `profile_view_adapter.py` : Adapter pour la vue de profil

#### Adapters API (`apps/api/adapters/`)
- `internal_api_adapter.py` : Adapter pour l'API interne

## Mapping des fichiers

### Avant la refactorisation
```
apps/
├── accounts/
│   ├── models.py (User, UserProfile)
│   ├── views.py (profile_view)
│   └── forms.py
├── scans/
│   ├── models.py (Scan)
│   └── views.py
└── internal_api.py (API interne non structurée)

backend/
└── services/
    └── user_service.py (logique métier mélangée)
```

### Après la refactorisation
```
core/                           # Domain layer
├── entities/
│   ├── user.py
│   ├── profile.py
│   └── scan.py
├── value_objects/
│   ├── skin_type.py
│   ├── age_range.py
│   ├── ingredient.py
│   └── safety_score.py
└── exceptions.py

usecases/                       # Application layer
└── user/
    ├── get_user_profile.py
    ├── get_user_allergies.py
    ├── format_profile_for_ai.py
    └── update_user_profile.py

interfaces/                     # Interface layer
├── repositories/
│   ├── user_repository.py
│   ├── profile_repository.py
│   └── scan_repository.py
└── services/
    ├── ai_service.py
    ├── product_api_service.py
    └── payment_service.py

infrastructure/                 # Infrastructure layer
└── repositories/
    ├── django_user_repository.py
    ├── django_profile_repository.py
    └── django_scan_repository.py

apps/                          # Adapter layer
├── accounts/
│   ├── adapters/
│   │   └── profile_view_adapter.py
│   ├── models.py (inchangé)
│   └── views.py (devenu thin adapter)
├── api/                       # API interne structurée
│   ├── adapters/
│   │   └── internal_api_adapter.py
│   ├── views.py (endpoints API)
│   ├── urls.py (routes API)
│   └── README.md (documentation)
├── scans/
├── payments/
└── ai_routines/

backend/
└── services/
    └── user_service.py (devenu thin adapter)
```

## Tests

### Tests unitaires
- `tests/unit/test_domain_entities.py` : Tests des entités et objets de valeur
- `tests/unit/test_infrastructure_repositories.py` : Tests des repositories Django

### Tests d'intégration
- `tests/test_baseline_integration.py` : Tests de régression pour vérifier la compatibilité

## Fichiers statiques

### CSS extraits
- `static/css/accounts/profile.css` : Styles du profil utilisateur
- `static/css/accounts/signup.css` : Styles d'inscription

## Commandes de déploiement

### Tests
```bash
# Tests unitaires
python manage.py test tests.unit.test_domain_entities tests.unit.test_infrastructure_repositories

# Tests d'intégration
python manage.py test tests.test_baseline_integration

# Tous les tests
python manage.py test
```

### Migrations
```bash
# Vérifier les migrations
python manage.py showmigrations

# Créer de nouvelles migrations (si nécessaire)
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### Fichiers statiques
```bash
# Collecter les fichiers statiques
python manage.py collectstatic
```

## Règles de Clean Architecture respectées

1. **Indépendance des frameworks** : Le domaine et les use cases n'importent pas Django
2. **Testabilité** : Chaque couche peut être testée indépendamment
3. **Indépendance de l'UI** : L'interface utilisateur peut changer sans affecter la logique métier
4. **Indépendance de la base de données** : La logique métier ne dépend pas de l'ORM
5. **Indépendance des services externes** : Les services externes sont abstraits par des interfaces

## API Interne Sécurisée

### Structure de l'API (`apps/api/`)
L'API interne a été refactorisée en app Django structurée :

```
apps/api/
├── views.py              # Endpoints API sécurisés
├── urls.py               # Routes API
├── adapters/
│   └── internal_api_adapter.py  # Adapter Clean Architecture
└── README.md             # Documentation complète
```

### Endpoints Disponibles
- `GET /internal-api/health/` - Health check
- `GET /internal-api/user-profile/<user_id>/` - Profil utilisateur
- `POST /internal-api/enhanced-ai/comprehensive-routine/` - Routine IA
- `POST /internal-api/ai/analyze-product/` - Analyse produit
- `GET /internal-api/ingredients/info/` - Info ingrédient
- `POST /internal-api/ai/general-question/` - Question générale

### Sécurité
- **Authentification** : Token `X-Internal-Token: internal_beautyscan_2024`
- **Restriction IP** : `127.0.0.1` et `localhost` uniquement
- **Logs** : Tous les accès sont tracés
- **Non-public** : API strictement interne

## Compatibilité

- ✅ **Comportement préservé** : Tous les endpoints et réponses sont identiques
- ✅ **UI préservée** : L'interface utilisateur reste inchangée
- ✅ **Base de données** : Aucun changement de schéma
- ✅ **API** : Toutes les APIs internes et externes fonctionnent identiquement
- ✅ **Sécurité** : Même niveau de sécurité avec structure améliorée

## Avantages obtenus

1. **Séparation des responsabilités** : Chaque couche a un rôle clair
2. **Testabilité améliorée** : Tests unitaires pour chaque couche
3. **Maintenabilité** : Code plus facile à comprendre et modifier
4. **Extensibilité** : Facile d'ajouter de nouvelles fonctionnalités
5. **Indépendance** : Possibilité de changer de framework sans refactoriser le domaine

## Prochaines étapes recommandées

1. **Tests de performance** : Vérifier que les performances ne sont pas dégradées
2. **Documentation API** : Documenter les nouvelles interfaces
3. **Monitoring** : Ajouter des métriques pour surveiller la nouvelle architecture
4. **Formation équipe** : Former l'équipe aux principes Clean Architecture
