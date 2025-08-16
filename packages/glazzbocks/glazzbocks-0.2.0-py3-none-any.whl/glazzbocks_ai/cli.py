from openai import OpenAI
from .prompt_templates import SYSTEM_PROMPT, USER_PROMPT
import os, json
from pathlib import Path

def cmd_explain(args):
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY before running this command.")

    client = OpenAI()
    facts = json.loads(Path(args.facts).read_text(encoding="utf-8"))

    user = USER_PROMPT.format(facts_json=json.dumps(facts, ensure_ascii=False))
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    resp = client.chat.completions.create(
        model=model_name,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user},
        ],
    )
    text = resp.choices[0].message.content
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"Wrote {args.out}")
