# 📋 Documentation Technique - BeautyScan

## 1. Introduction

### 1.1 Présentation de BeautyScan

**BeautyScan** est une application web intelligente développée en Django qui révolutionne l'expérience cosmétique en proposant des conseils personnalisés basés sur l'intelligence artificielle. L'application utilise Azure OpenAI GPT-4 pour analyser les ingrédients cosmétiques, générer des routines personnalisées et fournir des recommandations adaptées au profil unique de chaque utilisateur.

### 1.2 Objectifs du Projet

- **Transparence cosmétique** : Décrypter les listes d'ingrédients complexes
- **Personnalisation avancée** : Routines adaptées au type de peau, allergies et objectifs
- **Intelligence artificielle** : Conseils experts via Azure OpenAI GPT-4
- **Expérience utilisateur** : Interface intuitive et design élégant
- **Performance** : Système de cache intelligent pour optimiser les temps de réponse

### 1.3 Justification de la Clean Architecture

La Clean Architecture a été adoptée pour BeautyScan afin de :

- **Séparer les responsabilités** : Chaque couche a un rôle bien défini
- **Faciliter les tests** : Isolation des composants métier
- **Améliorer la maintenabilité** : Code modulaire et découplé
- **Permettre l'évolutivité** : Ajout facile de nouvelles fonctionnalités
- **Réduire les dépendances** : Inversion de dépendance avec les interfaces

## 2. Structure du Projet

### 2.1 Architecture Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        PRESENTATION                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web UI    │  │   Mobile    │  │   API REST  │        │
│  │  (Django)   │  │     App     │  │   Endpoints │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE ADAPTATION                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Views     │  │ Controllers │  │   Adapters  │        │
│  │  (Django)   │  │   (API)     │  │  (External) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE APPLICATION                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Use Cases   │  │   Services  │  │   Workflows │        │
│  │  (Business) │  │   (Domain)  │  │  (Process)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                       COUCHE DOMAINE                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Entities   │  │ Value Objs  │  │  Interfaces │        │
│  │  (Models)   │  │  (Types)    │  │ (Contracts) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE INFRASTRUCTURE                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Database   │  │ External    │  │    Cache    │        │
│  │   (ORM)     │  │    APIs     │  │  (Redis)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Arborescence du Projet

```
Application-cosm-tique/
├── 📁 apps/                          # Applications Django (Couche Adaptation)
│   ├── 📁 accounts/                  # Gestion des comptes utilisateurs
│   │   ├── 📁 migrations/            # Migrations de base de données
│   │   ├── 📁 templates/             # Templates HTML des comptes
│   │   ├── models.py                 # Modèles User et UserProfile
│   │   ├── views.py                  # Vues d'authentification et profil
│   │   ├── forms.py                  # Formulaires de gestion des comptes
│   │   └── urls.py                   # Routes des comptes
│   ├── 📁 ai_routines/               # Assistant beauté IA
│   │   ├── 📁 services/              # Services métier IA
│   │   ├── 📁 templates/             # Templates de l'assistant
│   │   ├── views.py                  # Vues de l'assistant IA
│   │   └── urls.py                   # Routes de l'assistant
│   ├── 📁 scans/                     # Scan et analyse de produits
│   │   ├── 📁 management/            # Commandes de gestion
│   │   ├── 📁 migrations/            # Migrations spécifiques aux scans
│   │   ├── 📁 templates/             # Templates de scan
│   │   ├── 📁 templatetags/          # Tags et filtres personnalisés
│   │   ├── models.py                 # Modèles Scan et ProductCache
│   │   ├── services.py               # Services d'analyse de produits
│   │   ├── views.py                  # Vues de scan et analyse
│   │   └── urls.py                   # Routes de scan
│   ├── 📁 payments/                  # Gestion des paiements Premium
│   │   ├── 📁 templates/             # Templates de paiement
│   │   ├── views.py                  # Vues de paiement et webhooks
│   │   ├── setup_ngrok_stripe.py     # Configuration Stripe pour dev
│   │   └── urls.py                   # Routes de paiement
│   └── 📁 api/                       # API REST endpoints
│       ├── views.py                  # Vues API REST
│       └── urls.py                   # Routes API
├── 📁 backend/                       # Services backend (Couche Application)
│   ├── 📁 services/                  # Services métier principaux
│   │   ├── ai_service.py             # Service principal IA
│   │   ├── enhanced_routine_service.py # Service de génération de routines
│   │   ├── user_service.py           # Service de gestion utilisateur
│   │   ├── ingredient_service.py     # Service d'analyse d'ingrédients
│   │   ├── rag_service.py            # Service RAG pour la recherche
│   │   ├── product_cache_service.py  # Service de cache intelligent
│   │   ├── openbeauty_service.py     # Service OpenBeautyFacts
│   │   ├── pubchem_service.py        # Service PubChem
│   │   ├── real_product_service.py   # Service de recherche de produits
│   │   └── base_service.py           # Classe de base pour tous les services
│   └── 📁 core/                      # Configuration core (Couche Domaine)
│       ├── config.py                 # Configuration des services
│       ├── exceptions.py             # Gestion des exceptions
│       └── logging.py                # Configuration des logs
├── 📁 core/                          # Couche Domaine
│   ├── 📁 entities/                  # Entités métier
│   │   ├── user.py                   # Entité utilisateur
│   │   ├── profile.py                # Entité profil utilisateur
│   │   └── scan.py                   # Entité scan de produit
│   └── 📁 value_objects/             # Objets de valeur
│       ├── skin_type.py              # Type de peau
│       ├── age_range.py              # Tranche d'âge
│       ├── ingredient.py             # Ingrédient
│       └── safety_score.py           # Score de sécurité
├── 📁 usecases/                      # Couche Application (Use Cases)
│   └── 📁 user/                      # Cas d'usage utilisateur
│       ├── get_user_profile.py       # Récupération du profil
│       ├── update_user_profile.py    # Mise à jour du profil
│       ├── get_user_allergies.py     # Récupération des allergies
│       └── format_profile_for_ai.py  # Formatage pour l'IA
├── 📁 interfaces/                    # Interfaces (Couche Domaine)
│   └── 📁 repositories/              # Contrats de repositories
│       ├── user_repository.py        # Interface repository utilisateur
│       ├── profile_repository.py     # Interface repository profil
│       └── scan_repository.py        # Interface repository scan
├── 📁 infrastructure/                # Couche Infrastructure
│   └── 📁 repositories/              # Implémentations des repositories
│       ├── django_user_repository.py # Repository utilisateur Django
│       ├── django_profile_repository.py # Repository profil Django
│       └── django_scan_repository.py # Repository scan Django
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
│   ├── utils.py                      # Utilitaires généraux
│   └── context_processors.py         # Processeurs de contexte
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
├── 📁 tests/                         # Tests automatisés
│   ├── 📁 unit/                      # Tests unitaires
│   ├── 📁 integration/               # Tests d'intégration
│   └── conftest.py                   # Configuration pytest
├── 📄 requirements.txt               # Dépendances Python
├── 📄 start_server.py                # Script de démarrage automatique
├── 📄 manage.py                      # Gestionnaire Django
├── 📄 .env.example                   # Template des variables d'environnement
└── 📄 README.md                      # Documentation du projet
```

