from pathlib import Path
import typer
from glazzbocks.runtime.loaders import load_model, load_table
from glazzbocks.reporting.build import build_report_run

def report(
    model: Path = typer.Argument(..., help="Path to pickled/sklearn model"),
    train: Path = typer.Argument(..., help="CSV/Parquet train data"),
    test: Path = typer.Argument(..., help="CSV/Parquet test data"),
    target: str = typer.Argument(..., help="Target column name"),
    out: Path = typer.Option(Path("outputs_llm"), "--out", help="Output directory"),
):
    m = load_model(str(model))
    df_train = load_table(str(train))
    df_test = load_table(str(test))
    out.mkdir(parents=True, exist_ok=True)
    build_report_run(m, df_train, df_test, target, out_dir=str(out))
    typer.secho(f"✔ Report generated in {out}", fg=typer.colors.GREEN)
