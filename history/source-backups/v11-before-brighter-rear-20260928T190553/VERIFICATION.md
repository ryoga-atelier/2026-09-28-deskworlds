# Deskworlds 導入・検証記録

確認日: 2026-09-28 / タスク: `01a0e3a9-82bc-7353-be3f-dacf575f7cea`

## 最新: natural-guppy-v11（17:57導入・担当が採用判定）

見た目の判定も委任する依頼を受け、実物写真との比較から尾の過剰な尖り、変形する鰭と光のずれ、模様の反復、密集しすぎる群れを修正した。横・斜め・正面・反対側・旋回・通常遊泳と、Macアプリの表示を確認し、普段の水槽壁紙としてv11を採用した。実写と区別不能との判定はしない。水草・石・砂はv10を点検して継続採用した。判定理由は `VISUAL-REVIEW.md`、21項目の点検範囲は `evidence/v11-comprehensive-audit.json`、比較と映像は `review/V11-RESULTS.html`。

### 採用物・ビルド・保全

- 検査コピー：`preview/natural-guppy-v11-r1`。導入先：`~/Applications/Deskworlds.app`。実機側44ファイルとコピーの内容・ハッシュが一致。`evidence/v11-installed-source-check.json`。
- 上流固定版 `3950c45ef5798ed2df9f78037994bcddacebbb01`、原本は差分なし。Swiftビルド・署名検査・Info.plist・LaunchAgent検査成功。`evidence/v11-install.log`。
- `npm run check`、既存9スイートの `npm test`、`check-guppy.mjs`、`check-v10.mjs <tree> natural-guppy-v11` が成功。`evidence/v11-{check,tests,guppy,regression}.log`。check-v10は今回、期待する版名を引数で指定できるようにした。検査内容の緩和はしていない。
- バイナリSHA256 `7610e50fde2c3f064c907c2505a64c29e220d7f0c3592afd8b69a96e8a3c545e`。最終状態はPID 53556、LaunchAgent running、RunAtLoad=true、world=riverscape、paused=0。`evidence/v11-final-state.json`。
- v10アプリとAgentは `rollback/20260928T175718361798+0900/previous/`、編集前コード・文書は `rollback/v10-before-comprehensive-20260928T175230/`。削除していない。
- 壁紙とmacOSのアクセシビリティplistはv10観測時と同じハッシュ。壁紙は初回基準とも一致。アクセシビリティは以前から初回基準と異なるため、初回以降の不変とは扱わない。`evidence/v11-preserved-settings.json`。

### 描画・行動・再起動

- 赤の横向き、青の斜め、正面、全周回転を同じ照明・倍率で比較。全周映像の3.9秒と7.85秒もデコードして、後ろ向きと反対側を確認。`natural-v11-turn-20260928T090920Z-comparison.webm`、`v11-turn-back.png`、`v11-turn-other-side.png`。この最終比較タブのerrorログは0件。
- 通常遊泳動画はVP9、1500×975、24.966388秒。拡大遊泳は24.987388秒。両方をIABの標準動画コントロールから再生し、ended=trueを確認。`v11-{tank,swim}-video-probe.json` と `v11-browser-verification.json`。
- ブラウザのFeedとマウス入力により計20粒を投下、17粒摂食・3粒消滅・残り0。pointerResponses=2・escapes=4。停止時5753フレームで2回固定を観測、再開後6981。壁紙アプリはクリックを透過するため、ブラウザのクリック給餌とネイティブのFeedは別経路。
- 素材ロード失敗時の3Dへの復帰とGPU深度比較はv10で確認済み。該当処理・背景素材は今回不変。通常描画で魚と水草の前後関係も目視した。葉1本ごとの衝突と正確な一致は保証しない。
- MacアプリをCUAで目視し、内部WebView画像 `natural-guppy-v11-native.png` を保存。画像は負荷測定後のSIGUSR1診断（4秒間の強制描画）で、デスクトップ合成キャプチャや性能測定には使っていない。
- アプリ固有のpaused=trueを保存して再起動し、両画面の1フレーム固定を60秒確認。元のpaused=falseとworldを復元して再起動し、10秒で動作画面1983→2283フレーム、もう一方は1→1を観測。`v11-process-state-cycle.json`、`v11-frames-resumed.json`。正常なプロセス停止・再起動の確認であり、メニューのQuit/Pauseクリックを試した証拠ではない。

