import questionary
from drfgen.utils.pypi import get_latest_django_versions


def choose_drf():
    use_drf = questionary.confirm(
        "Do you want to use Django REST Framework (DRF) ? "
    ).ask()
    if not use_drf:
        return None
    
    versions = get_latest_django_versions("djangorestframework")
    
    version_choices = [f"{v}" for v in versions]
    version_choices[0] += " (latest) "
    version_choices.append("manual input...")
    
    choice = questionary.select(
        "What version of Django REST Framework do you want to use?",
        choices=version_choices
    ).ask()
    
    if choice == "manual input...":
        version = questionary.text(
            "Please manually enter the desired Django version (e.g. 3.2.18):"
        ).ask()
    else:
        version = choice.split(" ")[0]
        
    return version