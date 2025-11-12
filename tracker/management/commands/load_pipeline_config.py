import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from tracker.models import Pipeline, Stage, SubStage, Project


class Command(BaseCommand):
    help = 'Load or update a pipeline configuration from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to pipeline JSON file')
        parser.add_argument('--project-id', type=int, help='Project id to attach pipeline to (optional)')

    def handle(self, *args, **options):
        path = options['path']
        project_id = options.get('project_id')
        try:
            with open(path, 'r') as f:
                cfg = json.load(f)
        except Exception as e:
            raise CommandError(f'Failed to read JSON: {e}')

        pipeline_name = cfg.get('pipeline_name') or cfg.get('name')
        if not pipeline_name:
            raise CommandError('pipeline_name required in JSON')

        project = None
        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if not project:
                raise CommandError(f'Project id={project_id} not found')

        with transaction.atomic():
            # Create or update pipeline
            pipeline, _ = Pipeline.objects.get_or_create(name=pipeline_name, defaults={'project': project or Project.objects.first(), 'description': cfg.get('description', '')})
            pipeline.description = cfg.get('description', pipeline.description)
            pipeline.save()

            # Stage ordering and creation
            stages_cfg = cfg.get('stages', [])
            for s_idx, s in enumerate(stages_cfg, start=1):
                stage_obj, created = Stage.objects.update_or_create(
                    pipeline=pipeline,
                    name=s['name'],
                    defaults={
                        'weight': float(s.get('weight', 0.0)),
                        'order': s_idx,
                        'definition_of_done': s.get('definition_of_done', ''),
                        'auto_check_endpoint': s.get('endpoint', '') or s.get('auto_check_endpoint', ''),
                        'dod_type': s.get('type', 'manual')
                    }
                )
                # Substages
                for ss_idx, ss in enumerate(s.get('substages', []), start=1):
                    SubStage.objects.update_or_create(
                        stage=stage_obj,
                        name=ss['name'],
                        defaults={
                            'weight': float(ss.get('weight', 0.0)),
                            'order': ss_idx,
                            'definition_of_done': ss.get('definition_of_done', ''),
                            'auto_check_endpoint': ss.get('endpoint', ''),
                            'dod_type': ss.get('type', 'manual')
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f'Loaded/updated pipeline "{pipeline_name}"'))
