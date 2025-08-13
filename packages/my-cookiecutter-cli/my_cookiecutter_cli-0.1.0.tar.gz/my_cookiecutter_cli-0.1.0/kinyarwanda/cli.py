import os
import click
from cookiecutter.main import cookiecutter

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")

@click.group()
def cli():
    """ABST - Scaffold your project fast."""
    pass

@cli.command()
@click.argument("project_name")
def new(project_name):
    """Create a new project using the default template."""
    click.echo(f"Creating project: {project_name}")
    cookiecutter(TEMPLATE_DIR, extra_context={"project_slug": project_name})

if __name__ == "__main__":
    cli()
