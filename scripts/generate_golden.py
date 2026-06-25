#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.support.normalization import parse_replay_payloads, write_payloads


DEFAULT_REPLAY = Path("tests/fixtures/replays/local/2026-06-24_15-49-48_Silver_City.StormReplay")
DEFAULT_OUTPUT = Path("tests/golden/local/silver_city_2026-06-24")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", type=Path, default=DEFAULT_REPLAY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--update", action="store_true", help="overwrite an existing golden directory")
    args = parser.parse_args(argv)

    if not args.replay.exists():
        raise SystemExit("Replay fixture not found: %s" % args.replay)
    if args.output_dir.exists() and any(args.output_dir.iterdir()) and not args.update:
        raise SystemExit("Golden output exists; rerun with --update to overwrite: %s" % args.output_dir)

    payloads = parse_replay_payloads(args.replay)
    write_payloads(payloads, args.output_dir)

    print("wrote %d golden payloads to %s" % (len(payloads), args.output_dir))


if __name__ == "__main__":
    main()
