import typer

from topmodels.cli.actions.scaffold import scaffold_app

app = typer.Typer()
app.add_typer(scaffold_app,
              name="scaffold",
              help="Manage scaffolding of machine learning projects")

if __name__ == "__main__":
    app()
