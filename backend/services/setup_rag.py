#!/usr/bin/env python
"""
Script de configuration du RAG pour BeautyScan.

Ce script :
1. Crée l'index Azure Cognitive Search
2. Ajoute des données de test pour les routines et ingrédients
3. Teste le RAG
"""

import os
import sys
import django
from pathlib import Path

# Ajouter le chemin du projet au PYTHONPATH
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from backend.services.rag_service import RAGService

def create_sample_data():
    """Créer des données d'exemple pour le RAG."""
    return [
        # Données pour les routines
        {
            "id": "routine_dry_skin_morning",
            "title": "Routine Matin Peau Sèche",
            "content": "Nettoyant doux + Sérum acide hyaluronique + Crème hydratante + SPF 50+",
            "ingredients": "acide hyaluronique, céramides, urée, spf",
            "category": "routine",
            "brand": "La Roche-Posay, Avène, Eucerin",
            "safety_score": 95,
            "benefits": "Hydratation 24h, protection solaire, réparation barrière cutanée",
            "warnings": "Éviter les produits avec alcool dénaturé",
            "skin_types": "sèche, sensible",
            "tags": "matin, hydratation, protection solaire",
            "price_range": "medium"
        },
        {
            "id": "routine_oily_skin_evening",
            "title": "Routine Soir Peau Grasse",
            "content": "Démaquillant + Nettoyant purifiant + Sérum niacinamide + Crème légère",
            "ingredients": "niacinamide, acide salicylique, zinc, rétinol",
            "category": "routine",
            "brand": "The Ordinary, CeraVe, La Roche-Posay",
            "safety_score": 90,
            "benefits": "Contrôle du sébum, réduction des pores, prévention de l'acné",
            "warnings": "Rétinol seulement 2-3x par semaine",
            "skin_types": "grasse, mixte",
            "tags": "soir, purifiant, anti-acné",
            "price_range": "low"
        },
        {
            "id": "ingredient_hyaluronic_acid",
            "title": "Acide Hyaluronique",
            "content": "L'acide hyaluronique est un humectant puissant qui peut retenir jusqu'à 1000 fois son poids en eau. Il hydrate la peau en profondeur et réduit l'apparence des rides.",
            "ingredients": "acide hyaluronique, sodium hyaluronate",
            "category": "ingredient",
            "brand": "The Ordinary, La Roche-Posay, Vichy",
            "safety_score": 98,
            "benefits": "Hydratation intense, réduction des rides, compatibilité tous types de peau",
            "warnings": "Peut causer des picotements si concentration > 2%",
            "skin_types": "tous types",
            "tags": "hydratant, anti-âge, humectant",
            "price_range": "medium"
        },
        {
            "id": "ingredient_niacinamide",
            "title": "Niacinamide",
            "content": "La niacinamide (vitamine B3) réduit la production de sébum, minimise les pores et améliore la texture de la peau. Efficace contre l'acné et les taches.",
            "ingredients": "niacinamide, vitamine B3",
            "category": "ingredient",
            "brand": "The Ordinary, CeraVe, Paula's Choice",
            "safety_score": 95,
            "benefits": "Contrôle du sébum, réduction des pores, éclaircissement des taches",
            "warnings": "Peut causer des rougeurs au début",
            "skin_types": "grasse, mixte, acnéique",
            "tags": "purifiant, anti-acné, éclaircissant",
            "price_range": "low"
        },
        {
            "id": "product_toleriane_ultra",
            "title": "La Roche-Posay Toleriane Ultra",
            "content": "Crème hydratante pour peaux sensibles avec céramides et acide hyaluronique. Testée sur peaux sensibles et intolérantes.",
            "ingredients": "céramides, acide hyaluronique, niacinamide",
            "category": "product",
            "brand": "La Roche-Posay",
            "safety_score": 96,
            "benefits": "Hydratation 24h, apaisement, réparation barrière",
            "warnings": "Testez d'abord sur une petite zone",
            "skin_types": "sensible, sèche, normale",
            "tags": "hydratant, apaisant, réparateur",
            "price_range": "medium"
        }
    ]

def main():
    """Fonction principale."""
    print("🚀 Configuration du RAG pour BeautyScan")
    print("=" * 50)
    
    try:
        # Initialiser le service RAG
        print("1. Initialisation du service RAG...")
        rag_service = RAGService()
        
        if not rag_service.is_available():
            print("❌ RAG Service non disponible - vérifiez votre configuration Azure Search")
            print("   Assurez-vous d'avoir configuré :")
            print("   - AZURE_SEARCH_ENDPOINT")
            print("   - AZURE_SEARCH_KEY") 
            print("   - AZURE_SEARCH_INDEX_NAME")
            return False
        
        print("✅ RAG Service initialisé avec succès")
        
        # Créer l'index
        print("\n2. Création de l'index...")
        if rag_service.create_index():
            print("✅ Index créé avec succès")
        else:
            print("⚠️  Index déjà existant ou erreur de création")
        
        # Ajouter des données d'exemple
        print("\n3. Ajout des données d'exemple...")
        sample_data = create_sample_data()
        
        if rag_service.add_documents(sample_data):
            print(f"✅ {len(sample_data)} documents ajoutés avec succès")
        else:
            print("❌ Erreur lors de l'ajout des documents")
            return False
        
        # Tester le RAG
        print("\n4. Test du RAG...")
        test_queries = [
            "routine peau sèche matin",
            "acide hyaluronique",
            "niacinamide peau grasse"
        ]
        
        for query in test_queries:
            print(f"\n   Test: '{query}'")
            context = rag_service.get_context_for_ai(query)
            if context:
                print(f"   ✅ Contexte généré ({len(context)} caractères)")
                print(f"   📝 Aperçu: {context[:100]}...")
            else:
                print("   ❌ Aucun contexte généré")
        
        print("\n🎉 Configuration du RAG terminée avec succès !")
        print("\n📋 Prochaines étapes :")
        print("   1. Testez l'Assistant Beauté avec des questions")
        print("   2. Ajoutez plus de données selon vos besoins")
        print("   3. Intégrez le RAG dans les routines si souhaité")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration : {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