### 実機負荷

他のWebGL検査タブを閉じ、専用5PIDをlibprocで2秒ごとに測定。SIGUSR2の受動診断を5秒ごとに採取。CPUは1コア=100%。GPU使用率・電池消費は未測定。

| 状態 | 測定時間 | CPU合計 | 実送出fps |
|---|---:|---:|---|
| 1789×1006画面は動作、1665×1081画面は被覆による停止 | 300秒 | 11.79% | 29.999 / 0 |
| アプリの停止設定を保存して再起動 | 60秒 | 0.183% | 両画面0 |

動作画面の最終4096区間は描画間隔中央値28ms、p95 43ms、最大45ms。CPUは本体4.18%、GPUプロセス3.15%、活動中WebContent4.43%などの合計。GPU作業量そのものの測定値ではない。

GPUプロセスのphysical footprintは323.28→324.81MiB。最初の1分内で268.78MiBまで減る区間があり、その後の4分間は324.78〜324.84MiBに収まった。長時間のリーク不在までは証明しないが、前回の90秒計測で見えた増加が同じ勢いで続く挙動はこの窓では見られなかった。本体22.39→22.41MiB、WebContentは329.19→328.00MiBと334.86→335.55MiB。共有領域を考慮せず合算したRAM使用量としては扱わない。

停止状態ではGPUプロセスのfootprintが344.83→30.77MiBへ低下。起動直後の確保を含む。停止時もWebContentのメモリは保持される。生データと集計は `v11-load-running-300s.json`、`v11-load-paused.json`、`v11-frames-*.json`、`v11-performance-summary.json`。

### 確認できなかった範囲

- ネイティブメニュー操作：SystemUIServer取得がCUA timeout -10005。アイコンが存在しないとは断定しない。
- Finderのアイコン選択・ドラッグ・Dockとデスクトップ合成の実操作：未確認。コードではdesktopWindowレベル、ignoresMouseEvents=true、フォーカスを奪わない設定を確認。
- 実スリープ復帰と実再ログイン：未実施。スリープ/画面ロック/セッション通知の停止再開処理、RunAtLoadの登録状態を確認。
- 両画面が同時に動く場合と、両画面が完全に覆われた場合のCPU値：今回の測定範囲外。

## 過去: photo-depth-v10（17:15導入）

「まだイメージに達していないのに作業が終わって見える」という指摘を受け、水槽全体の表示方式を変更した。写真風に生成した背景・近似深度に、実時間の3Dグッピーを合成する。細い水草、根元の影、砂・石の質感を一体で作り直し、青いグラス系素材を追加。表示・動画は `review/V10-RESULTS.html`。利用者による最終受領はまだ確認していない。

### 採用版と保全

- 採用コピー `preview/photo-depth-v10-final`。17:15:40 JSTに導入。バイナリSHA256 `25b3278579610462480b317629d59acaa13572f900870d3d020c070ee1749f65`。
- `scenes/riverscape` のシーン・素材・由来等37ファイルがインストール済み資産と内容・SHA256一致。`evidence/v10-installed-source-check.json`。
- 上流 `3950c45ef5798ed2df9f78037994bcddacebbb01` は差分なし。v8アプリ・専用Agentは `rollback/20260928T171540657669+0900/previous/`。編集前ソース・文書は `rollback/v8-before-natural-tank-20260928T164903/`。
- 最終状態はLaunchAgent running、PID 25919、RunAtLoad=true、world=riverscape、paused=0。`evidence/manifest.json`、`v10-final-state.json`。実再ログインは未実施。
- macOS壁紙、全体アクセシビリティ、他アプリ設定は今回変更していない。壁紙Storeは初回基準とSHA256一致。アクセシビリティplistはv7観測時と一致し、初回基準とは以前から不一致のため、初回以降の完全不変とは言わない。`evidence/v10-preserved-settings.json`。診断・停止状態の検証ではDeskworlds固有のpausedのみ変更し、最後にfalseへ戻した。

### 表現の構成と限界

