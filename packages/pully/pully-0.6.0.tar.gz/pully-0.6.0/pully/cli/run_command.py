# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from termcolor import colored

from .. import pullyfile
from ..constants import BASE_DIR, PULLY_LOG
from ..pullyfile import PullyProject


def run_process(command: List[str], repo_dir: Path, stdout, stderr):
    subprocess.run(
        command,
        cwd=repo_dir,
        text=True,
        check=True,
        stdout=stdout,
        stderr=stderr,
    )


def run_process_in_project(
    config_dir: Path, project: PullyProject, log_path: Path, command: List[str]
):
    repo_dir = config_dir / project.local_path
    if not repo_dir.exists():
        print(
            colored("skipping", "yellow"),
            f"{repo_dir} not found, run pull to clone project",
        )
        return
    try:
        if log_path:
            with open(log_path, "a") as output_stream:
                output_stream.write(f"\n--------- {project.local_path} ---------\n")
                output_stream.flush()
                run_process(command, repo_dir, output_stream, subprocess.STDOUT)
        else:
            width, _ = shutil.get_terminal_size((80, 20))
            headline = (
                colored("running", "green") + " " + colored(project.local_path, "white")
            )
            lines = width - len(f"running {project.local_path}") - 1
            print(headline, "-" * lines)
            run_process(command, repo_dir, None, None)
    except subprocess.CalledProcessError:
        print(
            colored("failed", "red"),
            project.local_path,
        )


def resolve_executable_path(path: Path) -> Path:
    """
    Resolve an executable path both inside and outside of PATH.
    """
    try:
        return str(Path(shutil.which(path)).absolute())
    except TypeError:
        raise FileNotFoundError(path)


def build_pully_run_command(args, input_file=sys.stdin) -> List[str]:
    """
    Build fully-qualified subprocess arguments from args/command options.
    """
    if args.args:
        prog = resolve_executable_path(args.args[0])
        return [prog, *args.args[1:]]

    elif args.command:
        if args.command == "-":
            return [*args.entrypoint, input_file.read().rstrip()]
        return [*args.entrypoint, args.command]

    raise NotImplementedError("reached impossible parser state")


def run_command(args):
    base_dir = Path(args.directory) if args.directory else BASE_DIR

    command = build_pully_run_command(args)

    with pullyfile.project_context(base_dir, search=not args.directory) as context:
        config_dir, projects, groups = context
        if args.output == "pully-log":
            log_path = config_dir / PULLY_LOG
        else:
            log_path = None
        for project_id, project in projects.items():
            if args.output == "project-log":
                log_path = config_dir / project.local_path / PULLY_LOG
            run_process_in_project(config_dir, project, log_path, command)
