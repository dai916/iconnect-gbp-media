# GA4 で AI 経由の流入と予約を計測する手順

AIチャットからの流入は、参照元ドメインで見分けられる「チャットAI経由」（計測できる）と、
Google検索と区別できない「AI Overviews / AIモード経由」（計測できない）の2種類がある。
ここでは前者を確実に取る。

## 1. カスタムチャネルグループ「AI Referral」を作る

GA4 管理 → データの表示 → チャネルグループ → 新しいチャネルグループ を作成し、
先頭に次のチャネルを追加する（上にあるほど優先される）。

- チャネル名：`AI Referral`
- 条件：参照元（source）が正規表現に一致

```
^(claude\.ai|chatgpt\.com|chat\.openai\.com|perplexity\.ai|gemini\.google\.com|copilot\.microsoft\.com|www\.bing\.com/chat|you\.com|felo\.ai|genspark\.ai)$
```

Copilot は参照元が `bing.com` になる場合があるので、必要なら別チャネルに分ける。

## 2. 予約完了をコンバージョン（キーイベント）にする

- 予約フォーム送信の完了ページ（またはサンクス表示）で `reservation_complete` イベントを送る。
- 外部予約システム（EPARK等）に遷移する場合は、遷移リンクのクリックを `reservation_click` として計測する。
- GA4 管理 → イベント → キーイベントとしてマークする。

## 3. 見るレポート

- 探索 → 自由形式：ディメンション「セッションのデフォルトチャネルグループ（作成したグループ）」× 指標「セッション」「キーイベント（reservation_complete）」
- 月次で `AI Referral` の行を `01-measurement/intake-question.md` の記録シートに転記する。

## 4. 自院が管理するリンクの目印（既存の `src=` 方式に合わせる）

GBPのウェブサイト欄はすでに `https://iconnect-ortho.com/?src=gbp_site` に変更済みで、GA4側で `src` を拾う設定がある（2026-09-21 GMBセッション）。
新しく置くリンクも同じ `src=` 方式で揃え、UTMと混在させない。

| 置き場所 | URL例 |
|---|---|
| GBP のウェブサイト欄（設定済み） | `https://iconnect-ortho.com/?src=gbp_site` |
| GBP 投稿内のリンク | `https://iconnect-ortho.com/contact?src=gbp_post` |
| Instagram / Threads プロフィール | `https://iconnect-ortho.com/?src=instagram` / `?src=threads` |

AIは自院サイトを直接引用するため、AI経由の流入に目印は付けられない。AI経由は上記1のチャネル（参照元ドメイン）で見る。

【要確認】`src` がGA4でどう記録されているか（カスタムディメンション名、またはGTMで `session_source` に転写しているか）。
「ホームページコラム検証結果」セッションのGA4設定メモを参照して埋める。

## 5. 注意

- 参照元が `(direct)` の中にもAI経由が混ざる（アプリ内ブラウザからの遷移など）。問診票の回答と合わせて解釈する。
- クロスドメインで予約システムに飛ぶ場合、遷移先ドメインを「参照元除外」に入れないと参照元が途切れる。
