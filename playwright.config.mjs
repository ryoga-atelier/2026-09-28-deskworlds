import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/browser", workers: 1, timeout: 90000,
  // Hosted Windows renders WebGL in software, so this is a correctness check,
  // not a 24fps performance benchmark. Allow submitted frames to finish.
  expect: { timeout: 30000 },
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
