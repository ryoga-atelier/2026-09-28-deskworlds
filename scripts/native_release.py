"""r15: release the page of a screen that stays hidden, then rebuild it when seen.

Applied to the build copy of Wallpaper.swift only (after the passive probe patch);
the pinned upstream source is never edited. A covered screen, or one whose display or
session is asleep, keeps its WebGL page for 60 s. It then discards that WKWebView, so
WebKit can end the page process and free its WebGL/JS memory; the window shows the
scene's own startup colour. When the screen is seen again a fresh view reloads the
scene. Navigating to an empty page was not enough in measurement: the page process
kept its memory. Pause and Low Power Mode keep the still scene because it is on show.
"""


def _swap(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'native release patch anchor not unique: {old[:60]!r}')
    return source.replace(old, new)


def apply_native_release(source):
    source = _swap(source, '  let view: WKWebView\n', '  var view: WKWebView\n')
    source = _swap(source, '  private var battery = false\n', '''  private var battery = false
  private var released = false
  private var releaseWork: DispatchWorkItem?
  private let sceneURL: URL
  private let pageConfiguration: WKWebViewConfiguration
  private let pageBackground: NSColor
''')
    source = _swap(source, '    super.init()\n\n    view.navigationDelegate = self', '''    sceneURL = URL(string: "\\(sceneScheme)://\\(sceneHost)\\(world.page)")!
    pageConfiguration = settings
    pageBackground = world.background
    super.init()

    view.navigationDelegate = self''')
    source = _swap(source, '''  func setRate(_ wanted: Int) -> Bool {
    guard wanted != rate else { return false }''', '''  func setRate(_ wanted: Int, releasable: Bool = false) -> Bool {
    scheduleRelease(wanted == 0 && releasable)
    if wanted > 0 && released { restore() }
    guard wanted != rate else { return false }''')
    source = _swap(source, '  func setPower(_ onBattery: Bool) {', '''  /// A hidden screen gives its page back after 60 s; nobody can see it.
  private func scheduleRelease(_ should: Bool) {
    if !should {
      releaseWork?.cancel()
      releaseWork = nil
      return
    }
    guard releaseWork == nil, !released else { return }
    let work = DispatchWorkItem { [weak self] in self?.release() }
    releaseWork = work
    DispatchQueue.main.asyncAfter(deadline: .now() + 60, execute: work)
  }

  private func release() {
    releaseWork = nil
    guard !released, rate == 0 else { return }
    released = true
    loaded = false
    inside = false
    NSLog("deskworlds: released hidden scene page")
    let old = view
    old.stopLoading()
    old.navigationDelegate = nil
    old.removeFromSuperview()
    window.contentView = nil
    // Unloaded placeholder: no page, no web content process until restore() loads it.
    view = WKWebView(frame: window.frame, configuration: pageConfiguration)
  }

  private func restore() {
    released = false
    NSLog("deskworlds: reloading scene page after release")
    if view.responds(to: NSSelectorFromString("setWindowOcclusionDetectionEnabled:"))
      || view.responds(to: NSSelectorFromString("_setWindowOcclusionDetectionEnabled:"))
    {
      view.setValue(false, forKey: "windowOcclusionDetectionEnabled")
    }
    view.underPageBackgroundColor = pageBackground
    view.autoresizingMask = [.width, .height]
    view.navigationDelegate = self
    window.contentView = view
    view.load(URLRequest(url: sceneURL))
  }

  func setPower(_ onBattery: Bool) {''')
    source = _swap(source, '      if screen.setRate(rate) { changed = true }',
        '      if screen.setRate(rate, releasable: !awake || (!stopped && !lowPower && showing < 0.15)) { changed = true }')
    # r16: the page draws 24 fps, so sampling the cursor faster only adds page calls.
    source = _swap(source, '    let wanted = min(30, applied)', '    let wanted = min(24, applied)')
    return source
