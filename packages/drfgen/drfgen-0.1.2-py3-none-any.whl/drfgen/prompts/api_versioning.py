import questionary

def choose_api_versioning():
    return questionary.confirm(
        "🧩 Do you want APIs to be versioned? (e.g. api/v1/)"
    ).ask()