# v29 r10 — 薄さを保ち、大きな半円を腹の枠内へ

更新: 2026-09-29T12:31:50.250389+09:00  
状態: Macへ反映し、比較画面と実機WKWebViewの外観を確認。全セットアップの完了とは区別する。

## 今回の修正

r9は縦半分の斑を腹の内層へ収めたため、斑が小さくなり、白い腹の後端が見えすぎた。本人の最新指定に沿い、薄さは保持して大きな半円へ戻した。

- 斑の中心と縦横比をr8の大きな半円へ戻した。原マスクの標本被覆率はr9の1.919%からr8と同じ3.918%へ。
- r9で了承された灰褐色（0.105, 0.097, 0.079）と最大混合係数0.67を保持。r8の濃い黒には戻していない。
- 半円の見える範囲を広げ、淡い縁だけが残らないよう内部の色面を確保。
- 白と斑は同じ腹の外周を共有。斑は内層だけでなく外層にも届き、尖った後端の白い縁を目立ちにくくした。腹の枠の外へは塗らない。
- 眼・エラ・口・体型・ヒレ・24匹・8色・水景・動作はr9と同一。場面ソース12ファイルのうち変更はphoto-material.jsのみ。

## 比較と検証

- 最終横: evidence/bronze-gradient-v29-side-7-photo-detail1-20260929T032847Z.png
- 横の抜粋: evidence/v29-r10-final-comparison.png（上下の余白のみ除去）
- 斜め: evidence/bronze-gradient-v29-oblique-7-photo-detail1-20260929T032918Z.png
- review/shape-v29-r10.html は左r9、右r10。同じ個体・光・姿勢で比較。
- 横と斜めで、半円が上方まで広がり、白と共通の腹の枠に収まる表示を確認。Macでも反映を観測。ネイティブ画像ファイルは保存していない。
- r10適用済みプレビューでnpm run check、npm test、check-photo-guppy-v29、check-photo-guppy-v28、check-guppy-v17、check-v17、check-living-water成功。最後の色面の範囲調整後に構文・材質検査を再実行して成功。比較ページのコンソールエラーは0件。
- 新しい65秒動画・90秒負荷測定は実施していない。
- 差分: evidence/v29-r10-material.patch。r9記録: evidence/V29-R9-VERIFICATION.md。

## 導入

- 版: bronze-gradient-guppy-v29-r10
- 上流: 3950c45ef5798ed2df9f78037994bcddacebbb01
- ビルド: /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/build/20260929T122929687473+0900/Deskworlds.app
- r9のアプリとLaunchAgent: /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/rollback/20260929T122931884288+0900/previous/
- PID（検証時）: 78862。署名、導入ソース12ファイル一致、専用LaunchAgent稼働、RunAtLoadを確認。
- 記録: evidence/v29-r10-final-integrity.json

## 未完了

全画面の連続動作（一方のウィンドウが1フレームのまま）、Macメニュー・Dock・ドラッグ・実カーソル反応、実スリープ・再ログイン、負荷比較は残る。今回の腹の外観確認を、これらの合格や本人の最終合格に数えない。
