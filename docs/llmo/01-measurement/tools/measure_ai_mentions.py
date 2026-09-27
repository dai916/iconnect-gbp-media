#!/usr/bin/env python3
"""AI言及率の月次計測ツール。

prompts.csv の各質問を Claude（Web検索あり）に投げ、
  - 自院名が回答に含まれたか
  - 競合名が含まれたか
  - 引用されたURL
を CSV / JSON に記録する。月1回、同じプロンプトで実行して推移を見る。

使い方:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...   # または `ant auth login`
    python measure_ai_mentions.py --prompts ../prompts.csv --out ../results

注意:
    - このツールは Anthropic API 経由の Claude の回答を測る。claude.ai（消費者向け）の回答と
      完全に同じではないが、同じ Web 検索基盤を使うため傾向の把握には十分。
    - ChatGPT / Gemini は手動で同じプロンプトを投げ、results/manual-YYYYMM.csv に記録する。
    - 公開リポジトリなので API キーはコードに書かない。
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import re
import sys
import time

import anthropic

CLINIC_ALIASES = [
    "アイコネクト大森矯正歯科",
    "アイコネクト",
    "iconnect-ortho.com",
    "iconnect ortho",
]

# 計測時点で大森駅周辺の「おすすめ」記事に載っている競合（必要に応じて更新）
COMPETITORS = [
    "大森駅前矯正歯科",
    "大森沢田通り歯科",
    "おおもり北口歯科",
    "大森CT歯科",
    "Luz大森アプル歯科",
    "大森矯正歯科クリニック",
    "大森イースト歯科",
]

SYSTEM_PROMPT = (
    "あなたは東京都在住の一般の利用者から質問を受けるアシスタントです。"
    "必ずWeb検索を使って最新情報を確認し、具体的な医院名を挙げて日本語で回答してください。"
)

TOKYO_LOCATION = {
    "type": "approximate",
    "city": "Shinagawa",
    "region": "Tokyo",
    "country": "JP",
    "timezone": "Asia/Tokyo",
}


def load_prompts(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return [row for row in csv.DictReader(f)]


def extract_text_and_urls(message) -> tuple[str, list[str]]:
    texts: list[str] = []
    urls: list[str] = []
    for block in message.content:
        btype = getattr(block, "type", "")
        if btype == "text":
            texts.append(block.text)
            for cit in getattr(block, "citations", None) or []:
                url = getattr(cit, "url", None)
                if url:
                    urls.append(url)
        elif btype == "web_search_tool_result":
            content = getattr(block, "content", None)
            # 成功時は list、エラー時は error オブジェクト
            if isinstance(content, list):
                for item in content:
                    url = getattr(item, "url", None)
                    if url:
                        urls.append(url)
    text = "\n".join(texts)
    # 本文中の生URLも拾う
    urls.extend(re.findall(r"https?://[^\s)\]」』>]+", text))
    seen: set[str] = set()
    uniq = [u for u in urls if not (u in seen or seen.add(u))]
    return text, uniq


def ask(client: anthropic.Anthropic, model: str, prompt: str, use_fallbacks: bool):
    kwargs = dict(
        model=model,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 6,
                "user_location": TOKYO_LOCATION,
            }
        ],
        output_config={"effort": "medium"},
    )
    if use_fallbacks:
        # 安全分類器による拒否時に別モデルへ自動フォールバック（通常この用途では発火しない）
        return client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **kwargs,
        )
    return client.messages.create(**kwargs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompts", default="../prompts.csv", help="prompts.csv のパス")
    ap.add_argument("--out", default="../results", help="結果の出力ディレクトリ")
    ap.add_argument("--model", default="claude-opus-5", help="使用モデル")
    ap.add_argument("--only", default="", help="実行するID（例: P01,P05）。空なら全部")
    ap.add_argument("--no-fallbacks", action="store_true", help="server-side fallbacks を使わない")
    ap.add_argument("--sleep", type=float, default=2.0, help="リクエスト間の待機秒")
    args = ap.parse_args()

    here = pathlib.Path(__file__).resolve().parent
    prompts_path = (here / args.prompts).resolve()
    out_dir = (here / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    prompts = load_prompts(prompts_path)
    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        prompts = [p for p in prompts if p["id"] in wanted]
    if not prompts:
        print("実行対象のプロンプトがありません", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()
    stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y%m%d-%H%M")
    rows: list[dict] = []

    for i, p in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {p['id']} {p['prompt'][:40]}…", flush=True)
        try:
            msg = ask(client, args.model, p["prompt"], use_fallbacks=not args.no_fallbacks)
        except anthropic.RateLimitError as e:
            print(f"  rate limited, 60秒待機: {e}", file=sys.stderr)
            time.sleep(60)
            msg = ask(client, args.model, p["prompt"], use_fallbacks=not args.no_fallbacks)
        except anthropic.APIStatusError as e:
            print(f"  API error {e.status_code}: {e.message}", file=sys.stderr)
            rows.append({**p, "error": str(e)})
            continue
        except anthropic.APIConnectionError as e:
            print(f"  connection error: {e}", file=sys.stderr)
            rows.append({**p, "error": str(e)})
            continue

        if msg.stop_reason == "refusal":
            rows.append({**p, "error": "refusal"})
            continue

        text, urls = extract_text_and_urls(msg)
        mentioned = any(a.lower() in text.lower() for a in CLINIC_ALIASES)
        own_urls = [u for u in urls if "iconnect-ortho.com" in u]
        comps = [c for c in COMPETITORS if c in text]
        # 自院が何番目に出てくるか（0 = 未言及）
        first_pos = min((text.find(a) for a in CLINIC_ALIASES if a in text), default=-1)
        rank = 0
        if first_pos >= 0:
            earlier = [c for c in comps if 0 <= text.find(c) < first_pos]
            rank = len(earlier) + 1

        rows.append(
            {
                **p,
                "run": stamp,
                "model": getattr(msg, "model", args.model),
                "mentioned": int(mentioned),
                "rank_among_named": rank,
                "own_urls": " ".join(own_urls),
                "competitors": " / ".join(comps),
                "cited_urls": " ".join(urls),
                "answer": text,
                "error": "",
            }
        )
        time.sleep(args.sleep)

    # 保存
    json_path = out_dir / f"claude-{stamp}.json"
    csv_path = out_dir / f"claude-{stamp}.csv"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = [
        "id", "category", "prompt", "run", "model", "mentioned", "rank_among_named",
        "own_urls", "competitors", "cited_urls", "error",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    ok = [r for r in rows if not r.get("error")]
    hit = sum(int(r.get("mentioned", 0)) for r in ok)
    print()
    print(f"言及率: {hit}/{len(ok)} = {hit / len(ok) * 100:.0f}%" if ok else "有効な回答なし")
    comp_count: dict[str, int] = {}
    for r in ok:
        for c in filter(None, r.get("competitors", "").split(" / ")):
            comp_count[c] = comp_count.get(c, 0) + 1
    if comp_count:
        print("競合の出現回数:")
        for c, n in sorted(comp_count.items(), key=lambda x: -x[1]):
            print(f"  {n:2d}  {c}")
    print(f"保存: {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
