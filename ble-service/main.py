from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from switchbot import GetSwitchbotDevices

app = FastAPI(title="BLE Service", description="Microservice Python pour contrôler SwitchBot via BLE")

SCAN_DURATION = 5


class PressRequest(BaseModel):
    mac_address: str = None


@app.get("/")
async def root():
    return {"status": "ok", "service": "BLE Service", "version": "1.0.0"}


@app.get("/scan")
async def scan_devices():
    try:
        # Nouveau scan moderne pyswitchbot
        devices = await GetSwitchbotDevices().discover(duration=SCAN_DURATION)

        # devices = dictionnaire : { "aa:bb:...": SwitchbotDevice() }
        fingerbots = [
            {
                "mac_address": dev.address,
                "model": dev.device_type,
                "rssi": dev.rssi,
            }
            for dev in devices.values()
            if dev.device_type == "WoHand"
        ]

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
async def press_fingerbot(request: PressRequest):
    try:
        mac_address = request.mac_address

        if not mac_address:
            raise HTTPException(
                status_code=400,
                detail="Adresse MAC requise"
            )

        devices = await GetSwitchbotDevices().discover(duration=SCAN_DURATION)

        target = devices.get(mac_address.lower())

        if not target:
            raise HTTPException(
                status_code=404,
                detail=f"Fingerbot {mac_address} non trouvé"
            )

        # Nouvelle méthode moderne :
        await target.hand_press()

        return {
            "status": "ok",
            "message": "Fingerbot actionné avec succès",
            "mac_address": mac_address
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BLE: {str(e)}")
