# v14 — 明るい体色と自然な厚みのグッピー

Status: 実装反映・負荷測定済み。ただし利用者の最新評価により外観は不合格。稼働版は次候補の採用まで暫定保持。

## 採用内容

- 固定上流 `3950c45ef5798ed2df9f78037994bcddacebbb01` を変更せず、コピーへ適用。
- 採用候補 `preview/pearl-guppy-v14-r3`。色素PNGは既存2枚を保持し、地色・模様・ヒレを共通パレットで制御。
- 水色3、赤3、シャンパン4、青緑2、桃色2、薄紫4、淡い黄土色3、濃い青3（計24）。
- 腹側を滑らかに約12%、最大胴幅を18%増加。頭・尾柄は保持。眼とヒレ付け根も同じ連続変形を適用。法線は変形の逆転置で補正し、色素参照座標は変形前のままにする。
- 胴体0.78倍・ヒレ0.82倍の減光を除去。半球光0.42→0.64、前方補助光0.50→0.95、後方補助光0.42→0.62。露出1.06と背景構成は固定。
- 白い発光を足すのでなく、淡い地色と柔らかい反射・ヒレの透けを調整。瞳、鰓、尾の斑点を残す。

## 見た目

比較画面は同じ姿勢・画角・露出で、旧版、影なし、補助光強化、新素材+光+体型を並べた。素材と光の合成効果は確認できるが、最終列は体型も変えているため素材だけの厳密な寄与率ではない。

- 8系統の側面・斜め・正面・反対側を画像で点検。薄紫、水色、シャンパン、黄土色を区別できる。眼の埋没・ヒレ付け根の離脱・大きな模様の伸びは見つからなかった。
- 通常遊泳約65秒、薄紫の全周旋回約65秒、8色同時の全周旋回約65秒を録画。8色全周では正面から反対側まで繰り返し旋回して確認。
- 素材なしの代替描画でも8色を維持。検査UIで素材使用を無効化して確認したもので、実際の通信失敗試験ではない。
- 画像上の胴体固定領域の中央値L*は旧版42.5〜47.4→新66.0〜73.0。背景を除外するが模様は含むため、厳密な体色だけの測色ではない。目視と併用。領域内でRGB全成分が0.98を超える画素はゼロ。
- 影なしだけの改善はわずか。補助光だけではL*48.9〜53.5に留まり、素材の暗い地色の再配色が主要な改善になった。
- 限界：色素画像は2種類なので模様には共通性がある。8品種の生物学的な再現ではない。ヒレの揺れ・屈折・体型は近似。背景は写真風2.5Dのまま。

## コード・ブラウザ検査

採用候補r3で `npm run check` と既存9スイートの `npm test` が成功。形状・配色、グッピー、v10回帰、水粒子の専用検査も成功。最大胴幅比1.180000、最大腹変位0.009573。使用中の全頂点で有限な単位法線を確認。

初期候補では削除済みヒレの未使用頂点にゼロ法線があり、正規化時にNaNを検出。未使用点の法線を有限値にしてからr3を再検査した。上流原本は変更していない。

プレビューで停止前後の描画カウンターは4198→4198、水の時計139.8661→139.8661。再開後は5697、189.8001へ進んだ。給餌計20粒は12粒捕食・8粒消散・残り0。水草と水面は同じ時計、泡28、砂イベントの増加を確認。カーソル反応の既存自動テストは通ったが、今回の実機のマウス移動からの反応はまだ未確認。

IABのログに出典URLのないMutationObserver.observeエラーを1件確認。シーン停止やシェーダーエラーは起きず、魚・水と操作は継続。過去v13でも同様の記録があり、原因は未特定のため「ログエラーなし」とは記録しない。

## 実機検証

後述の実測・操作結果を追記する。

### 導入照合

Swift最適化ビルド、ad-hoc署名と厳格検証、plist検査が成功。導入先は `~/Applications/Deskworlds.app`。104ファイルがr3と一致。上流原本は固定コミット・差分なし。元の壁紙とアクセシビリティplistはv13時点とSHA256一致。`evidence/v14-installed-integrity.json`。

変更前のアプリとAgentは `rollback/20260928T205506131351+0900/previous/`、コード・文書は `rollback/v13-before-pearl-20260928T203313/`。現在のバイナリSHA256は `bdea775df20b27c01d6e8b45f78c9d3a1c1603a3eb6e4ee8fa6530762645ef09`。`evidence/manifest.json`。

Macアプリの実WebViewをCUAで目視。さらにアプリ内診断で `evidence/pearl-guppy-v14-native.png` を保存・再読込した。診断は最初の画面を4秒強制描画するため、負荷測定前に終え、再起動後の測定には含めていない。画像はデスクトップ全レイヤーの合成キャプチャではない。

保存した通常遊泳64.968秒、8色全周64.950秒をIABで終端まで再生し、両方ended=true、error=nullを確認。録画完了と再生完了を別々に確認した。

### 実操作の結果

| 項目 | 判定 | 根拠／残る確認 |
|---|---|---|
| Finderの普通の操作 | 観測済み | 新規ウィンドウ、Windowメニュー、外部画面へ移動、画面いっぱいに表示、閉じる |
| デスクトップのアイコン選択 | 観測済み | v14稼働時、CapCut.appがAX上selectedに変化。アプリは開いていない |
| 水槽のFeed/Pause/Resume/Quitメニュー | 未確認 | SystemUIServer取得が5秒でtimeout。キーボード経路も操作対象が得られない |
| Dock | 未確認 | Dock取得が5秒でtimeout |
| デスクトップのドラッグ | 未確認 | アイコンAXはあるがデスクトップ画像が白く、位置を取得できないため推測でドロップしない |
| 実カーソルから魚への反応 | 未確認 | 既存の行動テスト成功と実入力は区別。実機のpointerResponsesは0 |
| プロセス終了・再起動と設定保持 | 観測済み | 専用Agentの通常停止・再起動。World/paused保存を照合。メニューのQuit成功とは別 |
| 実システムスリープ・復帰 | 本人操作待ち | ロック／画面スリープで代用しない。イベント記録を保持 |
| 再ログインと自動起動 | 本人操作待ち | RunAtLoad登録と通常起動は確認。GUIセッション変化の記録が必要 |

