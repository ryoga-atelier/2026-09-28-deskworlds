# Deskworlds 導入・検証記録

確認日: 2026-09-28 / タスク: `01a0e3a9-82bc-7353-be3f-dacf575f7cea`

## 最新: natural-guppy-v7（15:40導入）

グッピーの体・眼・口・尾模様と個体差、水槽の左右差、植栽の反復と材質、流木・石・背面光を変更。循環フィルターは右奥で吸水・配管・水中戻り口・背面固定具をつなげて残した。新しい生物は追加していない。比較は `review/V7-RESULTS.html`。残るCGらしさは `VISUAL-REVIEW.md` に記録。

### ビルド・ソースの確定

- 上流の固定commit `3950c45ef5798ed2df9f78037994bcddacebbb01` は差分なし。採用プレビューは `preview/natural-guppy-v7-final`。最終18本のシーンJSとインストール済み資産がSHA256・内容一致。
- 最終版で `npm run check`、`npm test` の9スイート、`check-guppy.mjs`、`check-v7.mjs` がすべて成功。`evidence/v7-final-{check,tests,guppy,regression}.log`。回帰検査は実フレーム計測の停止境界・有界履歴、GLSL負の座標、接続設備、共有座標の地形配置、魚形状を含む。
- Swiftビルド、ad-hoc署名、Info.plist、LaunchAgent検査が成功。導入バイナリSHA256 `5f96efc844e8e58614ba964a03726ed7a66d4f667d424ff6655b5728aba4454f`。`evidence/manifest.json`、`v7-installed-source-check.json`。
- v6アプリ・Agentは `rollback/20260928T154014557728+0900/previous/`、編集前ソース・文書は `rollback/clearwater-v6-source-20260928T152125/`。上流の削除付きinstallerは実行していない。
- ネイティブ変更はビルドコピーへの受動SIGUSR2診断だけ。フレームレートを上書きせず、画面ごとのframe数と時刻を読む。SIGUSR1の強制描画は今回の負荷測定に使用していない。

### 実描画と動作確認の境界

代表個体の横・斜め・正面、25秒の追尾遊泳、同じ寸法・画質での全景前後を保存。WebMはデコード可能、前24.93秒、後24.96秒。全景静止画は動画5秒時点の抽出。初回の黒いcanvas PNGは不採用としてrollbackへ退避した。比較動画の再生完了をIABの実プレイヤーで確認。これはブラウザと同一資産の描画確認で、実デスクトップ合成表示の証拠ではない。

Macには2つのWebViewがあり、1665×1081はネイティブの被覆判定による要求0fps、1789×1006はBalanced上限30fps。画面取得（Finder/Deskworlds）とSystemUIServerの取得がCUAのtimeout -10005で失敗。デスクトップ合成、メニューバーFeed/Pause/Resume/Quit、アイコンドラッグ、Dockの直接操作は未確認。ツールが取得できないことから壁紙自体の表示不良と断定していない。Show Desktopのキー送信は試みたが、ログ上の片画面停止は変わらず、成功として数えていない。

アプリ専用paused設定をtrueにして通常停止・再起動した状態で両画面1フレームのまま維持。その後paused=falseにして再起動し、world=riverscapeを維持して再描画を確認。これはCLIでのアプリ設定・起動管理の確認で、メニュー操作の確認ではない。ネイティブは停止をsceneRate(0)で伝えるため、JavaScriptのloop.paused=falseでも、この状態では実際の描画は停止している。

最終版の確認画面ではFeedクリック後、10粒投下・7粒摂食・3粒溶解を確認。Pause後の3898フレームが別時点でも固定し、Resume後4230へ増加した。これはIABの確認画面から同じsceneFeed/scenePauseを呼んだ検証。IABコンソールにURLなしのMutationObserver.observeエラー1件があり、出所は確定していない。THREEシェーダーエラーは観測されず、画面は描画・操作できた。

### 負荷の実測

