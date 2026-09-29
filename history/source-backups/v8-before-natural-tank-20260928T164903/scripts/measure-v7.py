#!/usr/bin/env python3
"""Sample caller-attributed PIDs without reading argv, environment, or memory.

macOS libproc proc_pid_rusage(RUSAGE_INFO_V0) supplies CPU Mach ticks and
ri_phys_footprint bytes. CPU ticks are converted with mach_timebase_info.
No RSS fallback, PID discovery, GPU estimate, or UI use.
Use --output - for stdout; file outputs are exclusive (existing files refused).
Run --self-test for synthetic failure cases and a short owned-child live probe.
"""

import argparse
import ctypes
from datetime import datetime, timezone
import errno
import json
import math
import select
import subprocess
import sys
import time


class RUsageV0(ctypes.Structure):
    # SDK sys/resource.h: 16 UUID bytes followed by ten uint64_t fields.
    _fields_ = [("ri_uuid", ctypes.c_uint8 * 16)] + [
        ("ri_" + field, ctypes.c_uint64)
        for field in (
            "user_time", "system_time", "pkg_idle_wkups", "interrupt_wkups",
            "pageins", "wired_size", "resident_size", "phys_footprint",
            "proc_start_abstime", "proc_exit_abstime",
        )
    ]


class Missing(Exception):
    def __init__(self, reason, error_number=None):
        self.reason = reason
        self.error_number = error_number
        super().__init__(reason)


class MachTimebase(ctypes.Structure):
    _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]


class MacOSReader:
    """One aggregate-only, unprivileged call per PID per sample."""

    def __init__(self):
        self.unavailable = None
        self.timebase = None
        if sys.platform != "darwin":
            self.unavailable = "unsupported_platform"
            return
        try:
            self.lib = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
            self.call = self.lib.proc_pid_rusage
            # libproc.h spells the output rusage_info_t*; the buffer is a struct,
            # not a pointer-to-pointer allocation. void* preserves that ABI.
            self.call.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
            self.call.restype = ctypes.c_int
        except (OSError, AttributeError):
            self.unavailable = "libproc_unavailable"
            return
        if ctypes.sizeof(RUsageV0) != 96:
            self.unavailable = "unsupported_rusage_layout"
            return
        try:
            libsystem = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
            get_timebase = libsystem.mach_timebase_info
            get_timebase.argtypes = [ctypes.POINTER(MachTimebase)]
            get_timebase.restype = ctypes.c_int
            timebase = MachTimebase()
            if get_timebase(ctypes.byref(timebase)) or not timebase.numer or not timebase.denom:
                self.unavailable = "mach_timebase_unavailable"
                return
            self.timebase = {"numer": timebase.numer, "denom": timebase.denom}
        except (OSError, AttributeError):
            self.unavailable = "mach_timebase_unavailable"

    def read(self, pid):
        if self.unavailable:
            raise Missing(self.unavailable)
        usage = RUsageV0()
        ctypes.set_errno(0)
        if self.call(pid, 0, ctypes.byref(usage)) != 0:
            code = ctypes.get_errno()
            reason = {
                errno.ESRCH: "process_missing_or_exited",
                errno.EPERM: "permission_denied",
                errno.EACCES: "permission_denied",
                errno.ENOSYS: "api_unavailable",
                errno.EINVAL: "api_unavailable",
                errno.ENOTSUP: "api_unavailable",
            }.get(code, "api_error")
            raise Missing(reason, code)
        # libproc can also return statistics for zombies. Never count these as
        # live endpoint samples, even when the final CPU counter is available.
        if usage.ri_proc_exit_abstime:
            raise Missing("process_exited")
        if not usage.ri_proc_start_abstime:
            raise Missing("process_identity_unavailable")
        return {
            # UUID remains internal. It additionally detects a changed image.
            "identity": (usage.ri_proc_start_abstime, bytes(usage.ri_uuid)),
            "cpu_user_ns": usage.ri_user_time * self.timebase["numer"] // self.timebase["denom"],
            "cpu_system_ns": usage.ri_system_time * self.timebase["numer"] // self.timebase["denom"],
            "physical_footprint_bytes": int(usage.ri_phys_footprint),
        }


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Tracker:
    def __init__(self, reader):
        self.reader = reader
        self.identities = {}
        self.previous = {}
        self.last_counters = {}
        self.terminal = {}

    def sample(self, pid, origin_ns):
        before = time.monotonic_ns()
        row = {
            "pid": pid, "observed_at_utc": utc_now(),
            "status": "missing", "reason": None, "errno": None,
            "cpu_user_ns": None, "cpu_system_ns": None, "cpu_total_ns": None,
            "physical_footprint_bytes": None,
            "cpu_interval": {
                "elapsed_seconds": None, "cpu_seconds": None,
                "percent_one_core": None, "reason": "current_sample_missing",
            },
        }
        previous = self.previous.get(pid)
        try:
            if pid in self.terminal:
                raise Missing(self.terminal[pid])
            value = self.reader.read(pid)
            identity = value["identity"]
            if pid in self.identities and identity != self.identities[pid]:
                raise Missing("process_identity_changed")
            self.identities.setdefault(pid, identity)
            counters = (value["cpu_user_ns"], value["cpu_system_ns"])
            last = self.last_counters.get(pid)
            if last and any(new < old for new, old in zip(counters, last)):
                raise Missing("cpu_counter_reset")
            self.last_counters[pid] = counters
            row.update({key: value[key] for key in (
                "cpu_user_ns", "cpu_system_ns", "physical_footprint_bytes"
            )})
            row.update(status="ok", cpu_total_ns=sum(counters))
        except Missing as error:
            row["reason"], row["errno"] = error.reason, error.error_number
            if error.reason in {
                "process_missing_or_exited", "process_exited",
                "process_identity_changed", "cpu_counter_reset",
            }:
                self.terminal[pid] = error.reason
            elif pid not in self.identities:
                # Do not adopt a later process when the originally supplied PID
                # could not be anchored at baseline (e.g. initial access denial).
                self.terminal[pid] = "baseline_identity_unavailable"
        after = time.monotonic_ns()
        # Each PID has its own actual observation midpoint and call duration.
        midpoint = (before + after) // 2
        row["elapsed_seconds"] = (midpoint - origin_ns) / 1e9
        row["read_duration_seconds"] = (after - before) / 1e9
        if row["status"] == "ok":
            if previous and previous["status"] == "ok":
                elapsed = row["elapsed_seconds"] - previous["elapsed_seconds"]
                cpu_seconds = (row["cpu_total_ns"] - previous["cpu_total_ns"]) / 1e9
                if elapsed > 0:
                    row["cpu_interval"] = {
                        "elapsed_seconds": elapsed, "cpu_seconds": cpu_seconds,
                        "percent_one_core": 100 * cpu_seconds / elapsed,
                        "reason": None,
                    }
                else:
                    row["cpu_interval"]["reason"] = "nonpositive_elapsed_time"
            else:
                row["cpu_interval"]["reason"] = (
                    "previous_sample_missing" if previous else "baseline"
                )
        self.previous[pid] = row
        return row


