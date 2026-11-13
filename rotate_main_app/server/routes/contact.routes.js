import { Router } from "express";
import { postContact } from "../controllers/contact.controller.js";

const router = Router();
router.post("/", postContact);
export default router;