各90秒、2秒ごとに本体とWebKitの5 PIDをlibprocで測定。CPUはMach timebaseでnsに変換した累積CPU時間差、100%=1コア。メモリは `ri_phys_footprint` で、RSSではない。PIDは専用アプリの停止・起動と同時に全5件が置換され、他のWebKit群は観測されなかった。PPIDがlaunchdになるため、親PIDだけで帰属させていない。`sample`のヘッダーはプロセス名・パスだけ採取した。GPUプロセスのCPU値はGPU使用率ではない。

| 状態 | 観測 | CPU合計 | 1789×1006の実送出fps | 1665×1081 |
|---|---:|---:|---:|---:|
| 1画面動作・もう1画面被覆停止、十分動作した後 | 90秒 | 17.74% | 30.005 | 0 |
| 同じ状態、再開の再起動直後 | 90秒 | 19.12% | 29.996 | 0 |
| 停止設定で再起動 | 90秒 | 0.136% | 0 | 0 |

動作中のフレーム間隔は中央値28–29ms、95パーセンタイル43ms。別の受動診断を5秒間隔で呼び、ページ内の実renderedFrames差÷観測時刻差で約85秒のfpsを算出。要求30という設定値だけをfpsと呼んでいない。ただしこれはCPUのrender送出間隔で、GPU presentation／ディスプレイ更新の測定ではない。初回90秒は途中まで比較用の停止画面（静止描画）が別ブラウザに残っていたため、再起動後の90秒ではそのWebGLを完全に閉じて測り直した。別ブラウザの保存済み動画の再生はあり、機械全体をアイドルにした厳密なベンチマークではない。

physical footprint、MiB。OLSは90秒内の傾向で、リーク判定ではない。プロセス別のOS帰属量を示し、共有領域の重複を除いた実RAMとして合算しない。

| 状態 | プロセス / PID | 開始 → 終了 MiB | 最小–最大 MiB | OLS MiB/分 |
|---|---|---:|---:|---:|
| 十分動作した後 | アプリ本体 / 47253 | 22.5 → 22.5 | 22.5–22.5 | +0.00 |
| 十分動作した後 | WebKit GPUプロセス / 47255 | 535.1 → 536.1 | 372.1–536.2 | -7.24 |
| 十分動作した後 | WebKit Networking / 47256 | 5.2 → 5.2 | 5.2–5.2 | +0.00 |
| 十分動作した後 | WebContent（停止画面） / 47257 | 350.5 → 350.4 | 350.4–350.6 | -0.06 |
| 十分動作した後 | WebContent（動作画面） / 47258 | 355.5 → 355.2 | 355.0–355.5 | +0.04 |
| 再開の再起動直後 | アプリ本体 / 50045 | 27.0 → 22.1 | 22.1–27.0 | -3.57 |
| 再開の再起動直後 | WebKit GPUプロセス / 50046 | 377.6 → 531.0 | 368.5–531.1 | +131.86 |
| 再開の再起動直後 | WebKit Networking / 50047 | 4.2 → 4.1 | 4.1–4.2 | -0.01 |
| 再開の再起動直後 | WebContent（停止画面） / 50048 | 354.2 → 348.3 | 348.2–354.2 | -2.20 |
| 再開の再起動直後 | WebContent（動作画面） / 50049 | 355.8 → 350.1 | 350.1–360.3 | -3.04 |
| 停止設定で再起動 | アプリ本体 / 48576 | 24.8 → 24.8 | 24.8–24.8 | -0.01 |
| 停止設定で再起動 | WebKit GPUプロセス / 48577 | 38.3 → 38.3 | 38.3–38.3 | +0.00 |
| 停止設定で再起動 | WebKit Networking / 48578 | 4.0 → 4.0 | 4.0–4.0 | +0.00 |
| 停止設定で再起動 | WebContent（停止画面） / 48579 | 350.3 → 349.3 | 349.2–350.3 | -0.59 |
| 停止設定で再起動 | WebContent（動作画面） / 48580 | 332.8 → 331.9 | 331.9–332.8 | -0.50 |

再開直後のGPUプロセスの帰属メモリは約154MiB増えており、安定したとは判定しない。十分動作した後の別窓では約535→536MiBだった。停止状態は再起動して作ったため、動作中からPauseを押した時に同じメモリまで解放されるという意味ではない。長時間の増加傾向は未検証。

