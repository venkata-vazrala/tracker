from django.db import models
from django.utils import timezone


class Organization(models.Model):
    """Top-level organization."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Team(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.organization.name} / {self.name}"


class Project(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    repo_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.team} / {self.name}"


class Pipeline(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipelines')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, default='v1.0')

    def __str__(self) -> str:
        return f"{self.project} / {self.name}"


class Stage(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=200)
    weight = models.FloatField(default=0.0)
    order = models.IntegerField(default=0)
    definition_of_done = models.TextField(blank=True)
    auto_check_endpoint = models.CharField(max_length=500, blank=True)
    dod_type = models.CharField(max_length=10, choices=(('manual', 'Manual'), ('auto', 'Auto')), default='manual')

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f"{self.pipeline} / {self.order} - {self.name}"


class SubStage(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='substages')
    name = models.CharField(max_length=200)
    weight = models.FloatField(default=0.0)
    order = models.IntegerField(default=0)
    definition_of_done = models.TextField(blank=True)
    auto_check_endpoint = models.CharField(max_length=500, blank=True)
    dod_type = models.CharField(max_length=10, choices=(('manual', 'Manual'), ('auto', 'Auto')), default='manual')

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f"{self.stage} / {self.order} - {self.name}"


class Run(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='runs')
    triggered_by = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='running')

    class Meta:
        ordering = ['-start_time']

    def __str__(self) -> str:
        return f"Run {self.id} - {self.pipeline} - {self.status}"

    @property
    def overall_score(self) -> float:
        """Compute the overall weighted score dynamically by aggregating StageResults.
        Returns a float in 0.0 to 1.0 range (not percent).
        """
        stage_results = self.stage_results.all()
        if not stage_results:
            return 0.0
        
        total_stage_weight = sum([sr.stage.weight for sr in stage_results])
        if total_stage_weight <= 0:
            return 0.0
        
        total = 0.0
        for sr in stage_results:
            # sr.completion_percent is 0..100, so divide by 100
            completion_frac = (sr.completion_percent or 0.0) / 100.0
            total += sr.stage.weight * completion_frac
        
        # Normalize by total stage weight
        return total / total_stage_weight


class StageResult(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='stage_results')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    completion_percent = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('run', 'stage')

    def __str__(self) -> str:
        return f"Run {self.run.id} - StageResult {self.stage.name} - {self.completion_percent}%"


class SubStageResult(models.Model):
    stage_result = models.ForeignKey(StageResult, on_delete=models.CASCADE, related_name='substage_results')
    substage = models.ForeignKey(SubStage, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    completion_percent = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('stage_result', 'substage')

    def __str__(self) -> str:
        return f"Run {self.stage_result.run.id} - SubStage {self.substage.name} - {self.completion_percent}%"
