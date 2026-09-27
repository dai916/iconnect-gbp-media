# NAP（名称・住所・電話）統一チェックリスト

Claude は複数ソースを突き合わせて医院を特定する。表記ゆれがあると別の医院と判定されたり、確信が持てず名前を出さなくなる。
すべての掲載先で **1文字単位で同じ表記** にする。

## 正とする表記（マスター）（2026-09-26 院内確定）

| 項目 | マスター表記 |
|---|---|
| 正式名称 | アイコネクト大森矯正歯科 |
| 英語表記 | iConnect Omori Orthodontic Clinic |
| 住所 | 東京都品川区南大井6丁目28-9 大成ビル1階（数字は半角、ハイフンは半角） |
| 郵便番号 | 140-0013 |
| 電話 | 050-3138-3592（ハイフン2つ。JSON-LDでは +81-50-3138-3592） |
| 診療時間 | 10:30〜13:30／14:30〜19:00（月・火・水・金・土・日） |
| 休診日 | 木曜日・祝日 |
| URL | https://iconnect-ortho.com/ （末尾スラッシュあり、http/wwwなし） |
| WEB予約URL | https://omorikyousei.reserve.ne.jp/sp/index.php （`_gl=` などの追跡パラメータは付けない） |
| 診療科目 | 矯正歯科 |
| 院長 | 冨田 大介 |
| 最寄駅 | JR京浜東北線 大森駅 東口 徒歩1分 |
| Googleマップ | https://maps.app.goo.gl/yRmx6NjLhAxbRZDe7 |

公式サイト内でも「南大井６丁目２８−９」（全角）と「南大井6丁目28-9」（半角）が混在している（お問い合わせページと料金表ページ）。
マスターは半角に統一し、サイト側の全角表記は制作会社に修正を依頼する。

## 掲載先一覧と点検

| 掲載先 | URL | 名称 | 住所 | 電話 | 時間 | URL | 写真 | 確認日 |
|---|---|---|---|---|---|---|---|---|
| Googleビジネスプロフィール | https://maps.app.goo.gl/yRmx6NjLhAxbRZDe7 | | | | | | | |
| Apple Maps（Apple Business Connect） | 【要確認：未登録なら登録】 | | | | | | | |
| Yahoo!マップ / Yahoo!ロコ | 【要確認】 | | | | | | | |
| Bing Places | 【要確認：未登録なら登録】 | | | | | | | |
| 医療情報ネット（ナビイ） | https://www.iryou.teikyouseido.mhlw.go.jp/znk-web/juminkanja/S2430/initialize?kikanCd=3136300135&kikanKbn=3&prefCd=13 | | | | | | | |
| EPARK歯科 | https://haisha-yoyaku.jp/bun2sdental/detail/index/id/z200012208/ | | | | | | | |
| 矯正歯科ネット | https://www.kyousei-shika.net/clinic/174281/ | | | | | | | |
| メディカルドック（医院ページ） | https://medicaldoc.jp/clinic/398809/ | | | | | | | |
| ドクターズ・ファイル | https://doctorsfile.jp/h/212745/df/1/ | | | | | | | |
| 東京ドクターズ | https://tokyo-doctors.com/dentalList/84481/ | | | | | | | |
| Instagram | https://www.instagram.com/iconnect_ortho_official/ | | | | | | | |
| Threads | https://www.threads.com/@iconnect_ortho_official | | | | | | | |
| 品川区歯科医師会 会員名簿 | 【要確認：掲載の有無】 | | | | | | | |

## まとめ記事への掲載（AIの引用元になりやすい）

| 記事 | URL | 掲載状況 | 対応 |
|---|---|---|---|
| メディカルドック「大森駅の矯正歯科 おすすめ8医院」 | https://medicaldoc.jp/d/orthodontic/recommend-orthodontic/omori-st-kyousei/ | **未掲載**（2026-09-26 確認。本文に医院名なし） | 掲載条件を問い合わせ。医院ページ https://medicaldoc.jp/clinic/398809/ は存在する |
| Oh my teeth「大森の矯正歯科・マウスピース矯正13医院」 | https://www.oh-my-teeth.com/posts/orthodontics-in-omori | **未掲載**（2026-09-26 確認） | 同上 |
| その他「品川区 矯正歯科 おすすめ」「大森 矯正歯科 おすすめ」で上位の記事 | 月次で検索して追加 | | |

## 進め方

1. マスター表記を院内で確定し、この表の最上部を埋める。
2. 各掲載先を開き、マスターと1文字単位で比較。相違があれば修正申請。
3. 修正できたら確認日を記入。四半期に1回、全行を再点検。