生データ: `v7-load-{one-screen-running,resumed,paused}.json`、`v7-frames-{one-screen-running,resumed,paused}.json`、集計 `v7-performance-summary.json`。測定器の自己検証13件と既知CPU負荷・触ったメモリの検証も成功。両画面完全被覆時の状態別負荷、GPU利用率、消費電力、実スリープ復帰、実ログアウト・再ログインは未確認。

### 既存設定の保全

元の壁紙Store/Index.plistは導入前とSHA256一致。アクセシビリティのplistは今回の作業で書いていないが、01:25の基準ハッシュとは現在不一致だったため、ファイル全体の不変は証明できない。差分の原因は未特定で、利用者や他プロセスの変更もありうる。これを勝手に巻き戻していない。`evidence/v7-preserved-settings.json`。他アプリ設定やモデル・effortは変更していない。

## 履歴: 透明度調整 clearwater-guppy-v6（12:17導入）

水の緑灰色の霞を弱め、背面色を中立寄りにし、水面光を控えめに追加。背景の茎草と粒子を抑え、中央に泳ぐ空間を残した。魚と水草の造形は手続き生成の3Dで、写実的な実物同等とは判定していない。ユーザーからは左右の水草密度と尾模様の均一さに違和感が残るとの最新評価。次の構図変更案はこのファイル時点で未実装。

- `python3 -m py_compile`（provision/customize/aquascape/review-server）、`node scripts/check-aquascape-v6.mjs preview/clearwater-guppy-v6-crystal-water-r2`、`node scripts/check-guppy.mjs preview/clearwater-guppy-v6-crystal-water-r2` が成功。Upstream `npm run check` と9スイートの `npm test` も今回の見た目変更前に成功済み。Nodeのmodule.register deprecation warningは非致命。
- Swiftアプリの再ビルド、署名・Info.plist検査、LaunchAgentのplist検査、`launchctl print gui/501/com.chaselean.deskworlds` のrunning確認が成功。12:17に導入。固定ソースは `3950c45ef5798ed2df9f78037994bcddacebbb01`、現在の版・バイナリSHA-256・退避先は `evidence/manifest.json`。
- アプリ内SIGUSR1診断でWebGL2=true、描画1665×1081。内部スナップショット `evidence/clearwater-guppy-v6-native-20260928T121756.png` と20秒遊泳動画 `evidence/clearwater-guppy-v6-20260928T025441Z-swim.webm` はレンダリングの証拠であり、Finder/WindowServerと合成されたデスクトップ表示の証拠ではない。
- LaunchAgentは `RunAtLoad=true` で登録中。実ログアウト・再ログインによる自動起動は未確認。ネイティブメニューバーのFeed/Pause/Resume/Quit、実デスクトップでのカーソル反応、アイコン操作、Dock操作、スリープ復帰は未確認。Chromeが前面だったため画面全体での水槽合成表示は今回確証を取れていない。
- v6で状態別CPU・メモリの比較測定は未実施。過去版の測定をこの版の値として流用しない。GPU負荷・消費電力も未測定。
- 現行ビルドは上流の `desktopWindow` レベルのまま。重なり位置の一時的な診断ビルドは `rollback/` に保存し、最終導入版には混ぜていない。元のmacOS壁紙ファイルと全体アクセシビリティ設定をこの作業で変更していない。

## 履歴: 水槽全体の調整 planted-tank-v3（02:24導入）

「魚だけでなく水草や水槽の中身にも違和感がある」という指摘への変更。背の高い草が均一に並び、大きな流木が中央を横切る構図を見直した。明るい家庭の水草水槽を既定の方向として、左右で異なる高さの株、広葉の茎草、低い中央の植栽、開いた砂地と遊泳空間へ変更した。魚のモデルはnatural-v2を維持した。

