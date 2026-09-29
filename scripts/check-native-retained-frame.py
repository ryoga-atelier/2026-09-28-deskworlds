#!/usr/bin/env python3
"""Exercise real AppKit/WKWebView release transitions in a macOS desktop session.

Only the generated test copy changes the 60-second delay to 0.5 seconds. This
creates a small, non-interactive desktop-level window and exits after ~15 seconds.
No system wallpaper, preferences, or other app windows are changed.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from native_diagnostics import apply_native_probe
from native_release import apply_native_release

ROOT = Path(__file__).resolve().parents[1]
if sys.platform != "darwin":
    raise SystemExit("This integration check requires a macOS desktop session")

HTML = '''<!doctype html><html><body style="margin:0;background:#208cbb">
<canvas id="scene" width="600" height="360" style="width:100vw;height:100vh"></canvas>
<div id="loading">Loading</div><div id="error" hidden></div><script>
window.sceneRate = () => {}; window.scenePower = () => {};
window.sceneStats = () => ({renderedFrames: 1});
webkit.messageHandlers.ready.postMessage('ready');
setTimeout(() => {
  const c = document.querySelector('canvas').getContext('2d');
  c.fillStyle='#208cbb'; c.fillRect(0,0,600,360);
  c.fillStyle='#efd458'; c.fillRect(50,50,120,100);
  document.querySelector('#loading').hidden = true;
}, 1200);
</script></body></html>'''

HARNESS = r'''
extension Wallpaper {
  var testLargeBitmapLimit: Bool {
    let context = CGContext(data: nil, width: 4096, height: 2304, bitsPerComponent: 8,
      bytesPerRow: 4096 * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    guard let bitmap = boundedBitmap(context.makeImage()!) else { return false }
    return bitmap.pixelsWide * bitmap.pixelsHigh <= 1_800_000
  }
  var testReleased: Bool { released }
  var testPoster: Bool { !retainedFrame.isHidden && retainedFrame.image != nil }
  var testAttached: Bool { view.superview === surface && window.contentView === surface }
  var testBitmap: Bool {
    guard let rep = retainedFrame.image?.representations.first as? NSBitmapImageRep,
          let blue = rep.colorAt(x: rep.pixelsWide * 3 / 4, y: rep.pixelsHigh / 2),
          let yellow = rep.colorAt(x: rep.pixelsWide / 6, y: rep.pixelsHigh / 4)
    else { return false }
    return blue.blueComponent > blue.redComponent + 0.2 &&
      yellow.redComponent > yellow.blueComponent + 0.2 &&
      rep.pixelsWide * rep.pixelsHigh <= 1_805_000
  }
}
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
guard let screen = NSScreen.screens.first else { fatalError("No desktop session") }
let root = URL(fileURLWithPath: CommandLine.arguments[1])
let wallpaper = Wallpaper(screen: screen, root: root, world: .riverscape)
wallpaper.window.setFrame(NSRect(x: 40, y: 40, width: 600, height: 360), display: true)
wallpaper.setRate(24)
var failures = 0
func check(_ condition: Bool, _ name: String) {
  print("\(condition ? "PASS" : "FAIL") \(name)")
  if !condition { failures += 1 }
}
func after(_ seconds: Double, _ block: @escaping () -> Void) {
  DispatchQueue.main.asyncAfter(deadline: .now() + seconds, execute: block)
}
after(3) {
  check(wallpaper.testLargeBitmapLimit, "4K snapshot is bounded to 1.8 million pixels")
  wallpaper.setRate(0) // User Pause never frees the visible scene.
}
after(4) {
  check(!wallpaper.testReleased && wallpaper.testAttached, "pause keeps page")
  wallpaper.setRate(0, releasable: true)
}
after(5.5) {
  check(wallpaper.testReleased && wallpaper.testPoster, "covered release keeps frame")
  check(wallpaper.testBitmap, "retained bitmap contains canvas pixels and is bounded")
  wallpaper.setRate(24)
  check(wallpaper.testPoster && wallpaper.testAttached, "reload stays behind frame")
}
after(6) {
  check(wallpaper.testPoster, "callback-ready does not expose loading page")
}
after(8) {
  check(!wallpaper.testPoster && wallpaper.testAttached, "first rendered frame replaces poster")
  wallpaper.setRate(0, releasable: true)
  after(0.15) { wallpaper.setRate(24) }
}
after(9) {
  check(!wallpaper.testReleased && wallpaper.testAttached, "visibility cancels pending release")
  wallpaper.view.evaluateJavaScript("document.querySelector('#loading').hidden = false") { _, _ in
    wallpaper.setRate(0, releasable: true)
  }
}
after(10.5) {
  check(!wallpaper.testReleased && wallpaper.testAttached, "unready capture preserves page")
  wallpaper.setRate(24)
  wallpaper.view.evaluateJavaScript("document.querySelector('#loading').hidden = true") { _, _ in
    wallpaper.setRate(0, releasable: true)
  }
}
after(12) {
  check(wallpaper.testReleased && wallpaper.testPoster, "repeat release retains frame")
  let page = root.appendingPathComponent("scenes/riverscape/wallpaper.html")
  try! FileManager.default.moveItem(at: page, to: page.appendingPathExtension("saved"))
  wallpaper.setRate(24)
}
after(14) {
  check(wallpaper.testPoster && wallpaper.testAttached, "failed reload retains aquarium")
  wallpaper.setRate(0, releasable: true)
  wallpaper.close()
}
after(15) {
  check(wallpaper.window.contentView == nil, "close cancels pending release")
  print("RESULT failures=\(failures)")
  exit(failures == 0 ? 0 : 1)
}
app.run()
'''

source = (ROOT / "upstream/deskworlds/wallpaper/Wallpaper.swift").read_text()
patched = apply_native_release(apply_native_probe(source))
assert patched.count("private let releaseDelay: TimeInterval = 60") == 1
patched = patched.replace("private let releaseDelay: TimeInterval = 60",
                          "private let releaseDelay: TimeInterval = 0.5")
with tempfile.TemporaryDirectory(prefix="deskworlds-native-check-") as folder:
    tmp = Path(folder)
    page = tmp / "scenes/riverscape/wallpaper.html"
    page.parent.mkdir(parents=True)
    page.write_text(HTML)
    swift = tmp / "main.swift"
    swift.write_text(patched.split("final class Controller:", 1)[0] + HARNESS)
    binary = tmp / "RetainedFrameCheck"
    subprocess.run(["swiftc", "-o", str(binary), str(swift), "-framework", "Cocoa",
                    "-framework", "WebKit", "-framework", "IOKit"], check=True)
    result = subprocess.run([str(binary), str(tmp)], capture_output=True, text=True, timeout=60)
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence/native-retained-frame-test.json").write_text(json.dumps({
        "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
        "production_release_seconds": 60, "test_release_seconds": 0.5,
    }, indent=2) + "\n")
    raise SystemExit(result.returncode)