背景は `aquarium-photo-v10.png`（1555×1012）と `aquarium-depth-v10.png`（1554×1012）。双方を正規化UVで対応付ける。魚の素材は赤系モザイクと青系グラスの2枚（各1774×887 RGBA）を使う。生成元・ハッシュ・プロンプトは `custom/guppy/assets/` と `evidence/v10-asset-origins.json`。組み込みimage_genで生成した原PNGを透明度も含めて保存し、ビットマップ加工はしていない。

背景は2.5Dで、上部の葉の極小な画像変形と水底の光を加えている。魚は閉じた3D胴体・変形するヒレ・元の行動ロジック。奥行きは実測値ではなく、元の3D地形に基づく障害物回避と葉1本ごとの厳密な一致は保証しない。背景・魚とも実写真ではない。24種類の独立した写真や正確な5品種の再現とは扱わない。

v9で試した手続き生成の葉・石の改善だけではCG感と細い輪郭の点状の輝きが残ったため、主表示には不採用。原因は未確定。手続き生成の環境は素材読込に失敗した時の代替表示として保持している。

### 検査と実表示

- 最終コピーで `npm run check`、既存9スイートの `npm test`、`check-guppy.mjs`、`check-v10.mjs` が成功。`evidence/v10-final-{check,tests,guppy,regression}.log`。Swiftビルド、署名、Info.plist・LaunchAgent検査も成功。`v10-install.log`。
- `check-v10.mjs` の設備・地形検査は代替の3D環境も含む。主表示の画像による深度処理は別に実GPU描画で確認。葉の同じ場所に同じ見かけの大きさで魚を置き、手前1367画素→後ろ467画素、開いた水中では1399→1399画素。`review/occlusion-v10.html`、`evidence/natural-v10-metrics-{front-1790583307380,back-1790583308202}.{png,json}`。位置を固定した遮蔽検査であり、通常遊泳の証拠ではない。
- 確認専用コピーで背景画像URLを意図的に404へ変更。habitat.enabled=falseとなり、24匹と既存の3D環境が描画された。黒画面で停止しないことをCUAで確認。`preview/photo-depth-v10-fallback-check`、`review/fallback-v10.html`。インストール版にはこの故障条件を混ぜていない。
- 最終版のブラウザUIで停止フレーム11610の固定を2回確認し、再開後12354へ増加。カーソル移動でpointerResponses=2・escapes=2。20粒の餌のうち12粒摂食・8粒消滅・残り0。`evidence/v10-browser-verification.json`。Macのネイティブメニュー操作とは区別する。
- 採用版の25秒映像は `natural-v10-tank-after-20260928T082122Z.webm`。VP9・1500×975・24.967秒、デコード可能。対応JSONに行動とフレーム統計を保存。IABの標準プレイヤーでended=true・24.967秒の再生完了も確認。全景PNGは5秒時点の抽出。給餌が含まれるため、無刺激の通常遊泳だけの動画ではない。
- MacアプリのウィンドウをCUAで目視。初回の停止フレームにも背景・赤と青の魚素材が読み込まれた。両画面の診断でも全素材loaded=true。`photo-depth-v10-native.png` は負荷測定後にSIGUSR1で保存した内部WebView画像で、デスクトップの合成キャプチャではない。
- IABでURL不明のMutationObserver.observeエラーが1件あり出所は未特定。THREEのシェーダーエラーは観測されなかった。
- ネイティブメニューFeed/Pause/Resume/Quit、実デスクトップのカーソル反応、アイコンドラッグ、Dock操作、実スリープ復帰、実再ログインは未確認。過去のSystemUIServer取得でCUA timeout -10005が反復したため、設定を変更して検証を強行しなかった。

### v10の実測

確認用WebGLタブを閉じ、専用5 PIDをlibprocで2秒ごとに計測。SIGUSR2を5秒ごとに送り、実renderedFrames差から送出fpsを計算。SIGUSR1による強制描画・スナップショットは測定後。専用WebKit群は同時起動し、アプリ停止で全て消え、再起動で全て置き換わることを確認した。`v10-processes-{paused,resumed}.json`。

| 状態 | 時間 | CPU合計（1コア=100%） | 実送出fps |
|---|---:|---:|---|
| 1789×1006の1画面動作・1665×1081は被覆停止 | 90秒 | 12.24% | 動作画面29.999 / 被覆画面0 |
| ネイティブpaused=trueを保存して再起動 | 60秒 | 0.146% | 両画面0、最初の1枚から増えず |

