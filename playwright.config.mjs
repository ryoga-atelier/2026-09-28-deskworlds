import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/browser", workers: 1, timeout: 90000,
  use: {
    // Use the full Chromium compositor, closer to Lively's CEF host. The
    // headless-shell compositor stalls captures on the Windows runner.
    channel: "chromium",
    viewport: { width: 1000, height: 620 },
    launchOptions: {
      ...(process.env.GUPPY_CHROME ? { executablePath: process.env.GUPPY_CHROME } : {}),
      args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"],
    },
  },
  webServer: {
    command: "node tests/browser/serve.mjs",
    url: "http://127.0.0.1:8877/index.html",
    reuseExistingServer: false,
  },
});
