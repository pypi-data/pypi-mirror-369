import questionary

def choose_swagger():
    use_docs = questionary.confirm("📄 Do you want to add API documentation (Swagger)?").ask()

    if not use_docs:
        return None

    options = [
        "drf-spectacular",
        "drf-yasg"
    ]

    choice = questionary.select(
        "Which Swagger tool do you prefer?",
        choices=options
    ).ask()

    return choice.lower() if choice else None