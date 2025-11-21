from colorama import Fore, Style, Back
from app.core import db
# from flask import Flask, Blueprint, render_template
from app.init import app
from app.core.logger_config import setup_logger
from apply_migrations import apply_migrations

print(f"{Fore.GREEN}LAUNCHING {Style.BRIGHT}{Fore.MAGENTA}Do{Fore.CYAN}Dep{Fore.MAGENTA} 2{Style.RESET_ALL}{Fore.GREEN}...{Style.RESET_ALL}")
setup_logger(app)
app.logger.info("STARTING APP")


if __name__ == '__main__':
    try:
        apply_migrations()
        print(f"{Fore.GREEN}Hello, world!{Style.RESET_ALL}")
        app.run(host="0.0.0.0", port=34778, debug=True)
        
    finally:
        print(f"{Fore.RED}Exiting...{Style.RESET_ALL}")
        print(f"{Fore.RED}Goodbye, world!{Style.RESET_ALL}")
        db.conn.close()
        