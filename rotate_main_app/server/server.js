import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import locationsRoutes from "./routes/locations.routes.js";
import climateRoutes from "./routes/climate.routes.js";
import historicalRoutes from "./routes/historical.routes.js";
import strategiesRoutes from "./routes/strategies.routes.js";
import analyzeRoutes from "./routes/analyze.routes.js";
import scenarioRoutes from "./routes/scenario.routes.js";
import healthRoutes from "./routes/health.routes.js";
import cropsRoutes from "./routes/crops.routes.js";
import contactRoutes from "./routes/contact.routes.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

// Data note: every endpoint below currently serves the demonstration dataset
// in /data. Swap the relevant service in /services for a real NASA Earth
// Observation or agronomic-model client to move off mock data.
app.use("/api/locations", locationsRoutes);
app.use("/api/climate", climateRoutes);
app.use("/api/historical", historicalRoutes);
app.use("/api/strategies", strategiesRoutes);
app.use("/api/analyze", analyzeRoutes);
app.use("/api/scenario", scenarioRoutes);
app.use("/api/health", healthRoutes);
app.use("/api/crops", cropsRoutes);
app.use("/api/contact", contactRoutes);

app.use((req, res) => {
  res.status(404).json({ error: `Route ${req.method} ${req.originalUrl} not found` });
});

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

app.listen(PORT, () => {
  console.log(`ROTATE API listening on http://localhost:${PORT}`);
});
