from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from polls.api.v1.urls import urlpatterns as polls_v1

schema_view = get_schema_view(
    openapi.Info(
        title="Poll API",
        default_version='v1',
        contact=openapi.Contact(email="viacheslavlab@gmail.com"),
        license=openapi.License(name="Apache License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # V1
    path('v1/polls/', include(polls_v1)),
]
