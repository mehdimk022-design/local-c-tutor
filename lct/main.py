
from __future__ import annotations

import argparse
import json

from lct.compile_run import analyze_c_file
from lct.test_harness import run_test_harness
from lct.presenter import print_check_result, print_detected_topics, print_harness_result



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Local CTutor",
        description="Local CTutor (LCT) - local offline-first tutor for simple C exercises.",
    )

    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser(
        "check",
        help="Compile and run a C file.",
    )
    check_parser.add_argument("source", help="Path to the C source file.")
    check_parser.add_argument(
        "--stdin",
        default="",
        help="Optional text passed to standard input.",
    )
    check_parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Execution timeout in seconds.",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON output.",
    )

    test_parser = subparsers.add_parser(
        "test",
        help="Run multiple test cases against a C file.",
    )
    test_parser.add_argument("source", help="Path to the C source file.")
    test_parser.add_argument("tests", help="Path to the JSON test case file.")
    test_parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Execution timeout in seconds.",
    )
    test_parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON output.",
    )

    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        print("Local CTutor (LCT) is ready.")
        return

    if args.command == "check":
        handle_check_command(args)
        return

    if args.command == "test":
        handle_test_command(args)
        return

    parser.error("Unknown command.")


def handle_check_command(args) -> None:
    result = analyze_c_file(
        source_path=args.source,
        stdin_text=args.stdin,
        timeout_seconds=args.timeout,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return

    print_check_result(result, source_path=args.source)
    print_detected_topics(args.source)


def handle_test_command(args) -> None:
    result = run_test_harness(
        source_path=args.source,
        test_file_path=args.tests,
        timeout_seconds=args.timeout,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return

    print_harness_result(result, source_path=args.source)
    print_detected_topics(args.source)

if __name__ == "__main__":
    main()