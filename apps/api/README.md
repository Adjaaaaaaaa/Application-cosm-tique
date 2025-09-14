# API Interne BeautyScan

## Vue d'ensemble

L'API interne BeautyScan fournit des endpoints sécurisés pour les services internes de l'application. Cette API utilise Clean Architecture et est **strictement réservée aux services internes**.

## 🔒 Sécurité

### Authentification Requise
Tous les endpoints nécessitent :
- **Token d'authentification** : `X-Internal-Token: internal_beautyscan_2024`
- **IP autorisée** : `127.0.0.1` ou `localhost` uniquement

### Exemple de requête autorisée
```bash
curl -H "X-Internal-Token: internal_beautyscan_2024" \
     http://localhost:8000/internal-api/health/
```

## 📋 Endpoints Disponibles

### 1. Health Check
**GET** `/internal-api/health/`

Vérifie l'état de l'API et de la base de données.

**Réponse :**
```json
{
  "status": "success",
  "service": "internal-api",
  "version": "1.0.0",
  "database": {
    "connected": true,
    "users_count": 42,
    "profiles_count": 38
  },
  "timestamp": {"checked_at": "now"}
}
```

### 2. Profil Utilisateur
**GET** `/internal-api/user-profile/<user_id>/`

Récupère le profil complet d'un utilisateur.

**Paramètres :**
- `user_id` (int) : ID de l'utilisateur

**Réponse :**
```json
{
  "status": "success",
  "data": {
    "username": "utilisateur",
    "email": "user@example.com",
    "skin_type": "sensitive",
    "age_range": "25-35",
    "allergies": ["parfum", "alcool"],
    "budget": 50
  }
}
```

### 3. Routine Complète IA
**POST** `/internal-api/enhanced-ai/comprehensive-routine/`

Génère une routine de soins complète personnalisée.

**Corps de la requête :**
```json
{
  "user_id": 1,
  "routine_type": "evening",
  "user_question": "Routine pour peau sensible",
  "budget": 50,
  "product_ingredients": "acide hyaluronique, niacinamide"
}
```

**Réponse :**
```json
{
  "status": "success",
  "data": {
    "routine": "Routine personnalisée...",
    "products": [...],
    "recommendations": [...]
  }
}
```

### 4. Analyse de Produit
**POST** `/internal-api/ai/analyze-product/`

Analyse un produit cosmétique avec l'IA.

**Corps de la requête :**
```json
{
  "user_id": 1,
  "product_ingredients": "ingrédient1, ingrédient2",
  "user_question": "Ce produit convient-il à ma peau ?",
  "product_info": {
    "name": "Crème hydratante",
    "brand": "Marque"
  }
}
```

**Réponse :**
```json
{
  "analysis": "Analyse détaillée...",
  "safety_score": 8.5,
  "recommendations": [...],
  "ingredients_analysis": [...]
}
```

### 5. Informations Ingrédient
**GET** `/internal-api/ingredients/info/`

Récupère les informations détaillées d'un ingrédient.

**Paramètres :**
- `ingredient` (string) : Nom de l'ingrédient

**Exemple :**
```
GET /internal-api/ingredients/info/?ingredient=niacinamide
```

**Réponse :**
```json
{
  "name": "Niacinamide",
  "description": "Vitamine B3...",
  "benefits": [...],
  "side_effects": [...],
  "safety_rating": 9.2
}
```

### 6. Question Générale IA
**POST** `/internal-api/ai/general-question/`

Répond aux questions générales sur les soins de la peau.

**Corps de la requête :**
```json
{
  "user_id": 1,
  "question": "Comment traiter l'acné ?"
}
```

**Réponse :**
```json
{
  "status": "success",
  "data": {
    "answer": "Réponse détaillée...",
    "recommendations": [...],
    "related_topics": [...]
  }
}
```

## 🏗️ Architecture

### Structure des fichiers
```
apps/api/
├── __init__.py
├── apps.py              # Configuration Django
├── urls.py              # Routes API
├── views.py             # Endpoints API
├── adapters/
│   └── internal_api_adapter.py  # Adapter Clean Architecture
└── README.md            # Cette documentation
```

### Clean Architecture
L'API utilise Clean Architecture avec :
- **Use Cases** : Logique métier (`usecases/user/`)
- **Repositories** : Accès aux données (`infrastructure/repositories/`)
- **Adapters** : Adaptation des frameworks (`apps/api/adapters/`)

## 🚨 Gestion d'Erreurs

### Codes de statut HTTP
- `200` : Succès
- `400` : Données invalides
- `403` : Accès non autorisé
- `404` : Ressource non trouvée
- `500` : Erreur serveur
- `503` : Service indisponible

### Format des erreurs
```json
{
  "status": "error",
  "message": "Description de l'erreur"
}
```

## 🔧 Configuration

### Variables d'environnement
- `INTERNAL_API_TOKEN` : Token d'authentification (défaut: `internal_beautyscan_2024`)

### Django Settings
L'app `apps.api` doit être dans `INSTALLED_APPS` :
```python
LOCAL_APPS = [
    # ...
    'apps.api',  # API interne sécurisée
    # ...
]
```

## 📝 Logs

Tous les accès et erreurs sont loggés avec :
- Adresse IP de la requête
- Token utilisé (masqué)
- Résultat de l'opération
- Erreurs détaillées

## ⚠️ Important

- **Cette API n'est PAS accessible au public**
- **Utilisation interne uniquement**
- **Authentification obligatoire**
- **Restriction IP active**
- **Tous les accès sont loggés**

## 🧪 Tests

Pour tester l'API :
```bash
# Test de santé
curl -H "X-Internal-Token: internal_beautyscan_2024" \
     http://localhost:8000/internal-api/health/

# Test de profil
curl -H "X-Internal-Token: internal_beautyscan_2024" \
     http://localhost:8000/internal-api/user-profile/1/
```
