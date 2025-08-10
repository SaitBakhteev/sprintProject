from django.urls import path
from .views import PerevalCreateView

urlpatterns = [
    path('submitData/', PerevalCreateView.as_view(), name='submitData'),
]