流木は根元を基準に縮め、付着したシダと苔を共通の座標変換で移動。流木の衝突判定と魚の観察地点は変更後の曲線から生成する。石の深い穴・陰影を弱め、照明と水中の色を中立寄りにし、背面に緩やかな明暗を設けた。浮遊物900個を246個に減らした。水草の生成時の寸法を変更しており、描画後のメッシュだけを縮める方法は使っていない。

- 適用済みコピーで構文検査と既存9スイート成功。`evidence/aquascape-check.log`、`aquascape-tests.log`。
- グッピーの形状・個体差検査成功。`aquascape-guppy-check.log`。検証対象の15本のJavaScriptとインストールしたファイルがバイト単位で一致。
- ChromeでMac相当の縦横比（1200×780）で実描画を確認。Feedクリック後の表示、PauseでFeed無効化、Resumeで再有効化を確認。コンソールエラーなし。ネイティブメニューの操作確認とは区別する。
- Swiftビルド・署名・plist検査成功。CUAでネイティブ水槽を目視。内蔵診断のWebGL2=true、1665×1081、カーソル受渡しを確認。画像は `evidence/aquascape-running.png`。画像は診断の強制描画を含むため通常のfpsの証拠にはしない。
- LaunchAgent running、world=riverscape、paused=0を維持。上流差分なし、OS壁紙とアクセシビリティ設定のハッシュ不変。`evidence/aquascape-final-state.json`。
- 旧版アプリとLaunchAgentは `rollback/20260928T022407720836+0900/previous/`、編集前のソースは `rollback/natural-v2-before-aquascape/` に保存。プレビュー用サーバーを終了、確認用ブラウザタブを閉じ、viewport変更を解除、隠したアプリを「すべてを表示」で復帰した。

各12秒のCPU測定（本体43603、専用WebKit43607/43608/43609）:

| 状態 | CPU合計（1コア=100%） | RSS単純合計 |
|---|---:|---:|
| 壁紙表示中 | 17.63% | 653.1 MiB |
| ウィンドウで隠れた時（要求0fps） | 0.17% | 689.9 MiB |

表示中の測定には、ネイティブ要求30fpsから20fpsへの切替が含まれた。前の版との性能比較には用いない。表示中の測定は診断画像の取得より前、隠れた状態の測定はその後。RSSには共有領域の重複が含まれうる。GPU負荷・電池持ちは未測定。負荷の生データは `load-aquascape-visible.json` と `load-aquascape-covered.json`。

3Dモデルの輪郭や泳ぎの人工的な印象が完全に解消されたとは判断していない。ネイティブメニュー操作、アイコンの直接ドラッグ、実際の再ログインとスリープ復帰は引き続き未確認。以下は以前の版の記録。

## 自然な質感のグッピー版 natural-v2（02:06導入）

「作り物感が強い」という追加指摘を受け、実物の観賞用グッピー写真をブラウザで確認し、外見を再制作。参照URLと選んだ特徴は `custom/guppy/REFERENCES.md`。

大きく塗った瞳と白一色の胴体、規則的な水玉を改めた。小さい目は頭部のくぼみと一緒に寸法を変更し、細めの胴体・上向きの口・低く後方へ流れる背びれ・不規則な尾びれの縁を作った。青緑の光沢、薄い膜、個体ごとの模様と尾びれの微かな揺れを追加。パターンは24個体で異なり、時間では変わらない。行動・餌のロジックと乱数列は保持。静止画像や実写動画ではなく3D描画である。

| 確認 | 結果 |
|---|---|
| 構文・既存テスト | 適用済みコピーで `npm run check` と既存9スイートが成功。`evidence/guppy-natural-syntax.log` / `guppy-natural-tests.log` |
| 形状・個体差の検査 | 有限値、頂点番号、尾びれ幅、脂びれ除去、24個体の固有模様、体・ひれの属性共有、泳いだ後の模様保持が成功。`guppy-natural-geometry.log` |
| 実WebGL | Chromeで水槽と3匹を拡大した確認用ページを描画。最初の版で鱗が強すぎたため、反射・鱗コントラストを弱めて再確認。WebGLのエラーログなし |
| ネイティブ版 | Swiftビルド、署名・plist検査成功。Macの壁紙に反映し、CUAで24匹の新しい外見と描画を目視。`guppy-natural-install.log` / `guppy-natural-running.png` |
| 保全 | 旧グッピー版アプリは `rollback/20260928T020607589734+0900/previous/`。旧ソースは `rollback/guppy-v1-source-before-natural/`。上流差分なし、OS壁紙とアクセシビリティ設定のハッシュ不変 |