### 2.3 Description des Couches

#### 2.3.1 Couche Domaine (core/)
- **Entités** : Objets métier centraux (User, Profile, Scan)
- **Value Objects** : Types primitifs du domaine (SkinType, AgeRange, SafetyScore)
- **Interfaces** : Contrats pour les repositories et services

#### 2.3.2 Couche Application (usecases/, backend/services/)
- **Use Cases** : Logique métier spécifique (get_user_profile, update_profile)
- **Services** : Orchestration des cas d'usage complexes
- **Workflows** : Processus métier multi-étapes

#### 2.3.3 Couche Infrastructure (infrastructure/, config/)
- **Repositories** : Implémentations concrètes des interfaces
- **Configuration** : Paramètres Django et services externes
- **Base de données** : Migrations et modèles ORM

#### 2.3.4 Couche Adaptation (apps/)
- **Views** : Contrôleurs Django pour l'interface web
- **Templates** : Vues HTML avec intégration JavaScript
- **API** : Endpoints REST pour les clients externes

## 3. Workflows Fonctionnels

### 3.1 Workflow de Scan de Produit

Le workflow de scan de produit suit une approche en cascade pour optimiser les performances :

#### 3.1.1 Description du Workflow

1. **Vérification du Cache** : Recherche dans le cache intelligent
2. **Base de Données Locale** : Vérification des scans précédents
3. **Base de Données Produits** : Recherche dans la DB interne
4. **APIs Externes** : OpenBeautyFacts, UPCItemDB, BarcodeLookup
5. **Analyse des Ingrédients** : PubChem pour les propriétés chimiques
6. **Calcul du Score** : Évaluation de sécurité et compatibilité
7. **Mise en Cache** : Stockage pour les futurs scans
8. **Retour** : Données formatées pour l'interface

#### 3.1.2 Workflow de Scan de Produit

#### Tableau des Étapes de Scan

| Étape | Composant | Action | Durée | Justification |
|-------|-----------|--------|-------|---------------|
| **0. Cache** | ProductCacheService | Vérification cache | 0.01s | Performance optimale |
| **1. Base Locale** | Django Models | Recherche scan existant | 0.1s | Éviter appels API |
| **2. OpenBeautyFacts** | API Externe | Récupération métadonnées | 2-5s | Source fiable produits |
| **3. PubChem** | API Externe | Analyse ingrédients | 10-30s | Base scientifique |
| **4. Calcul Score** | Algorithm | Score final | 0.5s | Logique métier |
| **5. Sauvegarde** | Database | Persistance données | 0.2s | Traçabilité |

#### Workflow Détaillé

```
1. UTILISATEUR SAISIT CODE-BARRES
   ├── Interface web (formulaire)
   ├── Validation format
   └── Envoi requête POST

2. VÉRIFICATION CACHE (ProductCacheService)
   ├── Génération clé cache: "complete_analysis_{barcode}_{user_id}"
   ├── Recherche dans cache
   ├── Vérification TTL (6h)
   └── Si valide : retour immédiat (0.01s)
   └── Si expiré : suppression + suite

3. RECHERCHE BASE LOCALE (Django Models)
   ├── Query: Scan.objects.filter(barcode=barcode, user_id=user_id)
   ├── Vérification timestamp (< 24h)
   ├── Si frais : mise en cache + retour (0.1s)
   └── Si obsolète : suite

4. APPEL OPENBEAUTYFACTS
   ├── URL: https://world.openbeautyfacts.org/api/v0/product/{barcode}.json
   ├── Extraction métadonnées (nom, marque, ingrédients)
   ├── Validation données
   └── Gestion erreurs (produit non trouvé)

5. ANALYSE INGRÉDIENTS (PubChem)
   ├── Pour chaque ingrédient de la liste
   ├── URL: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{ingredient}/property/MolecularWeight,CanonicalSMILES/json
   ├── Extraction propriétés chimiques
   ├── Identification H-codes (risques)
   └── Calcul poids sécurité

6. CALCUL SCORE FINAL
   ├── Poids H-codes × fréquence
   ├── Score base 100 - pénalités
   ├── Application profil utilisateur
   ├── Détermination niveau risque
   └── Génération recommandations

7. SAUVEGARDE ET CACHE
   ├── Création objet Scan
   ├── Mise en cache résultat
   ├── Définition TTL (6h)
   ├── Incrémentation compteur accès
   └── Logs audit

8. RETOUR UTILISATEUR
   ├── Rendu template avec données
   ├── Affichage score et recommandations
   ├── Options actions (partage, favoris)
   └── Statistiques usage
```

#### Justifications du Workflow

| Étape | Justification | Bénéfice |
|-------|---------------|----------|
| **Cache en Premier** | Éviter recalculs coûteux | Performance maximale |
| **Base Locale** | Réutiliser analyses récentes | Économie API calls |
| **OpenBeautyFacts** | Source officielle fiable | Données précises |
| **PubChem** | Base scientifique reconnue | Analyse rigoureuse |
| **Score Calculé** | Logique métier centralisée | Cohérence résultats |
| **Sauvegarde** | Traçabilité et historique | Audit et analytics |

### 3.2 Workflow de Paiement

Le système de paiement utilise Stripe pour les transactions sécurisées :

#### 3.2.1 Description du Workflow

1. **Initiation** : Utilisateur clique sur "Upgrade Premium"
2. **Validation** : Vérification du statut utilisateur
3. **Session Stripe** : Création d'une session de paiement
4. **Redirection** : Vers la page Stripe sécurisée
5. **Paiement** : Traitement côté Stripe
6. **Webhook** : Notification de succès/échec
7. **Activation** : Mise à jour du profil utilisateur
8. **Confirmation** : Redirection vers la page de succès

#### 3.2.2 Workflow de Paiement

#### Tableau des Étapes de Paiement

| Étape | Composant | Action | Durée | Justification |
|-------|-----------|--------|-------|---------------|
| **1. Initiation** | Django View | Clic "Upgrade Premium" | 0.1s | Point d'entrée utilisateur |
| **2. Validation** | User Service | Vérification statut | 0.05s | Éviter double paiement |
| **3. Session Stripe** | Stripe Service | Création session | 1-2s | Sécurité Stripe |
| **4. Redirection** | Frontend | Redirection Stripe | 0.5s | Interface sécurisée |
| **5. Paiement** | Stripe Platform | Traitement transaction | 5-15s | Processeur externe |
| **6. Webhook** | Webhook View | Notification succès | 0.2s | Confirmation asynchrone |
| **7. Activation** | Database | Mise à jour profil | 0.1s | Persistance statut |
| **8. Confirmation** | Django View | Page de succès | 0.1s | Feedback utilisateur |

