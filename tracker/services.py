from typing import Optional
from .models import Run, StageResult, SubStageResult


def calculate_run_score(run_id: int) -> float:
    """Calculate the overall weighted score for a Run.

    Algorithm:
    - For each StageResult in the run, read stage.weight (weight within pipeline) and
      the StageResult.completion_percent (0..100).
    - For each stage, contribution = (stage.weight) * (stage_result.completion_percent / 100.0)
    - Sum contributions. If pipeline stage weights don't sum to 1.0, normalize by total stage weight.

    Returns the final score as a float in 0.0 .. 1.0 (not percent). Caller may multiply by 100.
    """
    try:
        run = Run.objects.get(id=run_id)
    except Run.DoesNotExist:
        raise ValueError(f"Run with id={run_id} does not exist")

    stage_results = StageResult.objects.filter(run=run).select_related('stage')
    if not stage_results.exists():
        return 0.0

    total_stage_weight = sum([sr.stage.weight for sr in stage_results])
    if total_stage_weight <= 0:
        return 0.0

    total = 0.0
    for sr in stage_results:
        # sr.completion_percent is expected as 0..100
        stage_weight = sr.stage.weight
        completion_frac = (sr.completion_percent or 0.0) / 100.0
        total += stage_weight * completion_frac

    # Normalize in case weights don't sum to 1.0
    normalized = total / total_stage_weight
    return normalized
