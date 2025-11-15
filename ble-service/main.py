import asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from switchbot import Switchbot

app = FastAPI(title="BLE Service", description="Microservice Python pour contrôler SwitchBot via BLE")

# Configuration
FINGERBOT_MAC = os.getenv("FINGERBOT_MAC", "")
SCAN_DURATION = int(os.getenv("SCAN_DURATION", "5"))


class PressRequest(BaseModel):
    """Requête pour appuyer sur le Fingerbot"""
    mac_address: str = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "BLE Service", "version": "1.0.0"}


@app.get("/scan")
async def scan_devices():
    """
    Scanne les appareils SwitchBot BLE à proximité
    Retourne la liste des Fingerbot (WoHand) détectés
    """
    try:
        switchbot = Switchbot()
        
        # Scanner les appareils BLE
        devices = await switchbot.discover(duration=SCAN_DURATION)
        
        # Filtrer pour ne garder que les Fingerbot (WoHand)
        fingerbots = []
        for device in devices:
            # Vérifier si c'est un Fingerbot
            if device.get("modelName") == "WoHand" or device.get("model") == "WoHand":
                fingerbots.append({
                    "mac_address": device.get("address"),
                    "model": device.get("modelName") or device.get("model"),
                    "rssi": device.get("rssi"),
                })
        
        if not fingerbots:
            return {
                "found": False,
                "devices": [],
                "message": "Aucun Fingerbot détecté"
            }
        
        return {
            "found": True,
            "devices": fingerbots,
            "count": len(fingerbots)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du scan BLE: {str(e)}")


@app.post("/press")
async def press_fingerbot(request: PressRequest = None):
    """
    Appuie sur le Fingerbot spécifié par son adresse MAC
    Si aucune adresse n'est fournie, utilise FINGERBOT_MAC de l'environnement
    """
    try:
        # Déterminer l'adresse MAC à utiliser
        mac_address = request.mac_address if request and request.mac_address else FINGERBOT_MAC
        
        if not mac_address:
            raise HTTPException(
                status_code=400, 
                detail="Adresse MAC requise (via body ou variable FINGERBOT_MAC)"
            )
        
        # Créer l'instance Switchbot
        switchbot = Switchbot()
        
        # Attendre et récupérer le device
        device = await switchbot.wait_for_device(mac_address, timeout=10)
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail=f"Fingerbot avec MAC {mac_address} non trouvé"
            )
        
        # Appuyer sur le Fingerbot
        success = await device.press()
        
        if success:
            return {
                "status": "ok",
                "message": "Fingerbot actionné avec succès",
                "mac_address": mac_address
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Échec de l'activation du Fingerbot"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BLE: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
