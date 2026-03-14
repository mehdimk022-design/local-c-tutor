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
