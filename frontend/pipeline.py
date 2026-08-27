from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)


PIPELINE_MODULES = [
    "src.drilldown.sales",
    "src.context.events",
    "src.evidence.validator",
    "src.learning.history",
    "src.learning.engine",
    "src.hypotheses.engine",
    "src.recommendations.engine",
    "src.rootcause.engine",
    "src.experiments.engine",
    "src.decision.engine",
    "src.llm.narrative",
]


def run_pipeline() -> tuple[bool, list[str]]:

    logs = []

    for module in PIPELINE_MODULES:

        process = subprocess.run(
            [
                sys.executable,
                "-m",
                module,
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        output = (
            process.stdout
            + "\n"
            + process.stderr
        ).strip()

        logs.append(
            f"=== {module} ===\n{output}"
        )

        if process.returncode != 0:

            logs.append(
                f"\nPipeline stopped at "
                f"{module} "
                f"(exit code "
                f"{process.returncode})."
            )

            return False, logs

    return True, logs