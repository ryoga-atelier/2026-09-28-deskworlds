import test from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import { readFileSync } from "node:fs";

const source = readFileSync(new URL("../platforms/windows/lively-bridge.js", import.meta.url), "utf8");
function harness() {
  const events = {};
  const calls = { rate: [], pause: [], feed: 0 };
  const document = { hidden: false, addEventListener: (k, fn) => { events[k] = fn; } };
  const window = {
    addEventListener: (k, fn) => { events[k] = fn; },
    sceneRate: n => calls.rate.push(n),
    scenePause: n => calls.pause.push(n),
    sceneFeed: () => calls.feed++,
  };
  vm.runInNewContext(source, { window, document });
  return { window, document, calls, ready: events["guppy-scene-ready"], events };
}
test("properties arriving before scene initialization are retained", () => {
  const h = harness();
  h.window.livelyPropertyListener("playing", false);
  assert.equal(h.calls.rate.length, 0);
  h.ready();
  assert.equal(h.calls.rate.at(-1), 24);
  assert.equal(h.calls.pause.at(-1), true);
});
test("host resume does not override the user's paused setting", () => {
  const h = harness(); h.ready();
  h.window.livelyPropertyListener("playing", false);
  h.window.livelyWallpaperPlaybackChanged('{"IsPaused":true}');
  h.window.livelyWallpaperPlaybackChanged('{"IsPaused":false}');
  assert.equal(h.calls.pause.at(-1), true);
  h.window.livelyPropertyListener("playing", true);
  assert.equal(h.calls.pause.at(-1), false);
});
test("hidden pages and host pause stop feeding and survive malformed host data", () => {
  const h = harness(); h.ready();
  h.window.livelyWallpaperPlaybackChanged({ IsPaused: true });
  h.window.livelyWallpaperPlaybackChanged("invalid");
  h.window.livelyPropertyListener("feed", true);
  assert.equal(h.calls.feed, 0);
  h.window.livelyWallpaperPlaybackChanged({ IsPaused: false });
  h.document.hidden = true; h.events.visibilitychange();
  h.window.livelyPropertyListener("feed", true);
  assert.equal(h.calls.feed, 0);
  assert.equal(h.calls.pause.at(-1), true);
  h.document.hidden = false; h.events.visibilitychange();
  h.window.livelyPropertyListener("feed", true);
  assert.equal(h.calls.feed, 1);
});
