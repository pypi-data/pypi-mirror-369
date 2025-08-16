from pathlib import Path
import typer
from glazzbocks.integrations.azureml.client import AzureMLConnector
from glazzbocks.runtime.loaders import load_model, load_table
from glazzbocks.reporting.build import build_report_run

def azureml_pull(
    config: Path = typer.Option(..., "--config", help="Path to azureml.yaml"),
    model: str = typer.Option(..., "--model", help="Registered Azure ML model name"),
    version: int = typer.Option(None, "--version", help="Model version (default: latest)"),
    train: Path = typer.Option(..., "--train", help="CSV/Parquet train data"),
    test: Path = typer.Option(..., "--test", help="CSV/Parquet test data"),
    target: str = typer.Option(..., "--target", help="Target column"),
    out: Path = typer.Option(Path("outputs_llm"), "--out", help="Output directory"),
):
    conn = AzureMLConnector.from_yaml(str(config))
    local_model_path = conn.download_model(name=model, version=version)
    m = load_model(local_model_path)
    df_train = load_table(str(train))
    df_test = load_table(str(test))
    out.mkdir(parents=True, exist_ok=True)
    build_report_run(m, df_train, df_test, target, out_dir=str(out))
    typer.secho(f"✔ Report generated in {out}", fg=typer.colors.GREEN)
