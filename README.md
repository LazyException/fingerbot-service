# 🤖 Fingerbot Service

Microservice dockerisé pour piloter un **Switchbot Fingerbot** via Bluetooth Low Energy (BLE) et exposer une API REST sécurisée accessible sur Internet via **Cloudflare Tunnel**.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Démarrage](#-démarrage)
- [Utilisation de l'API](#-utilisation-de-lapi)
- [Déploiement](#-déploiement)
- [Dépannage](#-dépannage)
- [Sécurité](#-sécurité)

---

## ✨ Fonctionnalités

- ✅ **Architecture Microservices** : Séparation propre entre API métier et contrôle BLE
- ✅ **BLE Stable** : Service Python avec PySwitchbot (utilisé par Home Assistant)
- ✅ **API REST Node.js** : API Express simple et légère
- ✅ **Authentification** : Sécurisation par clé API
- ✅ **Docker** : Déploiement conteneurisé avec Docker Compose
- ✅ **Reverse Proxy** : Nginx avec headers de sécurité et compression
- ✅ **Cloudflare Tunnel** : Exposition sécurisée sur Internet sans ouverture de ports
- ✅ **Auto-restart** : Redémarrage automatique en cas de crash
- ✅ **Production-ready** : Architecture robuste et évolutive

---

## 🏗️ Architecture

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────────┐
                    │ Cloudflare      │
                    │ Tunnel          │
                    │ (cloudflared)   │
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │ Nginx           │
                    │ (Port 8080)     │
                    │ - Sécurité      │
                    │ - Compression   │
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │ Node.js API     │
                    │ (Port 3000)     │────────────┐
                    │ - Express       │            │
                    │ - Auth API Key  │            │ HTTP
                    └─────────────────┘            │
                                            ┌──────▼──────────┐
                                            │ Python BLE      │
                                            │ Service         │
                                            │ (Port 4000)     │
                                            │ - FastAPI       │
                                            │ - PySwitchbot   │
                                            └──────┬──────────┘
                                                   │
                                            ┌──────▼──────────┐
                                            │ Bluetooth LE    │
                                            │ (Raspberry Pi)  │
                                            └──────┬──────────┘
                                                   │
                                            ┌──────▼──────────┐
                                            │   Fingerbot     │
                                            │   (WoHand)      │
                                            └─────────────────┘
```

### Architecture Microservices

Ce projet utilise une **architecture microservices** pour séparer les responsabilités :

1. **Node.js API** (Port 3000)
   - Logique métier et API REST
   - Authentification et sécurité
   - Communication HTTP avec le service BLE

2. **Python BLE Service** (Port 4000)
   - Gestion exclusive du Bluetooth Low Energy
   - Utilise PySwitchbot (bibliothèque stable et maintenue)
   - API FastAPI exposant `/scan` et `/press`

**Pourquoi cette architecture ?**

✅ **Stabilité** : PySwitchbot est la bibliothèque BLE SwitchBot la plus stable et maintenue (utilisée par Home Assistant)  
✅ **Simplicité** : Node.js n'a plus de dépendances natives BLE (pas de node-gyp, pas de compilation C++)  
✅ **Maintenabilité** : Chaque service a une responsabilité unique  
✅ **Scalabilité** : Possibilité d'ajouter d'autres appareils SwitchBot facilement  

### Structure du projet

```
fingerbot-service/
├── ble-service/            # 🐍 Microservice Python BLE
│   ├── Dockerfile          # Image Python 3.11
│   ├── requirements.txt    # PySwitchbot, FastAPI, Uvicorn
│   └── main.py             # API BLE (scan, press)
├── src/
│   ├── api.js              # API REST Express
│   ├── config.js           # Configuration centralisée
│   └── fingerbot.js        # Appels HTTP vers BLE service
├── nginx/
│   └── nginx.conf          # Configuration Nginx
├── cloudflare/
│   ├── config.yml          # Configuration du tunnel
│   └── fingerbot.json      # Credentials Cloudflare (à créer)
├── docker-compose.yml      # Orchestration des 4 services
├── Dockerfile              # Image Docker Node.js (API)
├── package.json            # Dépendances Node.js (Express, Axios)
├── .env.example            # Template des variables d'environnement
└── README.md               # Ce fichier
```

---

## 🔧 Prérequis

### Matériel
- **Raspberry Pi** (ou serveur Linux avec Bluetooth LE)
- **Switchbot Fingerbot** (modèle WoHand)
- Bluetooth 4.0+ (BLE)

### Logiciels
- **Docker** (v20+)
- **Docker Compose** (v2.0+)
- **Compte Cloudflare** (pour le tunnel)

### Système d'exploitation
- Linux (Raspberry Pi OS, Ubuntu, Debian, etc.)
- Bluetooth activé et fonctionnel

---

## 📦 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/fingerbot-service.git
cd fingerbot-service
```

### 2. Installer Docker et Docker Compose

**Sur Raspberry Pi / Debian / Ubuntu :**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Vérifier le Bluetooth

```bash
# Vérifier que le Bluetooth est actif
hciconfig

# Scanner les périphériques BLE à proximité
sudo hcitool lescan
```

Notez l'**adresse MAC** de votre Fingerbot (format `XX:XX:XX:XX:XX:XX`).

---

## ⚙️ Configuration

### 1. Variables d'environnement

Créez un fichier `.env` à partir du template :

```bash
cp .env.example .env
nano .env
```

Configurez les variables suivantes :

```env
# Adresse MAC de votre Fingerbot (obligatoire)
FINGERBOT_MAC=XX:XX:XX:XX:XX:XX

# Clé secrète pour authentifier les requêtes (obligatoire)
SECRET_API_KEY=VotreCleSuperSecrete123!

# Port de l'API Node.js (optionnel, défaut: 3000)
PORT=3000

# Durée du scan BLE en secondes (optionnel, défaut: 5)
SCAN_DURATION=5

# URL du service BLE Python (optionnel, défaut: http://localhost:4000)
BLE_SERVICE_URL=http://localhost:4000
```

> ⚠️ **Important** : Utilisez une clé API forte et unique !

### 2. Configuration Cloudflare Tunnel

#### a) Créer un tunnel Cloudflare

```bash
# Installer cloudflared localement
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Se connecter à Cloudflare
cloudflared tunnel login

# Créer un nouveau tunnel
cloudflared tunnel create fingerbot

# Récupérer l'ID du tunnel et le fichier credentials
ls ~/.cloudflared/
```

#### b) Configurer le tunnel

Copiez le fichier `credentials.json` :

```bash
cp ~/.cloudflared/TUNNEL_ID.json cloudflare/fingerbot.json
```

Modifiez `cloudflare/config.yml` :

```yaml
tunnel: fingerbot
credentials-file: /etc/cloudflared/fingerbot.json

ingress:
  - hostname: votre-domaine.example.com  # Remplacez par votre domaine
    service: http://localhost:8080
  - service: http_status:404
```

#### c) Créer un enregistrement DNS

```bash
cloudflared tunnel route dns fingerbot votre-domaine.example.com
```

---

## 🚀 Démarrage

### Mode Production (recommandé)

```bash
# Démarrer tous les services (BLE, API, Nginx, Cloudflare)
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Vérifier les logs d'un service spécifique
docker-compose logs -f ble-service
docker-compose logs -f fingerbot-api

# Arrêter les services
docker-compose down
```

### Vérifier le statut

```bash
# Vérifier que les conteneurs sont actifs
docker ps

# Vous devriez voir :
# - ble-service (Python BLE)
# - fingerbot-api (Node.js)
# - nginx-fingerbot (Reverse proxy)
# - cloudflare-tunnel (Tunnel)

# Tester le service BLE directement
curl http://localhost:4000/

# Tester l'API Node.js
curl -X POST http://localhost:3000/fingerbot/press \
  -H "x-api-key: VotreCleSuperSecrete123!"
```

---

## 📡 Utilisation de l'API

### Endpoints disponibles

#### `POST /fingerbot/press`

Actionne le Fingerbot (appuie sur le bouton).

**Headers requis :**
```
x-api-key: VotreCleSuperSecrete123!
Content-Type: application/json
```

#### `GET /fingerbot/scan`

Scanne et détecte les Fingerbot BLE à proximité.

**Headers requis :**
```
x-api-key: VotreCleSuperSecrete123!
```

### Exemples de requêtes

**Appuyer sur le Fingerbot (local) :**
```bash
curl -X POST http://localhost:3000/fingerbot/press \
  -H "x-api-key: VotreCleSuperSecrete123!" \
  -H "Content-Type: application/json"
```

**Appuyer sur le Fingerbot (via Cloudflare) :**
```bash
curl -X POST https://votre-domaine.example.com/fingerbot/press \
  -H "x-api-key: VotreCleSuperSecrete123!" \
  -H "Content-Type: application/json"
```

**Scanner les Fingerbot à proximité :**
```bash
curl -X GET http://localhost:3000/fingerbot/scan \
  -H "x-api-key: VotreCleSuperSecrete123!"
```

**Avec JavaScript (fetch) :**
```javascript
fetch('https://votre-domaine.example.com/fingerbot/press', {
  method: 'POST',
  headers: {
    'x-api-key': 'VotreCleSuperSecrete123!',
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err));
```

**Avec Python (requests) :**
```python
import requests

url = "https://votre-domaine.example.com/fingerbot/press"
headers = {
    "x-api-key": "VotreCleSuperSecrete123!",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers)
print(response.json())
```

### Réponses

**✅ Succès (200) :**
```json
{
  "status": "ok",
  "message": "Fingerbot actionné"
}
```

**❌ Erreur d'authentification (403) :**
```json
{
  "error": "Accès refusé"
}
```

**❌ Erreur serveur (500) :**
```json
{
  "error": "Message d'erreur détaillé"
}
```

---

## 🌐 Déploiement

### Sur Raspberry Pi

1. **Mise à jour du système :**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Activer le démarrage automatique :**
```bash
# Docker Compose démarrera automatiquement au boot
sudo systemctl enable docker
```

3. **Créer un service systemd (optionnel) :**
```bash
sudo nano /etc/systemd/system/fingerbot.service
```

Contenu du fichier :
```ini
[Unit]
Description=Fingerbot Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/fingerbot-service
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Activer le service :
```bash
sudo systemctl enable fingerbot.service
sudo systemctl start fingerbot.service
```

### Mise à jour du service

```bash
# Arrêter les conteneurs
docker-compose down

# Récupérer les dernières modifications
git pull

# Reconstruire et redémarrer
docker-compose up -d --build
```

---

## 🛠️ Dépannage

### Le service BLE ne démarre pas

**Vérifications :**
```bash
# 1. Vérifier les logs du service BLE
docker logs ble-service

# 2. Vérifier que le Bluetooth est activé
hciconfig

# 3. Redémarrer le Bluetooth
sudo systemctl restart bluetooth

# 4. Redémarrer le conteneur BLE
docker-compose restart ble-service
```

### Le Fingerbot n'est pas détecté

**Vérifications :**
```bash
# 1. Scanner manuellement depuis le conteneur Python
docker exec -it ble-service python3 -c "
from switchbot import Switchbot
import asyncio
async def scan():
    sb = Switchbot()
    devices = await sb.discover(duration=5)
    print(devices)
asyncio.run(scan())
"

# 2. Vérifier la portée (distance < 10m)

# 3. Vérifier l'adresse MAC dans .env
cat .env | grep FINGERBOT_MAC
```

### L'API Node.js ne communique pas avec le service BLE

```bash
# 1. Vérifier que le service BLE répond
curl http://localhost:4000/

# 2. Vérifier les logs de l'API
docker logs fingerbot-api

# 3. Vérifier la variable BLE_SERVICE_URL
docker exec fingerbot-api env | grep BLE_SERVICE_URL
```

### Le tunnel Cloudflare ne fonctionne pas

```bash
# Vérifier les logs
docker logs cloudflare-tunnel

# Tester la connexion
cloudflared tunnel info fingerbot

# Vérifier la route DNS
cloudflared tunnel route dns fingerbot votre-domaine.example.com
```

### Erreur "FINGERBOT_MAC non défini"

Vérifiez que le fichier `.env` existe et contient la bonne variable :
```bash
cat .env | grep FINGERBOT_MAC
```

---

## 🔐 Sécurité

### Bonnes pratiques implémentées

✅ **Architecture microservices** : Isolation des services  
✅ **Service BLE isolé** : Seul le service Python a accès au Bluetooth  
✅ **Authentification par clé API** : Toutes les requêtes nécessitent un header `x-api-key`  
✅ **Reverse proxy Nginx** : L'API n'est pas exposée directement  
✅ **Headers de sécurité** : X-Frame-Options, X-Content-Type-Options, X-XSS-Protection  
✅ **Cloudflare Tunnel** : Pas d'ouverture de ports sur le routeur  
✅ **Variables d'environnement** : Secrets non versionnés dans Git  
✅ **Images Docker optimisées** : Node.js Alpine, Python Slim

### Recommandations supplémentaires

⚠️ **Changez la clé API** : Utilisez une clé forte (32+ caractères aléatoires)  
⚠️ **Limitez l'accès** : Configurez un pare-feu (UFW, iptables)  
⚠️ **Surveillez les logs** : Mettez en place un système de monitoring  
⚠️ **Mises à jour** : Gardez Docker et les dépendances à jour

### Générer une clé API sécurisée

```bash
# Générer une clé aléatoire de 32 caractères
openssl rand -base64 32
```

---

## 🚀 Améliorations futures

- [ ] Ajouter un endpoint `/health` pour le monitoring
- [ ] Implémenter un rate limiting (éviter les spams)
- [ ] Ajouter des logs structurés (Winston/Pino)
- [ ] Créer des tests unitaires et d'intégration
- [ ] Ajouter un système de retry en cas d'échec BLE
- [ ] Ajouter une interface web pour contrôler le Fingerbot
- [ ] Support multi-Fingerbot
- [ ] Webhooks pour notifications
- [ ] Métriques Prometheus/Grafana

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🙏 Remerciements

- [PySwitchbot](https://github.com/Danielhiversen/pySwitchbot) - Bibliothèque Python stable pour SwitchBot (utilisée par Home Assistant)
- [FastAPI](https://fastapi.tiangolo.com/) - Framework API moderne et performant
- [Express.js](https://expressjs.com/) - Framework web Node.js minimaliste
- [Cloudflare](https://www.cloudflare.com/) - Tunnel sécurisé
- [Docker](https://www.docker.com/) - Containerisation

---

**Fait avec ❤️ pour automatiser votre maison avec une architecture professionnelle et stable**
