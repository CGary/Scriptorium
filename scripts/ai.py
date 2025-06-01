#!/usr/bin/env python3

import argparse
import logging
import subprocess
from pathlib import Path
from typing import List, Optional

class TaskRunner:
    def __init__(self):
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s: %(message)s",
            level=logging.INFO
        )

    def execute(self, command: List[str]) -> bool:
        try:
            result = subprocess.run(
                command,
                check=True,
                timeout=30,
                capture_output=True,
                text=True
            )
            logging.info(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            logging.error("Command timed out")
            return False

def make_commit(args):
    commit_command = ["git", "add", "."]
    if args.dry_run:
        commit_command = ["git", "diff", "--cached"]
    
    runner = TaskRunner()
    if not runner.execute(commit_command):
        return
    
    commit_message = f"'{args.message}'" if args.message else "Auto-commit"
    commit_args = ["git", "commit", "-m", commit_message]
    
    if runner.execute(commit_args) and not args.dry_run:
        runner.execute(["git", "push", "origin", args.branch])

def setup_parsers():
    parser = argparse.ArgumentParser(
        description="AI-powered task automation tool",
        epilog="Example: ai make-commit --branch=main --message='Update'"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Make commit command
    commit_parser = subparsers.add_parser(
        "make-commit", 
        help="Automate git commit and push workflow"
    )
    commit_parser.add_argument(
        "-b", "--branch",
        default="main",
        help="Target branch for push operation"
    )
    commit_parser.add_argument(
        "-m", "--message",
        default=None,
        help="Custom commit message"
    )
    commit_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show diff instead of committing"
    )
    commit_parser.set_defaults(func=make_commit)

    return parser

def main():
    parser = setup_parsers()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

