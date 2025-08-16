# glazzbocks_cli/commands/databricks_pull.py
from pathlib import Path
import typer

from glazzbocks.integrations.databricks.client import DatabricksConnector
from glazzbocks.runtime.loaders import load_model, load_table
from glazzbocks.reporting.build import build_report_run

app = typer.Typer()

def databricks_pull(
    config: Path = typer.Option(..., "--config", help="Path to databricks.yaml"),
    model: str = typer.Option(..., "--model", help="Registered model name"),
    version: int = typer.Option(..., "--version", help="Model version"),
    train: Path = typer.Option(..., "--train", help="CSV path for train data"),
    test: Path = typer.Option(..., "--test", help="CSV path for test data"),
    target: str = typer.Option(..., "--target", help="Target column name"),
    out: Path = typer.Option(Path("outputs_llm"), "--out", help="Output directory"),
):
    # 1) Connect & download
    conn = DatabricksConnector.from_yaml(str(config))
    local_model_path = conn.download_model(model, version)
    typer.secho(f"✅ Pulled {model} v{version} to {local_model_path}", fg=typer.colors.GREEN)

    # 2) Load artifacts and build report (same flow as azureml-pull)
    m = load_model(local_model_path)
    df_train = load_table(str(train))
    df_test  = load_table(str(test))

    result_paths = build_report_run(
        m, df_train, df_test, target_col=target, out_dir=str(out)
    )

    typer.echo("✔ Report generated:")
    typer.echo(f"  - {out}/report.md")
    typer.echo(f"  - {out}/model_facts.json")
