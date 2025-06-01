#!/usr/bin/env python3
import argparse
import logging
import readline
import signal
import subprocess
from pathlib import Path
from typing import List

class ShellCore:
    def __init__(self):
        self.history_file = Path.home() / ".py_shell_history"
        self._setup_logging()
        self._load_history()

    def _setup_logging(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s: %(message)s",
            level=logging.INFO
        )

    def _load_history(self):
        if self.history_file.exists():
            readline.read_history_file(self.history_file)

    def execute_command(self, command: List[str]) -> str:
        try:
            subprocess.run(
                command,
                check=True,
                timeout=30
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e.stderr}")
            return ""
        except subprocess.TimeoutExpired:
            logging.error("Command timed out")
            return ""

class PyShell:
    BUILTIN_COMMANDS = {
        "exit": lambda _: exit(0),
        "history": lambda self: print("\n".join(
            [str(i+1) + " " + readline.get_history_item(i+1) 
             for i in range(readline.get_current_history_length())])
        )
    }

    def __init__(self):
        self.core = ShellCore()
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _handle_sigint(self, signum, frame):
        print("\nInterrupt received. Type 'exit' to quit.")

    def _parse_input(self, input_str: str) -> List[str]:
        return input_str.strip().split()

    def _process_builtin(self, command: List[str]) -> bool:
        if command[0] in self.BUILTIN_COMMANDS:
            self.BUILTIN_COMMANDS[command[0]](self)
            return True
        return False

    def repl(self):
        while True:
            try:
                input_str = input("\033[34mpy-shell>\033[0m ")
                command = self._parse_input(input_str)
                
                if not command:
                    continue
                
                if self._process_builtin(command):
                    continue

                output = self.core.execute_command(command)
                
                readline.add_history(input_str)
                readline.write_history_file(str(self.core.history_file))

            except EOFError:
                print("\nGoodbye!")
                break

def main():
    parser = argparse.ArgumentParser(
        description="Python Shell with advanced features",
        epilog="Example: ./pyshell.py"
    )
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    shell = PyShell()
    shell.repl()

if __name__ == "__main__":
    main()

