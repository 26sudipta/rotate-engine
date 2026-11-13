import { Router } from "express";
import { getStrategies, getRankedStrategies } from "../controllers/strategies.controller.js";

const router = Router();

router.get("/", getStrategies);
router.get("/ranked", getRankedStrategies);

export default router;
