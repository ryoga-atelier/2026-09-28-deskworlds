import { test, expect } from "@playwright/test";

test("packaged scene renders, feeds, and handles both pause sources", async ({ page }) => {
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.addInitScript(() => localStorage.setItem("deskworlds-quality", "detail"));
  await page.goto("http://127.0.0.1:8877/index.html");
  await page.waitForFunction(() => window.sceneStats?.().renderedFrames > 5);
  const before = await page.evaluate(() => sceneStats());
  expect(before.profile).toBe("balanced");
  expect(await page.evaluate(() => localStorage.getItem("deskworlds-quality"))).toBe("detail");
  expect(before.loop.fps).toBe(24);
  await page.evaluate(() => livelyPropertyListener("feed", true));
  await expect.poll(() => page.evaluate(() => sceneStats().food.dropped)).toBeGreaterThan(before.food.dropped);

  await page.evaluate(() => livelyWallpaperPlaybackChanged('{"IsPaused":true}'));
  await page.waitForTimeout(250);
  const stopped = await page.evaluate(() => sceneStats().renderedFrames);
  await page.waitForTimeout(1100);
  expect(await page.evaluate(() => sceneStats().renderedFrames)).toBe(stopped);
  await page.evaluate(() => {
    livelyPropertyListener("playing", false);
    livelyWallpaperPlaybackChanged('{"IsPaused":false}');
  });
  await page.waitForTimeout(600);
  expect(await page.evaluate(() => sceneStats().renderedFrames)).toBe(stopped);
  await page.evaluate(() => livelyPropertyListener("playing", true));
  await expect.poll(() => page.evaluate(() => sceneStats().renderedFrames)).toBeGreaterThan(stopped + 2);
  await page.screenshot({ path: "test-results/windows-package.png" });
  expect(errors).toEqual([]);
});