#### Workflow Détaillé

```
1. UTILISATEUR INITIE PAIEMENT
   ├── Clic bouton "Upgrade Premium"
   ├── Validation côté client
   └── Envoi requête POST

2. VÉRIFICATION STATUT UTILISATEUR
   ├── Query: User.objects.get(id=user_id)
   ├── Vérification is_premium
   ├── Si Premium : redirection profil
   └── Si Free : suite du processus

3. CRÉATION SESSION STRIPE
   ├── Appel StripeService.create_premium_checkout_session()
   ├── Configuration prix (19.99€)
   ├── Métadonnées utilisateur
   ├── URLs de retour (succès/échec)
   └── Génération session ID

4. REDIRECTION VERS STRIPE
   ├── URL: https://checkout.stripe.com/pay/{session_id}
   ├── Interface Stripe sécurisée
   ├── Saisie informations paiement
   └── Validation côté Stripe

5. TRAITEMENT PAIEMENT
   ├── Validation carte bancaire
   ├── Vérification solvabilité
   ├── Débit du compte
   └── Génération reçu

6. WEBHOOK DE CONFIRMATION
   ├── Stripe → WebhookView
   ├── Événement: checkout.session.completed
   ├── Validation signature webhook
   ├── Extraction session ID
   └── Vérification montant

7. ACTIVATION PREMIUM
   ├── Query: User.objects.get(stripe_customer_id=customer_id)
   ├── Mise à jour: is_premium = True
   ├── Enregistrement date activation
   ├── Sauvegarde transaction ID
   └── Envoi email confirmation

8. CONFIRMATION UTILISATEUR
   ├── Redirection vers page succès
   ├── Affichage message confirmation
   ├── Accès immédiat fonctionnalités Premium
   └── Logs audit transaction
```

#### Justifications du Workflow

| Aspect | Justification | Bénéfice |
|--------|---------------|----------|
| **Stripe Platform** | Sécurité PCI DSS certifiée | Conformité réglementaire |
| **Webhooks Asynchrones** | Confirmation fiable | Robustesse transaction |
| **Validation Statut** | Éviter double paiement | Protection utilisateur |
| **Métadonnées** | Traçabilité complète | Audit et support |
| **URLs de Retour** | UX fluide | Expérience utilisateur optimale |
| **Gestion Erreurs** | Fallback sur échec | Fiabilité système |

### 3.3 Workflow d'Intégration IA

L'intégration Azure OpenAI suit un processus structuré pour l'analyse et les recommandations :

#### 3.3.1 Description du Workflow

1. **Récupération Profil** : Données utilisateur et préférences
2. **Construction Contexte** : Assemblage des informations pertinentes
3. **Génération Prompt** : Création du prompt optimisé pour GPT-4
4. **Appel Azure** : Communication avec l'API OpenAI
5. **Parsing Réponse** : Extraction et validation des données
6. **Mise en Cache** : Stockage des résultats
7. **Retour Formaté** : Données structurées pour l'interface

#### 3.3.2 Workflow d'Intégration IA

#### Tableau des Étapes d'Intégration IA

| Étape | Composant | Action | Durée | Justification |
|-------|-----------|--------|-------|---------------|
| **1. Input** | Django View | Réception question IA | 0.1s | Point d'entrée utilisateur |
| **2. Profil** | User Service | Récupération profil | 0.05s | Personnalisation |
| **3. Contexte** | Ingredient Service | Analyse sécurité | 0.2s | Enrichissement données |
| **4. Cache** | Cache Service | Vérification cache | 0.01s | Performance optimale |
| **5. Prompt** | AI Service | Construction prompt | 0.1s | Optimisation IA |
| **6. Azure** | Azure OpenAI | Appel GPT-4 | 2-5s | Intelligence artificielle |
| **7. Parsing** | AI Service | Validation réponse | 0.1s | Sécurité données |
| **8. Cache** | Cache Service | Stockage résultat | 0.05s | Réutilisation future |

#### Workflow Détaillé

```
1. UTILISATEUR FAIT UNE DEMANDE IA
   ├── Question sur routine beauté
   ├── Analyse d'ingrédients
   ├── Conseil personnalisé
   └── Validation côté client

2. RÉCUPÉRATION PROFIL UTILISATEUR
   ├── UserService.get_user_profile(user_id)
   ├── Extraction: âge, type de peau, allergies
   ├── Historique: produits scannés, préférences
   └── Métadonnées: statut Premium, objectifs

3. CONSTRUCTION CONTEXTE
   ├── IngredientService.analyze_ingredients_safety()
   ├── RAGService.get_context_for_ai()
   ├── Enrichissement avec base de données
   ├── Contexte scientifique (PubChem)
   └── Recommandations générales

4. VÉRIFICATION CACHE IA
   ├── Génération clé: "ai_analysis_{question_hash}_{user_id}"
   ├── Recherche dans cache (TTL: 12h)
   ├── Si trouvé : retour immédiat (0.1s)
   └── Si non trouvé : suite du processus

5. GÉNÉRATION PROMPT OPTIMISÉ
   ├── Construction contexte utilisateur
   ├── Ajout instructions spécifiques
   ├── Formatage pour GPT-4
   ├── Exemples de réponses attendues
   └── Contraintes de sécurité

6. APPEL AZURE OPENAI
   ├── Authentification API Key
   ├── Envoi requête POST
   ├── Attente réponse GPT-4 (2-5s)
   ├── Gestion timeout et erreurs
   └── Validation réponse JSON

7. PARSING ET VALIDATION
   ├── Extraction données JSON
   ├── Validation format réponse
   ├── Vérification cohérence
   ├── Nettoyage données
   └── Formatage pour interface

8. MISE EN CACHE
   ├── Stockage résultat analysé
   ├── Définition TTL (12h)
   ├── Incrémentation compteur accès
   ├── Métadonnées usage
   └── Logs audit

9. RETOUR UTILISATEUR
   ├── Rendu template avec réponse IA
   ├── Affichage recommandations
   ├── Options d'actions (sauvegarder, partager)
   └── Feedback utilisateur
```

#### Justifications du Workflow IA

| Aspect | Justification | Bénéfice |
|--------|---------------|----------|
| **Personnalisation** | Profil utilisateur enrichit réponse | Recommandations adaptées |
| **Cache Intelligent** | Éviter appels Azure coûteux | Performance et économie |
| **Prompt Engineering** | Optimisation pour GPT-4 | Qualité réponse maximale |
| **Validation Stricte** | Sécurité et cohérence | Fiabilité données |
| **Contexte Enrichi** | Base de données + APIs | Réponses complètes |
| **Gestion Erreurs** | Fallback sur échec | Robustesse système |

