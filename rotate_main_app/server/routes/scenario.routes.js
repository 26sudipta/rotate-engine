import { Router } from "express";
import { postScenario } from "../controllers/scenario.controller.js";

const router = Router();

router.post("/", postScenario);

export default router;
