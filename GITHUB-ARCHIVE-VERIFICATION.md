# GitHub保存の確認（2026-09-29）

保存先: https://github.com/ryoga-atelier/2026-09-28-deskworlds （本人所有・非公開）

## 今回の確認

- GitHub上の所有者 `ryoga-atelier`、可視性 `PRIVATE` を照合。
- 追加ソース282ファイルを作業元とバイト単位で照合し、差なし。
- 過去プレビュー105版・12,138ファイルを422個の内容へ重複排除。全422個のSHA-256と全マニフェストの参照・サイズを照合。
- 別の保存用チェックアウトへr16、r14、r15、比較依存v18-r8を復元。
- 復元したr16で `npm run check`、`npm test`、`check-photo-guppy-v29`、`check-photo-guppy-v28`、`check-guppy-v17`、`check-v17`、`check-living-water` がすべて成功。
- GitHubから新たに取得した上流2件の固定コミットを照合。上流の作業ツリーは変更なし。
- 保存用チェックアウトで `python3 scripts/provision.py build` 成功。Swift最適化ビルド、アドホック署名、署名検査、Info.plist検査まで完了。
- 秘密鍵・代表的なトークン形式・機密ファイル名・JSONの機密フィールドをローカルで走査し、候補0件。秘密情報のファイルは収録しない。
- 代表画像7枚と実測・検証の証拠を収録。全動画、全画面撮影、常時ログ、ビルドとアプリの退避コピーはローカルに保持。詳細は収録一覧を参照。
- 導入済みアプリのmetadataは `bronze-gradient-guppy-v29-r16`。この保存作業でインストール・再起動・設定変更は行っていない。

生の検査結果は `evidence/github-archive-checks.json`、ビルドは `evidence/github-archive-build.json`、導入版の照合は `evidence/github-archive-installed-version.json`。

過去のMarkdownの改行用空白、保存patch、上流由来blob等に `git diff --check` の空白警告があります。歴史的資料のバイト一致を保つため変更していません。今回作成したREADME・出典・履歴・保存用スクリプトには同警告がありません。

## 残る確認

本作業はソースと経緯のGitHub保存です。メニュー・Dock・ドラッグ、実スリープ・再ログインの未確認を解消したことにはしません。実機の見た目を今回撮り直していません。採用版の負荷の数値は同日15時台までの既存測定で、保存時に再測定した値ではありません。

## 保存構成の理由

全作業フォルダには約10GBの生成・退避コピーがあります。復元に必要な内容を重複排除し、約111MiB（Git圧縮前、submodule本体を除く）へ整理しました。個別ファイルの最大は約9.4MBです。過去版はスナップショットで保持し、実在しない時点のGit履歴は作っていません。
