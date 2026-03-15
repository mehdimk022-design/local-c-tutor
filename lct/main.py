from __future__ import annotations

import argparse
import json

from lct.compile_run import analyze_c_file
from lct.explainer import explain_analysis_result, explain_harness_result
from lct.test_harness import run_test_harness


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


def print_check_result(result) -> None:
    print(f"Mode: {result.mode}")
    print(f"Message: {result.message}")
    print(f"Compile success: {result.compile_result.success}")
    print(f"Compile return code: {result.compile_result.returncode}")

    if result.compile_result.stderr:
        print("Compile stderr:")
        print(result.compile_result.stderr)

    if result.run_result is not None:
        print(f"Run success: {result.run_result.success}")
        print(f"Run return code: {result.run_result.returncode}")
        print(f"Timed out: {result.run_result.timed_out}")
        print(f"Duration ms: {result.run_result.duration_ms:.2f}")

        if result.run_result.stdout:
            print("Run stdout:")
            print(result.run_result.stdout)

        if result.run_result.stderr:
            print("Run stderr:")
            print(result.run_result.stderr)

    print()
    print(explain_analysis_result(result))


def print_harness_result(result) -> None:
    print(f"Mode: {result.mode}")
    print(f"Message: {result.message}")
    print(f"Compile success: {result.compile_result.success}")
    print(f"Compile return code: {result.compile_result.returncode}")
    print(f"Total cases: {result.total}")
    print(f"Passed: {result.passed}")
    print(f"Failed: {result.failed}")
    print(f"Likely logic bug: {result.likely_logic_bug}")

    if result.compile_result.stderr:
        print("Compile stderr:")
        print(result.compile_result.stderr)

    for case in result.case_results:
        print()
        print(f"Case: {case.name}")
        print(f"Passed: {case.passed}")
        print(f"Timed out: {case.timed_out}")
        print(f"Return code: {case.returncode}")

        if case.failure_reason:
            print(f"Failure reason: {case.failure_reason}")

        if case.stdin:
            print("stdin:")
            print(case.stdin)

        print("Expected stdout:")
        print(case.expected_stdout)

        print("Actual stdout:")
        print(case.actual_stdout)

        if case.stderr:
            print("stderr:")
            print(case.stderr)

    print()
    print(explain_harness_result(result))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        print("Local CTutor (LCT) is ready.")
        return

    if args.command == "check":
        result = analyze_c_file(
            source_path=args.source,
            stdin_text=args.stdin,
            timeout_seconds=args.timeout,
        )

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
            return

        print_check_result(result)
        return

    if args.command == "test":
        result = run_test_harness(
            source_path=args.source,
            test_file_path=args.tests,
            timeout_seconds=args.timeout,
        )

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
            return

        print_harness_result(result)
        return

    parser.error("Unknown command.")


if __name__ == "__main__":
    main()