# v29 r9 — 腹の白と斑を一つの輪郭へ

更新: 2026-09-29T12:24:24.675093+09:00  
状態: Macへ反映済み。今回の腹の調整を比較画面と実機WKWebViewで確認。全セットアップ完了とは区別する。

## 調整

- 尻びれ付け根の斑を灰褐色へ持ち上げ、濃度係数を0.93から0.67へ弱めた。局所的な光の吸収も弱めた。
- 付け根を基準に斑の高さを半分へ圧縮。横方向の幅は維持。領域の標本被覆率（しきい値0.25）はr8の3.918%から1.919%へ。
- 白い腹と斑に共通の外周・内層を使う。斑で腹の外形を別途削る計算をやめ、斑を腹の内層に収めた。銀色の外層は白・灰褐色をまとめて囲み、その内側で色が分かれる。
- 小さくした目・湾曲したエラ・上向きの口、胴寸法、ヒレ、24匹・8色、水景・動き・Balancedを維持。上書き12ファイルのうち、r8から変わった場面ソースはphoto-material.jsだけ。

## 確認と保存物

- 横向き比較: evidence/bronze-gradient-v29-side-7-photo-detail1-20260929T032038Z.png
- 上下余白を除いた比較: evidence/v29-r9-final-comparison.png
- 斜め比較: evidence/bronze-gradient-v29-oblique-7-photo-detail1-20260929T032136Z.png
- 比較ページ: review/shape-v29-r9.html。左r8、右r9。同一の色・光・姿勢。
- 横と斜めで、低く薄い斑が腹の輪郭内に収まり、白い腹との外周が連続することを確認。実機WKWebViewでも反映を観測。ネイティブ画像のファイル保存はしていない。
- 適用済みpreview/bronze-gradient-guppy-v29-r9でnpm run check、npm test成功。check-photo-guppy-v29、check-photo-guppy-v28、check-guppy-v17、check-v17、check-living-water成功。腹の共通化後に構文・上流テスト・材質検査を再実行した。
- 旧r8の旋回動画は旧版の記録として保持。今回新しい65秒動画・90秒負荷比較は実施していない。
- ソース差分: evidence/v29-r9-material.patch。r8の記録: evidence/V29-R8-VERIFICATION.md。
- ビルド・署名検証・導入ソース12ファイルの一致・LaunchAgentの稼働を確認。evidence/v29-r9-final-integrity.json。

## 導入

- 上流: 3950c45ef5798ed2df9f78037994bcddacebbb01
- 版: bronze-gradient-guppy-v29-r9
- ビルド: /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/build/20260929T122204597993+0900/Deskworlds.app
- r8のアプリとLaunchAgentの退避: /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/rollback/20260929T122207070102+0900/previous/
- PID（検証時）: 62731。RunAtLoadを確認。実再ログインは未実施。

## 残る確認

今回の変更は腹の外観調整。既存の全画面連続動作の問題、Macメニュー・Dock・ドラッグ・実カーソル反応、実スリープ・再ログイン、各90秒の負荷比較は未完了。魚の写実性と本人の見た目の最終合格も別に扱う。
