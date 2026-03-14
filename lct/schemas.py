from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class CompileResult:
    success: bool
    command: list[str]
    returncode: Optional[int]
    stdout: str
    stderr: str
    source_path: str
    output_path: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    success: bool
    command: list[str]
    returncode: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool
    duration_ms: float
    binary_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    mode: str
    message: str
    compile_result: CompileResult
    run_result: Optional[RunResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "message": self.message,
            "compile_result": self.compile_result.to_dict(),
            "run_result": None if self.run_result is None else self.run_result.to_dict(),
        }


@dataclass
class TestCase:
    name: str
    stdin: str
    expected_stdout: str
    exact_match: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TestCaseResult:
    name: str
    stdin: str
    expected_stdout: str
    actual_stdout: str
    passed: bool
    timed_out: bool
    returncode: Optional[int]
    stderr: str
    failure_reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HarnessResult:
    mode: str
    message: str
    compile_result: CompileResult
    case_results: list[TestCaseResult]
    total: int
    passed: int
    failed: int
    likely_logic_bug: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "message": self.message,
            "compile_result": self.compile_result.to_dict(),
            "case_results": [case.to_dict() for case in self.case_results],
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "likely_logic_bug": self.likely_logic_bug,
        }




