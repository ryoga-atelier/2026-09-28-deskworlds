// Lively's documented property and playback callbacks. No polling loop,
// system input hooks, network access, or extra animation timer.
(() => {
  let ready = false;
  let playing = true;
  let hostPaused = false;
  function apply() {
    if (!ready) return;
    window.sceneRate(24);
    window.scenePause(!playing || hostPaused || document.hidden);
  }
  window.livelyPropertyListener = (name, value) => {
    if (name === "playing" && (typeof value === "boolean" || value === "true" || value === "false")) {
      playing = value === true || value === "true";
      apply();
    } else if (name === "feed" && ready && playing && !hostPaused && !document.hidden &&
               (value === true || value === "true")) {
      window.sceneFeed();
    }
  };
  window.livelyWallpaperPlaybackChanged = (data) => {
    try {
      const state = typeof data === "string" ? JSON.parse(data) : data;
      if (typeof state?.IsPaused !== "boolean") return;
      hostPaused = state.IsPaused;
      apply();
    } catch { /* Invalid host notifications do not change playback. */ }
  };
  window.addEventListener("guppy-scene-ready", () => {
    ready = true;
    apply();
  }, { once: true });
  document.addEventListener("visibilitychange", apply);
  window.addEventListener("pageshow", apply);
})();
