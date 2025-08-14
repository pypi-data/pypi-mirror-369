import sys
import random
from .dictionary_of_themes import THEMES as DEFAULT_THEMES

def error_handler(exc_type,
                  exc_value,
                  exc_traceback,
                  message="🍆🍆🍆🍆🍆🍆 ur mom is so beautiful", 
                  theme_name=None,
                  custom_themes=None,
                  theme_mode="default",
                  want_original=False):
    
    bad_theme = False
    
    if theme_mode == "default":
        theme = DEFAULT_THEMES
    elif theme_mode == "custom":
        if custom_themes is None:
            print("No cusotm themes broski")
        else:
            theme = custom_themes
    elif theme_mode == "both":
        if custom_themes is None:
            print("no custom themes so going to default themes")
        else:
            theme = DEFAULT_THEMES.copy()
            for key, messages in custom_themes.items():
                if key in theme:
                    theme[key] += messages
                else:
                    theme[key] = messages
    else:
        print("idk what the FUCK you put in to get this but you get default themes")
        theme = DEFAULT_THEMES

    if theme_name == "motivate me":
        while True:
            print("gay ")

    elif theme_name is None:
        print(f"{message}")

    elif theme_name == "random":
        key = random.choice(list(theme.keys()))
        msg = random.choice(theme[key])
        print(msg)

    else:
        if theme_name in theme:
            msg = random.choice(theme[theme_name])
            print(msg)
        else:
            bad_theme = True
            print(f"Theme {theme_name} not found fuckhead")
            print("This is the original excepthook bc u can't figure out how to put the theme in properly:")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

    if want_original and not bad_theme:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