動作中のフレーム間隔は中央値28ms、p95 43ms、最大45ms。三角形は約163万、draw calls 13〜15（同一資産のブラウザ観測）。停止設定はネイティブ側が要求fpsを0にするため、JSのpaused=falseと矛盾しない。再開は固有設定をfalseに戻して再起動し、2秒で730→790フレームの増加を確認。メニューのPause/Resumeをクリックした証拠ではない。

v8の同様の窓は18.15%だったが、他プロセス・熱・負荷を統制した性能比較ではない。GPU使用率・消費電力・両画面動作・両画面完全被覆時の測定は行っていない。

physical footprintは各PIDへのOS帰属量で、共有領域を除いたRAMとして合算しない。

| 状態 | PID / 役割 | footprint開始→終了 MiB | OLS MiB/分 |
|---|---|---:|---:|
| 動作90秒 | 1486 / アプリ | 20.8→20.8 | -0.01 |
| 動作90秒 | 1488 / WebKit GPU | 272.0→328.0 | +12.05 |
| 動作90秒 | 1489 / Networking | 5.0→5.0 | 0.00 |
| 動作90秒 | 1490 / WebContent | 329.3→327.8 | -0.45 |
| 動作90秒 | 1491 / WebContent | 338.8→337.0 | -0.11 |
| 停止60秒 | 21138 / アプリ | 29.7→27.4 | -0.42 |
| 停止60秒 | 21139 / WebKit GPU | 30.6→30.6 | 0.00 |
| 停止60秒 | 21140 / Networking | 4.0→4.0 | 0.00 |
| 停止60秒 | 21141 / WebContent | 327.6→326.5 | -0.67 |
| 停止60秒 | 21142 / WebContent | 308.5→307.5 | -0.68 |

動作窓でGPUプロセスの帰属メモリが約56MiB増加したため、メモリ安定性や長時間リークなしとは判定しない。停止側は再起動後の測定なので、動作中にPauseするだけで同じ量まで解放されるとは言えない。生データは `v10-load-{running,paused}.json`、`v10-frames-{running,paused}.json`、集計 `v10-performance-summary.json`。

## 履歴: textured-guppy-v8（16:30導入・final-r2）

「本物そっくり」の目標を維持して、滑らかすぎる体表と規則的な尾膜を再制作した。AI生成の写実素材を閉じた3D胴体・変形する尾膜へ対応付け、生成画像の輪郭に合わせて体と尾柄の寸法も調整した。水草・石・流木・循環設備はv7のまま。魚は前進したが、水槽全体の写実化は未達。比較画像・25秒動画・残る問題は `review/V8-RESULTS.html` と `VISUAL-REVIEW.md`。

### 採用版・素材・保全

- 採用コピーは `preview/textured-guppy-v8-final-r2`。16:30:53 JSTに `~/Applications/Deskworlds.app` へ反映。バイナリSHA256は `22bf0a300bdd4e3435bfe6dee940a9fd32593708a318cba0ea7870a570fbbbb0`。19本のシーンJSと素材・由来・プロンプトの計22ファイルが採用コピーと一致。`evidence/manifest.json`、`v8-installed-source-check.json`。
- 上流は `3950c45ef5798ed2df9f78037994bcddacebbb01` のまま差分なし。Swiftビルド、署名、Info.plist、LaunchAgent検査に成功。終了時もLaunchAgent running、PID 65462、RunAtLoad=true、world=riverscape、paused=0を確認。実際の再ログインは未確認。
- 生成経路は内蔵image_gen。素材は `custom/guppy/assets/red-mosaic-material-v8.png`、1774×887 RGBA。元の透明度を保持した原画像を同梱し、ビットマップの切り抜き・加工は行っていない。SHA256 `48698e6e5bb989e5c2a393716b688f4ac8e5e5ff21ba57f0480b9d7772588e5c`。生成プロンプトと由来JSONも同じフォルダに保存。
- 実魚の写真ではない。1個体の生成素材を5系統に色替えして24匹に使用しているため、5品種の正確な再現や24種類の独立した模様とは呼ばない。実写真の無断同梱はしていない。
- v7のアプリ・Agentは `rollback/20260928T162824060202+0900/previous/`、変更前ソース・文書は `rollback/natural-v7-before-photo-20260928T162113/` に保持。途中のv8アプリは `rollback/20260928T163053631300+0900/previous/`。OS壁紙・全体アクセシビリティ設定は今回書き換えていない。

