import questionary
from drfgen.utils.pypi import get_latest_django_versions


def choose_django_version():
    versions = get_latest_django_versions("Django")

    version_choices = [f"{v}" for v in versions]
    version_choices[0] += " (latest)"
    version_choices.append("manual input...")
    # versions = [
    #     "5.0.4 (latest)",
    #     "5.0.3",
    #     "4.2.11",
    #     "4.2.10",
    #     "manual input..."
    # ]
    
    choice = questionary.select(
        "What version of Django do you want to use?",
        choices=version_choices
    ).ask()
    
    if choice == "manual input...":
        version = questionary.text(
            "Please manually enter the desired Django version (e.g. 3.2.18):"
        ).ask()
    else:
        version = choice.split(" ")[0]
        
    return version