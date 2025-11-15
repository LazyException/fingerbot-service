import { Switchbot } from "@openwonderlabs/node-switchbot";
import { FINGERBOT_MAC, SCAN_DURATION } from "./config.js";

export async function scanFingerbot() {
  const switchbot = new Switchbot();

  const devices = await switchbot.discover({
    duration: SCAN_DURATION
  });

  const bot = devices.find(d => d.address === FINGERBOT_MAC || d.model === "WoHand");

  if (!bot) return null;

  return {
    address: bot.address,
    modelName: bot.model,
    rssi: bot.rssi
  };
}

export async function pressFingerbot() {
  const switchbot = new Switchbot();
  const device = await switchbot.wait(FINGERBOT_MAC);

  await device.press();
}