### 3.4 Workflow d'Appels aux APIs Externes

#### 3.4.1 OpenBeautyFacts API

#### Tableau du Workflow OpenBeautyFacts

| Étape | Composant | Action | Durée | Justification |
|-------|-----------|--------|-------|---------------|
| **1. Cache Check** | Cache Service | Vérification données | 0.01s | Performance optimale |
| **2. API Call** | OpenBeautyFacts | GET /product/{barcode}.json | 2-5s | Source fiable produits |
| **3. Parsing** | Product Service | Extraction métadonnées | 0.1s | Formatage données |
| **4. Cache Store** | Cache Service | Stockage résultat | 0.05s | Réutilisation future |

#### Workflow Détaillé OpenBeautyFacts

```
1. VÉRIFICATION CACHE
   ├── Clé: "product_info_{barcode}"
   ├── TTL: 24h (métadonnées stables)
   ├── Si trouvé : retour immédiat
   └── Si non trouvé : appel API

2. APPEL OPENBEAUTYFACTS
   ├── URL: https://world.openbeautyfacts.org/api/v0/product/{barcode}.json
   ├── Headers: User-Agent, Accept: application/json
   ├── Timeout: 10s
   └── Gestion erreurs (produit non trouvé)

3. EXTRACTION DONNÉES
   ├── Nom produit: product.product_name
   ├── Marque: product.brands
   ├── Ingrédients: product.ingredients_text
   ├── Catégorie: product.categories_tags
   └── Image: product.image_url

4. MISE EN CACHE
   ├── Stockage données extraites
   ├── TTL: 24h (métadonnées stables)
   ├── Métadonnées: timestamp, source
   └── Incrémentation compteur accès
```

#### 3.4.2 PubChem API

#### Tableau du Workflow PubChem

| Étape | Composant | Action | Durée | Justification |
|-------|-----------|--------|-------|---------------|
| **1. Cache Check** | Cache Service | Vérification ingrédient | 0.01s | Performance optimale |
| **2. PubChem Call** | PubChem API | GET /compound/name/{ingredient} | 3-8s | Base scientifique |
| **3. AI Fallback** | Azure OpenAI | Analyse IA si non trouvé | 5-10s | Complétude données |
| **4. Cache Store** | Cache Service | Stockage résultat | 0.05s | Réutilisation future |

#### Workflow Détaillé PubChem

```
1. VÉRIFICATION CACHE INGRÉDIENT
   ├── Clé: "ingredient_{ingredient_name}"
   ├── TTL: 12h (propriétés chimiques stables)
   ├── Si trouvé : retour immédiat
   └── Si non trouvé : appel API

2. APPEL PUBCHEM
   ├── URL: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{ingredient}/property/MolecularWeight,CanonicalSMILES/json
   ├── Headers: Accept: application/json
   ├── Timeout: 15s
   └── Gestion erreurs (ingrédient non trouvé)

3. TRAITEMENT RÉPONSE
   ├── Extraction CID (Compound ID)
   ├── Propriétés chimiques (poids moléculaire, SMILES)
   ├── Classification H-codes (risques)
   ├── Validation données
   └── Formatage pour système

4. FALLBACK IA (si non trouvé)
   ├── Appel Azure OpenAI
   ├── Prompt: "Analyse sécurité ingrédient {nom}"
   ├── Extraction H-codes estimés
   ├── Validation cohérence
   └── Marquage "estimé par IA"

5. MISE EN CACHE
   ├── Stockage propriétés chimiques
   ├── TTL: 12h (données scientifiques stables)
   ├── Métadonnées: source (PubChem/IA), confiance
   └── Incrémentation compteur accès
```

#### Justifications des APIs Externes

| API | Justification | Bénéfice |
|-----|---------------|----------|
| **OpenBeautyFacts** | Base de données collaborative fiable | Données produits précises |
| **PubChem** | Base scientifique reconnue | Analyse rigoureuse ingrédients |
| **Cache Intelligent** | Réduction appels API | Performance et économie |
| **Fallback IA** | Complétude données | Aucun ingrédient ignoré |
| **TTL Différencié** | Optimisation selon stabilité | Équilibre fraîcheur/performance |

## 4. Gestion du Cache et de la Base de Données

### 4.1 Stratégie de Cache Intelligent

Le système de cache de BeautyScan utilise une approche multi-niveaux pour optimiser les performances :

#### 4.1.1 Types de Cache

- **Cache Produit Complet** : TTL 6h - Analyse complète avec score
- **Cache Analyse IA** : TTL 12h - Recommandations et routines
- **Cache Informations Produit** : TTL 24h - Métadonnées OpenBeautyFacts
- **Cache Analyse Ingrédients** : TTL 12h - Données PubChem
- **Cache Scores Sécurité** : TTL 48h - Calculs de sécurité

#### 4.1.2 Logique de Cache

#### Tableau des Niveaux de Cache

| Niveau | Source | Durée | Justification | Performance |
|--------|--------|-------|---------------|-------------|
| **1. Cache Intelligent** | ProductCache Model | 6h | Données calculées | 0.01s |
| **2. Base Locale** | Django Models | 24h | Analyses récentes | 0.1s |
| **3. APIs Externes** | OpenBeautyFacts/PubChem | N/A | Données fraîches | 15-60s |

#### Workflow de Cache Multi-Niveaux

```
1. UTILISATEUR FAIT UNE DEMANDE
   ├── Analyse produit (code-barres)
   ├── Question IA
   └── Demande d'information

2. NIVEAU 1: CACHE INTELLIGENT
   ├── Recherche dans ProductCache
   ├── Vérification TTL (6h pour analyses complètes)
   ├── Si valide : retour immédiat (0.01s)
   └── Si expiré : suppression + niveau 2

3. NIVEAU 2: BASE LOCALE
   ├── Query: Scan.objects.filter(barcode=barcode, user_id=user_id)
   ├── Vérification timestamp (< 24h)
   ├── Si frais : mise en cache + retour (0.1s)
   └── Si obsolète : niveau 3

4. NIVEAU 3: APIs EXTERNES
   ├── Appel OpenBeautyFacts (métadonnées)
   ├── Appel PubChem (ingrédients)
   ├── Appel Azure OpenAI (analyse IA)
   ├── Calcul score sécurité
   ├── Sauvegarde en base locale
   ├── Mise en cache intelligent
   └── Retour utilisateur (15-60s)

5. MISE À JOUR CACHE
   ├── Incrémentation compteur accès
   ├── Mise à jour timestamp
   ├── Nettoyage données expirées
   └── Statistiques usage
```

#### Justifications de la Logique de Cache

