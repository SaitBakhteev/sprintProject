from django.urls import path
from .views import PerevalCreateView

urlpatterns = [
    path('pereval/', PerevalCreateView.as_view(), name='pereval-create'),
]