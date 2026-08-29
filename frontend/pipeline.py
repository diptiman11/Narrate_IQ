from pathlib import Path
import subprocess
import sys

from src.pipeline import (
    reset_processed_outputs,
    validate_core_dataset,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


PIPELINE_MODULES = [
    "src.kpi.engine",
    "src.anomaly.engine",
    "src.drivers.engine",
    "src.attribution.engine",
    "src.confidence.engine",
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

    try:
        validate_core_dataset()
    except FileNotFoundError as exc:
        return False, [str(exc)]

    # IMPORTANT:
    # Remove stale results before processing the
    # newly uploaded dataset.
    reset_processed_outputs()

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
                f"(exit code {process.returncode})."
            )

            return False, logs

    return True, logs