各12秒のCPU測定（本体PID 24760、同時起動した専用WebKit 24762/24763/24764）:
- Finderの小さなウィンドウが一部重なり水槽が見える状態: 合計CPU **12.96%**（1コア=100%）、RSS合計 **752.1 MiB**。この時のネイティブ要求は20fpsだった。
- 通常のアプリ表示へ戻し水槽が隠れた状態: **0.17%**、**752.2 MiB**。ネイティブ要求は0fps。

初回版の「全面表示30fps」と条件が違うので、上記から高速化や省電力化を断定しない。GPU使用率・電池持ちは未測定。RSSは共有領域の重複を含みうる。診断画像は負荷測定の後で取得。確認用Finderウィンドウを閉じ、隠したアプリは「すべてを表示」で戻した。プレビュー用サーバーは終了。

導入・版のハッシュは `evidence/manifest.json` と `evidence/guppy-natural-final-state.json`。自動起動と `world=riverscape` / `paused=0` を維持。以下の各節は以前の版の履歴。実際のログイン、スリープ復帰、ネイティブメニュー経由の操作は以前と同じ未確認範囲。

## 追加変更: グッピー版（01:52導入）

利用者の「もっと可愛い魚、グッピーにしたい」という希望を受け、Riverbedのテトラモデルを基にしたグッピーの外見を適用した。大きな扇形の尾びれ、長めの背びれ、少し大きい瞳、赤・オレンジ・青の3色。24匹の行動と餌への反応の処理は維持し、脂びれの描画を除いた。上流コミットは同じで、Git差分なし。生物学的に厳密な品種の再現ではなく、この水槽向けのローカルモデル。

- 適用済みコピーで `npm run check` と既存9スイートが成功。`evidence/guppy-syntax-check.log`、`guppy-tests.log`。
- 独自検査は形状属性の有限値、頂点インデックス、尾びれの幅、脂びれの除去、24匹の体とひれの色の対応、泳いでいる間の個体色の保持を確認。`evidence/guppy-geometry.log`。
- 初回ブラウザプレビューではGLSLの予約語 `patch` が原因で魚のシェーダーが失敗。`bodyMark` へ変更し、再読込後に魚の描画が成功した。構文検査のみでは検出できないため、実WebGLで確認した。
- Chromeのプレビューで3色の魚と尾びれの動きを目視し、Feedをクリックした後の群れを確認。ネイティブのメニュー操作確認とは分ける。
- Swiftビルド、署名・plist検査が成功。既存アプリ・専用LaunchAgentを `rollback/20260928T015259214683+0900/previous/` に保存し、新版を配置。`evidence/guppy-install.log`。
- ネイティブ壁紙のAXタイトルがGuppy Gardenになり、水草と3色のグッピーの実描画をCUAで確認。内蔵診断の保存画像は `evidence/guppy-running.png`。
- 単一プロセスPID 16163、LaunchAgent running、設定 `world=riverscape` / `paused=0` を確認。`evidence/guppy-final-state.json`。
- 元のOS壁紙・アクセシビリティ設定のハッシュは導入前と同じ。上流原本と元の版を保持。

最新版の導入先・バックアップ先は `evidence/manifest.json`。採用オーバーレイSHA-256は `16623e3f9a6104dc8374b0779601701c827adbfa8fc3af4b5d23d98b4a722174`。

以下は初回のテトラ版の検証履歴。負荷数値は初回版のもので、グッピー版では再測定していない。メニュー・実スリープ復帰・実再ログインの未確認範囲は継続する。

## 導入結果

