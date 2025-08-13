import questionary

def choose_settings_structure():
    structures = [
        "simple (just use a settings.py)",
        "advanced (use base.py, dev.py, prod.py)"
    ]
    
    choice = questionary.select(
        "⚙️ What kind of configuration structure do you want?",
        choices= structures
    ).ask()
    
    if choice:
        return choice.split(" ")[0]