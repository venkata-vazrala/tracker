from django.urls import path, include
from rest_framework import routers
from .views import PipelineViewSet, RunViewSet, dashboard_view

router = routers.DefaultRouter()
router.register(r'pipelines', PipelineViewSet, basename='pipeline')
router.register(r'runs', RunViewSet, basename='run')

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('api/', include(router.urls)),
]
