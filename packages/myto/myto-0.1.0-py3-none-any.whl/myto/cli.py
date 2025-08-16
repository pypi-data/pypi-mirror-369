import click
from myto.base.runner import MyToRunner

@click.group()
def cli():
    pass

@cli.command()
@click.argument("basepath")
@click.option("--runnervar", default="runner", help="Variable name for the runner in the script")
@click.option("--path", multiple=True, help="additional paths to be merged")
def run(basepath, runnervar, path):
    """
    Run the MyToRunner from a specified base path.
    
    Args:
        basepath (str): The base path where the MyToRunner script is located.
        runnervar (str): The variable name for the runner in the script.
        path (tuple): Additional paths to be merged into the runner.
    """

    runner = MyToRunner()
    runner.mergeFromPath(basepath, targetVar=runnervar)

    if path:
        for p in path:
            runner.mergeFromPath(p, targetVar=runnervar)

    runner.run()

    click.echo("All tasks completed.")