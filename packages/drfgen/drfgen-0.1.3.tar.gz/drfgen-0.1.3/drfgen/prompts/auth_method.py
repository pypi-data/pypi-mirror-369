import questionary

def choose_auth_method():
    
    methods = [
        "JWT",
        "OAuth2",
        "Session-Based",
        "custom/manual setup..."
    ]
    
    choice = questionary.select(
        "Please select the desired authentication type: ",
        choices=methods
    ).ask()
    
    if choice:
        return choice.lower()
    return None