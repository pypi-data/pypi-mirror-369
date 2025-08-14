# testing_errors.py (in the tests folder)
import sys
import os

# Add the parent directory (custom_error_msg) to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from customErrorMessagesToSaveYourMentalHealth import error_handler

sys.excepthook = lambda exc_type, exc_value, exc_tb: error_handler(
    exc_type, exc_value, exc_tb, theme_name="loser"
)

# Trigger an error
1/0