def summarize(rows, completed):
    valid = [row for row in rows if row["status"] == "ok"]
    reason = None
    if not completed:
        reason = "run_interrupted"
    elif len(rows) < 2:
        reason = "insufficient_samples"
    elif len(valid) != len(rows):
        reason = "missing_samples"
    start, end = (rows[0], rows[-1]) if rows else ({}, {})
    span = end.get("elapsed_seconds", 0) - start.get("elapsed_seconds", 0)
    if reason is None and span <= 0:
        reason = "nonpositive_elapsed_time"
    cpu = {
        "start_total_ns": start.get("cpu_total_ns"),
        "end_total_ns": end.get("cpu_total_ns"),
        "delta_seconds": None, "mean_percent_one_core": None, "reason": reason,
    }
    footprint = {
        "start_bytes": start.get("physical_footprint_bytes"),
        "end_bytes": end.get("physical_footprint_bytes"),
        "min_bytes": min((r["physical_footprint_bytes"] for r in valid), default=None),
        "max_bytes": max((r["physical_footprint_bytes"] for r in valid), default=None),
        "delta_bytes": None, "endpoint_bytes_per_second": None,
        "ols_bytes_per_second": None, "trend": "unknown", "reason": reason,
    }
    if reason is None:
        cpu["delta_seconds"] = (end["cpu_total_ns"] - start["cpu_total_ns"]) / 1e9
        cpu["mean_percent_one_core"] = 100 * cpu["delta_seconds"] / span
        footprint["delta_bytes"] = footprint["end_bytes"] - footprint["start_bytes"]
        footprint["endpoint_bytes_per_second"] = footprint["delta_bytes"] / span
        xs = [r["elapsed_seconds"] - start["elapsed_seconds"] for r in rows]
        ys = [r["physical_footprint_bytes"] for r in rows]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum(
            (x - mx) ** 2 for x in xs
        )
        footprint["ols_bytes_per_second"] = slope
        footprint["trend"] = "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat"
    return {
        "pid": start.get("pid"), "sample_count": len(rows),
        "valid_sample_count": len(valid), "missing_sample_count": len(rows) - len(valid),
        "missing_reasons": sorted({r["reason"] for r in rows if r["reason"]}),
        "complete": reason is None, "observed_span_seconds": span,
        "start_elapsed_seconds": start.get("elapsed_seconds"),
        "end_elapsed_seconds": end.get("elapsed_seconds"),
        "cpu": cpu, "physical_footprint": footprint,
    }


