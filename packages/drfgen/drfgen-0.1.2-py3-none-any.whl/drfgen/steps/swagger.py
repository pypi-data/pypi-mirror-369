def apply_spectacular_config(project_path, project_name, settings_structure):
    settings_path = project_path / project_name / "settings" / "base.py" if settings_structure == "advanced" \
        else project_path / project_name / "settings.py"
    
    # Append config to settings file
    with open(settings_path, "a") as f:
        f.write("\n\n# DRF Spectacular\n")
        f.write("INSTALLED_APPS += ['drf_spectacular']\n")
        f.write("REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'\n")

    # Update urls.py
    urls_path = project_path / project_name / "urls.py"
    with open(urls_path, "r+") as f:
        content = f.read()
        if "from django.urls" not in content:
            content = "from django.urls import path, include\n" + content
        content += """

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
"""
        f.seek(0)
        f.write(content)
        
        
def apply_yasg_config(project_path, project_name, settings_structure):
    settings_path = (
        project_path / project_name / "settings" / "base.py"
        if settings_structure == "advanced"
        else project_path / project_name / "settings.py"
    )

    # Add drf_yasg to INSTALLED_APPS and SWAGGER_SETTINGS
    with open(settings_path, "a") as f:
        f.write("\n\n# drf-yasg configuration\n")
        f.write("INSTALLED_APPS += ['drf_yasg']\n")
        f.write("""
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
}
""")

    # Update urls.py
    urls_path = project_path / project_name / "urls.py"

    with open(urls_path, "r+") as f:
        content = f.read()

        if "from django.urls" not in content:
            content = "from django.urls import path, include\n" + content

        if "urlpatterns" not in content:
            content += "\nurlpatterns = []\n"

        # Append imports and schema view
        content += """

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
      description="Your project API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
"""

        f.seek(0)
        f.write(content)