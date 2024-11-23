from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardStatsView

router = DefaultRouter()
router.register('stats', DashboardStatsView, basename='dashboard-stats')

urlpatterns = [
    path('', include(router.urls)),
]