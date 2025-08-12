from django.urls import path
from .views import (
    PerevalListCreateView,
    PerevalDetailView,
    PerevalUpdateView,
    PerevalUserListView
)

urlpatterns = [
    path('submitData/', PerevalListCreateView.as_view(), name='submitData'),
    path('submitData/<int:pk>/', PerevalDetailView.as_view(), name='pereval-detail'),
    path('submitData/<int:pk>/update/', PerevalUpdateView.as_view(), name='pereval-update'),
]