| Stratégie | Justification | Bénéfice |
|-----------|---------------|----------|
| **Cache Multi-Niveaux** | Optimisation selon fraîcheur données | Performance progressive |
| **TTL Différencié** | Cycle de vie des données varié | Équilibre fraîcheur/performance |
| **Base Locale Intermédiaire** | Réduction appels API externes | Économie coûts et latence |
| **Cache Intelligent** | Données calculées coûteuses | Performance maximale |
| **Nettoyage Automatique** | Gestion mémoire optimisée | Maintenance transparente |

### 4.2 Schéma de Base de Données

#### 4.2.1 Schéma de Base de Données

#### Schéma ASCII des Relations

```
┌─────────────────────────────────────────────────────────────┐
│                    🗃️ BASE DE DONNÉES                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  👤 User (auth_user)                                       │
│  ├── id (PK)                                               │
│  ├── username, email                                       │
│  ├── date_joined, is_active                               │
│  └── 1:1 → UserProfile                                    │
│      └── 1:N → Scan                                       │
│      └── 1:N → Allergy                                    │
│                                                             │
│  📊 Scan (scans_scan)                                      │
│  ├── id (PK)                                               │
│  ├── user_id (FK → User)                                  │
│  ├── barcode, product_name, product_brand                 │
│  ├── product_score, product_risk_level                    │
│  ├── product_ingredients_text                             │
│  ├── created_at                                           │
│  └── 1:1 → ProductCache                                   │
│                                                             │
│  ⚡ ProductCache (scans_productcache)                      │
│  ├── id (PK)                                               │
│  ├── cache_key (UK)                                       │
│  ├── data (JSON)                                          │
│  ├── data_type                                            │
│  ├── created_at, expires_at                               │
│  └── access_count, last_accessed                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Tableau des Relations

| Table | Relation | Table Cible | Type | Justification |
|-------|----------|-------------|------|---------------|
| **User** | 1:1 | UserProfile | OneToOne | Profil unique par utilisateur |
| **User** | 1:N | Scan | ForeignKey | Historique scans utilisateur |
| **User** | 1:N | Allergy | ForeignKey | Allergies personnelles |
| **Scan** | 1:1 | ProductCache | OneToOne | Cache par analyse |
| **UserProfile** | 1:N | Allergy | ManyToMany | Allergies dans profil |

#### Tableau des Tables Principales

| Table | Champs Clés | Rôle | Justification |
|-------|-------------|------|---------------|
| **auth_user** | id, username, email | Gestion comptes | Authentification Django |
| **scans_userprofile** | user_id, skin_type, age_range | Profil beauté | Personnalisation |
| **scans_allergy** | name, category, severity | Base allergies | Sécurité utilisateur |
| **scans_scan** | barcode, product_score, ingredients | Historique analyses | Traçabilité |
| **scans_productcache** | cache_key, data, TTL | Cache intelligent | Performance |

#### Justifications du Schéma

| Aspect | Justification | Bénéfice |
|--------|---------------|----------|
| **Séparation User/Profile** | Logique métier distincte | Maintenance facilitée |
| **Cache Dédié** | Performance optimisée | Réponse rapide |
| **Relations Optimisées** | Foreign Keys appropriées | Intégrité référentielle |
| **Index sur cache_key** | Recherche cache rapide | Performance maximale |
| **JSON pour données** | Flexibilité stockage | Évolutivité |

#### 4.2.2 Tables Principales

**Table `auth_user` (Django)**
- Gestion des comptes utilisateurs
- Authentification et autorisation

**Table `accounts_userprofile`**
- Profil détaillé de l'utilisateur
- Préférences cosmétiques et allergies

**Table `scans_scan`**
- Historique des scans de produits
- Métadonnées des produits analysés

**Table `scans_productcache`**
- Cache intelligent des analyses
- Optimisation des performances

**Table `accounts_allergy`**
- Base de données des allergènes
- Classification par catégorie et gravité

## 5. Calcul du Score de Sécurité

### 5.1 Algorithme de Calcul

Le score de sécurité de BeautyScan utilise un système de pondération basé sur les codes de danger GHS (H-codes) :

#### 5.1.1 Formule de Calcul

```
Score_Final = max(0, 100 - (Poids_Base × Facteur_Classe × Facteur_Catégorie))

Où :
- Poids_Base : Poids du H-code selon sa dangerosité (5-15 points)
- Facteur_Classe : Multiplicateur selon le type de danger (0.5-2.0)
- Facteur_Catégorie : Multiplicateur selon la catégorie (0.8-1.5)
```

#### 5.1.2 Système de Pondération H-codes

| Catégorie | H-codes | Poids | Description |
|-----------|---------|-------|-------------|
| **Santé Grave** | H350, H340, H360 | 12-15 | Cancérogénicité, mutagénicité, reprotoxicité |
| **Santé Modéré** | H314, H318, H315 | 5-8 | Corrosion, lésions oculaires, irritation |
| **Physique** | H224, H225, H226 | 3-6 | Inflammabilité |
| **Environnement** | H400, H410, H411 | 4-8 | Danger aquatique |

#### 5.1.3 Facteurs Multiplicateurs

**Facteur Classe :**
- Dangers graves (H3xx) : 2.0
- Dangers modérés (H2xx) : 1.5
- Dangers physiques (H2xx) : 1.0
- Dangers environnementaux (H4xx) : 0.8

**Facteur Catégorie :**
- Santé : 1.5
- Physique : 1.0
- Environnement : 0.8

### 5.2 Exemple de Calcul

**Produit : Shampooing avec Sodium Laureth Sulfate**

1. **Ingrédient analysé** : Sodium Laureth Sulfate
2. **H-codes identifiés** : H315 (Irritation cutanée), H319 (Irritation oculaire)
3. **Calcul** :
   - H315 : Poids=5, Classe=1.5, Catégorie=1.5 → 5×1.5×1.5 = 11.25
   - H319 : Poids=3, Classe=1.5, Catégorie=1.5 → 3×1.5×1.5 = 6.75
   - Poids total = 18 points
4. **Score final** : max(0, 100 - 18) = **82/100**

### 5.3 Classification des Risques

| Score | Niveau | Recommandation |
|-------|--------|----------------|
| 75-100 | Excellent | Produit excellent pour votre profil |
| 50-74 | Bon | Produit bon pour votre profil |
| 25-49 | Médiocre | Produit médiocre, surveillez les réactions |
| 0-24 | Mauvais | Produit déconseillé pour votre profil |

## 6. Intégration Azure

### 6.1 Services Azure Utilisés

#### 6.1.1 Azure OpenAI Service

**Utilisation :**
- Génération de routines personnalisées
- Analyse d'ingrédients avec IA
- Nettoyage et normalisation des listes d'ingrédients
- Recommandations contextuelles

**Configuration :**
```python
AZURE_OPENAI_ENDPOINT = "https://beautyscan.openai.azure.com"
AZURE_OPENAI_API_KEY = "clé-secrète"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
OPENAI_MODEL = "gpt-4.1"
```

#### 6.1.2 Architecture d'Intégration Azure

#### Schéma ASCII de l'Intégration

```
┌─────────────────────────────────────────────────────────────┐
│                🎯 BeautyScan Application                    │
├─────────────────────────────────────────────────────────────┤
│  👁️ Django Views (apps/ai_routines/views.py)               │
│  🤖 AI Services (backend/services/ai_service.py)           │
│  🔗 Azure OpenAI Client (OpenAI SDK)                       │
└─────────────────┬───────────────────────────────────────────┘
                  │ API Call
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                ☁️ Azure Cloud Services                      │
├─────────────────────────────────────────────────────────────┤
│  🚀 Azure OpenAI Service (beautyscan.openai.azure.com)     │
│  🧠 GPT-4 Model (gpt-4.1 Deployment)                      │
│  ⚡ Response Processing (JSON Formatting)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ Structured Data
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                📊 Data Flow Process                         │
├─────────────────────────────────────────────────────────────┤
│  👤 User Input → ✍️ Prompt Engineering → 🔍 AI Analysis    │
│  📝 Response Parsing → 💾 Cache Storage → 🖥️ User Interface │
└─────────────────────────────────────────────────────────────┘
```

#### Tableau du Flux d'Intégration Azure

| Étape | Composant | Action | Données | Justification |
|-------|-----------|--------|---------|---------------|
| **1. Input** | Django Views | Réception requête utilisateur | Question/Routine | Point d'entrée web |
| **2. Processing** | AI Services | Initialisation client Azure | Configuration API | Gestion centralisée |
| **3. API Call** | Azure Client | Envoi requête à Azure | Prompt structuré | Communication standardisée |
| **4. Model** | Azure OpenAI | Traitement par GPT-4 | Analyse IA | Intelligence artificielle |
| **5. Response** | Azure Service | Retour réponse JSON | Données enrichies | Format standardisé |
| **6. Parsing** | AI Services | Validation et parsing | JSON → Python | Sécurité des données |
| **7. Cache** | Cache Service | Stockage résultat | Données persistantes | Performance future |
| **8. Display** | Django Views | Rendu interface | HTML/CSS | Expérience utilisateur |

#### Workflow Détaillé

```
1. UTILISATEUR FAIT UNE DEMANDE
   ├── Interface web (formulaire)
   ├── Question sur routine beauté
   └── Validation côté client

