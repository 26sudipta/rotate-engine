import { Router } from "express";
import { analyzeLocation } from "../controllers/analyze.controller.js";

const router = Router();

router.post("/", analyzeLocation);

export default router;
