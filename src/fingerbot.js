import Switchbot from "switchbot-ble";
import { FINGERBOT_MAC, SCAN_DURATION } from "./config.js";

export async function pressFingerbot() {
  if (!FINGERBOT_MAC) throw new Error("FINGERBOT_MAC non défini dans .env");

  const switchbot = new Switchbot();

  const devices = await switchbot.discover({
    duration: SCAN_DURATION,
    model: "WoFingerbot"
  });

  const bot = devices.find(d => d.address === FINGERBOT_MAC);

  if (!bot) throw new Error("Fingerbot introuvable");

  await bot.connect();
  await bot.run();
  await bot.disconnect();
}