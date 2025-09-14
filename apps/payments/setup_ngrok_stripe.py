#!/usr/bin/env python3
"""
ngrok setup script for Stripe BeautyScan.

This script helps configure ngrok to share the Stripe webhook URL
with the development team.
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ngrok():
    """Install ngrok if necessary."""
    print("📥 Installation de ngrok...")
    
    if sys.platform.startswith('win'):
        # Windows
        print("🌐 Téléchargez ngrok depuis: https://ngrok.com/download")
        print("📁 Extrayez ngrok.exe dans un dossier du PATH")
        return False
    elif sys.platform.startswith('darwin'):
        # macOS
        try:
            subprocess.run(['brew', 'install', 'ngrok'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation avec Homebrew")
            return False
    else:
        # Linux
        try:
            subprocess.run(['sudo', 'snap', 'install', 'ngrok'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation avec snap")
            return False

def start_ngrok(port=8000):
    """Start ngrok on the specified port."""
    print(f"🚀 Démarrage de ngrok sur le port {port}...")
    
    try:
        # Démarrer ngrok en arrière-plan
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre que ngrok démarre
        time.sleep(3)
        
        # Récupérer l'URL publique
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    print(f"✅ ngrok démarré: {public_url}")
                    return public_url, process
        except requests.RequestException:
            pass
        
        print("⚠️  Impossible de récupérer l'URL ngrok automatiquement")
        print("🔍 Vérifiez manuellement sur: http://localhost:4040")
        return None, process
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de ngrok: {e}")
        return None, None

def update_env_file(ngrok_url):
    """Update .env file with ngrok URL."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    try:
        # Lire le contenu actuel
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si NGROK_URL existe déjà
        if 'NGROK_URL=' in content:
            # Mettre à jour l'URL existante
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('NGROK_URL='):
                    lines[i] = f'NGROK_URL={ngrok_url}'
                    break
            content = '\n'.join(lines)
        else:
            # Ajouter NGROK_URL
            content += f'\n# URL ngrok pour Stripe\nNGROK_URL={ngrok_url}\n'
        
        # Écrire le contenu mis à jour
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fichier .env mis à jour avec NGROK_URL={ngrok_url}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du fichier .env: {e}")
        return False

def print_stripe_instructions(ngrok_url):
    """Affiche les instructions pour configurer Stripe."""
    print("\n" + "="*60)
    print("🔧 CONFIGURATION STRIPE POUR L'ÉQUIPE")
    print("="*60)
    print(f"🌐 URL ngrok: {ngrok_url}")
    print(f"🔗 Webhook URL: {ngrok_url}/payments/stripe-webhook/")
    print(f"✅ Success URL: {ngrok_url}/payments/stripe-success/")
    print(f"❌ Cancel URL: {ngrok_url}/payments/upgrade/")
    print("\n📋 ÉTAPES POUR L'ÉQUIPE:")
    print("1. Allez sur: https://dashboard.stripe.com/webhooks")
    print("2. Cliquez sur 'Ajouter un endpoint'")
    print(f"3. URL: {ngrok_url}/payments/stripe-webhook/")
    print("4. Événements à sélectionner:")
    print("   - checkout.session.completed")
    print("   - payment_intent.succeeded")
    print("   - payment_intent.payment_failed")
    print("   - customer.subscription.created")
    print("   - customer.subscription.updated")
    print("   - customer.subscription.deleted")
    print("5. Cliquez sur 'Ajouter des événements' puis 'Créer un endpoint'")
    print("6. Copiez le 'Signing secret' (commence par whsec_)")
    print("7. Ajoutez-le dans votre .env: STRIPE_WEBHOOK_SECRET=whsec_...")
    print("\n🧪 TEST:")
    print("• Utilisez les cartes de test Stripe")
    print("• Numéro: 4242 4242 4242 4242")
    print("• Date: 12/25, CVC: 123")
    print("="*60)

def main():
    """Fonction principale."""
    print("🚀 Configuration ngrok pour Stripe BeautyScan")
    print("="*50)
    
    # Vérifier si ngrok est installé
    if not check_ngrok_installed():
        print("❌ ngrok n'est pas installé")
        if not install_ngrok():
            print("📥 Veuillez installer ngrok manuellement")
            return
        print("✅ ngrok installé avec succès")
    
    # Démarrer ngrok
    ngrok_url, process = start_ngrok(8000)
    
    if not ngrok_url:
        print("❌ Impossible de démarrer ngrok")
        return
    
    # Mettre à jour le fichier .env
    update_env_file(ngrok_url)
    
    # Afficher les instructions
    print_stripe_instructions(ngrok_url)
    
    print(f"\n🔄 ngrok fonctionne sur: {ngrok_url}")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter ngrok")
    
    try:
        # Garder ngrok en cours d'exécution
        process.wait()
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt de ngrok...")
        if process:
            process.terminate()

if __name__ == "__main__":
    main()
