
# DRFGen CLI

[![PyPI Version](https://img.shields.io/pypi/v/drfgen.svg)](https://pypi.org/project/drfgen/)  
[![Python Versions](https://img.shields.io/pypi/pyversions/drfgen.svg)](https://pypi.org/project/drfgen/)  

**DRFGen** is a powerful and interactive CLI tool to quickly bootstrap Django REST Framework projects with best practices and customizable options. It helps you create a ready-to-use DRF project with authentication, API versioning, swagger integration, and more — saving you hours of manual setup.

---

## Features

- Interactive prompt-based project creation (Django version, DRF, database, auth method, etc.)  
- Virtual environment setup and package installation automation  
- Supports multiple Django versions and DRF versions  
- Choice of authentication methods including JWT and OAuth2  
- Configurable settings structure (simple or advanced with `.env`)  
- Automatic API versioning support  
- Integration with swagger tools (`drf-spectacular` or `drf-yasg`) for API documentation  
- Default common Django packages installed and configured  
- Generates a `requirements.txt` file automatically  
- Saves project configuration in `drfgen_config.json` for easy reference  
- **Custom Django management command `drfgen_startapp`** to create Django apps tailored to your project settings — automatically adds the app to `INSTALLED_APPS` and applies your custom templates  
- Dockerize support (optional) (commented out in current version)  

---

## Installation

You can install DRFGen from PyPI using pip:

```bash
pip install drfgen
```

---

## Usage

After installation, you get the `drfgen` CLI command:

```bash
drfgen
```

This launches an interactive wizard that will guide you through:

1. Naming your Django project  
2. Choosing the Django version to use  
3. Selecting whether to include Django REST Framework (and its version)  
4. Picking a Swagger tool for API docs (optional)  
5. Choosing authentication method (JWT, OAuth2, or none)  
6. Selecting project settings structure (simple or advanced with `.env` support)  
7. Picking your database backend  
8. Enabling or disabling API versioning  

Once you finish answering the prompts, DRFGen will:

- Create a project directory with the chosen name  
- Create a Python virtual environment inside the project folder  
- Install Django and other required packages into the venv  
- Initialize a Django project with the specified Django version  
- Apply advanced settings if requested  
- Freeze dependencies into `requirements.txt`  
- Install and configure Django REST Framework and authentication packages as needed  
- Install and configure Swagger tools if selected  
- Install common Django packages depending on your database and settings  
- Save your configuration to `drfgen_config.json`  
- Generate a custom management command called `drfgen_startapp` for creating apps  

You will see colorful terminal output indicating the progress of each step.

---

## The `drfgen_startapp` Custom Command

Creating Django apps with specific customizations can be time-consuming, especially if you want to keep your project consistent with your choices such as DRF integration, authentication setup, and settings structure.

To solve this, DRFGen generates a **custom Django management command** named:

```bash
python manage.py drfgen_startapp <app_name>
```

### How does it differ from the default `startapp`?

| Aspect                | Default `startapp`                       | DRFGen `drfgen_startapp`                         |
|-----------------------|----------------------------------------|-------------------------------------------------|
| Base Template         | Minimal default Django app template    | Custom app template aligned with your project setup, including DRF integrations, auth scaffolding, etc. |
| `INSTALLED_APPS`      | You must manually add app to settings  | Automatically adds the new app to your `INSTALLED_APPS` in settings file |
| Extra Boilerplate      | None                                   | Includes ready-to-use files like serializers, views, urls configured according to your auth, API versioning, etc. |
| Saves Time & Reduces Errors | Requires manual customization post-creation | Automates and standardizes app creation based on your DRFGen project choices |
| CLI Command           | `python manage.py startapp <app_name>`| `python manage.py drfgen_startapp <app_name>`   |

### Benefits

- **Consistency:** All your apps follow the same conventions and patterns.  
- **Speed:** No more repetitive boilerplate code creation — saves hours per app.  
- **Easy Integration:** Apps come pre-configured to work with authentication and API versioning as per your initial choices.  
- **Less Error-Prone:** Automatically modifies your `INSTALLED_APPS`, preventing forgotten steps.  

---

## Example Workflow

1. Run `drfgen` CLI and select options (Django 4.2, DRF 3.14, JWT auth, PostgreSQL, advanced settings, etc.)  
2. After project setup finishes, navigate into your new project folder:  
   ```bash
   cd myproject
   ```  
3. Use the custom app creation command:  
   ```bash
   python manage.py drfgen_startapp users
   ```  
4. The `users` app will be created with your custom structure, and automatically added to `INSTALLED_APPS`.  

---

## Why Use DRFGen?

Manually setting up Django REST Framework projects for production-grade apps involves many tedious steps — from environment setup, dependency management, to configuring authentication and documentation. DRFGen automates this entire process with a user-friendly CLI.

The **custom app command** ensures that every new app fits perfectly into your project without wasting time on repetitive boilerplate and manual config edits.

---

## Development

To contribute or develop locally:

```bash
git clone https://github.com/tahericode/DRFgen.git
cd drfgen
pip install -e .
drfgen
```

---

## License

MIT License

---

## Contact

For questions or feedback, please open an issue on GitHub or contact the maintainer.

