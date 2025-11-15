# 🤖 Fingerbot Service

Microservice Node.js dockerisé pour piloter un **Switchbot Fingerbot** via Bluetooth Low Energy (BLE) et exposer une API REST sécurisée accessible sur Internet via **Cloudflare Tunnel**.

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
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

- ✅ **Contrôle BLE** : Pilotage du Fingerbot via Bluetooth Low Energy
- ✅ **API REST** : Endpoint simple pour déclencher le Fingerbot
- ✅ **Authentification** : Sécurisation par clé API
- ✅ **Docker** : Déploiement conteneurisé avec Docker Compose
- ✅ **Reverse Proxy** : Nginx avec headers de sécurité et compression
- ✅ **Cloudflare Tunnel** : Exposition sécurisée sur Internet sans ouverture de ports
- ✅ **Auto-restart** : Redémarrage automatique en cas de crash
- ✅ **Production-ready** : Architecture robuste et évolutive

---

## 🏗️ Architecture

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
                    │ Express API     │
                    │ (Port 3000)     │
                    │ - Auth API Key  │
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │ Bluetooth LE    │
                    │ (switchbot-ble) │
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │   Fingerbot     │
                    │   (WoFingerbot) │
                    └─────────────────┘
```

### Structure du projet

```
fingerbot-service/
├── src/
│   ├── api.js          # API REST Express
│   ├── config.js       # Configuration centralisée
│   └── fingerbot.js    # Logique de contrôle BLE
├── nginx/
│   └── nginx.conf      # Configuration Nginx
├── cloudflare/
│   ├── config.yml      # Configuration du tunnel
│   └── fingerbot.json  # Credentials Cloudflare (à créer)
├── docker-compose.yml  # Orchestration des services
├── Dockerfile          # Image Docker de l'API
├── package.json        # Dépendances Node.js
├── .env.example        # Template des variables d'environnement
├── .env                # Variables d'environnement (à créer)
└── README.md           # Ce fichier
```

---

## 🔧 Prérequis

### Matériel
- **Raspberry Pi** (ou serveur Linux avec Bluetooth LE)
- **Switchbot Fingerbot** (modèle WoFingerbot)
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

# Port de l'API (optionnel, défaut: 3000)
PORT=3000

# Durée du scan BLE en millisecondes (optionnel, défaut: 3000)
SCAN_DURATION=3000
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
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

### Mode Développement

```bash
# Installer les dépendances
npm install

# Démarrer l'API seule (sans Docker)
npm start
```

### Vérifier le statut

```bash
# Vérifier que les conteneurs sont actifs
docker ps

# Vérifier les logs de l'API
docker logs fingerbot-api

# Vérifier les logs du tunnel Cloudflare
docker logs cloudflare-tunnel
```

---

## 📡 Utilisation de l'API

### Endpoint disponible

#### `POST /fingerbot/press`

Actionne le Fingerbot (appuie sur le bouton).

**Headers requis :**
```
x-api-key: VotreCleSuperSecrete123!
Content-Type: application/json
```

**Exemples de requêtes :**

**Avec curl (local) :**
```bash
curl -X POST http://localhost:3000/fingerbot/press \
  -H "x-api-key: VotreCleSuperSecrete123!" \
  -H "Content-Type: application/json"
```

**Avec curl (via Cloudflare) :**
```bash
curl -X POST https://votre-domaine.example.com/fingerbot/press \
  -H "x-api-key: VotreCleSuperSecrete123!" \
  -H "Content-Type: application/json"
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
  "error": "Fingerbot introuvable"
}
```

ou

```json
{
  "error": "FINGERBOT_MAC non défini dans .env"
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

### Le Fingerbot n'est pas détecté

**Vérifications :**
```bash
# 1. Vérifier que le Bluetooth est activé
hciconfig

# 2. Scanner manuellement
sudo hcitool lescan

# 3. Vérifier la portée (distance < 10m)

# 4. Redémarrer le Bluetooth
sudo systemctl restart bluetooth
```

**Dans les logs Docker :**
```bash
docker logs fingerbot-api
# Si vous voyez "Fingerbot introuvable", vérifiez l'adresse MAC dans .env
```

### Erreur "FINGERBOT_MAC non défini"

Vérifiez que le fichier `.env` existe et contient la bonne variable :
```bash
cat .env | grep FINGERBOT_MAC
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

### L'API ne répond pas

```bash
# Vérifier que le conteneur est actif
docker ps

# Vérifier les logs
docker logs fingerbot-api

# Tester en local
curl -X POST http://localhost:3000/fingerbot/press \
  -H "x-api-key: VotreCleSuperSecrete123!"
```

### Permissions Bluetooth

Si vous avez des erreurs de permission BLE :
```bash
# Ajouter l'utilisateur au groupe bluetooth
sudo usermod -aG bluetooth $USER

# Redémarrer Docker
sudo systemctl restart docker
```

---

## 🔐 Sécurité

### Bonnes pratiques implémentées

✅ **Authentification par clé API** : Toutes les requêtes nécessitent un header `x-api-key`  
✅ **Reverse proxy Nginx** : L'API n'est pas exposée directement  
✅ **Headers de sécurité** : X-Frame-Options, X-Content-Type-Options, X-XSS-Protection  
✅ **Cloudflare Tunnel** : Pas d'ouverture de ports sur le routeur  
✅ **Variables d'environnement** : Secrets non versionnés dans Git  
✅ **Mode production** : `npm install --production` (pas de dépendances de dev)

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
- [ ] Implémenter un timeout configurable pour le scan BLE
- [ ] Ajouter une interface web pour contrôler le Fingerbot
- [ ] Support multi-Fingerbot
- [ ] Webhooks pour notifications

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

## 📧 Contact

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

## 🙏 Remerciements

- [Switchbot BLE](https://github.com/OpenWonderLabs/node-switchbot) - Bibliothèque Node.js pour Switchbot
- [Express.js](https://expressjs.com/) - Framework web minimaliste
- [Cloudflare](https://www.cloudflare.com/) - Tunnel sécurisé
- [Docker](https://www.docker.com/) - Containerisation

---

**Fait avec ❤️ pour automatiser votre maison**
