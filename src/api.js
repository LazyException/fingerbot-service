import express from "express";
import { pressFingerbot } from "./fingerbot.js";
import { SECRET_API_KEY, PORT } from "./config.js";
import { scanFingerbot } from "./fingerbot.js";


const app = express();
app.use(express.json());

app.post("/fingerbot/press", async (req, res) => {
  const token = req.headers["x-api-key"];
  if (token !== SECRET_API_KEY)
    return res.status(403).json({ error: "Accès refusé" });

  try {
    await pressFingerbot();
    res.json({ status: "ok", message: "Fingerbot actionné" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Fingerbot API démarrée sur le port ${PORT}`);
});

app.get("/fingerbot/scan", async (req, res) => {
  const token = req.headers["x-api-key"];

  if (token !== SECRET_API_KEY)
    return res.status(403).json({ error: "Accès refusé" });

  try {
    const result = await scanFingerbot();
    if (!result) return res.json({ found: false });

    res.json({
      found: true,
      ...result
    });
  } catch (err) {
    res.status(500).json({ found: false, error: err.message });
  }
});
