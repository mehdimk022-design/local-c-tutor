from __future__ import annotations

import json
from pathlib import Path

from lct.compile_run import compile_c_file, run_binary
from lct.schemas import HarnessResult, TestCase, TestCaseResult


def normalize_output(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).strip("\n")


def outputs_match(actual: str, expected: str, exact_match: bool = True) -> bool:
    actual_normalized = normalize_output(actual)
    expected_normalized = normalize_output(expected)

    if exact_match:
        return actual_normalized == expected_normalized

    return expected_normalized in actual_normalized


def load_test_cases(test_file_path: str) -> list[TestCase]:
    path = Path(test_file_path).resolve()

    data = json.loads(path.read_text(encoding="utf-8"))
    raw_cases = data.get("cases", [])

    cases: list[TestCase] = []

    for index, item in enumerate(raw_cases, start=1):
        cases.append(
            TestCase(
                name=item.get("name", f"case_{index}"),
                stdin=item.get("stdin", ""),
                expected_stdout=item.get("expected_stdout", ""),
                exact_match=item.get("exact_match", True),
            )
        )

    return cases


def run_test_harness(
    source_path: str,
    test_file_path: str,
    compiler: str = "gcc",
    timeout_seconds: float = 2.0,
) -> HarnessResult:
    compile_result = compile_c_file(source_path=source_path, compiler=compiler)

    if not compile_result.success or compile_result.output_path is None:
        return HarnessResult(
            mode="compile_error",
            message="Compilation failed before running test cases.",
            compile_result=compile_result,
            case_results=[],
            total=0,
            passed=0,
            failed=0,
            likely_logic_bug=False,
        )

    test_cases = load_test_cases(test_file_path)
    case_results: list[TestCaseResult] = []

    had_timeout = False
    had_runtime_error = False
    passed_count = 0

    for case in test_cases:
        run_result = run_binary(
            binary_path=compile_result.output_path,
            stdin_text=case.stdin,
            timeout_seconds=timeout_seconds,
        )

        failure_reason = ""

        if run_result.timed_out:
            had_timeout = True
            passed = False
            failure_reason = "timeout"
        elif not run_result.success:
            had_runtime_error = True
            passed = False
            failure_reason = "runtime_error"
        elif outputs_match(
            actual=run_result.stdout,
            expected=case.expected_stdout,
            exact_match=case.exact_match,
        ):
            passed = True
        else:
            passed = False
            failure_reason = "wrong_output"

        if passed:
            passed_count += 1

        case_results.append(
            TestCaseResult(
                name=case.name,
                stdin=case.stdin,
                expected_stdout=case.expected_stdout,
                actual_stdout=run_result.stdout,
                passed=passed,
                timed_out=run_result.timed_out,
                returncode=run_result.returncode,
                stderr=run_result.stderr,
                failure_reason=failure_reason,
            )
        )

    total = len(case_results)
    failed = total - passed_count

    if had_timeout:
        mode = "runtime_timeout"
        message = "At least one test case timed out."
        likely_logic_bug = False
    elif had_runtime_error:
        mode = "runtime_error"
        message = "At least one test case failed at runtime."
        likely_logic_bug = False
    elif failed > 0:
        mode = "logic_bug"
        message = "Program compiles and runs, but at least one output is wrong."
        likely_logic_bug = True
    else:
        mode = "tests_ok"
        message = "All test cases passed."
        likely_logic_bug = False

    return HarnessResult(
        mode=mode,
        message=message,
        compile_result=compile_result,
        case_results=case_results,
        total=total,
        passed=passed_count,
        failed=failed,
        likely_logic_bug=likely_logic_bug,
    )