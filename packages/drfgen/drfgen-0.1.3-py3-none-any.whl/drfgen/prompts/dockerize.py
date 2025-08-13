import questionary

def ask_dockerize():
    return questionary.confirm(
        "🐳 Do you want the project to be built with Docker?",
    ).ask()