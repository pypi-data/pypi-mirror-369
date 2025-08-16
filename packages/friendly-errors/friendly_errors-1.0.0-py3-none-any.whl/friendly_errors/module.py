import traceback
import sys
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

def friendly_try(func, *args, suggestion="Check the code above for mistakes", **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        filename, lineno, funcname, text = tb[-1]

        # Highlight the line with error
        print(f"{Back.RED}{text}{Style.RESET_ALL}")

        # Exception message
        print(f"{Fore.YELLOW}Exception: {e}{Style.RESET_ALL}")

        # Suggestion in cyan
        print(f"{Fore.CYAN}Suggestion: {suggestion}{Style.RESET_ALL}")
