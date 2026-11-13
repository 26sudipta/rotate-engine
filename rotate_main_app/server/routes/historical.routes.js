import { Router } from "express";
import { getHistorical } from "../controllers/historical.controller.js";

const router = Router();

router.get("/:locationId", getHistorical);

export default router;