def measure(pids, label, duration, interval, reader=None):
    tracker = Tracker(reader if reader is not None else MacOSReader())
    started_at = utc_now()
    origin = time.monotonic_ns()
    scheduled = 0.0
    samples = []
    completed = False
    try:
        while True:
            wait_seconds = scheduled - (time.monotonic_ns() - origin) / 1e9
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            sample_start = (time.monotonic_ns() - origin) / 1e9
            rows = [tracker.sample(pid, origin) for pid in pids]
            samples.append({
                "scheduled_elapsed_seconds": scheduled,
                "elapsed_seconds": sample_start,
                "sampling_lag_seconds": max(0.0, sample_start - scheduled),
                "processes": rows,
            })
            if scheduled >= duration:
                completed = True
                break
            # Skip missed ticks rather than producing catch-up bursts. Always
            # request one final sample at duration, even for interval > duration.
            elapsed = (time.monotonic_ns() - origin) / 1e9
            scheduled = min(duration, (math.floor(elapsed / interval) + 1) * interval)
    except KeyboardInterrupt:
        pass
    summaries = [summarize([s["processes"][i] for s in samples], completed)
                 for i in range(len(pids))]
    for pid, summary in zip(pids, summaries):
        summary["pid"] = pid
    return {
        "schema_version": 1, "label": label, "pids": pids,
        "requested_duration_seconds": duration, "requested_interval_seconds": interval,
        "started_at_utc": started_at, "ended_at_utc": utc_now(),
        "actual_duration_seconds": (time.monotonic_ns() - origin) / 1e9,
        "completed": completed,
        "backend": "libproc.proc_pid_rusage/RUSAGE_INFO_V0",
        "cpu_definition": "delta(ri_user_time + ri_system_time) after Mach ticks to ns conversion; 100% = one core",
        "mach_timebase": getattr(tracker.reader, "timebase", None),
        "memory_definition": "per-PID ri_phys_footprint bytes; not RSS; no cross-PID memory sum",
        "attribution": "caller-supplied PIDs only; no automatic discovery or replacement",
        "gpu": {"status": "unknown", "value": None, "reason": "not_measured"},
        "notes": [
            "No argv, environment, paths, memory contents, or raw command output are collected.",
            "CPU covers each specified process only, not descendants or GPU work.",
            "Missing observations invalidate full-window deltas and trends; they are not zero.",
            "Missed scheduled ticks are skipped; actual timestamps and sampling lag are recorded.",
            "An OLS footprint slope is descriptive, not proof of a leak or a significance test.",
            "A same-PID exec of the same image with continuous counters may be undetectable.",
            "Unknown new helper/restart PIDs must be re-attributed by the caller in a new run.",
            "A PID without a valid initial identity stays missing for the entire run.",
        ],
        "summary": {"processes": summaries}, "samples": samples,
    }


def positive_seconds(value):
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a finite positive number") from None
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return number


def parse_pids(tokens):
    try:
        pids = [int(value) for token in tokens for value in token.split(",")]
    except ValueError:
        raise ValueError("PIDs must be positive integers, separated by spaces or commas") from None
    if not pids or any(pid <= 0 or pid > 2147483647 for pid in pids):
        raise ValueError("PIDs must be in 1..2147483647")
    if len(set(pids)) != len(pids):
        raise ValueError("duplicate PIDs are not allowed")
    return pids


