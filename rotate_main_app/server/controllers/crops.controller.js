import { listCrops } from "../services/crops.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const getCrops = asyncHandler(async (req, res) => {
  res.json({ data: listCrops() });
});
