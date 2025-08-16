# python -m glazzbocks.runtime --model ... --train ... --test ... --target y
import argparse
from glazzbocks.runtime.loaders import load_model, load_table
from glazzbocks.reporting.build import build_report_run

def main():
    ap = argparse.ArgumentParser(description="Glazzbocks runtime quick runner")
    ap.add_argument("--model", required=True)
    ap.add_argument("--train", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--out", default="outputs_llm")
    args = ap.parse_args()

    m = load_model(args.model)
    df_train = load_table(args.train)
    df_test  = load_table(args.test)
    build_report_run(m, df_train, df_test, args.target, out_dir=args.out)
    print(f"Report written to {args.out}")

if __name__ == "__main__":
    main()
