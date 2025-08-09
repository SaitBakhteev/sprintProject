from django.urls import path, include

from django.views.generic import TemplateView
from django.templatetags.static import static

# from django.contrib import admin

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', include('fstr_app.urls')),
    path('api/docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': static('openapi-schema.yml')}
    )
         )
]
