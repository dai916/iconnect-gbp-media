# GA4 で AI 経由の流入と予約を計測する手順

AIチャットからの流入は、参照元ドメインで見分けられる「チャットAI経由」（計測できる）と、
Google検索と区別できない「AI Overviews / AIモード経由」（計測できない）の2種類がある。
ここでは前者を確実に取り、後者は問診票（`intake-question.md`）で補う。

## 0. 既存のGA4設定（2026-09-25 確認済み）

| 項目 | 内容 |
|---|---|
| 対象サイト | `https://iconnect-ortho.com/`（WordPress・Xserver） |
| 測定ID / プロパティID | `G-V9ECX6FNG1` / `352420487` |
| タグの入れ方 | GTM `GTM-5BVCBHW`（制作会社アウトカムがテーマ `header.php` に直書き）。GA4タグはGTM内 |
| 権限 | 院長アカウントは **閲覧者のみ**。管理系（チャネルグループ作成・イベント編集）はアウトカム |
| キーイベント（予約CV） | `web_予約`（WEB予約リンク）/ `denwa_yoyaku`（電話）/ `line_yoyaku`（LINE）/ `form_submit`（フォーム） |
| `src=` の記録方法 | カスタムディメンションもGTM転写も無い。**ランディングページのクエリ文字列**（`landingPagePlusQueryString`）にそのまま残る。参照元/メディアはGA4の自動判定のまま |
| APIでの取得 | 非公開リポジトリ `dai916/iconnect-column` の `scripts/sources/ga4.py`（週次レポート）と `ga4-adhoc.yml`（任意クエリ・読み取り専用） |
| 既知の不具合 | GTM内に同一測定IDのGoogleタグが重複登録され、エンゲージメント時間が0秒になる（2026-08-26 判明・アウトカムへ修正依頼中） |

### 予約完了は取れない

予約システム `omorikyousei.reserve.ne.jp` は外部ドメインで、完了画面にタグを置けない。
本CV（`reservation_complete`）は作らず、既存の4キーイベント（予約リンクのタップ）を「予約アクション」として使う。

## 1. チャネルグループは作らなくてよい

GA4のデフォルトチャネルグループに **`AI Assistant`** が既に存在し、chatgpt.com・gemini.google.com・perplexity・copilot 等を自動で分類している
（2026-09-25 のAPI応答で `sessionDefaultChannelGroup = "AI Assistant"` を確認）。
閲覧者権限ではカスタムチャネルグループを作れないので、この標準チャネルをそのまま使う。

見落としを防ぐため、月次の確認では参照元の正規表現でも突き合わせる（§3）。

## 2. 重要な事実：claude.ai は参照元に出ない

2026-01-01〜2026-09-24 の全期間で、参照元が `claude` `anthropic` のセッションは **0件**。
AI経由の参照元はほぼ chatgpt.com で、他は perplexity / gemini / copilot / felo が年に数件ずつ。

一方で院内には「Claudeで調べて来た」初診相談が毎月数人いる。理由はどちらか、または両方。

- Claude の回答内リンクを開いても参照元が送られず `Direct` に入る
- Claude は医院名を答えるだけで、患者は次に Google で医院名を検索して来る（`Organic Search` の指名検索に入る）

**したがって Claude 由来は GA4 では取れない。問診票の「AIに聞いた」設問が唯一の一次データ**になる。
GA4 で追う補助指標は次の2つ。

1. `AI Assistant` チャネルのセッションと予約アクション（ChatGPT等の実数。Claude の代理指標）
2. Search Console の指名検索（「アイコネクト」「アイコネクト 大森」等）の月次推移（Claude が名前を答えた結果を拾う）

## 3. 月次で見る方法

### 管理画面（閲覧者権限で可）

- レポート → 集客 → トラフィック獲得 → 行に `AI Assistant` があるか確認。指標は「セッション」「キーイベント」
- 探索 → 自由形式：ディメンション「セッションの参照元」× 指標「セッション」「キーイベント」に、参照元フィルタ（正規表現一致）

```
(claude|anthropic|chatgpt|openai|perplexity|gemini|copilot|bing\.com|you\.com|felo|genspark)
```

### API（`iconnect-column` の ga4-adhoc ワークフロー）

`gh workflow run ga4-adhoc.yml -R dai916/iconnect-column -f 'queries=<JSON>'` に次を渡す。
結果は Actions のログに出るだけで、どこにも保存されない。

