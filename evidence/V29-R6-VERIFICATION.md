# v29 r6 — 腹部輪郭と鱗の細分化

更新日: 2026-09-29 11:11 JST  
状態: Macアプリへ導入済み。実機WebViewで描画を確認。見た目の最終合格は未取得。

## 変更

- 鱗の配置を27×8列から34×11列へ細分化し、鱗縁のアンチエイリアス幅と局所色のコントラストを調整した。黒い格子ではなく、体色に沿う弧を狙っている。
- 腹部を暖色の外縁、象牙色の主面、淡い中央反射の3層に分けた。
- 白い腹の上側に、エラ蓋の境界を追う小さなくぼみを追加した。
- 尻びれ付け根では輪郭を浅くへこませ、黒くならない灰茶色の局所陰影を加えた。
- 魚の体形、24匹と8色系統、水草・水面・泡・砂、Balanced設定は変えていない。

## 写真比較と実機表示

同じ横向き・照明・色条件でv27、v28、r6を並べた比較PNGを保存した。PNGは魚3版の比較部で、本人写真はレビューHTMLの上部に併置している。右端が今回のr6。鱗はr5より細かくなり、腹部の象牙色と局所的なエラ・尻びれ境界が残る。拡大画像では見分けられるが、通常の壁紙距離ではこの細部はまだ控えめで、写真と同等の写実表現とは扱わない。本人の最終判断は未取得。

- 比較画像: [`evidence/bronze-gradient-v29-side-2-photo-detail1-20260929T020636Z.png`](evidence/bronze-gradient-v29-side-2-photo-detail1-20260929T020636Z.png)
- r6拡大: [`evidence/bronze-gradient-v29-r6-champagne-detail-20260929T020636Z.png`](evidence/bronze-gradient-v29-r6-champagne-detail-20260929T020636Z.png)
- r5の粗い鱗を確認した拡大: [`evidence/bronze-gradient-v29-r5-champagne-detail-20260929T020144Z.png`](evidence/bronze-gradient-v29-r5-champagne-detail-20260929T020144Z.png)

## 検証結果

- 固定した上流コミット `3950c45ef5798ed2df9f78037994bcddacebbb01` は変更なし。
- `upstream/deskworlds` で `npm run check` と `npm test` が成功。
- v29腹部・鱗テスト、v28互換テスト、魚形状・24匹の色割当、胴体寸法、living-waterテストが成功。
- `python3 scripts/provision.py install --variant guppy-v29` が成功。バックアップは [`rollback/20260929T111050429971+0900/`](rollback/20260929T111050429971+0900/) に保存。
- インストール済みの `photo-material.js` と `fish-anatomy-base.js` のSHA-256は候補ソースと一致。コード署名検証成功。
- `gui/501/com.chaselean.deskworlds` は `RunAtLoad` 登録・稼働中（PID 51278）。実際のログインし直し後の自動起動は未確認。
- MacアプリのWKWebViewで水槽を撮影確認。実行ログにWebGL2、24匹、Balanced、30 fps、動作中が記録された。これはアプリ内WebViewであり、DockやFinderを含むデスクトップ全体の確認ではない。

## 未確認

- Dock・メニュー・ドラッグ操作と実カーソルへの反応。
- 実スリープからの復帰、実際のログアウト・再ログイン。
- 表示中・ウィンドウに隠れた時・停止中の負荷比較、停止時にフレームが増えないこと。
- 8色すべての実機表示と60秒以上の旋回・遊泳を実機で確認すること。
- 本人による今回の見た目の合否。

## 検証コマンドの補足

検証初回に案件ルートでnpmコマンドを実行し、上流ではなく親`apps`パッケージのMiraiCheckテストと`npm ci`が起動した。この結果は上流検証として数えていない。親リポジトリで確認できた追跡対象の変更は既存のAGENTS.md変更のみで、以後の上流検査は`upstream/deskworlds`を作業ディレクトリにして再実行し、成功を確認した。
