import { spawnSync } from "node:child_process";
import { writeFileSync, unlinkSync } from "node:fs";
import { fileURLToPath } from "node:url";

const apiDir = fileURLToPath(new URL("../apps/api/", import.meta.url));
const python = process.env.API_PYTHON || `${apiDir}.venv/bin/python`;
const result = spawnSync(
  python,
  ["-c", "import json; from app.main import app; print(json.dumps(app.openapi()))"],
  {
    cwd: apiDir,
    encoding: "utf8",
    env: { ...process.env, APP_ENV: "test" },
  },
);
if (result.status !== 0) {
  process.stderr.write(
    result.stderr || "Could not generate API schema. Set up apps/api/.venv first.\n",
  );
  process.exit(1);
}
const temp = fileURLToPath(new URL("../apps/api/.openapi.tmp.json", import.meta.url));
writeFileSync(temp, result.stdout);
try {
  const types = spawnSync(
    "npx",
    ["--no-install", "openapi-typescript", temp, "-o", "apps/web/src/lib/api-schema.d.ts"],
    { stdio: "inherit", shell: process.platform === "win32" },
  );
  process.exitCode = types.status ?? 1;
} finally {
  unlinkSync(temp);
}