2. TRAITEMENT DJANGO
   ├── View reçoit requête POST
   ├── Validation données
   ├── Appel AI Service
   └── Gestion erreurs

3. PRÉPARATION PROMPT
   ├── Construction contexte utilisateur
   ├── Enrichissement avec profil
   ├── Formatage pour GPT-4
   └── Ajout instructions spécifiques

4. APPEL AZURE OPENAI
   ├── Authentification (API Key)
   ├── Envoi requête HTTP POST
   ├── Attente réponse (timeout)
   └── Gestion erreurs réseau

5. TRAITEMENT RÉPONSE
   ├── Validation JSON
   ├── Parsing données
   ├── Extraction informations
   └── Formatage pour interface

6. MISE EN CACHE
   ├── Génération clé cache
   ├── Stockage résultat
   ├── Définition TTL
   └── Statistiques usage

7. RETOUR UTILISATEUR
   ├── Rendu template
   ├── Affichage résultats
   ├── Options supplémentaires
   └── Logs audit
```

#### Justifications Techniques Azure

| Aspect | Justification | Avantage |
|--------|---------------|----------|
| **Azure vs OpenAI Direct** | Contrôle données, conformité RGPD | Sécurité renforcée |
| **GPT-4.1** | Modèle le plus avancé disponible | Qualité analyse maximale |
| **API Versioning** | `2024-02-15-preview` pour dernières fonctionnalités | Accès innovations |
| **Endpoint Dédié** | `beautyscan.openai.azure.com` | Isolation et monitoring |
| **Cache Intelligent** | Réduction coûts API Azure | Optimisation économique |

### 6.2 Workflow d'Intégration IA

#### 6.2.1 Génération de Routines

1. **Récupération Profil** : Données utilisateur et préférences
2. **Construction Prompt** : Assemblage du contexte complet
3. **Appel GPT-4** : Génération de la routine personnalisée
4. **Validation Réponse** : Vérification de la structure JSON
5. **Cache Intelligent** : Stockage pour réutilisation
6. **Formatage** : Adaptation pour l'interface utilisateur

#### 6.2.2 Analyse d'Ingrédients

1. **Normalisation** : Nettoyage des noms d'ingrédients
2. **Contexte Sécurité** : Ajout des informations de sécurité
3. **Prompt Spécialisé** : Focus sur les H-codes et risques
4. **Analyse Structurée** : Extraction des données formatées
5. **Validation** : Vérification de la cohérence des résultats

### 6.3 Optimisations de Performance

- **Cache Multi-Niveau** : Réduction des appels API
- **Prompt Engineering** : Optimisation des requêtes
- **Temperature Faible** : Réponses cohérentes (0.1)
- **Token Limitation** : Contrôle des coûts
- **Fallback Intelligent** : Gestion des erreurs

## 7. Documentation des Apps Django

### 7.1 App `accounts` - Gestion des Utilisateurs

#### 7.1.1 Modèles

**User (Django standard)**
- Authentification et autorisation
- Gestion des sessions

**UserProfile**
- Profil cosmétique personnalisé
- Type de peau, âge, objectifs
- Statut Premium et abonnement

**Allergy**
- Base de données des allergènes
- Classification par catégorie

#### 7.1.2 Fonctionnalités

- **Inscription/Connexion** : Authentification sécurisée
- **Gestion Profil** : Mise à jour des préférences
- **Gestion Allergies** : Ajout/suppression d'allergènes
- **Statut Premium** : Vérification et activation

### 7.2 App `scans` - Analyse de Produits

#### 7.2.1 Modèles

**Scan**
- Historique des analyses de produits
- Métadonnées et scores de sécurité
- Association utilisateur-produit

**ProductCache**
- Cache intelligent des analyses
- Optimisation des performances
- Gestion des TTL

#### 7.2.2 Fonctionnalités

- **Scan de Produit** : Analyse par code-barres
- **Historique** : Suivi des analyses précédentes
- **Dashboard** : Statistiques et tendances
- **Cache Management** : Gestion du cache intelligent

### 7.3 App `payments` - Gestion des Paiements

#### 7.3.1 Fonctionnalités

- **Upgrade Premium** : Processus de paiement
- **Intégration Stripe** : Paiements sécurisés
- **Webhooks** : Validation des transactions
- **Gestion Abonnements** : Activation/désactivation

#### 7.3.2 Workflow Paiement

1. **Sélection Méthode** : Stripe ou PayPal
2. **Création Session** : Configuration du paiement
3. **Redirection** : Vers la plateforme sécurisée
4. **Validation** : Webhook de confirmation
5. **Activation** : Mise à jour du profil

### 7.4 App `ai_routines` - Assistant IA

#### 7.4.1 Fonctionnalités

- **Assistant Beauté** : Interface conversationnelle
- **Routines Personnalisées** : Génération automatique
- **Analyse d'Ingrédients** : Décryptage IA
- **Questions Générales** : Conseils personnalisés

#### 7.4.2 Services

**PremiumAIService**
- Génération de routines Premium
- Analyse approfondie avec RAG
- Filtrage par budget

**EnhancedRoutineService**
- Routines personnalisées
- Adaptation au profil utilisateur
- Recommandations contextuelles

## 8. Schémas Architecturaux

### 8.1 Architecture Clean - Structure Hiérarchique

#### Schéma ASCII de l'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    🎨 PRESENTATION LAYER                    │
├─────────────────────────────────────────────────────────────┤
│  🌐 Web Interface (Django Templates)                       │
│  📱 Mobile App (Future)                                    │
│  🔌 API REST (Django REST Framework)                       │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP Requests / API Calls
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  🔌 ADAPTATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  👁️ Django Views (apps/accounts, scans, payments)          │
│  🎮 API Controllers (apps/api/views)                       │
│  🔗 External Adapters (OpenBeautyFacts, PubChem)           │
└─────────────────┬───────────────────────────────────────────┘
                  │ Business Logic
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  ⚙️ APPLICATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  📋 Use Cases (usecases/user/)                             │
│  🔧 Domain Services (backend/services/)                    │
│  🔄 Workflows (Product Analysis, AI Routines)              │
└─────────────────┬───────────────────────────────────────────┘
                  │ Domain Rules
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    🏗️ DOMAIN LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  📦 Entities (core/entities/)                              │
│  💎 Value Objects (core/value_objects/)                    │
│  📜 Interfaces (interfaces/repositories/)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ Persistence / External Data
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                🗄️ INFRASTRUCTURE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  💾 Database (SQLite/PostgreSQL)                           │
│  🌐 External APIs (Azure OpenAI, Stripe)                   │
│  ⚡ Cache (ProductCache Model)                             │
└─────────────────────────────────────────────────────────────┘
```