Macのユーザー用Applicationsにアプリを設置し、専用LaunchAgentを登録・起動した。最終状態はRiverbed、アプリ固有のpaused=false。上流ソースは固定コミットのままで差分なし。Apple M5 Max / arm64 / macOS 26.6.2 / 内蔵3024×1964ディスプレイで確認した。

上流のインストーラー・アンインストーラーは未実行。既存物を保存退避する `scripts/provision.py` を使用した。今回、同名アプリ・同名LaunchAgentの既存物はなかった。したがって既存版からの自動ロールバックは実行検証していない。

## 確認できたこと

| 項目 | 結果・根拠 |
|---|---|
| JavaScript構文 | 上流 `npm run check` 成功。`evidence/syntax-check.log` |
| 上流テスト | `npm test` の9スイート成功。群泳、カーソルへの反応、餌、描画停止・復帰などのロジック。`evidence/upstream-tests.log` |
| ネイティブビルド | Swift 6.4でarm64/macOS 13以上向けに成功。ad-hoc署名検証・Info.plist検査成功 |
| 実描画 | CUAでアプリのRiverbedウィンドウと水草・流木・魚を目視。`evidence/riverbed-running.png` はアプリ内蔵診断のスナップショット |
| WebGL・カーソル経路 | 内蔵診断でWebGL2=true、読み込み完了、pointer受渡し2回、描画サイズ1665×1081。魚の逃避動作そのもののライブ目視は未確認 |
| ウィンドウ被覆 | 壁紙表示中の要求値30fpsから、Finder全画面化で0fpsへ移行。全画面を解除すると描画へ戻ることをログで確認 |
| 通常ウィンドウ操作 | Finderの新規ウィンドウ、案件フォルダへの移動、全画面化・解除、閉じるが可能。確認のため隠した他アプリはFinderの「すべてを表示」で戻した |
| 停止の保存・再起動 | アプリ固有のpaused=trueを保存し、launchctlで停止・再起動。停止状態とRiverbedを保持。時間を空けたCUA画像2枚がバイト単位で一致 |
| 再開設定 | paused=falseへ戻し、LaunchAgentを再起動。アプリが単一プロセスで起動していることを確認 |
| 自動起動 | RunAtLoad=trueのplist登録とbootstrap成功、launchctlのrunning状態を確認 |
| 既存設定保全 | 壁紙Store/Index.plistとcom.apple.universalaccess.plistのSHA-256が導入前後で一致 |

停止・再開の保存確認はアプリ専用設定とlaunchctl経由で行った。メニューのPause/Resumeをクリックできたという証拠ではない。システムのReduce MotionとLow Power Modeは読取時にともにfalseだった。

## 負荷の短時間測定

各12秒、アプリ本体と同時に起動・終了する専用WebKitのGPU/Networking/WebContentプロセスを対象に、CPU累積時間の差分とRSSを採取した。別アプリの既存WebKitプロセスは対象外。

| 状態 | 合計CPU（1コア=100%） | RSS単純合計 |
|---|---:|---:|
| 壁紙が見える | 18.20% | 750.3 MiB |
| 全画面ウィンドウで隠れる | 0.08% | 782.5 MiB |
| paused=trueで再起動 | 0.00% | 802.3 MiB |

RSSは共有領域を重複計上する可能性があり、純増メモリの実測ではない。CPUの0.00%は測定分解能内の値。GPU使用率、温度、長時間の電池持ちは未測定。表示中の描画はBalancedの上限30fpsで、静止壁紙より電力を使う。生データは `evidence/load-*.json`。

## 残る手元確認

- メニューバーのFeed / Pause / Resume / Quit。CUAがDeskworldsのメニューバー項目を取得できず、利用者へアイコンの表示確認を依頼済み。
- デスクトップアイコンの直接ドラッグとDock操作。Finderのデスクトップへのクリックは自動操作ツール側のnoWindowsAvailableで実行できなかった。通常のFinderウィンドウ操作とは分けて扱う。
- 実機の画面スリープ・復帰、実際のログアウト・ログイン後の自動起動。今回のアプリ停止・再起動とは別の確認。

追加のmacOS権限は付与していない。ソース・既存テストは権限不要の設計で、画面やキーボード内容を取得する機能は導入していない。

