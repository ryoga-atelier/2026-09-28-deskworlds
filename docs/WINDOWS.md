# Windowsで同じ水槽を壁紙にする

Windows 11 x64を推奨します。ホストは無料の [Lively Wallpaper](https://www.rocksdanister.com/lively/) 2.2以上です。Windows 10はLively自身の対応範囲に従います。ARM版Windowsは未確認です。Windowsでの負荷や実デスクトップ検証はMacの結果と分けます。

## 必要なもの

- ソースから用意する場合: Git、Python 3.10以上、Node.js 22以上（npmを含む）。
- 完成した壁紙を動かす時: Lively Wallpaperのみ。常駐のPython/Nodeサーバーは不要です。

不足するものは公式サイト、または既に使えるWindows Package Managerで導入します。以下は本人の環境に必要なものだけ実行します。利用条件の同意・UAC・ログインは本人が行います。

~~~powershell
winget install --id Git.Git --exact
winget install --id Python.Python.3.12 --exact
winget install --id OpenJS.NodeJS.LTS --exact
winget install --id rocksdanister.LivelyWallpaper --exact
~~~

インストール後はターミナルを開き直し、Livelyを一度起動して初期画面を完了します。既存の設定やライブラリはそのまま使います。Microsoft Store版もZIPの手動取り込みに対応します。自動設定は実行ファイルを検出できる通常インストーラー版が扱いやすい構成です。

## 自動セットアップ

START-HERE.mdのGit clone後、PowerShellで次を実行します。

~~~powershell
py -3 setup.py doctor
py -3 setup.py build
py -3 setup.py install
~~~

buildは dist/windows/ に専用フォルダーとZIPを生成します。installは同じ処理に加え、LivelyのSettings.jsonからライブラリの場所だけを読み、新しい guppy-garden-r16-日時 フォルダーへコピーして、公式のsetwpコマンドを送信します。既存の水槽・他の壁紙・設定は上書きしません。既定はメイン画面です。

見つからない場合は場所を明示できます。--library は wallpapers の一つ上のLibraryフォルダーです。

~~~powershell
py -3 setup.py install --lively "C:\Users\YourName\AppData\Local\Programs\Lively Wallpaper\Lively.exe" --library "D:\Lively\Library" --monitor 1
~~~

CLIの終了成功は「表示命令を送れた」までです。ライブラリ内のGuppy Gardenを選び、デスクトップで実際に動いたことを確認してください。Livelyで個別画面・複製・全画面への配置を選べます。セットアップは他の画面や全体の配置設定を勝手に変更しません。

## ZIPから取り込む方法

1. buildが表示したZIPを使います。GitHub Actionsの成果物にもWindows用ZIPを保存します。ActionsのZIPの中にある、Guppy Garden本体のZIPを取り出してください。
2. Livelyを開き「＋ / Add Wallpaper」へ本体ZIPをドラッグします。
3. ライブラリのGuppy Gardenを選び、目的の画面に適用します。

GitHubのソース全体のDownload ZIPは、Livelyへ取り込むためのZIPではありません。

## 操作・省電力・解除

- Livelyでこの壁紙を右クリック → Customize / カスタマイズ。
- 「泳ぐ / Playing」で水槽だけを停止・再開。「餌やり / Feed」で給餌。
- 画面が隠れた時の一時停止や電池使用時の扱いはLivelyのPerformance設定を利用します。ホストから停止通知が来ると水槽側も描画を止めます。
- ログイン時の起動はLivelyの「Start with Windows」で設定します。このスクリプトはLively全体の設定を変更しません。
- 元の背景へ戻す時はLivelyの対象画面の壁紙を閉じます。自動起動を止めたい場合はStart with WindowsをOFFにします。
- 導入フォルダーは残ります。不要ならLivelyを閉じた後、そのGuppy Gardenフォルダーだけを別の場所へ退避できます。他の壁紙やライブラリ全体は削除しません。

Macの「隠れて60秒後のWKWebView破棄」はWindowsでは使いません。Windowsの停止・復帰・メモリ管理はLively/CEFに依存します。24fpsは共通ですが、Macと同じCPU/GPU/メモリ値になるとは限りません。

## 困った時

- CLIが成功しても表示されない: ライブラリ位置、モニター番号、Livelyの起動を確認し、ZIPからの取り込みを試します。
- 白い画面・描画エラー: Livelyを更新し、CEF/ChromiumのWebプレイヤーとGPUドライバーを確認します。Livelyのログと画面上のエラーを採取します。
- 動かない: CustomizeのPlaying、Livelyの一時停止・省電力設定、画面が別ウィンドウで隠れていないかを確認します。
- 餌が出ない: 停止中の餌やりは無効です。先に再開します。
- buildが失敗: Node.js 22以上とPython 3.10以上を確認し、エラーを保存します。上流の固定版や現行の魚を勝手に変更しません。

## 実装の根拠

- [Lively公式コマンド](https://github.com/rocksdanister/lively/wiki/Command-Line-Controls)
- [プロパティと操作](https://github.com/rocksdanister/lively/wiki/Web-Guide-IV-:-Interaction)
- [停止・再開通知](https://github.com/rocksdanister/lively/wiki/Web-Guide-V-:-System-Data#--pause-event)
- [メタデータの定義](https://github.com/rocksdanister/lively/blob/core-separation/src/Lively/Lively.Models/LivelyInfoModel.cs)

Lively自体はGPL-3.0で、このリポジトリに同梱していません。水槽と各素材の由来はSOURCES-AND-LICENSES.mdです。