#### Tableau des Responsabilités par Couche

| Couche | Composant | Responsabilité | Justification |
|--------|-----------|----------------|---------------|
| **Présentation** | Django Templates | Interface utilisateur | Séparation UI/logique métier |
| **Présentation** | API REST | Exposition des services | Interface standardisée |
| **Adaptation** | Django Views | Orchestration des requêtes | Point d'entrée unique |
| **Adaptation** | External Adapters | Intégration APIs externes | Isolation des dépendances |
| **Application** | Use Cases | Logique métier complexe | Réutilisabilité |
| **Application** | Domain Services | Services transversaux | Cohésion fonctionnelle |
| **Domaine** | Entities | Objets métier centraux | Règles invariantes |
| **Domaine** | Value Objects | Concepts immutables | Sécurité des données |
| **Infrastructure** | Database | Persistance des données | Séparation stockage/logique |
| **Infrastructure** | Cache | Performance | Optimisation des accès |

### 8.2 Intégration APIs Externes - Architecture

#### Schéma ASCII des Intégrations

```
┌─────────────────────────────────────────────────────────────┐
│                🏗️ BeautyScan Core Services                  │
├─────────────────────────────────────────────────────────────┤
│  🔍 Product Analysis Service (apps/scans/services.py)      │
│  🤖 AI Service (backend/services/ai_service.py)           │
│  👤 User Service (backend/services/user_service.py)       │
│  ⚡ Cache Service (backend/services/product_cache_service.py) │
└─────────────────┬───────────────────────────────────────────┘
                  │ API Calls
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    🌐 External APIs                         │
├─────────────────────────────────────────────────────────────┤
│  📊 OpenBeautyFacts (Product Metadata)                     │
│  🧪 PubChem (Chemical Properties)                          │
│  🤖 Azure OpenAI (GPT-4 Analysis)                         │
│  💳 Stripe (Payment Processing)                           │
└─────────────────┬───────────────────────────────────────────┘
                  │ Data Storage
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    💾 Data Storage                          │
├─────────────────────────────────────────────────────────────┤
│  🗃️ SQLite Database (Django Models)                        │
│  ⚡ Redis Cache (Fast Access)                              │
└─────────────────────────────────────────────────────────────┘
```

#### Tableau des Intégrations API

| Service Core | API Externe | Endpoint | Méthode | Données Échangées | Justification |
|--------------|-------------|----------|---------|-------------------|---------------|
| **Product Analysis** | OpenBeautyFacts | `/product/{barcode}` | GET | Métadonnées produit | Source fiable produits cosmétiques |
| **Product Analysis** | PubChem | `/compound/name/{ingredient}` | GET | Propriétés chimiques | Base scientifique des ingrédients |
| **AI Service** | Azure OpenAI | `/chat/completions` | POST | Analyse IA GPT-4 | Intelligence artificielle avancée |
| **User Service** | Stripe | `/checkout/sessions` | POST | Traitement paiements | Sécurité financière certifiée |

#### Workflow d'Intégration

```
1. RECEPTION REQUÊTE
   └── Service Core reçoit demande utilisateur

2. VÉRIFICATION CACHE
   ├── Cache Service vérifie données existantes
   └── Si trouvé : retour immédiat
   └── Si non trouvé : appel API externe

3. APPEL API EXTERNE
   ├── Authentification (clés API)
   ├── Envoi requête formatée
   ├── Réception réponse JSON
   └── Validation données

4. TRAITEMENT DONNÉES
   ├── Parsing JSON
   ├── Transformation format interne
   ├── Enrichissement données
   └── Calcul scores sécurité

5. MISE EN CACHE
   ├── Stockage résultat
   ├── Définition TTL
   └── Mise à jour statistiques

6. RETOUR UTILISATEUR
   └── Affichage données enrichies
```

#### Justifications Techniques

| Aspect | Justification | Bénéfice |
|--------|---------------|----------|
| **Séparation Services** | Chaque service a une responsabilité unique | Maintenance facilitée |
| **Cache Intelligent** | Réduction appels API externes | Performance optimisée |
| **APIs Standardisées** | Utilisation REST/JSON | Intégration simplifiée |
| **Gestion Erreurs** | Fallback et retry automatiques | Robustesse système |
| **Monitoring** | Logs détaillés chaque étape | Débogage facilité |

### 8.3 Architecture de Cache - Système Intelligent

#### Schéma ASCII du Système de Cache

