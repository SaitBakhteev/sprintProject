from django.urls import path
from .views import (
    PerevalCreateView,
    PerevalDetailView,
    PerevalUpdateView,
    PerevalUserListView
)

urlpatterns = [
    path('submitData/', PerevalCreateView.as_view(), name='submitData'),
    path('submitData/<int:pk>/', PerevalDetailView.as_view(), name='pereval-detail'),
    path('submitData/<int:pk>/', PerevalUpdateView.as_view(), name='pereval-update'),
    path('submitData/', PerevalUserListView.as_view(), name='pereval-user-list'),
]