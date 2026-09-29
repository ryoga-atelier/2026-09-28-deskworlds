# AIセットアップの入口

- 対応済みの入口は setup.py doctor / build / install / verify。OSを自動判定する。手順の正本はSTART-HERE.md。新しい魚や壁紙ホストを作り直さない。
- Macは専用アプリ、WindowsはLively Wallpaper。Windowsだけの橋渡しは platforms/windows/。共通の魚の採用版はv29-r16、24匹・8色・24fps。
- 公開リポジトリの取得にGitHub認証を求めない。外部ツールの規約同意、OSの許可は本人の操作へ引き継ぐ。認証情報をチャットで求めず、セキュリティ設定を無効化しない。
- 他の壁紙・OS全体の設定・ライブラリを上書きしない。Macの既存物はrollbackへ退避。Windowsは専用の新フォルダーを追加。
- doctor/build/CLI命令の送信、ブラウザーでの描画、実デスクトップ、スリープ・ログインを別々に確認する。未実施を合格にしない。
- 共通検査は setup.py verify。新しいセットアップ部分はPython unittest・npm test・npm run test:browser。GitHub ActionsはWindowsとMacで動かす。

# Deskworlds のローカル導入

セットアップの依頼では最初に START-HERE.md と対象OSの docs/MACOS.md または docs/WINDOWS.md を読む。他のPCに ~/.agents や作者個人の作業パスを用意する必要はない。このリポジトリだけで手順を完結する。元のworkspace内では親の規範も継承する。

- 上流は `upstream/deskworlds`。commit `3950c45ef5798ed2df9f78037994bcddacebbb01` を維持し、原本を変更しない。
- 現在の導入済み・既定は `guppy-v29`（`bronze-gradient-guppy-v29-r16`）。共通の基盤は `custom/guppy/`、現在の上書きは `custom/realism-v29/` と `scripts/exhibit_overlay.py`。v16は `--variant guppy-v16`、v14は `--variant guppy`、保存した立体試作v15は `--variant guppy-v15`。ビルド用コピーにだけ適用する。`install --variant original` で上流の外見へ戻せる。
- 相対参照を維持するため構造固定。上流 install/uninstall は直接実行しない。
- 導入は `python3 scripts/provision.py install`。既存物は rollback に移動し、削除しない。
- テストは上流の `npm run check` と `npm test`、アプリのビルドと実画面。
- グッピー変更時は適用済みのプレビューで既存テストと `node scripts/check-guppy-v17.mjs <プレビューのパス>` と `check-v17.mjs`（現行のスリムな腹・尾柄・厚みの寸法を検査。check-v25は過去版用として保持）、`check-living-water.mjs`、実際のWebGL描画を確認する。
- 元の壁紙、システムのアクセシビリティ設定、他アプリの設定は変更しない。
- 自動起動解除は `python3 scripts/provision.py disable-autostart`。アプリ退避は `python3 scripts/provision.py retire`。
- 証拠は evidence、操作説明は README.md。実測と未確認を分ける。

- v21は本人指定のv19/v20統合版。v19の色を局所的に戻し、v20の腹と尾、写真に沿う頭・後方胴を維持。v20単体は未導入。今後も別の外観案へ無断で切り替えない。

- v22はv21の形状と水槽を維持した材質修正。背中・眼の暗色と明るい腹、背鰭・尻鰭の淡色と透明部、尾の黒根元・有色中央・透明先端を本人の指定に合わせる。変更の正本は photo-material.js。

- v22の暗色面は本人不採用。v23で地肌と鱗の細線へ戻した。v24は頭→尾の淡→濃、広く丸い白い腹、細くなる顔、尾と背鰭の透明領域を追加。写真との完全一致は未達。

- v25-r2は白い腹の上端を物体座標の楕円にし、背中から頭も滑らかな凸曲線へ変更。v24の濃淡と透明ヒレを保持。写真との同一性や本人の最終合格は未達。

