"""Keep covered aquariums swimming; retain a frame when sleeping pages are freed.

Applied to the build copy of Wallpaper.swift only (after the passive probe patch);
the pinned upstream source is never edited. Awake scenes keep swimming at 12 fps
behind other windows (Balanced stays capped at 24 fps when exposed). Only a display
or session that is asleep can discard its WKWebView after 60 s, so
WebKit can free its WebGL/JS memory. A bounded, opaque native bitmap stays on screen
until the replacement scene has rendered. Partial coverage must never reveal the
system wallpaper. A failed snapshot keeps the paused page instead. Pause and Low
Power Mode keep the still scene because it is on show. Upstream remains untouched.
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
  private var canRelease = false
  private var capturing = false
  private var closed = false
  private var releaseEpoch = 0
  private let releaseDelay: TimeInterval = 60
  private let surface = NSView()
  private let retainedFrame = NSImageView()
  private var retainedPixels = [Int]()
  private let sceneURL: URL
  private let pageConfiguration: WKWebViewConfiguration
  private let pageBackground: NSColor
''')
    source = _swap(source, '    super.init()\n\n    view.navigationDelegate = self', '''    sceneURL = URL(string: "\\(sceneScheme)://\\(sceneHost)\\(world.page)")!
    pageConfiguration = settings
    pageBackground = world.background
    super.init()

    view.navigationDelegate = self''')
    source = _swap(source, '    view = WKWebView(frame: screen.frame, configuration: settings)', '''    // The usual ready message only means callbacks exist. Wait for the scene's
    // loading cover to disappear after its first render before uncovering a reload.
    settings.userContentController.addUserScript(WKUserScript(source: """
      (() => {
        const loading = document.querySelector('#loading');
        if (!loading) return;
        let sent = false;
        const check = () => {
          const error = document.querySelector('#error');
          const canvas = document.querySelector('#scene');
          if (sent || !loading.hidden || (error && !error.hidden) || !canvas?.width) return;
          if (typeof sceneStats === 'function' && sceneStats().renderedFrames < 1) return;
          sent = true;
          observer.disconnect();
          requestAnimationFrame(() => requestAnimationFrame(() =>
            webkit.messageHandlers.ready.postMessage('retained-frame-ready')));
        };
        const observer = new MutationObserver(check);
        observer.observe(loading, {attributes: true, attributeFilter: ['hidden']});
        check();
      })();
      """, injectionTime: .atDocumentEnd, forMainFrameOnly: true))
    view = WKWebView(frame: screen.frame, configuration: settings)''')
    source = _swap(source, '    window.contentView = view', '''    surface.frame = NSRect(origin: .zero, size: screen.frame.size)
    surface.wantsLayer = true
    surface.layer?.backgroundColor = pageBackground.cgColor
    window.contentView = surface
    view.frame = surface.bounds
    surface.addSubview(view)
    retainedFrame.frame = surface.bounds
    retainedFrame.autoresizingMask = [.width, .height]
    retainedFrame.imageScaling = .scaleAxesIndependently
    retainedFrame.isHidden = true
    surface.addSubview(retainedFrame)''')
    source = _swap(source, '  func close() {\n', '''  func close() {
    closed = true
    releaseEpoch += 1
    releaseWork?.cancel()
    releaseWork = nil
    retainedFrame.image = nil
''')
    source = _swap(source, '''  func setRate(_ wanted: Int) -> Bool {
    guard wanted != rate else { return false }''', '''  func setRate(_ wanted: Int, releasable: Bool = false) -> Bool {
    scheduleRelease(wanted == 0 && releasable)
    if wanted > 0 && released { restore() }
    guard wanted != rate else { return false }''')
    source = _swap(source, '  func setPower(_ onBattery: Bool) {', '''  /// Coverage can leave a visible strip: retain the aquarium when freeing its page.
  private func scheduleRelease(_ should: Bool) {
    if canRelease != should { releaseEpoch += 1 }
    canRelease = should
    if !should {
      releaseWork?.cancel()
      releaseWork = nil
      return
    }
    guard releaseWork == nil, !released, !capturing, !closed else { return }
    let work = DispatchWorkItem { [weak self] in self?.release() }
    releaseWork = work
    DispatchQueue.main.asyncAfter(deadline: .now() + releaseDelay, execute: work)
  }

  private func release() {
    releaseWork = nil
    guard !released, !closed, canRelease, rate == 0 else { return }
    // If another reload is still covered by our bitmap, retain it on load failure.
    if !retainedFrame.isHidden, retainedFrame.image != nil {
      discardPage()
      return
    }
    guard loaded else { return }
    capturing = true
    let epoch = releaseEpoch
    let old = view
    old.evaluateJavaScript("""
      Boolean(document.querySelector('#loading')?.hidden &&
        document.querySelector('#scene')?.width &&
        (!document.querySelector('#error') || document.querySelector('#error').hidden))
      """) { [weak self, weak old] ready, _ in
      guard let self, let old else { return }
      guard !self.closed, self.canRelease, self.rate == 0,
            self.releaseEpoch == epoch, self.view === old, ready as? Bool == true else {
        self.capturing = false
        return
      }
      let configuration = WKSnapshotConfiguration()
      let size = old.bounds.size
      // Ask WebKit for a smaller snapshot, then enforce the physical pixel limit
      // below: mixed-DPI displays do not always honour snapshotWidth's scale.
      let scale = min(1, sqrt(1_800_000 / max(1, size.width * size.height)))
      configuration.snapshotWidth = NSNumber(value: Double(size.width * scale / max(1, self.window.backingScaleFactor)))
      old.takeSnapshot(with: configuration) { [weak self, weak old] image, error in
        guard let self else { return }
        self.capturing = false
        guard let old, !self.closed, self.canRelease, self.rate == 0,
              self.releaseEpoch == epoch, self.view === old else { return }
        guard let image, error == nil, image.size.width > 0,
              let pixels = image.cgImage(forProposedRect: nil, context: nil, hints: nil),
              pixels.width > 0, pixels.height > 0 else {
          NSLog("deskworlds: retained-frame capture failed; keeping paused page")
          return
        }
        guard let bitmap = self.boundedBitmap(pixels) else {
          NSLog("deskworlds: retained-frame allocation failed; keeping paused page")
          return
        }
        let frame = NSImage(size: size)
        frame.addRepresentation(bitmap)
        self.retainedPixels = [bitmap.pixelsWide, bitmap.pixelsHigh]
        self.retainedFrame.image = frame
        self.retainedFrame.isHidden = false
        self.discardPage()
      }
    }
  }

  private func boundedBitmap(_ pixels: CGImage) -> NSBitmapImageRep? {
    let scale = min(1, sqrt(1_800_000 / Double(pixels.width * pixels.height)))
    let width = max(1, Int(Double(pixels.width) * scale))
    let height = max(1, Int(Double(pixels.height) * scale))
    guard let context = CGContext(data: nil, width: width, height: height,
      bitsPerComponent: 8, bytesPerRow: width * 4,
      space: CGColorSpace(name: CGColorSpace.sRGB)!,
      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return nil }
    let rect = CGRect(x: 0, y: 0, width: width, height: height)
    context.setFillColor(pageBackground.cgColor)
    context.fill(rect)
    context.interpolationQuality = .high
    context.draw(pixels, in: rect)
    guard let image = context.makeImage() else { return nil }
    return NSBitmapImageRep(cgImage: image)
  }

  private func discardPage() {
    released = true
    loaded = false
    inside = false
    NSLog("deskworlds: released hidden scene page; retained aquarium frame %@ window=%@", String(describing: retainedPixels), probeWindowID)
    let old = view
    old.stopLoading()
    old.navigationDelegate = nil
    old.removeFromSuperview()
    // Unloaded placeholder: no page, no web content process until restore() loads it.
    view = WKWebView(frame: surface.bounds, configuration: pageConfiguration)
  }

  private func restore() {
    released = false
    NSLog("deskworlds: reloading scene page after release; retaining aquarium frame window=%@", probeWindowID)
    if view.responds(to: NSSelectorFromString("setWindowOcclusionDetectionEnabled:"))
      || view.responds(to: NSSelectorFromString("_setWindowOcclusionDetectionEnabled:"))
    {
      view.setValue(false, forKey: "windowOcclusionDetectionEnabled")
    }
    view.underPageBackgroundColor = pageBackground
    view.autoresizingMask = [.width, .height]
    view.navigationDelegate = self
    surface.addSubview(view, positioned: .below, relativeTo: retainedFrame)
    view.load(URLRequest(url: sceneURL))
  }

  func setPower(_ onBattery: Bool) {''')
    source = _swap(source, '''    loaded = true
    send()
''', '''    guard !closed, message.webView === view else { return }
    if message.body as? String == "retained-frame-ready" {
      if retainedFrame.image != nil {
        retainedFrame.isHidden = true
        retainedFrame.image = nil
        retainedPixels = []
        NSLog("deskworlds: fresh aquarium frame visible window=%@", probeWindowID)
      }
      return
    }
    loaded = true
    send()
''')
    source = _swap(source, '  func probe(reason: String = "manual", eventID: String = "") {', '''  func probe(reason: String = "manual", eventID: String = "") {
    if released {
      let row: [String: Any] = ["windowID": probeWindowID, "probeReason": reason,
        "probeEventID": eventID, "pageReleased": true, "retainedFrame": retainedFrame.image != nil,
        "retainedPixels": retainedPixels, "requestedRate": rate]
      if let data = try? JSONSerialization.data(withJSONObject: row, options: [.sortedKeys]),
         let value = String(data: data, encoding: .utf8) {
        NSLog("deskworlds page state: %@", value)
      }
      return
    }''')
    source = _swap(source, '      if screen.setRate(rate) { changed = true }',
        '      if screen.setRate(rate, releasable: !awake) { changed = true }')
    source = _swap(source,
        '      let rate = still || showing < 0.15 ? 0 : showing < 0.4 ? 20 : full',
        '      let rate = still ? 0 : showing < 0.4 ? 12 : full')
    source = _swap(source,
        '  /// part of it showing, and nothing at all behind a full screen of work or a dark display.',
        '  /// part of it showing or fully covered. Stop only for Pause, Low Power or sleep.')
    # r16: the page draws 24 fps, so sampling the cursor faster only adds page calls.
    source = _swap(source, '    let wanted = min(30, applied)', '    let wanted = min(24, applied)')
    return source
