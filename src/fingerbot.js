import Switchbot from 'node-switchbot';
import { FINGERBOT_MAC, SCAN_DURATION } from './config.js';

export async function scanFingerbot() {
  const switchbot = new Switchbot();
  
  const devices = await switchbot.discover({
    duration: SCAN_DURATION
  });

  const bot = devices.find(d => d.address === FINGERBOT_MAC || d.serviceData?.model === "f");
  
  if (!bot) return null;

  return {
    address: bot.address,
    modelName: "WoFingerbot",
    rssi: bot.rssi
  };
}

export async function pressFingerbot() {
  const switchbot = new Switchbot();
  
  const devices = await switchbot.discover({
    duration: SCAN_DURATION
  });

  const bot = devices.find(d => d.address === FINGERBOT_MAC);

  if (!bot) throw new Error("Fingerbot introuvable");

  const device = await switchbot.wait(bot.address);
  await device.press();
}
