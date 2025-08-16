import importlib.metadata as im
import typer

# Import subcommand functions
from .commands.report import report
from .commands.azureml_pull import azureml_pull
from .commands.databricks_pull import databricks_pull   # <-- ADD THIS

app = typer.Typer(
    name="glazzbocks",
    help="Glazzbocks CLI – glassbox ML with diagnostics and AI reporting",
    no_args_is_help=True,
    add_completion=False,
)

# Register subcommands
app.command("report")(report)
app.command("azureml-pull")(azureml_pull)
app.command("databricks-pull")(databricks_pull)         # <-- ADD THIS

def _version_callback(value: bool):
    if value:
        typer.echo(f"glazzbocks {im.version('glazzbocks')}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show glazzbocks package version and exit.",
        is_eager=True,
        callback=_version_callback,
    )
):
    """
    Use one of the subcommands below. Try:
      glazzbocks report --help
      glazzbocks azureml-pull --help
      glazzbocks databricks-pull --help
    """
    return
