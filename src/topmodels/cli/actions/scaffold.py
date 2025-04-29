"""
Scaffolding module for creating ML projects with Jinja2 templates.

This module provides a CLI interface to generate the structure of a machine learning
project from customizable templates. It uses Jinja2 for file rendering and argparse
for command-line argument management.

Functions:
    build_parser() -> argparse.ArgumentParser:
        Builds and returns an argument parser for the scaffold CLI.

    scaffold(location, name, version):
        Generates the structure of an ML project from templates, replacing variables
        with the provided values (name, version, etc.).

    run(args):
        CLI entry point. Parses arguments and launches project generation.
"""

import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def build_parser() -> argparse.ArgumentParser:
    """
    Creates and returns an argument parser for the scaffold command.

    Returns:
        argparse.ArgumentParser: The configured parser for the scaffold CLI.
    """
    parser = argparse.ArgumentParser(
        prog="scaffold",
        description="Scaffold a new ML project"
    )
    parser.add_argument(
        "-n", "--name",
        type=str,
        help="Name of the project to build",
        default="sandboxML"
    )
    parser.add_argument(
        "-v", "--version",
        type=str,
        help="Version of the project to build",
        default="0.1.0"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Directory location for the project",
        default="."
    )
    return parser

def scaffold(location, name, version):
    """
    Generates the structure of an ML project from Jinja2 templates.

    Args:
        location (str): Path to the folder where the project will be created.
        name (str): Name of the project.
        version (str): Version of the project.

    Raises:
        FileNotFoundError: If the template folder does not exist.
    """
    template_dir: Path = (
        Path(__file__).parent.parent.parent
        / "conf" / "project_templates" / "root_ml_project"
    )
    project_dir = Path(location) / name

    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory {template_dir} does not exist.")

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True
    )

    for template_path in template_dir.rglob("*-jy2"):
        rel_path = (
            template_path
            .relative_to(template_dir)
            .as_posix()
        )
        new_path = rel_path.removesuffix("-jy2")

        target_path = project_dir / new_path

        target_path.parent.mkdir(parents=True, exist_ok=True)

        template = env.get_template(rel_path)
        rendered = template.render(
            project_name=name,
            project_version=version,
        )
        target_path.write_text(rendered, encoding="utf-8")

    print(f"Scaffold successfuly built in {project_dir}")

def run(args):
    """
    CLI entry point for project generation.

    Args:
        args (list): List of command-line arguments.
    """
    parser = build_parser()
    args = parser.parse_args(args)

    scaffold(location=args.output, name=args.name, version=args.version)
