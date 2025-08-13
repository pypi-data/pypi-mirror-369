import subprocess
import os
import platform
from pathlib import Path
import shutil


def convert_to_advanced_settings(
    project_path: str,
    project_name: str
    ):
    project_root = project_path / project_name
    settings_path = project_root / "settings"
    default_settings_path = project_root / "settings.py"
    manage_py_path = project_path / "manage.py"
    wsgi_py_path = project_root / "wsgi.py"
    asgi_py_path = project_root / "asgi.py"
    env_path = project_path / ".env"

    # 1. Create settings directory
    settings_path.mkdir(exist_ok=True)

    # 2. Move original settings.py into base.py
    base_settings = settings_path / "base.py"
    if default_settings_path.exists():
        shutil.move(str(default_settings_path), str(base_settings))
        
    # 2.1. Fix BASE_DIR in base.py
    base_content = base_settings.read_text()
    
    import re
    if "BASE_DIR" in base_content:
        base_content = re.sub(
            r'BASE_DIR\s*=\s*Path\(.*\)',
            "BASE_DIR = Path(__file__).resolve().parent.parent.parent",
            base_content
        )
    else:
        base_content = "from pathlib import Path\n\nBASE_DIR = Path(__file__).resolve().parent.parent.parent\n\n" + base_content

    base_settings.write_text(base_content)


    # 3. Create __init__.py in settings/
    (settings_path / "__init__.py").touch()

    # 4. Create dev.py and prod.py
    dev_settings = settings_path / "dev.py"
    prod_settings = settings_path / "prod.py"

    dev_settings.write_text("""\
from .base import *

DEBUG = True
ALLOWED_HOSTS = []

# Example SQLite config
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
""")

    prod_settings.write_text("""\
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}
""")

    # 5. Update manage.py
    update_file_env_loader(manage_py_path, project_name)

    # 6. Update wsgi.py
    update_file_env_loader(wsgi_py_path, project_name)

    # 7. Update asgi.py if exists
    if asgi_py_path.exists():
        update_file_env_loader(asgi_py_path, project_name)

    # 8. Create .env file
    env_path.write_text("""\
DJANGO_ENV=dev
DEBUG=True
SECRET_KEY=replace-this-key
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
""")


def update_file_env_loader(file_path: Path, project_name: str):
    if not file_path.exists():
        return

    original = file_path.read_text()

    # حذف خطی که ست کردن DJANGO_SETTINGS_MODULE رو انجام می‌ده
    lines = original.splitlines()
    new_lines = []
    for line in lines:
        if "DJANGO_SETTINGS_MODULE" not in line:
            new_lines.append(line)

    header = f"""\
import os
from dotenv import load_dotenv

load_dotenv()

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings." + DJANGO_ENV)
"""

    updated = header + "\n" + "\n".join(new_lines)
    file_path.write_text(updated)



def update_settings_reference(file_path: Path, project_name: str):
    text = file_path.read_text()
    new_text = text.replace(
        f"{project_name}.settings",
        f"{project_name}.settings.dev"
    )
    file_path.write_text(new_text)
    


def run_django_startproject(
        python_path: str,
        project_name: str,
        target_dir: str
    ):
    print("🚀 Building a Django project...")
    django_admin = os.path.join(
        os.path.dirname(python_path), "django-admin")
    
    if platform.system() == "Windows":
        django_admin += ".exe"
    
    subprocess.run(
        [django_admin, "startproject", project_name, target_dir],
        check=True)