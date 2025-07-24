"""
scaffold.py
-------------

This module provides the CLI commands to scaffold a new machine learning project structure. 
It defines the `Scaffold` class and a Typer CLI command for project creation.
"""
from pathlib import Path
from typing import Optional

import typer
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

scaffold_app = typer.Typer()

class Scaffold(BaseModel):
    """
    Scaffold a new machine learning project structure from Jinja2 templates.

    Attributes
    ----------
    name : str
        Name of the project to scaffold.
    version : str
        Version of the project.
    output : Path
        Output directory where the project will be created. 
        Defaulted to the current working directory.
    """
    name: str
    version: str
    output: Path

    def __call__(self) -> None:
        """
        Generate the project structure by rendering Jinja2 templates.
        """
        template_dir: Path = (
            Path(__file__).parents[2] / "conf" / "project_templates" / "root_ml_project"
        )
        project_dir = self.output / self.name

        environment = Environment(
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

            template = environment.get_template(rel_path)
            rendered = template.render(
                project_name=self.name,
                project_version=self.version,
            )
            target_path.write_text(rendered, encoding="utf-8")

        typer.echo(f'Scaffold successfuly built in {project_dir}. Enjoy!')

@scaffold_app.command(
    help="Scaffold a new machine learning project structure"
)
def create(
    name: str = typer.Option("sandboxML", help="Name of the project to build"),
    version: str = typer.Option("0.1.0", help="Version of the project to build"),
    output: Optional[str] = typer.Option(
        None,
        help="Directory location for the project. No value means current working directory."
    )
) -> None:
    """
    CLI command to scaffold a new machine learning project structure.

    Parameters
    ----------
    name : str, optional
        Name of the project to build (default is "sandboxML").
    version : str, optional
        Version of the project to build (default is "0.1.0").
    output : str, optional
        Directory location for the project (default is current working directory).

    Examples
    --------
    Create a project with default settings (name='sandboxML', version='0.1.0', output=current working directory):
        python -m topmodels scaffold create

    Create a project in a specific parameters:
        python -m topmodels scaffold create --name my_project --version 1.0.0 --output /path/to/directory
    """
    output_path = Path(output) if output else Path.cwd()
    scaffold = Scaffold(name=name, version=version, output=output_path)
    typer.echo(f'Launch creation of project << {scaffold.name} >>')
    scaffold()
