from django.urls import path
from .views import (
    PerevalListCreateView,
    PerevalDetailView,
    PerevalUpdateView,
)

urlpatterns = [
    path('getData/', PerevalListCreateView.as_view(), name='submitData'),
    path('submitData/<int:pk>/', PerevalDetailView.as_view(), name='pereval-detail'),
    path('submitData/<int:pk>', PerevalUpdateView.as_view(), name='pereval-update'),
]