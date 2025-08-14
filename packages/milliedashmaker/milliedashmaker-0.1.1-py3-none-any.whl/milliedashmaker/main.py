import click
from pathlib import Path
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException
import os
import shutil



@click.group()
@click.pass_context
def dashed(ctx: click.Context):
    """
    A custom cli tool to create a basic dash ag grid project.

    Commands include:
    create : dashed new [PROJECT_NAME]
    delete: dashed delete [PROJECT_NAME] -> Only deletes projects from the context folder

    """
    projects_directory_prnt = Path.home()
    projects_directory = Path(projects_directory_prnt / "dash_projects")
    projects_directory.mkdir(parents=True, exist_ok=True)
    ctx.ensure_object(dict)

    ctx.obj["projects_directory"] = projects_directory


@dashed.command()
@click.pass_context
@click.argument("folder_name")
@click.option('--template',
              type=click.Choice(['ag-grid', 'dash-knob', 'dash-table'], case_sensitive=False),
    prompt="Choose a template",
    help="Select a template from the available choices.",
               default="ag-grid")
@click.option("--author", default=Path.home().name)
def new(ctx:click.Context, folder_name, template, author):
    parent_dir = Path(ctx.obj["projects_directory"])
    
    
    new_dir = parent_dir / folder_name
    if Path(new_dir).exists():
        click.echo("Project with name already exists. Please choose a different name.")
    else:
     
            
        if template == "ag-grid":
            template_path = os.path.join(os.path.dirname(__file__), "ag-grid-cookiecutter")
        elif template == 'dash-knob':
            template_path = os.path.join(os.path.dirname(__file__), "dash-knob-cookiecutter")
        else:
            template_path = os.path.join(os.path.dirname(__file__), "dash-table-cookiecutter")
        try:
            cookiecutter(
            template=Path(template_path).as_posix(),
            output_dir=new_dir,
            no_input=True,
            # overwrite all cookiecutter.json's terms
            extra_context={
                "author": author, 
                "folder_name": folder_name

            },
        )
        except OutputDirExistsException:
            click.echo("Please create a new directory")

        

    # print(baking_path)
    print(new_dir)

@dashed.command()
@click.pass_context
@click.argument("folder_name")
def delete(ctx:click.Context, folder_name):

    parent_dir = Path(ctx.obj["projects_directory"])
    
    new_dir = parent_dir / folder_name
    try:

        shutil.rmtree(Path(new_dir))

        click.echo("Folder deleted successfully.")
    except Exception as e:
        click.echo(e)
