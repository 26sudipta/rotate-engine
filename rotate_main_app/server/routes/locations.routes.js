import { Router } from "express";
import { getAllLocations, getLocationById } from "../controllers/locations.controller.js";

const router = Router();

router.get("/", getAllLocations);
router.get("/:id", getLocationById);

export default router;
