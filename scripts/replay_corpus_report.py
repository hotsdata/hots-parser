#!/usr/bin/env python3
import argparse
import contextlib
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.support.normalization import parse_replay_payloads


def _default_corpus_dir():
    value = os.environ.get("HOTSDATA_REPLAY_CORPUS_DIR")
    return Path(value) if value else None


def _summarize(path, payloads):
    replayinfo = payloads["replayinfo"]
    return {
        "file": path.name,
        "size": path.stat().st_size,
        "replayId": replayinfo["id"],
        "mapName": replayinfo["mapName"],
        "gameVersion": replayinfo["gameVersion"],
        "players": len(payloads["players"]),
        "generalstats": len(payloads["generalstats"]),
        "teamgeneralstats": len(payloads["teamgeneralstats"]),
        "timelineEvents": len(payloads["timeline"].get("tl", [])),
    }


def _build_report(files, progress_every=None):
    successes = []
    failures = []

    for index, replay_path in enumerate(files, start=1):
        if progress_every and (index == 1 or index % progress_every == 0):
            print("Parsing %d/%d: %s" % (index, len(files), replay_path.name), file=sys.stderr, flush=True)

        parser_output = io.StringIO()
        try:
            with contextlib.redirect_stdout(parser_output):
                payloads = parse_replay_payloads(replay_path)
            successes.append(_summarize(replay_path, payloads))
        except SystemExit as exc:
            message = str(exc) or parser_output.getvalue().strip()
            failures.append(
                {
                    "file": replay_path.name,
                    "size": replay_path.stat().st_size,
                    "errorType": "SystemExit",
                    "error": message,
                }
            )
        except Exception as exc:
            failures.append(
                {
                    "file": replay_path.name,
                    "size": replay_path.stat().st_size,
                    "errorType": type(exc).__name__,
                    "error": str(exc),
                }
            )

    return {
        "total": len(files),
        "passed": len(successes),
        "failed": len(failures),
        "maps": dict(sorted(Counter(row["mapName"] for row in successes).items())),
        "builds": dict(sorted(Counter(str(row["gameVersion"]) for row in successes).items())),
        "successes": successes,
        "failures": failures,
    }


def _print_text_report(report, max_failures):
    print("Replay corpus: %d total, %d passed, %d failed" % (report["total"], report["passed"], report["failed"]))

    print("\nMaps:")
    for map_name, count in report["maps"].items():
        print("  %s: %d" % (map_name, count))

    print("\nBuilds:")
    for build, count in report["builds"].items():
        print("  %s: %d" % (build, count))

    if report["failures"]:
        print("\nFailures:")
        for row in report["failures"][:max_failures]:
            print("  %s: %s: %s" % (row["file"], row["errorType"], row["error"]))
        if len(report["failures"]) > max_failures:
            print("  ... %d more failures omitted" % (len(report["failures"]) - max_failures))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus_dir", nargs="?", type=Path, default=_default_corpus_dir())
    parser.add_argument("--limit", type=int, default=None, help="only parse the first N replay files by filename")
    parser.add_argument("--max-failures", type=int, default=20, help="maximum failures to print in text output")
    parser.add_argument(
        "--progress-every", type=int, default=None, help="print progress to stderr every N replay files"
    )
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    parser.add_argument("--fail-on-error", action="store_true", help="exit non-zero if any replay fails to parse")
    args = parser.parse_args(argv)

    if args.corpus_dir is None:
        raise SystemExit("Provide a corpus directory or set HOTSDATA_REPLAY_CORPUS_DIR")
    if not args.corpus_dir.exists():
        raise SystemExit("Replay corpus directory not found: %s" % args.corpus_dir)

    files = sorted(args.corpus_dir.glob("*.StormReplay"))
    if args.limit is not None:
        files = files[: args.limit]

    report = _build_report(files, progress_every=args.progress_every)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_text_report(report, args.max_failures)

    if args.fail_on_error and report["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
