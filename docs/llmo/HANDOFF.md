# 引継書：Claude由来の初診相談予約を最大化する（LLMO）

作成日: 2026-09-25 ／ 前セッション: 「AI検索対策1」（session_01SshBwxUVBpWzwauLk5SYQq）
リポジトリ: `dai916/iconnect-gbp-media` ブランチ `claude/iconect-omori-patient-acquisition-uvyvik`（push済み、PR未作成）

## 1. 目的と結論

アイコネクト大森矯正歯科に「Claudeで検索して来た」初診相談患者が毎月数人いる。これを計測し、意図的に増やす。

Claude は Brave 検索 + Google Maps/Places を使い、複数ソースで一致する事実を持つ医院だけを推薦する。勝ち筋は
①NAP（名称・住所・電話）の全ネット統一 ②サイトの「一文で答えられる」構造（FAQ・料金・限定解除4要件・JSON-LD）
③第三者の裏取り（Googleレビュー・まとめ記事・学会）④無料初診相談・24時間WEB予約が最初の画面にある導線。
最初に計測を入れる。

## 2. 完了したこと

| 項目 | 状態 |
|---|---|
| 戦略調査（Claudeの仕組み、国内外事例、医療広告ガイドライン） | 完了。`docs/llmo/README.md` に要約 |
| 実装キット `docs/llmo/`（20ファイル） | 作成・push済み（コミット 5cbce91, 5fc0a90） |
| 問診票に「AIに聞いた（Claude/ChatGPT/Gemini）」設問を追加 | **院長が実施済み**（2026-09-25） |
| GitHub push 権限（Claude GitHub App のインストール） | 解消済み |
| GA4手順書のリンク目印を既存の `src=` 方式に統一 | 完了（`?src=gbp_post` 等） |

`docs/llmo/` の構成
- `01-measurement/` 問診票設問、GA4 AI Referral 手順、固定プロンプト20本（`prompts.csv`）、計測ツール `tools/measure_ai_mentions.py`
- `02-website/` robots.txt / llms.txt 例、JSON-LD（Dentist, FAQPage）、FAQ草案35問、サイト点検表（限定解除4要件）
- `03-listings/` NAP統一チェックリスト（13掲載先）、まとめ記事2本の掲載確認
- `04-gbp/` 投稿本文ガイド（毎回「医院の事実」を1つ入れる）、Q&A欄の種10問
- `05-compliance/` 医療広告ガイドライン・ステマ規制・AI向け逆効果行為

## 3. 判明している事実（他セッションの記録より）

- GBPのウェブサイト欄は `https://iconnect-ortho.com/?src=gbp_site` に変更済みで、GA4で `src` を追跡している（2026-09-21「GMB新セッション作成」）。
  → iconnect-ortho.com にGA4は導入済み。流入元の目印は UTM ではなく `src=` パラメータ方式。
- コラム投稿の効果測定でGA4を使っている（院長談）。設定の詳細は Mac 上のセッション
  「ホームページコラム検証結果」（サイドバー「HPコラム」グループ）と Obsidian にある。クラウド側からは読めない。

## 4. 未完了・次にやること（優先順）

1. **GA4の既存設定を把握する**  
   Macで「ホームページコラム検証結果」を開き、次を入力して回答を新セッションに貼る:
   ```
   GA4の設定内容をまとめてください。測定ID、srcパラメータの記録方法（カスタムディメンション名かGTMか）、
   コンバージョンやキーイベントの一覧、コラム効果測定で見ている指標、管理画面の権限の有無。
   ```
   または Obsidian のGA4ノート（.md）を添付。
2. **GA4に AI Referral チャネルを作る**（`01-measurement/ga4-ai-referral.md` §1）  
   管理 → データの表示 → チャネルグループ → 新規作成。参照元の正規表現:
   `^(claude\.ai|chatgpt\.com|chat\.openai\.com|perplexity\.ai|gemini\.google\.com|copilot\.microsoft\.com|you\.com|felo\.ai|genspark\.ai)$`  
   院長はチャネルグループ画面のスクリーンショットを送る予定だった。予約完了イベント（`reservation_complete`）は既存の仕組みに合わせて設計し直す。
3. **`【要確認】` の事実確定**（院内）: 住所の番地・ビル名・階、電話、平日診療時間・休診日、料金の範囲と内訳、所属学会・資格、予約URL。  
   `02-website/`・`03-listings/`・`04-gbp/` のテンプレートに一括反映。
4. **ベースライン計測**: `cd docs/llmo/01-measurement/tools && pip install -r requirements.txt && export ANTHROPIC_API_KEY=... && python measure_ai_mentions.py --only P01,P18` で動作確認 → 20本実行。  
   ChatGPT/Gemini は同じ20本を手動で投げ `results/manual-YYYYMM.csv` に記録。結果本文は `.gitignore` 済み。
5. **制作会社に依頼**: `02-website/page-checklist.md` を渡す（JSON-LD、robots.txt、llms.txt、FAQ公開、限定解除表記）。
6. **NAP統一**: `03-listings/nap-checklist.md` のマスター表記を確定し、13掲載先を点検。メディカルドック「大森駅の矯正歯科8医院」への掲載有無を確認。
7. **GBP投稿本文の変更**: `04-gbp/post-text-guidelines.md` のルールを非公開リポジトリ `iconnect-gbp` の投稿生成に反映（本文に事実を1つ＋ `?src=gbp_post` リンク）。
8. 必要なら PR 作成（ブランチはpush済み。PRはまだ作っていない）。

## 5. 注意事項

- このリポジトリは **公開**。認証情報・患者情報・計測結果の本文は置かない（README に明記済み）。
- `measure_ai_mentions.py` は SDK 1.7.0 で構文とパラメータ名を確認済みだが、APIキーがなく実行は未検証。
- iconnect-ortho.com 本体はクラウド環境からアクセス遮断されており、既存の JSON-LD / robots.txt は未確認。
- 医療広告ガイドライン: 体験談・比較優良・保証表現は書かない。レビューの対価提供はしない。

## 6. 参照

- ブランチ: https://github.com/dai916/iconnect-gbp-media/tree/claude/iconect-omori-patient-acquisition-uvyvik
- 関連セッション: 「GMB新セッション作成」（`src=gbp_site` 設定）、「ホームページコラム検証結果」（GA4設定）、「アイコネクト大森矯正歯科集客レポート」（2026年9月 集客レポート artifact: https://claude.ai/artifact/9QSDwQSm1QzRfZf46jiCVX）
- 調査ソースは `docs/llmo/README.md` 末尾および前セッションの初回回答を参照
