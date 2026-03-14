from __future__ import annotations

import subprocess
import time
from pathlib import Path

from lct.schemas import AnalysisResult, CompileResult, RunResult


DEFAULT_TIMEOUT_SECONDS = 2.0


def compile_c_file(source_path: str, compiler: str = "gcc") -> CompileResult:
    source = Path(source_path).resolve()

    if not source.exists():
        return CompileResult(
            success=False,
            command=[compiler],
            returncode=None,
            stdout="",
            stderr=f"Source file not found: {source}",
            source_path=str(source),
            output_path=None,
        )

    build_dir = source.parent / ".lct_build"
    build_dir.mkdir(parents=True, exist_ok=True)

    output_path = build_dir / source.stem
    command = [compiler, str(source), "-o", str(output_path)]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return CompileResult(
            success=False,
            command=command,
            returncode=None,
            stdout="",
            stderr=f"Compiler not found: {compiler}",
            source_path=str(source),
            output_path=None,
        )

    success = completed.returncode == 0

    return CompileResult(
        success=success,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        source_path=str(source),
        output_path=str(output_path) if success else None,
    )


def run_binary(
    binary_path: str,
    stdin_text: str = "",
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> RunResult:
    binary = Path(binary_path).resolve()
    command = [str(binary)]

    start = time.perf_counter()

    try:
        completed = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration_ms = (time.perf_counter() - start) * 1000

        return RunResult(
            success=completed.returncode == 0,
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
            duration_ms=duration_ms,
            binary_path=str(binary),
        )

    except subprocess.TimeoutExpired as exc:
        duration_ms = (time.perf_counter() - start) * 1000

        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout.decode() if exc.stdout else "")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr.decode() if exc.stderr else "")

        return RunResult(
            success=False,
            command=command,
            returncode=None,
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
            duration_ms=duration_ms,
            binary_path=str(binary),
        )


def analyze_c_file(
    source_path: str,
    stdin_text: str = "",
    compiler: str = "gcc",
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> AnalysisResult:
    compile_result = compile_c_file(source_path=source_path, compiler=compiler)

    if not compile_result.success or compile_result.output_path is None:
        return AnalysisResult(
            mode="compile_error",
            message="Compilation failed.",
            compile_result=compile_result,
            run_result=None,
        )

    run_result = run_binary(
        binary_path=compile_result.output_path,
        stdin_text=stdin_text,
        timeout_seconds=timeout_seconds,
    )

    if run_result.timed_out:
        return AnalysisResult(
            mode="runtime_timeout",
            message="Program execution timed out.",
            compile_result=compile_result,
            run_result=run_result,
        )

    if not run_result.success:
        return AnalysisResult(
            mode="runtime_error",
            message="Program compiled but execution failed.",
            compile_result=compile_result,
            run_result=run_result,
        )

    return AnalysisResult(
        mode="runtime_ok",
        message="Compilation and execution succeeded.",
        compile_result=compile_result,
        run_result=run_result,
    )