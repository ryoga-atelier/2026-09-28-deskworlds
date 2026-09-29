"""A passive SIGUSR2 probe: no frame-rate override, no capture, no UI changes."""
def apply_native_probe(source):
    changes = [
        ('  private var snapshots: DispatchSourceSignal?',
         '  private var snapshots: DispatchSourceSignal?\n  private var telemetry: DispatchSourceSignal?'),
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
          stats: typeof sceneStats === 'function' ? sceneStats() : null,'''),
    ]
    for before, after in changes:
        if source.count(before) != 1:
            raise RuntimeError('Native diagnostic anchor changed: ' + before)
        source = source.replace(before, after)
    return source
