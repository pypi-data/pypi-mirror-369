import json
from pathlib import Path

def save_drfgen_config(
    project_path: Path,
    project_name: str,
    django_version: str,
    drf_version: str,
    swagger_tool: str,
    auth_method: str,
    settings_structure: str,
    database: str,
    api_versioned: bool,
    dockerize: bool = False
):
    config_data = {
        "project_name": project_name,
        "django_version": django_version,
        "drf_version": drf_version,
        "swagger_tool": swagger_tool,
        "auth_method": auth_method,
        "settings_structure": settings_structure,
        "database": database,
        "api_versioned": api_versioned,
        "dockerize": dockerize
    }

    config_path = project_path / "drfgen_config.json"
    config_path.write_text(json.dumps(config_data, indent=4))