def self_test():
    """No files: synthetic edge cases plus one short, owned Python workload."""
    checks = []

    class SequenceReader:
        def __init__(self, values):
            self.values = iter(values)

        def read(self, pid):
            value = next(self.values)
            if isinstance(value, Missing):
                raise value
            return value

    def value(cpu, footprint=100, identity=(1, b"a")):
        return {"identity": identity, "cpu_user_ns": cpu, "cpu_system_ns": 0,
                "physical_footprint_bytes": footprint}

    def sequence(values, count=None):
        tracker = Tracker(SequenceReader(values))
        return [tracker.sample(123, time.monotonic_ns() - 1000000000)
                for _ in range(count or len(values))]

    rows = sequence([value(0, 100), value(100000000, 120), value(300000000, 140)])
    for i, row in enumerate(rows):
        row["elapsed_seconds"] = float(i)
    summary = summarize(rows, True)
    assert summary["cpu"]["delta_seconds"] == 0.3
    assert summary["cpu"]["mean_percent_one_core"] == 15.0
    assert summary["physical_footprint"]["ols_bytes_per_second"] == 20.0
    checks.append("known CPU delta and footprint slope")

    rows = sequence([value(10), Missing("permission_denied", errno.EPERM), value(20)])
    assert rows[1]["physical_footprint_bytes"] is None
    assert rows[1]["errno"] == errno.EPERM
    assert rows[2]["cpu_interval"]["reason"] == "previous_sample_missing"
    assert summarize(rows, True)["cpu"]["delta_seconds"] is None
    assert summarize(rows, True)["physical_footprint"]["ols_bytes_per_second"] is None
    checks.append("permission failure remains null; no gap bridging")

    rows = sequence([Missing("permission_denied", errno.EPERM)], 2)
    assert rows[1]["reason"] == "baseline_identity_unavailable"
    checks.append("unknown baseline cannot adopt a later process")

    for error in ("process_missing_or_exited", "process_exited"):
        rows = sequence([value(10), Missing(error)], 3)
        assert rows[-1]["status"] == "missing" and rows[-1]["reason"] == error
        assert summarize(rows, True)["physical_footprint"]["trend"] == "unknown"
        checks.append(error + " stays missing")
    for name, replacement in (
        ("PID reuse", value(20, identity=(2, b"a"))),
        ("exec image change", value(20, identity=(1, b"b"))),
        ("counter reset", value(5)),
    ):
        rows = sequence([value(10), replacement], 3)
        assert rows[1]["status"] == rows[2]["status"] == "missing"
        assert rows[1]["cpu_total_ns"] is None
        checks.append(name + " stays missing")
    rows = sequence([Missing("unsupported_platform"), Missing("api_error", 1234)])
    assert summarize(rows, True)["physical_footprint"]["start_bytes"] is None
    assert summarize([], False)["cpu"]["reason"] == "run_interrupted"
    checks.append("unavailable API and interrupted run remain unknown")
    assert parse_pids(["1,2", "3"]) == [1, 2, 3]
    for tokens in (["0"], ["-1"], ["1,1"], ["2147483648"], ["x"], ["1,"]):
        try:
            parse_pids(tokens)
        except ValueError:
            continue
        raise AssertionError("invalid PID accepted")
    for token in ("0", "-1", "nan", "inf", "x"):
        try:
            positive_seconds(token)
        except argparse.ArgumentTypeError:
            continue
        raise AssertionError("invalid seconds accepted")
    checks.append("invalid and duplicate PID / duration rejection")

    # This child's stdout contains readiness and CPU aggregates only. It waits
    # for the first libproc baseline before allocating and doing bounded work.
    child_code = '''
import json, select, sys, time
print("ready", flush=True)
if not select.select([sys.stdin], [], [], 5)[0]: sys.exit(1)
sys.stdin.readline()
start_cpu = time.process_time_ns()
start = time.monotonic()
blocks = []
while time.monotonic() - start < 0.65:
    if len(blocks) < min(4, 1 + int((time.monotonic() - start) / 0.15)):
        block = bytearray(4 * 1024 * 1024)
        for i in range(0, len(block), 4096): block[i] = 1
        blocks.append(block)
    sum(i * i for i in range(1000))
print(json.dumps({"cpu_ns": time.process_time_ns() - start_cpu}), flush=True)
if select.select([sys.stdin], [], [], 5)[0]: sys.stdin.readline()
'''
    reader = MacOSReader()
    if reader.unavailable:
        raise Missing(reader.unavailable)
    child = subprocess.Popen(
        [sys.executable, "-B", "-c", child_code], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    try:
        assert select.select([child.stdout], [], [], 5)[0], "child readiness timeout"
        assert child.stdout.readline().strip() == "ready"

        class StartReader:
            started = False
            timebase = reader.timebase

            def read(self, pid):
                result = reader.read(pid)
                if not self.started:
                    child.stdin.write("start\n")
                    child.stdin.flush()
                    self.started = True
                return result

        report = measure([child.pid], "self-test-owned-child", 0.9, 0.1, StartReader())
        assert select.select([child.stdout], [], [], 5)[0], "child result timeout"
        child_cpu = json.loads(child.stdout.readline())["cpu_ns"] / 1e9
        result = report["summary"]["processes"][0]
        assert result["complete"], result["missing_reasons"]
        assert abs(result["cpu"]["delta_seconds"] - child_cpu) < 0.05, "live_cpu_timebase_mismatch"
        assert result["physical_footprint"]["delta_bytes"] >= 8 * 1024 * 1024, "live_footprint_growth_missing"
        assert result["physical_footprint"]["trend"] == "increasing", "live_footprint_slope_not_increasing"
        assert report["gpu"]["status"] == "unknown"
        intervals = [s["processes"][0]["cpu_interval"] for s in report["samples"][1:]]
        assert all(i["elapsed_seconds"] > 0 and i["percent_one_core"] >= 0 for i in intervals)
        assert math.isclose(sum(i["cpu_seconds"] for i in intervals), result["cpu"]["delta_seconds"])
        checks.append("live CPU agrees with child process_time_ns within 50ms")
        checks.append("live touched allocation increases physical footprint")
        child.stdin.close()
        assert child.wait(timeout=5) == 0
        exited = measure([child.pid], "self-test-exited-child", 0.02, 0.01)
        assert all(s["processes"][0]["status"] == "missing" for s in exited["samples"])
        assert exited["summary"]["processes"][0]["cpu"]["delta_seconds"] is None
        checks.append("live exited owned PID is missing")
        return {"self_test": "passed", "checks": checks, "live": {
            "pid": child.pid, "sample_count": result["sample_count"],
            "mach_timebase": report["mach_timebase"],
            "child_cpu_seconds": child_cpu, "cpu": result["cpu"],
            "physical_footprint": result["physical_footprint"], "gpu": report["gpu"],
        }}
    finally:
        if not child.stdin.closed:
            child.stdin.close()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.terminate()  # Only the exact child created above.
            child.wait(timeout=5)
        child.stdout.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="owned child and synthetic cases; stdout only")
    parser.add_argument("--pids", nargs="+", help="explicit caller-attributed PID list (spaces or commas)")
    parser.add_argument("--label", help="non-sensitive name of the manually established state")
    parser.add_argument("--duration", type=positive_seconds, help="requested elapsed seconds")
    parser.add_argument("--interval", type=positive_seconds, help="requested sample interval in seconds")
    parser.add_argument("--output", help="new JSON path, or - for stdout; existing paths refused")
    args = parser.parse_args(argv)
    if args.self_test:
        if any(getattr(args, field) is not None for field in ("pids", "label", "duration", "interval", "output")):
            parser.error("--self-test is standalone and writes only to stdout")
        try:
            report = self_test()
        except (AssertionError, Missing, OSError, subprocess.SubprocessError) as error:
            reason = str(error) if isinstance(error, (AssertionError, Missing)) else type(error).__name__
            print(json.dumps({"self_test": "failed", "reason": reason or type(error).__name__}))
            return 1
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0
    for field in ("pids", "label", "duration", "interval", "output"):
        if getattr(args, field) is None:
            parser.error("--" + field + " is required unless --self-test is used")
    if not args.label.strip() or len(args.label) > 160 or any(ord(c) < 32 for c in args.label):
        parser.error("--label must be 1..160 characters without control characters")
    try:
        pids = parse_pids(args.pids)
    except ValueError as error:
        parser.error(str(error))
    output = sys.stdout
    if args.output != "-":
        try:
            output = open(args.output, "x", encoding="utf-8")
        except OSError as error:
            parser.error("cannot create a new output file (errno " + str(error.errno) + ")")
    try:
        report = measure(pids, args.label, args.duration, args.interval)
        json.dump(report, output, indent=2, allow_nan=False)
        output.write("\n")
    finally:
        if output is not sys.stdout:
            output.close()
    return 0 if report["completed"] else 130


if __name__ == "__main__":
    sys.exit(main())
