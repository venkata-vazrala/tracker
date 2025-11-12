from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Run, StageResult, SubStageResult, Stage, SubStage


@receiver(post_save, sender=Run)
def create_stage_and_substage_results(sender, instance: Run, created: bool, **kwargs):
    """On Run creation, create StageResult for each Stage in the pipeline and corresponding SubStageResult.

    This ensures each run has an initial set of result rows that teams/automations can update.
    """
    if not created:
        return

    pipeline = instance.pipeline
    stages = pipeline.stages.all()
    for stage in stages:
        sr, _ = StageResult.objects.get_or_create(run=instance, stage=stage)
        # create substageresults
        substages = stage.substages.all()
        for sub in substages:
            SubStageResult.objects.get_or_create(stage_result=sr, substage=sub)
