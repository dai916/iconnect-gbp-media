# AI言及率 計測ツール

`measure_ai_mentions.py` は `../prompts.csv` の質問を Claude（Web検索あり）に投げ、
自院名の言及有無・競合名・引用URLを `../results/claude-YYYYMMDD-HHMM.csv` に保存する。

```bash
cd docs/llmo/01-measurement/tools
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # 公開リポジトリなので必ず環境変数で
python measure_ai_mentions.py             # 20本すべて
python measure_ai_mentions.py --only P01,P18   # 一部だけ
```

- 既定モデルは `claude-opus-5`。安全分類器による拒否時のサーバー側フォールバック（`fallbacks="default"`）を
  有効にしている。不要なら `--no-fallbacks`。
- 1回の実行（20本）で Web 検索を含むため、数百円程度のAPI費用がかかる想定。月1回で十分。
- 結果の `results/` は `.gitignore` で除外している（回答本文に第三者の情報が含まれるため公開しない）。
  月次の集計値（言及率、競合出現回数）だけを `../intake-question.md` の記録シートへ転記する。

## ChatGPT / Gemini の手動計測

同じ `prompts.csv` の20本を ChatGPT（検索ON）と Gemini に手で投げ、
`results/manual-YYYYMM.csv` に `id, engine, mentioned, competitors, cited_urls` で記録する。
