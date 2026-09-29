"""Passive frame and lifecycle diagnostics; no UI actions or forced rendering."""
def apply_native_probe(source):
    changes = [
        ('final class Wallpaper: NSObject, WKNavigationDelegate, WKScriptMessageHandler {',
         'final class Wallpaper: NSObject, WKNavigationDelegate, WKScriptMessageHandler {\n  private let probeWindowID = UUID().uuidString'),
        ('  private var snapshots: DispatchSourceSignal?',
         '  private var snapshots: DispatchSourceSignal?\n  private var telemetry: DispatchSourceSignal?\n  private var probeEpoch = 0'),
        ('    snapshots?.resume()', '''    snapshots?.resume()
    signal(SIGUSR2, SIG_IGN)
    telemetry = DispatchSource.makeSignalSource(signal: SIGUSR2, queue: .main)
    telemetry?.setEventHandler { [weak self] in
      self?.screens.forEach { $0.probe() }
    }
    telemetry?.resume()'''),
        ('          pointers: window.scenePointerCount,',
         '''          pointers: window.scenePointerCount,
          observedAtMs: performance.now(),
          stats: typeof sceneStats === 'function' ? sceneStats() : null,
          probeReason: "\\(reason)",
          probeEventID: "\\(eventID)",
          windowID: "\\(probeWindowID)",'''),
        ('  func probe() {', '  func probe(reason: String = "manual", eventID: String = "") {'),
        ('    addMenu()\n', '''    addMenu()
    auditFrames("launch")
'''),
        ('    let workspace = NSWorkspace.shared.notificationCenter', '''    let workspace = NSWorkspace.shared.notificationCenter
    workspace.addObserver(forName: NSWorkspace.willSleepNotification, object: nil, queue: .main) { [weak self] _ in
      self?.audit("system-will-sleep")
    }
    workspace.addObserver(forName: NSWorkspace.didWakeNotification, object: nil, queue: .main) { [weak self] _ in
      self?.auditFrames("system-did-wake")
    }
    workspace.addObserver(forName: NSWorkspace.willPowerOffNotification, object: nil, queue: .main) { [weak self] _ in
      self?.audit("session-will-power-off")
    }
    center.addObserver(forName: NSApplication.willTerminateNotification, object: nil, queue: .main) { [weak self] _ in
      self?.audit("application-will-terminate")
    }'''),
        ('        self?.awake = value\n        self?.applyRate()', '''        self?.awake = value
        self?.applyRate()
        if value { self?.auditFrames("display-or-session-active") }
        else { self?.audit("display-or-session-inactive") }'''),
        ('    feed.isEnabled = applied > 0', '''    feed.isEnabled = applied > 0
    audit("menu-open")'''),
        ('    for screen in screens { screen.feed() }', '''    for screen in screens { screen.feed() }
    auditFrames("menu-feed")'''),
        ('    UserDefaults.standard.set(stopped, forKey: "paused")\n    applyRate()', '''    UserDefaults.standard.set(stopped, forKey: "paused")
    applyRate()
    auditFrames(stopped ? "menu-pause" : "menu-resume")'''),
        ('    NSApp.terminate(nil)', '''    audit("menu-quit")
    NSApp.terminate(nil)'''),
        ('  // MARK: - The menu bar', '''  // Passive, event-triggered samples. No synthetic sleep/login/menu actions.
  @discardableResult private func audit(_ event: String) -> String {
    let eventID = UUID().uuidString
    let row: [String: Any] = [
      "eventID": eventID,
      "event": event, "at": ISO8601DateFormatter().string(from: Date()),
      "pid": ProcessInfo.processInfo.processIdentifier,
      "uptime": ProcessInfo.processInfo.systemUptime,
      "world": world.rawValue, "paused": stopped, "awake": awake,
      "requestedRate": applied, "menuVisible": status?.isVisible ?? false
    ]
    if let data = try? JSONSerialization.data(withJSONObject: row, options: [.sortedKeys]),
       let value = String(data: data, encoding: .utf8) {
      NSLog("deskworlds lifecycle: %@", value)
    }
    return eventID
  }

  private func auditFrames(_ event: String) {
    let eventID = audit(event)
    probeEpoch += 1
    let epoch = probeEpoch
    for delay in [0.5, 2.0, 8.0, 20.0] {
      DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
        guard let self = self, self.probeEpoch == epoch else { return }
        self.screens.forEach { $0.probe(reason: event, eventID: eventID) }
      }
    }
  }

  // MARK: - The menu bar'''),
    ]
    for before, after in changes:
        expected = 2 if before == '        self?.awake = value\n        self?.applyRate()' else 1
        if source.count(before) != expected:
            raise RuntimeError('Native diagnostic anchor changed: ' + before)
        source = source.replace(before, after)
    return source