```
┌─────────────────────────────────────────────────────────────┐
│                  💾 CACHE STORAGE LAYERS                    │
├─────────────────────────────────────────────────────────────┤
│  🧠 Application Memory Cache (Django Cache Framework)      │
│  🗃️ Database Cache Table (scans_productcache)              │
│  ⚡ External API Cache (Redis/Memcached)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ Cache Types & TTL
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                📊 DATA TYPES & TTL CONFIG                   │
├─────────────────────────────────────────────────────────────┤
│  📊 Product Analysis (TTL: 6h) - complete_analysis_{barcode} │
│  🤖 AI Analysis (TTL: 12h) - ai_analysis_{question}        │
│  📦 Product Info (TTL: 24h) - product_info_{barcode}       │
│  🧪 Ingredient Analysis (TTL: 12h) - ingredient_{name}     │
│  ⚠️ Safety Scores (TTL: 48h) - safety_score_{barcode}      │
└─────────────────┬───────────────────────────────────────────┘
                  │ Management Strategy
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                🔧 CACHE MANAGEMENT SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│  🔄 LRU Eviction (Least Recently Used)                     │
│  ⏰ TTL Expiration (Time To Live)                          │
│  📈 Access Counting (Usage Statistics)                     │
│  🧹 Cache Cleanup (Expired Data Removal)                   │
└─────────────────────────────────────────────────────────────┘
```

#### Tableau des Types de Cache

| Type de Données | TTL | Clé de Cache | Stockage | Justification |
|-----------------|-----|--------------|----------|---------------|
| **Product Analysis** | 6h | `complete_analysis_{barcode}` | Database | Données complètes, coût calcul élevé |
| **AI Analysis** | 12h | `ai_analysis_{question}` | Memory | Réponses IA coûteuses, réutilisables |
| **Product Info** | 24h | `product_info_{barcode}` | Database | Métadonnées stables, accès fréquent |
| **Ingredient Analysis** | 12h | `ingredient_{name}` | Memory | Analyse chimique complexe |
| **Safety Scores** | 48h | `safety_score_{barcode}` | Database | Scores stables, référence |

#### Workflow de Cache

```
1. REQUÊTE UTILISATEUR
   └── Demande d'analyse produit

2. VÉRIFICATION CACHE
   ├── Recherche clé cache
   ├── Vérification TTL
   └── Si valide : retour immédiat
   └── Si expiré : suppression + nouvel appel

3. APPEL API EXTERNE (si cache miss)
   ├── OpenBeautyFacts (métadonnées)
   ├── PubChem (ingrédients)
   ├── Azure OpenAI (analyse IA)
   └── Calcul scores sécurité

4. MISE EN CACHE
   ├── Stockage données
   ├── Définition TTL
   ├── Incrémentation compteur accès
   └── Mise à jour timestamp

5. RETOUR UTILISATEUR
   └── Données enrichies + cache

6. MAINTENANCE CACHE
   ├── Nettoyage périodique (TTL)
   ├── Éviction LRU (espace)
   └── Statistiques usage
```

#### Justifications du Système de Cache

| Stratégie | Justification | Impact Performance |
|-----------|---------------|-------------------|
| **TTL Différencié** | Données ont des cycles de vie différents | Optimisation mémoire |
| **Stockage Hybride** | Memory pour fréquent, DB pour persistant | Équilibre vitesse/persistance |
| **LRU Eviction** | Éviction intelligente des données peu utilisées | Gestion mémoire optimale |
| **Access Counting** | Métriques pour optimisation continue | Amélioration continue |
| **Cache Keys Structurées** | Identification unique et prévisible | Recherche efficace |

## 9. Résumé et Recommandations

### 9.1 Bonnes Pratiques Respectées

#### 9.1.1 Architecture

- ✅ **Clean Architecture** : Séparation claire des couches
- ✅ **SOLID Principles** : Respect des principes de conception
- ✅ **Dependency Inversion** : Interfaces et implémentations découplées
- ✅ **Single Responsibility** : Chaque classe a une responsabilité unique

#### 9.1.2 Code Quality

- ✅ **PEP 8** : Respect des standards Python
- ✅ **Type Hints** : Annotations de type pour la lisibilité
- ✅ **Documentation** : Docstrings complètes et commentaires
- ✅ **Error Handling** : Gestion d'erreurs robuste

#### 9.1.3 Performance

- ✅ **Cache Intelligent** : Optimisation des temps de réponse
- ✅ **Lazy Loading** : Chargement à la demande
- ✅ **Database Optimization** : Requêtes optimisées
- ✅ **API Rate Limiting** : Respect des limites externes

### 9.2 Maintenance et Évolution

#### 9.2.1 Maintenance Courante

**Monitoring :**
- Surveillance des performances de cache
- Monitoring des appels API externes
- Suivi des erreurs et exceptions

**Mises à Jour :**
- Dépendances Python régulières
- Migrations de base de données
- Évolution des modèles IA

#### 9.2.2 Évolutions Recommandées

**Tests :**
- Augmentation de la couverture de tests (>80%)
- Tests d'intégration automatisés
- Tests de performance et charge

**CI/CD :**
- Pipeline d'intégration continue
- Déploiement automatisé
- Tests automatisés avant déploiement

**Monitoring :**
- Logs structurés avec ELK Stack
- Métriques de performance avec Prometheus
- Alertes automatiques sur les erreurs

**Sécurité :**
- Audit de sécurité régulier
- Mise à jour des dépendances
- Chiffrement des données sensibles

### 9.3 Recommandations Techniques

#### 9.3.1 Court Terme

1. **Tests Unitaires** : Couvrir les services métier
2. **Documentation API** : OpenAPI/Swagger
3. **Monitoring** : Logs structurés et métriques
4. **Cache Optimization** : Ajustement des TTL

#### 9.3.2 Moyen Terme

1. **Microservices** : Séparation des services IA
2. **Message Queue** : Traitement asynchrone
3. **Load Balancing** : Distribution de charge
4. **Database Scaling** : Optimisation des requêtes

#### 9.3.3 Long Terme

1. **Machine Learning** : Modèles personnalisés
2. **Real-time Analytics** : Tableaux de bord temps réel
3. **Mobile App** : Application native
4. **Internationalization** : Support multi-langues

---

## Conclusion

BeautyScan représente une implémentation réussie de la Clean Architecture dans un contexte Django, démontrant comment structurer une application complexe avec intégrations multiples (IA, APIs externes, paiements). L'architecture modulaire facilite la maintenance et l'évolution, tandis que le système de cache intelligent optimise les performances utilisateur.

La documentation technique présentée fournit une base solide pour la compréhension, la maintenance et l'évolution future de l'application, respectant les meilleures pratiques de développement logiciel moderne.

---

*Documentation technique BeautyScan v1.0*  
*Rédigé par l'équipe de développement Simplon*  
*Septembre 2025*
