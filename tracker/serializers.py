from rest_framework import serializers
from .models import (
    Organization, Team, Project, Pipeline, Stage, SubStage,
    Run, StageResult, SubStageResult
)


class SubStageResultSerializer(serializers.ModelSerializer):
    substage_name = serializers.CharField(source='substage.name', read_only=True)

    class Meta:
        model = SubStageResult
        fields = ['id', 'substage', 'substage_name', 'start_time', 'end_time', 'status', 'completion_percent']


class StageResultSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    substage_results = SubStageResultSerializer(many=True, read_only=True)

    class Meta:
        model = StageResult
        fields = ['id', 'stage', 'stage_name', 'start_time', 'end_time', 'status', 'completion_percent', 'substage_results']


class RunSerializer(serializers.ModelSerializer):
    stage_results = StageResultSerializer(many=True, read_only=True)
    overall_score = serializers.SerializerMethodField()

    class Meta:
        model = Run
        fields = ['id', 'pipeline', 'triggered_by', 'start_time', 'end_time', 'status', 'stage_results', 'overall_score']

    def get_overall_score(self, obj):
        # return percent value 0..100 for convenience
        return round(obj.overall_score * 100, 2)


class SubStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStage
        fields = ['id', 'stage', 'name', 'weight', 'order', 'definition_of_done', 'auto_check_endpoint', 'dod_type']


class StageSerializer(serializers.ModelSerializer):
    substages = SubStageSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = ['id', 'pipeline', 'name', 'weight', 'order', 'definition_of_done', 'auto_check_endpoint', 'dod_type', 'substages']


class PipelineSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = ['id', 'project', 'name', 'description', 'version', 'stages']


class ProjectSerializer(serializers.ModelSerializer):
    pipelines = PipelineSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'team', 'name', 'repo_url', 'description', 'pipelines']


class TeamSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'organization', 'name', 'description', 'projects']


class OrganizationSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'teams']