`SETUP-VERIFICATION.md` の操作後、`scripts/lifecycle-check.py inspect` で実イベントと描画時計を照合する。本人からの操作結果はまだ受け取っていない。

## 90秒の変更前後比較

|版|状態|CPU（1コア=100%）|活動画面の平均fps|両画面の描画増加|
|---|---|---:|---:|---|
|v14baseline|running|15.80%|29.997|[0, 2700]|
|v14baseline|covered|0.34%|0.000|[0, 0]|
|v14baseline|paused|0.15%|0.000|[0, 0]|
|v14final|running|14.52%|29.999|[0, 2700]|
|v14final|covered|0.34%|0.000|[0, 0]|
|v14final|paused|0.18%|0.000|[0, 0]|

通常表示は外部画面1789×1006が描画、内蔵1665×1081は既存ウィンドウで停止。覆う時は実Finderを外部画面へ移動・画面全体に表示。停止はアプリ固有のpaused設定と普通の再起動で作り、元のpaused=0/world=riverscapeへ復元。いずれも一度90秒の観測であり、性能向上の統計的証明ではない。GPU演算・電池持ち・長時間リークは未測定。

### physical footprint（MiB、PID単位）

|版|状態|プロセス|開始→終了|
|---|---|---|---:|
|v14baseline|running|Deskworlds (71251)|32.4→25.0|
|v14baseline|running|com.apple.WebKit.GPU (71253)|440.0→321.8|
|v14baseline|running|com.apple.WebKit.Networking (71254)|4.1→4.0|
|v14baseline|running|com.apple.WebKit.WebContent (71255)|418.4→340.4|
|v14baseline|running|com.apple.WebKit.WebContent (71256)|375.6→341.7|
|v14baseline|covered|Deskworlds (71251)|25.1→25.1|
|v14baseline|covered|com.apple.WebKit.GPU (71253)|36.3→36.3|
|v14baseline|covered|com.apple.WebKit.Networking (71254)|4.9→4.9|
|v14baseline|covered|com.apple.WebKit.WebContent (71255)|342.5→342.6|
|v14baseline|covered|com.apple.WebKit.WebContent (71256)|352.4→352.4|
|v14baseline|paused|Deskworlds (90995)|29.8→29.2|
|v14baseline|paused|com.apple.WebKit.GPU (90997)|79.2→31.7|
|v14baseline|paused|com.apple.WebKit.Networking (90998)|4.0→4.0|
|v14baseline|paused|com.apple.WebKit.WebContent (90999)|346.9→340.9|
|v14baseline|paused|com.apple.WebKit.WebContent (91000)|326.9→321.4|
|v14final|running|Deskworlds (95603)|31.1→27.5|
|v14final|running|com.apple.WebKit.GPU (95605)|445.8→319.9|
|v14final|running|com.apple.WebKit.Networking (95606)|4.1→5.0|
|v14final|running|com.apple.WebKit.WebContent (95607)|417.5→343.3|
|v14final|running|com.apple.WebKit.WebContent (95608)|377.5→349.9|
|v14final|covered|Deskworlds (95603)|27.3→25.5|
|v14final|covered|com.apple.WebKit.GPU (95605)|37.4→37.4|
|v14final|covered|com.apple.WebKit.Networking (95606)|5.0→5.0|
|v14final|covered|com.apple.WebKit.WebContent (95607)|343.3→343.3|
|v14final|covered|com.apple.WebKit.WebContent (95608)|350.0→349.7|
|v14final|paused|Deskworlds (1814)|31.7→22.3|
|v14final|paused|com.apple.WebKit.GPU (1816)|67.0→36.1|
|v14final|paused|com.apple.WebKit.Networking (1817)|4.1→5.1|
|v14final|paused|com.apple.WebKit.WebContent (1818)|347.0→343.2|
|v14final|paused|com.apple.WebKit.WebContent (1819)|327.9→324.6|

RAM総量として合算しない。出典 `evidence/v14-performance-summary.json` と各状態の生ログ。停止・遮蔽では魚・水の時計も増加ゼロ。

## 最新評価による外観判定の訂正

利用者は「明るいグッピーになったけどグッピーじゃない」「なんかキモい」と評価。明度や色数、機能・性能の成功を外観合格の根拠にしない。均一な棒状胴体、全身への均等な塗色、三角板の尾、同じ顔・形の複製が問題との診断仮説を、実魚資料で照合する。次は1匹の解剖・素材・泳ぎと、水面から屈折・集光が連動する検査シーンを優先。

### 比較ハーネスの追加監査

同じWebGLRenderer上の複数版でonBeforeCompileを同一ラッパーにすると、Three.jsのプログラムキャッシュが版間で共有され得ることをv15作業中に発見。現行v15ハーネスへ版・メッシュ固有のcustomProgramCacheKeyを追加。v14の比較用ROI明度および旧新素材比較は、版別プログラムで再取得するまでは判定根拠から外す。単一版のMacアプリ表示・操作・90秒負荷の記録は別経路であり保持。
