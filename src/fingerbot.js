import axios from "axios";
import { FINGERBOT_MAC, BLE_SERVICE_URL } from "./config.js";

/**
 * Scanne les appareils Fingerbot via le microservice Python BLE
 */
export async function scanFingerbot() {
  try {
    const response = await axios.get(`${BLE_SERVICE_URL}/scan`, {
      timeout: 10000
    });

    const data = response.data;

    if (!data.found || !data.devices || data.devices.length === 0) {
      return null;
    }

    // Retourner le premier Fingerbot trouvé
    const bot = data.devices[0];
    
    return {
      address: bot.mac_address,
      modelName: bot.model,
      rssi: bot.rssi
    };
  } catch (error) {
    console.error("Erreur lors du scan BLE:", error.message);
    throw new Error(`Échec du scan BLE: ${error.message}`);
  }
}

/**
 * Appuie sur le Fingerbot via le microservice Python BLE
 */
export async function pressFingerbot() {
  try {
    const response = await axios.post(`${BLE_SERVICE_URL}/press`, 
      {
        mac_address: FINGERBOT_MAC
      },
      {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.data.status !== "ok") {
      throw new Error("Le Fingerbot n'a pas répondu correctement");
    }

    return response.data;
  } catch (error) {
    console.error("Erreur lors de l'activation du Fingerbot:", error.message);
    
    if (error.response) {
      throw new Error(`Erreur BLE: ${error.response.data.detail || error.response.statusText}`);
    }
    
    throw new Error(`Échec de l'activation: ${error.message}`);
  }
}
