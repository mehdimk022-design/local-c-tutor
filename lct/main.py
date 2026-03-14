from __future__ import annotations

import argparse
import json

from lct.compile_run import analyze_c_file


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

    return parser


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

        return

    parser.error("Unknown command.")


if __name__ == "__main__":
    main()