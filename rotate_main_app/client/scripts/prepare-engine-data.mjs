import { cp, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const clientDir = dirname(fileURLToPath(import.meta.url));
const projectDir = resolve(clientDir, "..");
const repoRoot = resolve(projectDir, "../..");
const outputDir = resolve(projectDir, "public/engine");

await mkdir(outputDir, { recursive: true });

for (const [source, target] of [
  ["fixtures/cards_ctg.json", "cards_ctg.json"],
  ["fixtures/cards_barind.json", "cards_barind.json"],
]) {
  await cp(resolve(repoRoot, source), resolve(outputDir, target));
}
