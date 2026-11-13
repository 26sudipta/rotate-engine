import { Router } from "express";
import { getCrops } from "../controllers/crops.controller.js";

const router = Router();
router.get("/", getCrops);
export default router;