## 証拠ファイル

- `evidence/manifest.json`: 導入先、ビルド先、固定コミット、バイナリSHA-256
- `evidence/baseline.json` / `final-state.json`: 導入前後の設定ファイルハッシュと最終設定
- `evidence/lifecycle.json`: 停止保存・再起動・再開の記録
- `evidence/deskworlds-runtime.log`: 描画レートと内蔵診断
- `evidence/install.log`: ビルド・署名・配置結果

診断用SIGUSR1は一時的に描画を要求して画像を作るため、その画像だけでは通常時のアニメーション速度や消費電力を証明しない。負荷測定は診断実行とは分けて行った。

## 2026-09-28 08:55 — livebearer-v4 / layered-plants-v4

当時の採用版。見た目の比較と未達点は `VISUAL-REVIEW.md`、閲覧用は `review/RESULTS.html`。プログラムの検証成功を実写同等の再現達成とは扱わない。

- 固定上流 `3950c45ef5798ed2df9f78037994bcddacebbb01` は変更なし。実際に導入された16個のシーンJSと、検査・録画に用いたプレビューJSがバイト一致。
- 最終候補の `npm run check`、既存9系統の `npm test` 成功。120秒の行動検査で24匹の移動、滑走、ポインター接近・急接近、餌への誘引と摂食を確認。これは自動検査であり実物らしさの判定ではない。
- 追加の形状検査: 有限座標、妥当な頂点参照、尾柄への膜の接続、余韻の位相連続性、3色・24個体の固定模様を確認。
- ChromeのWebGL描画で横・斜め・正面・一周の形を観測。20秒の実泳ぎ追尾動画と水槽全体の前後動画を保存。保存MP4のデコード・寸法・時間、比較ページでの再生を確認。
- 同じシーンを読み込むローカル確認画面で餌やり・停止・再開を操作。停止時にrenderedFrames=2603で固定し、再開後の増加を確認。ネイティブのメニューバーからの各操作は今回再実施していない。
- Swiftのビルド、署名検証、Info.plist/LaunchAgentの検査が成功。既存アプリとLaunchAgentは `rollback/20260928T085537088104+0900/previous/` へ保存してから導入。
- 導入アプリの実ウィンドウで描画を確認。アプリ自身のSIGUSR1診断はWebGL2、hidden=false、1665×1081の内部描画を報告。診断スナップショットは短時間強制描画なので、通常時の持続フレームレートと区別。
- 設定は world=riverscape、paused=0を引き継ぎ、LaunchAgentは登録・実行状態。OS壁紙とアクセシビリティ設定は導入前からSHA256一致。

負荷はアプリ本体と専用のWebKit GPU/Networking/WebContent、計4プロセスのCPU時間差。状態が切り替わった1秒区間を除外して集計した。

| 状態 | 有効観測時間 | CPU（1コア=100%） |
|---|---:|---:|
| 表示中、native要求60・Balanced上限30fps | 13.50秒 | 20.81% |
| ウィンドウに隠れて要求0fps | 10.36秒 | 0.10% |
| 別途の覆われた状態の観測 | 10.04秒 | 0.20% |

RSSの合算は観測期間に約147–636MiBで変動。共有ページの重複、OSによる回収・圧縮もあるため、前版に対するメモリ増減と断定しない。GPU使用率・消費電力ではない。前版の表示測定は途中に60→0fpsの切替が入り比較不成立。`load-livebearer-before-steady.json` も実際は停止状態だったため、表示中の値として採用しない。前後の速度・電力改善は主張しない。

物理スリープ復帰、実ログアウト・再ログイン、デスクトップアイコンのドラッグとDock操作を今回新たに確認した、という記録にはしない。元の壁紙へ戻す手順・自動起動解除・非破壊の退避手順はREADMEに維持。

証跡: `evidence/livebearer-v4-{check,tests,geometry,install}.log`, `livebearer-v4-final-state.json`, `livebearer-v4-media.json`, `load-livebearer-states.json`, `livebearer-v4-native.png`。
