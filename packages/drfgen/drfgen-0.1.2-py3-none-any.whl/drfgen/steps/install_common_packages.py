from drfgen.core.venv import install_package


def install_common_packages(pip_path, database_choice, settings_file, env_path):
    
    default_packages = [
        # "pillow",
        "django-cors-headers",
        "django-filter"
    ]
    
    if database_choice == "postgresql":
        default_packages.append("psycopg2-binary")
        
        
    for pkg in default_packages:
        install_package(pip_path, pkg)
        
    with open(settings_file, "a", encoding="utf-8") as f:
        f.write("\n\n# ------------------ Extra Installed Packages ------------------\n")
        f.write("INSTALLED_APPS += ['corsheaders', 'django_filters']\n")
        f.write("\n# CORS Configuration\n")
        f.write("MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')\n")
        f.write("import os\n")
        f.write("CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'\n")

    # add CORS_ALLOW_ALL_ORIGINS to .env file
    if env_path.exists():
        env_lines = env_path.read_text(encoding="utf-8").splitlines()
        if not any(line.startswith("CORS_ALLOW_ALL_ORIGINS") for line in env_lines):
            env_lines.append("CORS_ALLOW_ALL_ORIGINS=True")
            env_path.write_text("\n".join(env_lines), encoding="utf-8")
            
    else:
        # if env.path dont exist create it 
        env_path.write_text("CORS_ALLOW_ALL_ORIGINS=True\n", encoding="utf-8")