import { Router } from "express";
import { getClimate } from "../controllers/climate.controller.js";

const router = Router();

router.get("/:locationId", getClimate);

export default router;
