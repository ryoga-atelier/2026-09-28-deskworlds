# v17 — 本人が選んだミックスグッピーへの調整

状態：導入・技術検証済み。見た目の本人による最終承認と、下記の実機操作は未完了。

## 基準と実装

本人が「マジでこのイメージ」と確認した [ペットバルーンのミックスグッピー](https://www.petballoon.net/product/65143) の販売水槽・青系個体を基準とした。担当も本文と2写真を直接観察。暗い水・裸の販売槽・SOLD OUT文字はコピーしない。以前の品種写真、ベタ、長大なリボンは採用基準から外す。

- 青系写真の上の個体を代表に、細すぎた尾柄を厚くし、胴から滑らかにつないだ。尾柄/前腹部の高さは約0.52。前腹部の深さ0.188、幅0.091モデル単位。頭・眼と模様を形状に追随させ、法線は再計算・確認した。
- 大きすぎた扇形の尾と背びれを小さくし、丸みを持つ尾、後方の小さい背びれ、腹側の小さい膜へ調整。写真の比率は投影と姿勢の影響を含む概算で、生物学的計測値ではない。
- 銀色〜淡い黄褐色の地肌を保ち、後半部に乗る色柄・透明な膜・細いヒレ条を分けた。素材の黒い斑の寄与を下げ、白い単色個体ばかりにならないよう色柄の強さと尾の比率を個体ごとに固定した。
- 24匹・8色系統。水色3、赤〜ワイン3、シャンパン〜ライム4、青緑2、桃色2、紫〜パステル4、黄土3、コバルト3。青・黄色を含め、同じ魚の全身を一色で塗り替えない。
- 本人確認済みv14の左右の茂みと中央の砂道をそのまま使用。水面・水草・泡・砂の動きと24匹、Riverbed、Balanced、自動起動を維持。

## 見た目の判定と限界

代表個体を拡大と普段の壁紙に近いサイズで比較し、8色の横・斜め・正面・背面、約65秒の全周回転と通常遊泳を確認。実機WKWebViewの表示も確認した。明らかな眼の埋まり、ヒレの脱落、旋回の反転は観察されなかった。細い尾柄と大きな扇による違和感は軽減し、選ばれた写真の胴とヒレの比率へ近づいた。

一方、写真にある鱗や内臓の透け、雌雄・成長段階による形の幅を完全に再現したわけではない。2枚の既存AI生成素材を使うため共通した模様は残る。眼の輪郭・体色境界にはCGらしさがある。「本物と区別不能」「本人の外観承認済み」とはしない。

背景は写真風の色画像と推定深度による2.5D、魚は3D。真の立体葉・正確な水流・屈折・散乱の計算ではない。立体化する場合も、本人が選んだ青・素材・左右の茂み・中央の砂道を基準にする。

![インストール済みMacアプリの描画](evidence/mixed-v17-native.png)

WKWebView診断スナップショット。アイコンやDockを含むデスクトップ合成スクリーンショットではない。

## 検証結果

| 項目 | 結果 |
|---|---|
| 構文・既存9テスト | 成功。v17-r2-check.log / v17-r2-tests.log |
| 形状・法線・個体割当・接続 | 成功。v17-r2-anatomy.log / v17-r2-shape-swim.log。有限頂点・単位法線、24個体、600フレームの連続性 |
| 水・砂の挙動 | 底付近で移動する魚のみ砂を発生、上限96、静止・中層では発生しない。zero-dt停止、消散・解放も成功。v17-r2-living-water.log |
| 給餌 | プレビュー実操作で10粒投入、7粒捕食・3粒溶解、9回の捕食動作。v17-browser-operations.json |
| Pause/Resume | プレビュー実操作とネイティブ保存設定の両方を確認。ブラウザでは停止5099枚、再開後5555枚。ネイティブの90秒は下表 |
| Macビルド・導入 | 成功。v17-install.log。検査コピーと導入済み87ファイル一致。v17-integrity.json |
| 再起動・設定保持 | 専用ジョブの停止・起動、Riverbedとpaused復元を確認。ネイティブメニュー操作とは別 |
| 通常のFinder操作 | v16で同じネイティブウィンドウコードの新規窓、Windowメニュー、外部画面へ移動・拡大・閉じるを確認。v17被覆測定でも実操作 |
| 実機メニュー・Dock・ドラッグ・カーソル | 未確認。操作ツールがメニュー/Dock対象とデスクトップのドラッグ座標を取得できない。本人へ実施を依頼済み |
| 実スリープ/復帰・再ログイン | 未実施。登録だけを合格にしない。SETUP-VERIFICATION.mdの手順とOSイベント・描画を照合する |

v16で同じ姿勢・素材の影なし／補助光を比較すると、影だけの変更は小さく、写真素材を外すと暗い斑が大きく減った。v17ではその素材の混合率と黒斑の寄与を下げた。同一条件の青い代表個体で、眼・ヒレを避けた胴中央の内側504画素の中間L*は34.65→66.18、白つぶれ（全RGB250以上）は両版0%。evidence/v17-luminance-patch.jsonにROIを保存。身体全体や全色の集計ではなく、この局所比較だけの値。v17全色の照明別比較は未実施。旧v14のL*値は検査ハーネス不備により撤回済みで流用しない。

## 実機負荷

| 各90秒 | v16 CPU | v17 CPU | v17 描画 |
|---|---:|---:|---|
| 表示中 | 15.03% | 15.60% | 1665×1081: 0枚 (0.00fps) / 1789×1006: 2701枚 (30.01fps) |
| 両画面をウィンドウで被覆 | 0.40% | 0.33% | 1665×1081: 0枚 (0.00fps) / 1789×1006: 0枚 (0.00fps) |
| 一時停止中 | 0.15% | 0.14% | 1789×1006: 0枚 (0.00fps) / 1665×1081: 0枚 (0.00fps) |

2画面・Balanced。表示中は外部画面1789×1006が表示、内蔵1665×1081は隠れた条件。被覆時はFinderで外部も覆った。停止はアプリ固有設定で行い、最後にpaused=0とRiverbedへ復元。CPU100%=1コア。本体＋専用WebKit4プロセスのlibproc実測。実描画はレンダー投入数で、モニターの表示時刻ではない。GPU使用率と電池持ちは未測定。

| 版・状態 | プロセス | footprint MiB 開始→終了（最大） |
|---|---|---:|
| v16final 表示中 | Deskworlds PID91942 | 34.0 → 23.1 (34.0) |
| v16final 表示中 | com.apple.WebKit.GPU PID91944 | 457.3 → 271.8 (457.3) |
| v16final 表示中 | com.apple.WebKit.Networking PID91945 | 4.1 → 5.1 (5.1) |
| v16final 表示中 | com.apple.WebKit.WebContent PID91946 | 430.6 → 345.1 (430.6) |
| v16final 表示中 | com.apple.WebKit.WebContent PID91947 | 376.5 → 348.0 (376.5) |
| v16final 両画面をウィンドウで被覆 | Deskworlds PID91942 | 23.0 → 23.0 (23.0) |
| v16final 両画面をウィンドウで被覆 | com.apple.WebKit.GPU PID91944 | 36.4 → 36.4 (36.4) |
| v16final 両画面をウィンドウで被覆 | com.apple.WebKit.Networking PID91945 | 5.1 → 5.0 (5.1) |
| v16final 両画面をウィンドウで被覆 | com.apple.WebKit.WebContent PID91946 | 344.9 → 343.8 (345.0) |
| v16final 両画面をウィンドウで被覆 | com.apple.WebKit.WebContent PID91947 | 350.2 → 349.2 (350.7) |
| v16final 一時停止中 | Deskworlds PID94362 | 22.4 → 22.2 (22.4) |
| v16final 一時停止中 | com.apple.WebKit.GPU PID94364 | 77.3 → 36.7 (77.3) |
| v16final 一時停止中 | com.apple.WebKit.Networking PID94365 | 5.1 → 4.9 (5.1) |
| v16final 一時停止中 | com.apple.WebKit.WebContent PID94366 | 349.0 → 343.4 (349.0) |
| v16final 一時停止中 | com.apple.WebKit.WebContent PID94367 | 330.4 → 324.8 (330.4) |
| v17final 表示中 | Deskworlds PID14432 | 30.2 → 23.0 (30.2) |
| v17final 表示中 | com.apple.WebKit.GPU PID14434 | 400.6 → 325.5 (400.6) |
| v17final 表示中 | com.apple.WebKit.Networking PID14435 | 4.1 → 5.1 (5.1) |
| v17final 表示中 | com.apple.WebKit.WebContent PID14436 | 421.5 → 342.8 (421.5) |
| v17final 表示中 | com.apple.WebKit.WebContent PID14437 | 378.3 → 346.7 (378.3) |
| v17final 両画面をウィンドウで被覆 | Deskworlds PID14432 | 23.1 → 23.0 (23.1) |
| v17final 両画面をウィンドウで被覆 | com.apple.WebKit.GPU PID14434 | 36.4 → 36.4 (36.4) |
| v17final 両画面をウィンドウで被覆 | com.apple.WebKit.Networking PID14435 | 5.1 → 5.1 (5.1) |
| v17final 両画面をウィンドウで被覆 | com.apple.WebKit.WebContent PID14436 | 342.8 → 342.9 (343.2) |
| v17final 両画面をウィンドウで被覆 | com.apple.WebKit.WebContent PID14437 | 350.7 → 349.5 (350.7) |
| v17final 一時停止中 | Deskworlds PID15330 | 28.3 → 21.1 (28.3) |
| v17final 一時停止中 | com.apple.WebKit.GPU PID15332 | 67.7 → 31.2 (67.7) |
| v17final 一時停止中 | com.apple.WebKit.Networking PID15333 | 4.1 → 4.1 (4.1) |
| v17final 一時停止中 | com.apple.WebKit.WebContent PID15334 | 346.6 → 341.0 (346.6) |
| v17final 一時停止中 | com.apple.WebKit.WebContent PID15335 | 328.5 → 323.5 (328.5) |

メモリはphysical footprint。共有ページを含むのでPID間で合算しない。各1回90秒の結果で長期リークや負荷差の有意性を断定しない。生データはv17-performance-summary.json、v17final-*.json。

## 版と復旧

- 導入：2026-09-28T22:46:40.291515+09:00。`guppy-v17`。
- 上流固定：`3950c45ef5798ed2df9f78037994bcddacebbb01`、原本clean。Three.js r180。
- 正本 custom/realism-v17/。検査コピー preview/mixed-guppy-v17-r2/。
- アプリ `/Users/ryoga-atelier/Applications/Deskworlds.app`。旧v16の退避 `/Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/rollback/20260928T224640180929+0900`。
- 元の壁紙・macOSアクセシビリティ設定はv16時点のハッシュと一致。
- 起動・Feed・Pause/Resume・Quitと非破壊の退避はREADME.md。残る本人操作はSETUP-VERIFICATION.md。
- 参照・権利：custom/realism-v17/REFERENCES.md。店の写真は観察のみでアプリへ転載していない。