### 検査・描画・操作

- final-r2で `npm run check`、既存9スイートの `npm test`、`check-guppy.mjs`、`check-v8.mjs` が成功。`evidence/v8-r2-check.log`、`v8-r2-tests.log`、`v8-r2-install.log`。形状・有限値・属性・有界フレーム計測・v7設備の回帰に加え、PNG同梱、相対読込、シェーダー宣言順を検査した。体高の検査は今回の参照輪郭に合わせたもので、生物学的一般則ではない。
- 尾膜の分割を18から32へ増やしたため、三角形は約254万から約300万へ増加（観測3,000,116、draw calls 98）。負荷が減ったとは主張しない。
- 最初の導入では、被覆停止する画面が素材読込前の1枚で止まり、後からloaded=trueになっても外見が更新されなかった。final-r2では魚生成・初回描画の前に素材読込を待つ。CUAでMacアプリの最初のフレームに新素材が出ることを目視し、両画面の読込完了を診断で確認した。
- 横・斜め・正面のv7/v8比較と遊泳動画はr1／初期finalで保存。final-r2との差は初回読込待ちだけで、描画の形状・素材・遊泳は同一。保存動画はVP9、追尾24.975秒・全景24.968秒でデコード可能。実プレイヤーでの再生も確認。
- ブラウザ確認画面でFeed後10粒投下・10粒摂食、停止時4849フレームの固定、再開後6066への増加を確認。これは同じシーン資産の操作検査で、Macメニューバー操作の実証ではない。URL不明のMutationObserver.observeエラーが1件あり、出所は未特定。THREEのシェーダーエラーは観測されなかった。
- `evidence/textured-guppy-v8-native.png` は負荷測定後にSIGUSR1で取得したアプリ内部の診断画像。CUAでもアプリウィンドウを確認したが、どちらもFinderやDockを合成したデスクトップ全体のキャプチャではない。SIGUSR1の4秒強制描画は下記の負荷計測に含めていない。
- SystemUIServer取得はCUAのtimeout -10005で失敗。ネイティブFeed/Pause/Resume/Quit、デスクトップ上の魚のカーソル反応、アイコンドラッグ、Dock操作、実スリープ復帰は未確認。元のOS設定を変えて検証を強行していない。

### v8の90秒実測

比較用WebGLタブを閉じ、本体と再起動に伴って置換された専用WebKit群5 PIDを2秒ごとに測定。CPUは100%=1コア。SIGUSR2の受動診断を5秒ごとに読み、実renderedFrames差から送出fpsを算出した。GPUのpresentation、GPU使用率、消費電力ではない。

| 状態 | CPU合計 | 実送出fps | フレーム間隔 |
|---|---:|---:|---|
| 1789×1006の1画面動作・1665×1081は被覆停止 | 18.15% | 30.002 | 中央値28ms、p95 43ms、最大45ms |

被覆画面は最初の1枚から増えず0fps、両画面とも全観測で素材loaded=true。v7の同様の測定17.74–19.12%と大きく離れていないが、機械全体を統制したベンチマークではない。v8の両画面動作、全画面被覆、Pause中の負荷は未測定。下に残すv7の停止値をv8の値として流用しない。

physical footprint（MiB）はプロセス別のOS帰属量であり、共有領域の重複を除いたRAMとして合算しない。

| プロセス / PID | CPU | footprint 開始→終了 MiB | OLS MiB/分 |
|---|---:|---:|---:|
| アプリ / 65462 | 4.588% | 25.9→25.9 | 0.00 |
| WebKit GPU / 65466 | 5.477% | 556.0→556.0 | -0.02 |
| WebKit Networking / 65467 | 0.000% | 4.1→4.1 | 0.00 |
| 被覆WebContent / 65468 | 0.043% | 359.8→359.7 | -0.04 |
| 動作WebContent / 65469 | 8.047% | 360.4→360.3 | -0.59 |

この90秒窓で持続的増加は見られないが、長時間のリーク否定ではない。生データは `evidence/v8-load-running.json`、`v8-frames-running.json`、`v8-processes.json`、集計は `v8-final-state.json`。

## 履歴: natural-guppy-v7（15:40導入）

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
