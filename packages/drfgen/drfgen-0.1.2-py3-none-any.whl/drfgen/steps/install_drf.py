from pathlib import Path

def apply_drf_config(settings_file: Path, auth_method: str):
    with open(settings_file, "r", encoding="utf-8") as f:
        content = f.read()

    if "'rest_framework'" not in content:
        content = content.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'rest_framework',"
        )
        
    # If OAuth2 is selected, ensure 'oauth2_provider' is in INSTALLED_APPS
    if auth_method == "oauth2" and "'oauth2_provider'" not in content:
        content = content.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'oauth2_provider',"
        )

    if "REST_FRAMEWORK" not in content:
        drf_settings = f"""
# Django REST Framework Settings
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        '{get_auth_backend(auth_method)}',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}}
"""
        content += "\n" + drf_settings

    with open(settings_file, "w", encoding="utf-8") as f:
        f.write(content)


def get_auth_backend(auth_method: str) -> str:
    if not auth_method:
        return ""

    mapping = {
        "session": "rest_framework.authentication.SessionAuthentication",
        "jwt": "rest_framework_simplejwt.authentication.JWTAuthentication",
        "token": "rest_framework.authentication.TokenAuthentication",
        "basic": "rest_framework.authentication.BasicAuthentication",
        "oauth2": "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "custom/manual setup...": "",  # We skip setting it
    }

    return mapping.get(auth_method.lower(), "")