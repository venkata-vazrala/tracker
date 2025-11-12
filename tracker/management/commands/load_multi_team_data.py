"""
Management command to load sample data with multiple teams.
Demonstrates cross-team collaboration on shared pipelines.
"""
from django.core.management.base import BaseCommand
from tracker.models import Organization, Team, Project, Pipeline, Stage, SubStage, Run, StageResult, SubStageResult
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Load sample data with multiple teams collaborating on projects'

    def handle(self, *args, **options):
        self.stdout.write('Creating multi-team sample data...\n')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Organization.objects.all().delete()

        # Create Organization
        org = Organization.objects.create(
            name='ABC COMPANY - Firmware Division',
            description='System firmware and validation teams'
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created organization: {org.name}'))

        # Create Teams
        build_team = Team.objects.create(
            organization=org,
            name='Build Automation',
            description='Handles compilation, signing, and artifact management'
        )
        
        test_team = Team.objects.create(
            organization=org,
            name='Test Validation',
            description='Manages unit tests, integration tests, and regression suites'
        )
        
        deploy_team = Team.objects.create(
            organization=org,
            name='Release Engineering',
            description='Handles deployment, tagging, and distribution'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created teams: {build_team.name}, {test_team.name}, {deploy_team.name}'))

        # Create Projects (one per team)
        FW_project = Project.objects.create(
            team=build_team,
            name='FW-MCU_VM',
            repo_url='https://github.com/ti/FW-MCU_VM',
            description='System firmware for MCU_VM SoC'
        )
        
        validation_project = Project.objects.create(
            team=test_team,
            name='Validation Suite',
            repo_url='https://github.com/ti/validation-suite',
            description='Comprehensive test automation framework'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created projects: {FW_project.name}, {validation_project.name}'))

        # Create Pipeline 1: FW Build Pipeline (owned by Build team, shared with Test team)
        pipeline1 = Pipeline.objects.create(
            project=FW_project,
            name='FW Nightly Build & Test',
            description='Complete build and validation pipeline for FW',
            version='v2.0'
        )
        
        # Build Stage (owned by Build team)
        build_stage = Stage.objects.create(
            pipeline=pipeline1,
            name='Build',
            weight=0.4,
            order=1,
            definition_of_done='All build artifacts generated and signed',
            dod_type='auto',
            auto_check_endpoint='/api/checks/build_complete/'
        )
        
        SubStage.objects.create(
            stage=build_stage,
            name='Source Sync',
            weight=0.2,
            order=1,
            definition_of_done='Git repositories synced successfully',
            dod_type='auto',
            auto_check_endpoint='/api/checks/source_sync/'
        )
        
        SubStage.objects.create(
            stage=build_stage,
            name='Compilation',
            weight=0.5,
            order=2,
            definition_of_done='Build completes without errors',
            dod_type='auto',
            auto_check_endpoint='/api/checks/compilation/'
        )
        
        SubStage.objects.create(
            stage=build_stage,
            name='Binary Signing',
            weight=0.3,
            order=3,
            definition_of_done='Images signed with production keys',
            dod_type='manual'
        )
        
        # Test Stage (owned by Test team)
        test_stage = Stage.objects.create(
            pipeline=pipeline1,
            name='Test',
            weight=0.4,
            order=2,
            definition_of_done='All test suites passed',
            dod_type='auto',
            auto_check_endpoint='/api/checks/all_tests/'
        )
        
        SubStage.objects.create(
            stage=test_stage,
            name='Unit Tests',
            weight=0.3,
            order=1,
            definition_of_done='All unit tests passed (>95% coverage)',
            dod_type='auto',
            auto_check_endpoint='/api/checks/unit_tests/'
        )
        
        SubStage.objects.create(
            stage=test_stage,
            name='Integration Tests',
            weight=0.4,
            order=2,
            definition_of_done='Integration test suite completed',
            dod_type='auto',
            auto_check_endpoint='/api/checks/integration_tests/'
        )
        
        SubStage.objects.create(
            stage=test_stage,
            name='Regression Tests',
            weight=0.3,
            order=3,
            definition_of_done='No regressions detected',
            dod_type='manual'
        )
        
        # Deploy Stage (owned by Deploy team)
        deploy_stage = Stage.objects.create(
            pipeline=pipeline1,
            name='Deploy',
            weight=0.2,
            order=3,
            definition_of_done='Release tagged and artifacts published',
            dod_type='manual'
        )
        
        SubStage.objects.create(
            stage=deploy_stage,
            name='Artifact Upload',
            weight=0.5,
            order=1,
            definition_of_done='Artifacts uploaded to artifact server',
            dod_type='auto',
            auto_check_endpoint='/api/checks/artifact_upload/'
        )
        
        SubStage.objects.create(
            stage=deploy_stage,
            name='Release Tag',
            weight=0.5,
            order=2,
            definition_of_done='Git tag created and pushed',
            dod_type='manual'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created pipeline: {pipeline1.name} (3 stages, 8 substages)'))

        # Create Pipeline 2: Pure Validation Pipeline (owned by Test team)
        pipeline2 = Pipeline.objects.create(
            project=validation_project,
            name='Automated Regression Suite',
            description='Nightly regression testing across all platforms',
            version='v1.5'
        )
        
        # Test Preparation Stage
        prep_stage = Stage.objects.create(
            pipeline=pipeline2,
            name='Test Preparation',
            weight=0.2,
            order=1,
            definition_of_done='Test environment ready',
            dod_type='auto'
        )
        
        SubStage.objects.create(
            stage=prep_stage,
            name='Environment Setup',
            weight=0.6,
            order=1,
            definition_of_done='Test boards connected and flashed',
            dod_type='auto',
            auto_check_endpoint='/api/checks/env_setup/'
        )
        
        SubStage.objects.create(
            stage=prep_stage,
            name='Test Data Load',
            weight=0.4,
            order=2,
            definition_of_done='Test datasets loaded',
            dod_type='auto',
            auto_check_endpoint='/api/checks/data_load/'
        )
        
        # Test Execution Stage
        exec_stage = Stage.objects.create(
            pipeline=pipeline2,
            name='Test Execution',
            weight=0.6,
            order=2,
            definition_of_done='All test cases executed',
            dod_type='auto'
        )
        
        SubStage.objects.create(
            stage=exec_stage,
            name='Functional Tests',
            weight=0.4,
            order=1,
            definition_of_done='Functional tests passed',
            dod_type='auto',
            auto_check_endpoint='/api/checks/functional_tests/'
        )
        
        SubStage.objects.create(
            stage=exec_stage,
            name='Performance Tests',
            weight=0.3,
            order=2,
            definition_of_done='Performance benchmarks met',
            dod_type='auto',
            auto_check_endpoint='/api/checks/performance_tests/'
        )
        
        SubStage.objects.create(
            stage=exec_stage,
            name='Stress Tests',
            weight=0.3,
            order=3,
            definition_of_done='System stable under stress',
            dod_type='auto',
            auto_check_endpoint='/api/checks/stress_tests/'
        )
        
        # Reporting Stage
        report_stage = Stage.objects.create(
            pipeline=pipeline2,
            name='Reporting',
            weight=0.2,
            order=3,
            definition_of_done='Test reports generated and published',
            dod_type='manual'
        )
        
        SubStage.objects.create(
            stage=report_stage,
            name='Generate Reports',
            weight=0.7,
            order=1,
            definition_of_done='HTML and PDF reports generated',
            dod_type='auto',
            auto_check_endpoint='/api/checks/reports/'
        )
        
        SubStage.objects.create(
            stage=report_stage,
            name='Publish Results',
            weight=0.3,
            order=2,
            definition_of_done='Results uploaded to dashboard',
            dod_type='manual'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created pipeline: {pipeline2.name} (3 stages, 8 substages)'))

        # Create sample runs for Pipeline 1 (FW)
        self.stdout.write('\nCreating sample runs...')
        
        run_scenarios = [
            {'completion': 100, 'triggered_by': 'Nightly Jenkins', 'status': 'completed'},
            {'completion': 75, 'triggered_by': 'Manual PR Test', 'status': 'running'},
            {'completion': 40, 'triggered_by': 'Nightly Jenkins', 'status': 'running'},
            {'completion': 100, 'triggered_by': 'Release Build', 'status': 'completed'},
            {'completion': 0, 'triggered_by': 'Nightly Jenkins', 'status': 'failed'},
        ]
        
        for scenario in run_scenarios:
            run = Run.objects.create(
                pipeline=pipeline1,
                triggered_by=scenario['triggered_by'],
                status=scenario['status']
            )
            
            # Update stage/substage results based on completion
            completion = scenario['completion']
            for stage_result in run.stage_results.all():
                stage_completion = min(100, completion)
                stage_result.completion_percent = stage_completion
                stage_result.status = 'completed' if stage_completion == 100 else 'running'
                stage_result.save()
                
                for substage_result in stage_result.substage_results.all():
                    substage_completion = min(100, completion)
                    substage_result.completion_percent = substage_completion
                    substage_result.status = 'completed' if substage_completion == 100 else 'running'
                    substage_result.save()
                
                completion = max(0, completion - 35)  # Decrement for next stage
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created 5 runs for {pipeline1.name}'))

        # Create sample runs for Pipeline 2 (Validation)
        for i in range(3):
            completion = random.choice([60, 85, 100])
            run = Run.objects.create(
                pipeline=pipeline2,
                triggered_by='Automated Nightly',
                status='completed' if completion == 100 else 'running'
            )
            
            for stage_result in run.stage_results.all():
                stage_completion = min(100, completion)
                stage_result.completion_percent = stage_completion
                stage_result.status = 'completed' if stage_completion == 100 else 'running'
                stage_result.save()
                
                for substage_result in stage_result.substage_results.all():
                    substage_completion = min(100, completion)
                    substage_result.completion_percent = substage_completion
                    substage_result.status = 'completed' if substage_completion == 100 else 'running'
                    substage_result.save()
                
                completion = max(0, completion - 30)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created 3 runs for {pipeline2.name}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Multi-Team Data Load Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  Organizations: {Organization.objects.count()}')
        self.stdout.write(f'  Teams: {Team.objects.count()}')
        self.stdout.write(f'  Projects: {Project.objects.count()}')
        self.stdout.write(f'  Pipelines: {Pipeline.objects.count()}')
        self.stdout.write(f'  Stages: {Stage.objects.count()}')
        self.stdout.write(f'  SubStages: {SubStage.objects.count()}')
        self.stdout.write(f'  Runs: {Run.objects.count()}')
        
        self.stdout.write(f'\n🏢 Team Structure:')
        self.stdout.write(f'  • {build_team.name} → {FW_project.name}')
        self.stdout.write(f'  • {test_team.name} → {validation_project.name}')
        self.stdout.write(f'  • {deploy_team.name} (contributes to pipelines)')
        
        self.stdout.write(f'\n🔗 Pipelines:')
        self.stdout.write(f'  1. {pipeline1.name}')
        self.stdout.write(f'     - Build stage (Build team)')
        self.stdout.write(f'     - Test stage (Test team)')
        self.stdout.write(f'     - Deploy stage (Deploy team)')
        self.stdout.write(f'  2. {pipeline2.name}')
        self.stdout.write(f'     - Pure test automation (Test team)')
        
        self.stdout.write(f'\n🚀 Next Steps:')
        self.stdout.write(f'  1. View UI: http://127.0.0.1:8001/')
        self.stdout.write(f'  2. API: curl http://127.0.0.1:8001/api/pipelines/')
        self.stdout.write(f'  3. Admin: http://127.0.0.1:8001/admin/')
        self.stdout.write(f'\n✅ Ready for demo!\n')
