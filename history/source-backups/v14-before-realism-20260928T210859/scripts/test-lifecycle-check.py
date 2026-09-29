"""Guard against falsely calling a restart, lock, or stale sample a pass."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('check', Path(__file__).with_name('lifecycle-check.py'))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def state(asid='10', pid='7'):
    return {'at': 'test', 'preferences': {'world': 'riverscape', 'paused': '0'},
            'job': {'asid': asid, 'pid': pid, 'state': 'running', 'loaded': True,
                    'run_at_load': True, 'agent_program': '/app', 'expected_program': '/app'}}


def event(name, eid, pid='7', moving=True):
    rows = [{'kind': 'lifecycle', 'pid': pid, 'data': {'event': name, 'eventID': eid}}]
    for ms in (2000, 8000):
        n = ms if moving else 10
        rows.append({'kind': 'page state', 'pid': pid, 'data': {
            'probeEventID': eid, 'windowID': 'screen1', 'observedAtMs': ms,
            'stats': {'renderedFrames': n, 'simulationTime': n,
                      'livingWater': {'time': n}, 'habitat': {'motionTime': n},
                      'loop': {'running': moving}, 'food': {'dropped': 0}}}})
    return rows


class Verification(unittest.TestCase):
    def report(self, rows, current=None):
        return check.summarize(rows, {'machine': state()}, current or state())['checks']

    def test_restart_is_not_login(self):
        r = self.report(event('launch', 'a', pid='8'), state(pid='8'))
        self.assertEqual(r['startup_rendering']['status'], 'observed')
        self.assertEqual(r['relogin_autostart']['status'], 'pending')

    def test_changed_session_needs_saved_prefs_and_frames(self):
        rows = event('launch', 'a', pid='8')
        current = state(asid='11', pid='8')
        self.assertEqual(self.report(rows, current)['relogin_autostart']['status'], 'observed')
        current['preferences']['paused'] = '1'
        self.assertEqual(self.report(rows, current)['relogin_autostart']['status'], 'pending')

    def test_screen_unlock_is_not_sleep(self):
        rows = event('display-or-session-inactive', 'a') + event('display-or-session-active', 'b')
        self.assertEqual(self.report(rows)['system_sleep_wake']['status'], 'pending')

    def test_real_sleep_needs_matching_wake_and_animation(self):
        rows = event('system-will-sleep', 'a')
        self.assertEqual(self.report(rows)['system_sleep_wake']['status'], 'pending')
        rows += event('system-did-wake', 'b', moving=False)
        self.assertEqual(self.report(rows)['system_sleep_wake']['status'], 'pending')
        rows += event('display-or-session-active', 'c')
        self.assertEqual(self.report(rows)['system_sleep_wake']['status'], 'observed')

    def test_pause_requires_native_action_and_frozen_samples(self):
        rows = event('menu-pause', 'a', moving=False) + event('menu-resume', 'b')
        self.assertEqual(self.report(rows)['native_pause_resume']['status'], 'observed')
        rows = event('menu-pause', 'a') + event('menu-resume', 'b')
        self.assertEqual(self.report(rows)['native_pause_resume']['status'], 'pending')

    def test_stale_samples_from_another_process_do_not_pass(self):
        rows = event('menu-pause', 'a', moving=False) + event('menu-resume', 'b')
        for row in rows:
            if row['kind'] == 'page state':
                row['pid'] = 'other'
        self.assertEqual(self.report(rows)['native_pause_resume']['status'], 'pending')

    def test_dock_and_drag_are_never_inferred_from_app_logs(self):
        checks = self.report(event('launch', 'a'))
        self.assertEqual(checks['dock']['status'], 'pending')
        self.assertEqual(checks['desktop_drag']['status'], 'pending')

    def test_quit_requires_termination(self):
        rows = event('menu-quit', 'a')
        self.assertEqual(self.report(rows)['native_quit']['status'], 'pending')
        rows += event('application-will-terminate', 'b')
        self.assertEqual(self.report(rows)['native_quit']['status'], 'observed')


if __name__ == '__main__':
    unittest.main()
