# このリンクからセットアップする

このリポジトリは、Macを主とし、WindowsではLively Wallpaperを使って、同じグッピー24匹・8色・Balanced・24fpsの水槽を動かすためのソースと導入手順です。

## Claude Code・Codexに渡す文

> https://github.com/ryoga-atelier/2026-09-28-deskworlds をこのPCにセットアップしてください。README.md、START-HERE.md、AGENTS.mdを読み、OSと必要な道具を確認してください。採用版の魚・水景・24fpsを保ち、Macでは専用アプリ、WindowsではLively Wallpaperを使って導入し、実画面と操作を確認してください。既存環境は削除せず保存してください。アクセス権・OSの許可が必要なところだけ本人に引き継ぎ、未確認を成功扱いにしないでください。

リポジトリはPRIVATEです。受け取る人のGitHubアカウントを招待するか、所有者自身の認証済み環境で開きます。AIがリンクを読めない場合は、本人がGitHubにログインして招待を承諾してください。パスワード・トークンをチャットへ貼る必要はありません。ブラウザーだけで動くクラウドAIには、PCへのインストール権限はありません。対象PCで動くClaude CodeやCodexを使います。

## 取得

Gitと認証が揃っていれば、保存して使い続けるフォルダーで次を実行します。

~~~sh
git clone --recurse-submodules https://github.com/ryoga-atelier/2026-09-28-deskworlds.git
cd 2026-09-28-deskworlds
~~~

GitHub CLIが設定済みなら gh repo clone ryoga-atelier/2026-09-28-deskworlds -- --recurse-submodules でも取得できます。GitHubのDownload ZIPは上流のsubmoduleを含まないので、ソースからの導入にはGit cloneを使います。

## OSごとの入口

| OS | 環境の確認 | 導入 | 詳しい手順 |
|---|---|---|---|
| Mac | python3 setup.py doctor | python3 setup.py install | [Mac](docs/MACOS.md) |
| Windows | py -3 setup.py doctor | py -3 setup.py install | [Windows](docs/WINDOWS.md) |

setup-macos.command と setup-windows.cmd も同じ入口です。オプションを渡す場合はPythonから実行します。doctorは環境の診断だけを行い、アプリや壁紙を変更しません。上流が未取得ならbuild/install時に固定版を取得します。現行の導入版はv29-r16です。

## AI担当の手順と完了判定

1. OS、GitHubのアクセス権、Python 3.10以上を確認する。Macの開発ツールやWindowsのLively等が不足していれば、各OSの手順で用意する。認証・利用条件の同意・OSの権限画面は本人に操作してもらう。
2. doctorを通す。Macはbuildでコンパイルと署名検査、WindowsはbuildでLively ZIPを作る。既存の魚のデザインを変更しない。
3. 開発用検査をするならNode.js 22以上を用意し、下のverifyを実行する。
4. installを実行する。Macの旧アプリはrollbackへ移動。WindowsはLivelyライブラリ内の新しい専用フォルダーへ追加し、既存の壁紙や設定を上書きしない。
5. 実画面で魚が泳ぐこと、Feed、Pause/Resume、デスクトップ操作を確認する。WindowsのCLI送信成功やブラウザーでの描画だけでは、Windows壁紙の動作確認にならない。
6. 自動起動は登録と実際の再ログインを分ける。実スリープ・復帰・再ログインの未実施分を記録する。利用者の作業を中断するログアウトや再起動を勝手に行わない。
7. 実行したコマンド、採用版、実際に見た結果、未確認、元へ戻す方法を短く報告する。

~~~sh
# Macはpython3、Windowsはpy -3を使用
python3 setup.py verify
~~~

独自に新しいMac/Windowsホストを実装し直す必要はありません。既存の入口で導入し、失敗があればログに沿って該当箇所だけ修正します。GitHub Actionsの結果と実機の確認範囲は [対応状況](docs/PLATFORM-STATUS.md) を参照してください。
