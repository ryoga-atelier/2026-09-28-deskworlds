import http from "node:http";
import path from "node:path";
import { readFile } from "node:fs/promises";
const root = path.resolve(process.env.GUPPY_PACKAGE || "build/browser-package");
const mime = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css",
  ".png": "image/png", ".jpg": "image/jpeg", ".json": "application/json", ".svg": "image/svg+xml" };
http.createServer(async (req, res) => {
  try {
    const file = path.resolve(root, "." + decodeURIComponent(new URL(req.url, "http://localhost").pathname));
    if (!file.startsWith(root + path.sep)) throw new Error("Outside root");
    res.setHeader("Content-Type", mime[path.extname(file)] || "application/octet-stream");
    res.end(await readFile(file));
  } catch { res.statusCode = 404; res.end("Not found"); }
}).listen(8877, "127.0.0.1");
