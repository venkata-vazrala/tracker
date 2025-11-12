from django.urls import path, include
from rest_framework import routers
from .views import PipelineViewSet, RunViewSet

router = routers.DefaultRouter()
router.register(r'pipelines', PipelineViewSet, basename='pipeline')
router.register(r'runs', RunViewSet, basename='run')

urlpatterns = [
    path('api/', include(router.urls)),
]