- 直前のv26-r2は本人の「細身に・赤茶を弱め・鱗を見せる」指定を反映。腹の曲線と上端の楕円を保ち、体高・横幅を絞った。灰紫を帯びる銀色、頭から尾の濃淡、細い鱗と反射。尾と背鰭の透明領域、水槽は保持。

- 直前のv27は透明ヒレに家族色の薄いベール・鰭条・細い横脈、腹の後方付け根に柔らかな灰茶色、胴に細鱗を加えた。v26のスリム体型・8色・水景を保持。
- 過去版v28は写真比較を元に、赤茶一色を避けた暖色ブロンズ〜銀色の背側、明るく不均一な真珠色の腹、個体差のある鱗と8系統の体色、尾の青い色層を調整した。細身の輪郭・水景・24匹は維持。Macアプリへの導入とWebView描画を確認済み。壁紙サイズでは鱗の規則性と鰭条の弱さがまだ残り、写真への最終合格ではない。実機メニュー・Dock・ドラッグ・スリープ復帰・再ログインとv28の負荷測定は未確認。

- 現行v29-r12は本人の「黒が薄すぎる・頭から尾の濃淡・背中にも尾の色」指定を反映。r11の腹の曲線・鱗・頬を保ち、黒斑を明瞭にし、後方の胴と背中に各個体の色を重ねた。場面ソースの変更はphoto-material.jsのみ。Mac導入とロック解除後の実機外観を確認。起動時は両ウィンドウの描画進行を確認。残る実機操作・長時間動作・負荷はV29-VERIFICATION.mdに記録。

- 現行v29-r13は写真との差11項目（尾・背・尻鰭の着色と鰭条、胴の色相、腹上縁の帯、網目状の鱗、真珠色の腹、黒斑、銀色の虹彩、頭と吻先、艶）を調整。記録はV29-R13-VERIFICATION.md。
- 現行v29-r14は指示と写真の総点検22項目で残った6か所（エラの独自色、頬のきらめき、目を小さく見せる虹彩、目元・頭頂・背の稜線の暗い層、鱗の網目、四角い継ぎ目）を調整。点検表はGUPPY-CHECKLIST-V29-R14.md。
- 現行v29-r15はr14の見た目を保った軽量化（魚の三角形約4割、影1024、胴の粒感画像を省略）と、隠れた画面・眠った画面のページを60秒後に破棄する処理（scripts/native_release.py、ビルド用Swiftのみ）。r14時点の「外部モニター停止」は誤りで、止まっていたのは覆われたMac本体の画面。記録はV29-R15-VERIFICATION.md、負荷計測はscripts/measure-r15.py。
- 現行v29-r16はr15に本人選択の毎秒24コマ（Balanced上限24、カーソル追跡24回/秒）を加えた版。記録はV29-R15-VERIFICATION.mdの末尾。
- Macの`retained-frame-v1`は魚の版r16を維持した表示保持の修正。隠れて60秒後のページ解放時には水槽の静止画を残し、再読込の初回描画後に切り替える。`scripts/check-native-retained-frame.py`は実際のAppKit/WKWebViewを使う遷移検査（Macデスクトップセッションが必要）。上流やシステム壁紙を変更しない。

## GitHub保存（2026-09-29）

- 本人所有の保存・配布先: https://github.com/ryoga-atelier/2026-09-28-deskworlds 。2026-09-30の本人指示で公開へ変更。作者のリポジトリへpushしない。
- 元Macの作業フォルダでは、保存用の独立Gitチェックアウトは `build/github-session-repo/`。親appsの `web-app` リモートと混同しない。新規cloneした場合はそのclone自身を使用する。
- `SESSION-HISTORY.md`、`SOURCES-AND-LICENSES.md`、`GITHUB-ARCHIVE-VERIFICATION.md` が経緯・出典・保存検証の入口。過去プレビューは `history/` と `scripts/restore-preview.py` で復元する。大量のbuild/rollbackコピーと全動画はローカルのみ。
