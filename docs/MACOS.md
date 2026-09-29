# Macへの導入

macOS 13以上、Python 3.10以上、Git、Xcode Command Line Toolsが必要です。Intel/Apple Siliconとも、そのMacのCPU向けにSwiftでビルドします。検査も行う場合はNode.js 22以上を用意します。実際の対応確認範囲はPLATFORM-STATUS.mdに記録します。

## 準備

1. START-HERE.mdの手順でリポジトリを取得します。
2. python3 --version で版を確認します。古い場合は python.org のmacOS用インストーラー、または既に使っているHomebrewのPythonを利用します。
3. xcode-select -p で開発ツールを確認します。未導入なら xcode-select --install を実行し、本人が表示される案内を完了します。Xcodeの利用条件の同意やOSの権限設定をスクリプトで迂回しません。

~~~sh
python3 setup.py doctor
python3 setup.py build
python3 setup.py install
~~~

インストールは、ビルドと署名検査に成功してから既存物を保存退避します。アプリは ~/Applications/Deskworlds.app に配置し、専用LaunchAgent com.chaselean.deskworlds を登録します。ログは、このcloneの evidence/deskworlds-runtime.log に出ます。cloneは移動・削除せず保管してください。移動した場合は新しい場所でinstallを実行し、ログの保存先を更新します。

## 操作と確認

- メニューバーのDeskworldsでFeed、Pause/Resume、Quit。
- WorldはRiverbedがグッピー水槽です。他のWorldを既に保存していた場合はRiverbedを選択します。
- 全体の「視差効果を減らす」は保持します。初回が停止していればアプリのResumeで再開できます。
- 通常もブラウザなどの背後もBalanced・最大24コマ/秒。完全に隠れていても魚・水草・泡を動かし続け、ページのメモリを保持します。停止方式よりCPU/GPU負荷とメモリ使用量は増えるため、負荷を優先する時はPauseを使います。
- 一時停止・低電力モード・スリープ・画面ロック中は描画を止めます。スリープ／ロックが60秒続いた場合だけ、直前の水槽の静止画を残してページのメモリを手放します。復帰後は静止画の裏で読み込み、水槽を描けてから切り替えます。元の壁紙には戻しません。静止画を取得できなければ停止中のページを残します。
- 設定の保存、カーソル反応、Dock・ファイルのドラッグ、スリープ復帰・ログイン起動を実画面で確認します。手順と照合方法はSETUP-VERIFICATION.mdです。

## 元へ戻す

~~~sh
# 自動起動を解除し、水槽を停止。アプリは残す
python3 scripts/provision.py disable-autostart
# アプリも削除せず、このcloneのrollbackへ保存退避
python3 scripts/provision.py retire
~~~

単に一時的に元の背景を出すならQuitです。元のmacOS壁紙は変更しません。macOSが出す署名・実行の許可が必要なら、本人が対象を確認して通常のOS操作で許可してください。Gatekeeper全体を無効化する手順は使いません。
