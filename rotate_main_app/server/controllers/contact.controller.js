import { validateContact, saveContact } from "../services/contact.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const postContact = asyncHandler(async (req, res) => {
  const errors = validateContact(req.body ?? {});
  if (errors.length) {
    return res.status(400).json({ error: `Invalid message: ${errors.join(", ")}` });
  }
  const entry = saveContact(req.body);
  res.status(201).json({ data: { id: entry.id, receivedAt: entry.receivedAt } });
});