```json
[
 {"name":"AI経由セッション","body":{
   "dateRanges":[{"startDate":"2026-06-01","endDate":"yesterday"}],
   "dimensions":[{"name":"sessionSourceMedium"}],
   "metrics":[{"name":"sessions"},{"name":"totalUsers"},{"name":"engagedSessions"}],
   "dimensionFilter":{"filter":{"fieldName":"sessionSource","stringFilter":{"matchType":"PARTIAL_REGEXP",
     "value":"(claude|anthropic|chatgpt|openai|perplexity|gemini|copilot|bing\\.com|you\\.com|felo|genspark)"}}},
   "orderBys":[{"metric":{"metricName":"sessions"},"desc":true}]}},
 {"name":"AI経由の予約アクション","body":{
   "dateRanges":[{"startDate":"2026-06-01","endDate":"yesterday"}],
   "dimensions":[{"name":"sessionSource"},{"name":"eventName"}],
   "metrics":[{"name":"eventCount"}],
   "dimensionFilter":{"andGroup":{"expressions":[
     {"filter":{"fieldName":"sessionSource","stringFilter":{"matchType":"PARTIAL_REGEXP",
       "value":"(claude|anthropic|chatgpt|openai|perplexity|gemini|copilot|bing\\.com|you\\.com|felo|genspark)"}}},
     {"filter":{"fieldName":"eventName","inListFilter":{"values":["web_予約","denwa_yoyaku","line_yoyaku","form_submit"]}}}]}}}},
 {"name":"AI経由の月次推移","body":{
   "dateRanges":[{"startDate":"2026-01-01","endDate":"yesterday"}],
   "dimensions":[{"name":"yearMonth"},{"name":"sessionSource"}],
   "metrics":[{"name":"sessions"}],
   "dimensionFilter":{"filter":{"fieldName":"sessionSource","stringFilter":{"matchType":"PARTIAL_REGEXP",
     "value":"(claude|anthropic|chatgpt|openai|perplexity|gemini|copilot|bing\\.com|you\\.com|felo|genspark)"}}},
   "orderBys":[{"dimension":{"dimensionName":"yearMonth"}}]}},
 {"name":"AI経由のランディングページ","body":{
   "dateRanges":[{"startDate":"2026-06-01","endDate":"yesterday"}],
   "dimensions":[{"name":"landingPagePlusQueryString"},{"name":"sessionSource"}],
   "metrics":[{"name":"sessions"}],
   "dimensionFilter":{"filter":{"fieldName":"sessionSource","stringFilter":{"matchType":"PARTIAL_REGEXP",
     "value":"(claude|anthropic|chatgpt|openai|perplexity|gemini|copilot|bing\\.com|you\\.com|felo|genspark)"}}},
   "orderBys":[{"metric":{"metricName":"sessions"},"desc":true}]}}
]
```

月次の数値は公開リポジトリには置かず、Obsidian（`AI検索対策/`）と `intake-question.md` の記録シートに転記する。

## 4. 自院が管理するリンクの目印（既存の `src=` 方式に合わせる）

GBPのウェブサイト欄はすでに `https://iconnect-ortho.com/?src=gbp_site` に変更済み（2026-09-21）。
`src` はランディングページのクエリ文字列として GA4 に残るので、レポートでは
`landingPagePlusQueryString` が `src=gbp_site` を含むセッションを数える（週次レポートの LP 集計と同じ方法）。
新しく置くリンクも同じ `src=` 方式で揃え、UTMと混在させない。

| 置き場所 | URL例 |
|---|---|
| GBP のウェブサイト欄（設定済み） | `https://iconnect-ortho.com/?src=gbp_site` |
| GBP 投稿内のリンク | `https://iconnect-ortho.com/lp-consultation?src=gbp` （既存投稿と同じ） |
| Instagram / Threads プロフィール | `https://iconnect-ortho.com/?src=instagram` / `?src=threads` |

AIは自院サイトを直接引用するため、AI経由の流入に目印は付けられない。AI経由は §1 のチャネルで見る。

## 5. 注意

- 参照元が `(direct)` の中にもAI経由が混ざる（アプリ内ブラウザからの遷移、Claude からの遷移）。問診票の回答と合わせて解釈する。
- 予約システムは外部ドメインのため、参照元は「予約リンクのタップ」までしか追えない。来院数・契約数は院内実数（GMO予約システムの月次）で突き合わせる。
- `iconnect-column` の OAuth トークンは GCP アプリが「テスト」のままだと 7 日で失効する。週次レポートが止まったら `scripts/setup_google_oauth.py` を再実行する。
