import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import Pipeline, Run, StageResult, SubStageResult


class Command(BaseCommand):
    help = 'Simulate a run for a pipeline (creates a Run and random Stage/SubStage results)'

    def add_arguments(self, parser):
        parser.add_argument('pipeline_id', type=int, help='Pipeline id to simulate')
        parser.add_argument('--complete', action='store_true', help='Make all substages complete')

    def handle(self, *args, **options):
        pipeline_id = options['pipeline_id']
        complete = options['complete']
        pipeline = Pipeline.objects.filter(id=pipeline_id).first()
        if not pipeline:
            self.stderr.write(f'Pipeline id={pipeline_id} not found')
            return

        run = Run.objects.create(pipeline=pipeline, start_time=timezone.now(), status='running')
        # StageResults and SubStageResults are created by signals
        run.refresh_from_db()

        for sr in run.stage_results.all():
            for ssr in sr.substage_results.all():
                if complete:
                    val = 100.0
                else:
                    val = random.choice([0.0, 50.0, 100.0])
                ssr.completion_percent = val
                ssr.status = 'completed' if val >= 100.0 else ('partial' if val > 0 else 'pending')
                ssr.save()

            # aggregate stage completion as weighted average of substage completions
            sub_vals = [x.completion_percent for x in sr.substage_results.all()]
            if sub_vals:
                sr.completion_percent = sum(sub_vals) / len(sub_vals)
            else:
                sr.completion_percent = 0.0
            sr.status = 'completed' if sr.completion_percent >= 100.0 else ('partial' if sr.completion_percent > 0 else 'pending')
            sr.save()

        run.status = 'completed'
        run.end_time = timezone.now()
        run.save()

        self.stdout.write(self.style.SUCCESS(f'Created simulated run id={run.id} (pipeline={pipeline_id})'))
