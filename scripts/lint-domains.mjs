import { execSync } from "node:child_process";
import { readdirSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const domainsRoot = join(root, "openapi", "domains");

function walkJsonFiles(dir) {
  const files = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      files.push(...walkJsonFiles(full));
    } else if (entry.endsWith(".json") && entry !== "_index.json") {
      files.push(full);
    }
  }
  return files;
}

const files = walkJsonFiles(domainsRoot);
for (const file of files) {
  console.log(`Linting ${file}`);
  execSync(`npx redocly lint "${file}"`, { stdio: "inherit", cwd: root });
}

const webhooks = join(root, "openapi", "webhooks.yaml");
try {
  console.log(`Linting ${webhooks}`);
  execSync(`npx redocly lint "${webhooks}"`, { stdio: "inherit", cwd: root });
} catch {
  // webhooks.yaml optional
}
