from django.contrib import admin
from .models import (
    Organization, Team, Project, Pipeline,
    Stage, SubStage, Run, StageResult, SubStageResult
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'version')


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'pipeline', 'weight', 'order')


@admin.register(SubStage)
class SubStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage', 'weight', 'order')


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'status', 'start_time', 'end_time')


@admin.register(StageResult)
class StageResultAdmin(admin.ModelAdmin):
    list_display = ('run', 'stage', 'completion_percent', 'status')


@admin.register(SubStageResult)
class SubStageResultAdmin(admin.ModelAdmin):
    list_display = ('stage_result', 'substage', 'completion_percent', 'status')
