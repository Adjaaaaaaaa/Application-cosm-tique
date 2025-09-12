#!/usr/bin/env python3
"""
Script de démarrage pour BeautyScan.
Lance Django avec API intégrée sur le port 8000.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Fonction principale."""
    print("🎯 BeautyScan - Serveur Django avec API")
    print("=" * 50)
    print("📖 URLs disponibles:")
    print("   - Site web: http://127.0.0.1:8000")
    print("   - Assistant IA: http://127.0.0.1:8000/ai-routines/beauty-assistant/")
    print("   - API Health: http://127.0.0.1:8000/api/v1/health/")
    print("   - API Routine: http://127.0.0.1:8000/api/v1/enhanced-ai/comprehensive-routine/")
    print("=" * 50)
    
    try:
        # Démarrer Django
        subprocess.run([
            sys.executable, "manage.py", "runserver", "127.0.0.1:8000"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
