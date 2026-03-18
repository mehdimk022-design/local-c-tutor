from __future__ import annotations

from pathlib import Path

from lct.knowledge_base import detect_topics_in_source
from lct.explainer import explain_analysis_result, explain_harness_result





def print_detected_topics(source_path: str) -> None:
    try:
        source_code = Path(source_path).read_text(encoding="utf-8")
    except OSError:
        return

    topics = detect_topics_in_source(source_code)

    if not topics:
        return

    print()
    print("Notions detectees :")
    for topic in topics:
        print(f"- {topic['id']}: {topic['title']}") 

def print_check_result(result, source_path: str | None = None) -> None:
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
    print(explain_analysis_result(result, source_path=source_path))


def print_harness_result(result, source_path: str | None = None) -> None:
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
    print(explain_harness_result(result, source_path=source_path))