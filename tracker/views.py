from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Pipeline, Run, StageResult, SubStageResult
from .serializers import PipelineSerializer, RunSerializer, StageResultSerializer, SubStageResultSerializer
from .services import calculate_run_score


class PipelineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer

    @action(detail=True, methods=['get'])
    def trend(self, request, pk=None):
        """Return trend metrics (last N runs) for pipeline."""
        pipeline = self.get_object()
        n = int(request.query_params.get('n', 10))
        runs = pipeline.runs.all().order_by('-start_time')[:n]
        data = []
        for r in runs:
            data.append({'run_id': r.id, 'start_time': r.start_time, 'overall_score': round(r.overall_score * 100, 2)})
        return Response(data)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('pipeline')
    serializer_class = RunSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = serializer.save()
        # The signals will create StageResult/SubStageResult instances
        return Response(RunSerializer(run).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_stage(self, request, pk=None):
        """Update a stage or substage result. Expect payload like:
        {"stage_id": 1, "completion_percent": 100} or
        {"substage_id": 5, "completion_percent": 100}
        """
        run = self.get_object()
        stage_id = request.data.get('stage_id')
        substage_id = request.data.get('substage_id')
        completion_percent = float(request.data.get('completion_percent', 0))

        if substage_id:
            ssr = get_object_or_404(SubStageResult, substage_id=substage_id, stage_result__run=run)
            ssr.completion_percent = completion_percent
            ssr.status = request.data.get('status', ssr.status)
            ssr.save()
        elif stage_id:
            sr = get_object_or_404(StageResult, stage_id=stage_id, run=run)
            sr.completion_percent = completion_percent
            sr.status = request.data.get('status', sr.status)
            sr.save()
        else:
            return Response({'detail': 'stage_id or substage_id required'}, status=400)

        # Recalculate overall score
        new_score = calculate_run_score(run.id)
        # Optionally update run.status or save metrics; the property computes on the fly
        return Response({'overall_score': round(new_score * 100, 2)})

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        run = self.get_object()
        serializer = self.get_serializer(run)
        return Response(serializer.data)
