import questionary

def choose_database():
    db_choices = [
        "SQLite (Django default)",
        "PostgreSQL (Suitable for production)"
    ]
    
    choice = questionary.select(
        "💾 Which database do you want to use? ",
        choices=db_choices
    ).ask()
    
    if choice:
        return choice.split(" ")[0].lower()
    