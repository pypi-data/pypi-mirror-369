import os
from pathlib import Path
import click
from drfgen.prompts.django_version import choose_django_version
from drfgen.prompts.drf_version import choose_drf
from drfgen.prompts.auth_method import choose_auth_method
from drfgen.prompts.settings_structure import choose_settings_structure
from drfgen.prompts.database import choose_database
from drfgen.prompts.api_versioning import choose_api_versioning
# from drfgen.prompts.dockerize import ask_dockerize
from drfgen.prompts.swagger import choose_swagger
from drfgen.core.venv import create_venv, get_pip_path, get_python_path, install_package
from drfgen.generator.project_builder import run_django_startproject, convert_to_advanced_settings
import subprocess
from drfgen.steps.swagger import apply_spectacular_config
from drfgen.steps.install_common_packages import install_common_packages
from drfgen.steps.save_config import save_drfgen_config
from drfgen.steps.custom_drfgen_startapp import drfgen_startapp


@click.command()
def start_cli():
    click.secho(
        "👋 Welcome to DRFGen...",
        fg="yellow"
        )
    project_name = click.prompt(
        "📦 Whats your project name?",
        type =str
    )
    
    project_path = Path.cwd() / project_name
    
    if project_path.exists():
        click.secho(
            "⚠️  A folder with this name already exists!",
            fg= "red"
        )
        return
    
    #* STEP1: Create project directory
    os.makedirs(project_path)
    click.secho(
        f"✅ {project_name} project created in this path: {project_path}",
        fg = "green"
        )
    
    #* STEP2: Choose django version
    django_version = choose_django_version()
    click.secho(
        f"Selected version: {django_version}",
        fg = "cyan"
    )
    
    #* STEP3: Choose DRF
    drf_version = choose_drf()
    if drf_version:
        click.secho(f"✅ DRF was activated with version: {drf_version}", fg="green")
    else:
        click.secho(f"🚫 DRF not activated", fg="yellow")
        
    #* STEP3-1: Choose Swagger
    # Ask if Swagger / API Docs should be installed
    swagger_tool = choose_swagger()
    if swagger_tool:
        click.secho(f"Selected swagger tool: {swagger_tool}", fg="blue")
    else:
        click.secho("Swagger not active", fg="yellow")
    
    #* STEP4: Choose Authentication method
    auth_method = choose_auth_method()
    if auth_method:
        click.secho(f"Selected Authentication method: {auth_method}", fg="blue")
    else:
        click.secho("Authentication not active", fg="yellow")
        
    #* STEP5: Choose Settings structure    
    settings_structure = choose_settings_structure()
    click.secho(
        f" Selected settings structure : {settings_structure}",
        fg="magenta"
        )
    
    #* STEP6: Choose Database
    database = choose_database()
    click.secho(
        f" Selected database : {database}",
        fg="bright_blue"
        )
    
    #* STEP7: Choose API versioning
    api_versioned = choose_api_versioning()
    if api_versioned:
        click.secho(
            "📌 API versioning enabled: paths will be like /api/v1/...",
            fg="cyan"
        )
    else:
        click.secho(
            "📁 No versioning: Paths will be directly in /api/...",
            fg="yellow"
        )
        
    #* STEP8: Ask about dockerize
    # dockerize = ask_dockerize()
    # if dockerize:
    #     click.secho("✅ The project will be Dockerized.", fg="green")
    # else:
    #     click.secho("🚫 The project is built without Docker.", fg="yellow")
        
    #* STEP9: Create final virtualenv & install Dajgno
    venv_path = project_path / "venv"
    create_venv(str(venv_path))
    
    pip_path = get_pip_path(str(venv_path))
    python_path = get_python_path(str(venv_path))
    
    install_package(pip_path, f"django=={django_version}")
    
    install_package(pip_path, "python-dotenv")
    
    #* STEP10: Run startproject using selected Django version
    run_django_startproject(python_path, project_name, str(project_path))

    click.secho(
        "🎉 Django project initialized successfully!",
        fg="green"
    )
    
    #* STEP11: Apply advanced settings if needed
    if settings_structure == "advanced":
        convert_to_advanced_settings(project_path, project_name)
        click.secho("⚙️ Advanced settings applied with .env support", fg="green")
        
    #* STEP12: Freeze installed packages to requirements.txt
    # requirements_path = project_path / "requirements.txt"
    # subprocess.run([str(pip_path), "freeze"], stdout=open(requirements_path, "w"))
    # click.secho("📦 requirements.txt generated.", fg="cyan")
    
    #* STEP13: Install DRF if enabled
    if drf_version:
        install_package(pip_path, f"djangorestframework=={drf_version}")
        
        # If selected jwt:
        # if auth_method == "jwt":
        #     install_package(pip_path, "djangorestframework-simplejwt")
        
        # # Find settings file
        # if settings_structure == "advanced":
        #     settings_file = project_path / project_name / "settings" / "base.py"
        # else:
        #     settings_file = project_path / project_name / "settings.py"
        
        # from drfgen.steps.install_drf import apply_drf_config
        # apply_drf_config(settings_file, auth_method)

        click.secho("✅ Django REST Framework installed.", fg="green")
        
    #* STEP14: Setup Authentication system (including DRF config)
    if auth_method == "jwt":
        install_package(pip_path, "djangorestframework-simplejwt")
        click.secho("✅ Installed SimpleJWT for authentication", fg="green")

    elif auth_method == "oauth2":
        install_package(pip_path, "django-oauth-toolkit")
        click.secho("✅ Installed django-oauth-toolkit for OAuth2 support", fg="green")

    elif auth_method == "custom/manual setup...":
        click.secho("⚠️ Skipping auth setup. You need to configure it manually later.", fg="yellow")

    # Set the settings path
    if settings_structure == "advanced":
        settings_file = project_path / project_name / "settings" / "base.py"
    else:
        settings_file = project_path / project_name / "settings.py"

    # Apply DRF config regardless of auth type (but pass the method)
    from drfgen.steps.install_drf import apply_drf_config
    apply_drf_config(settings_file, auth_method)

    click.secho("✅ DRF & Authentication configured in settings.", fg="cyan")
    
    #* STEP15: Swagger / API Documentation
    if swagger_tool and drf_version:
        if swagger_tool == "drf-spectacular":
            install_package(pip_path, "drf-spectacular")

            
            apply_spectacular_config(project_path, project_name, settings_structure)

            click.secho("✅ drf-spectacular installed and configured!", fg="green")

        elif swagger_tool == "drf-yasg":
            install_package(pip_path, "drf-yasg")

            from drfgen.steps.swagger import apply_yasg_config
            apply_yasg_config(project_path, project_name, settings_structure)

            click.secho("✅ drf-yasg installed and configured!", fg="green")

        else:
            click.secho("🚫 Swagger tool not selected, skipping.", fg="yellow")
            
    #* STEP16: Install default Django packages
    env_path = project_path / ".env"
    install_common_packages(pip_path, database, settings_file, env_path)
    click.secho("📦 Default Django packages installed & configured!", fg="green")
    
    
    #* STEP16-2: Freeze installed packages to requirements.txt
    requirements_path = project_path / "requirements.txt"
    subprocess.run([str(pip_path), "freeze"], stdout=open(requirements_path, "w"))
    click.secho("📦 requirements.txt generated.", fg="cyan")
    
    
    #* STEP17: Create drfgen_config.json for save options that user selected
    save_drfgen_config(
        project_path=project_path,
        project_name=project_name,
        django_version=django_version,
        drf_version=drf_version,
        swagger_tool=swagger_tool,
        auth_method=auth_method,
        settings_structure=settings_structure,
        database=database,
        api_versioned=api_versioned,
        # dockerize=dockerize
    )
    click.secho("💾 drfgen_config.json saved with project settings!", fg="green")
    
    #* STEP18: Generate custom drfgen_startapp command
    drfgen_startapp(project_path, project_name)
    click.secho("🛠 Custom management command 'drfgen_startapp' created!", fg="green")
    