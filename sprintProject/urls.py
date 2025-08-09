from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


# from django.contrib import admin

urlpatterns = [
    #    path('admin/', admin.site.urls),

    # Генерируем схему OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='api-docs'),

    path('', include('fstr_app.urls')),


]
