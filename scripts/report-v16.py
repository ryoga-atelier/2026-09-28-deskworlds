"""Publish the measured v16 review without promoting pending checks to passes."""
from pathlib import Path
import json
from html import escape

root = Path(__file__).resolve().parents[1]
evidence = root / 'evidence'
summary = json.loads((evidence / 'v16-performance-summary.json').read_text())
rows = {(r['revision'], r['state']): r for r in summary['rows']}
assert len(rows) == 6 and all(r['complete'] for r in rows.values())
manifest = json.loads((evidence / 'manifest.json').read_text())
refresh = json.loads((evidence / 'v16final-refresh.json').read_text())
pause = json.loads((evidence / 'v16final-pause-cycle.json').read_text())
assert refresh['preferences_preserved'] and pause['before'] == pause['after']
assert all(w['frames_delta'] == 0 and w['water_delta'] == 0 and w['fish_delta'] == 0
           for state in ('covered', 'paused') for w in rows['v16final', state]['windows'])

labels = {'running': '表示中', 'covered': '両画面が隠れた時', 'paused': '一時停止中'}
table = ['| 状態（各90秒） | v14 CPU | v16 CPU | v16実描画 |',
         '|---|---:|---:|---|']
html_rows = []
for state, label in labels.items():
    old, new = rows['v14final', state], rows['v16final', state]
    frames = ' / '.join(f"{w['pixels'][0]}×{w['pixels'][1]}: {w['frames_delta']}枚 ({w['fps']:.2f}fps)" for w in new['windows'])
    vals = [label, f"{old['cpu_percent_one_core']:.2f}%", f"{new['cpu_percent_one_core']:.2f}%", frames]
    table.append('| ' + ' | '.join(vals) + ' |')
    html_rows.append('<tr>' + ''.join(f'<td>{escape(v)}</td>' for v in vals) + '</tr>')

memory = ['| 版・状態 | プロセス | footprint MiB 開始→終了（最大） |', '|---|---|---:|']
for (rev, state), r in rows.items():
    for p in r['memory_per_pid']:
        memory.append(f"| {rev}・{labels[state]} | {p['role']} / PID {p['pid']} | {p['start_MiB']:.1f} → {p['end_MiB']:.1f} ({p['max_MiB']:.1f}) |")

native = 'veiled-v16-native.png'
comparison = 'natural-v16-metrics-side-1-photo-20260928T131112Z.png'
tank = 'natural-v16-tank-after-20260928T131113Z.webm'
turn = 'natural-v16-turn-atlas-turn-1-20260928T131218Z.webm'
record = f'''# v16 検証記録

状態：導入・下記の技術検証済み。外観の最終採用と全項目完了ではない。
本人が選んだ「左右の明るい茂みと中央の砂道」を保持した比較用の現行版。
最新の記憶は「細長い尾、やや小さい背びれ、長い腹側のヒレ」。提示した品種写真は本人が「全部違う」と評価し、安価で色の多い販売水槽の実写真を照合中で、v16をその実物の再現とは扱わない。

## 外観と判定

- 銀色の頬・腹と局所的な鮮色を分離。深い紫・コバルト・ワインと淡色が共存。露出1.06を固定し、全景の白飛びで魚を明るくする処理は加えていない。
- 前腹部の丸み、細い尾柄、眼・鰓をつなぐ観察ベースの形。旧来の単純な倍率指定から、頭・腹・尾柄ごとの滑らかな輪郭へ調整した。
- v15に比べ尾・背びれの面積を増やし、胸・腹側のヒレの膜を読みやすくした。根元を固定し、先端へ遅れを伝える。雄の尻びれは細いまま。
- 8色系統・24匹。水色3、赤〜ワイン3、シャンパン〜ライム4、青緑2、桃色2、紫〜パステル4、黄土3、コバルト3。全身パステルという以前の配分から、後続の本人指示で銀肌と局所色へ変更。
- 同じ姿勢・光・露出のv14/v15/v16比較、8色の横・斜め・正面・背面、全周約65秒と通常遊泳約65秒を観察。素材なしも確認。正常終了まで保存動画を再生し、再生エラーなし。
- 担当の判定：銀肌と色の区別、前腹部の量感、広がるヒレは壁紙サイズでも読み取れる。明らかな眼の埋まり・根元の浮き・旋回時の形状反転は見られない。一方で尾の広い扇形は最新の記憶の「細長い尾」と一致未確認。正面の腹側と色素の斑は暗く、模様の共通性とCGらしい輪郭も残る。実物そっくりという合格は出さない。
- 背景は本人確認したv14の色・深度画像と動きを復元。魚の前後遮蔽、水草の揺れ、水面、泡、条件付き砂煙を保持。v15の立体植栽・CAUSTICは保存した試作で、現行では無効。

![導入済みMacアプリの描画](evidence/{native})

この画像はインストール済みWKWebViewの診断スナップショット。デスクトップのアイコンやDockを含む合成スクリーンショットではない。

## 技術・操作確認

| 項目 | 結果と証拠 |
|---|---|
| 構文・既存9テスト | 成功。v16-check.log / v16-tests.log |
| 形状・法線・色・ヒレ接続 | 成功。v16-anatomy.log / v16-shape-swim.log。24個体、有限頂点・単位法線、600フレームの連続性 |
| 砂煙 | 移動する底付近の魚だけ発生、上限96、停止時更新ゼロ。v16-living-water.log |
| 餌やり | プレビューのFeed実操作で10粒投入、7粒捕食・3粒溶解、接近・捕食行動を観察。v16-browser-operations.json |
| 停止・再開 | プレビューのPauseでフレーム16025固定、Resume後16789へ進行。Macでも保存したpaused設定と90秒の描画停止、復元を確認 |
| 影・補助光の寄与と明度の定量 | 同じ魚・姿勢・素材・露出で影の有無と弱い／現行の補助光を比較。影を消すだけの差は小さく、写真素材を外すと腹側の暗い斑が大きく減った。素材の暗さが残る。定量明度は未測定 |
| Macビルド・導入 | 成功。v16-build.log / v16-install.log。比較ソースと導入済み87ファイル一致（v16-integrity.json） |
| 終了・再起動・設定保持 | 専用ジョブの正常停止・再起動と設定復元を確認。ネイティブメニューからのQuit操作とは別 |
| Finderの通常操作 | 新規ウィンドウ、Windowメニュー、外部画面移動、画面全体へ拡大、閉じるを実操作 |
| 自動起動登録 | LaunchAgentのRunAtLoad・パス・実行状態を確認。実際の再ログインは未実施 |
| メニュー／Dock／デスクトップドラッグ／実カーソル | 未確認。メニュー・Dockの操作対象が取得できず、デスクトップ画像からドラッグ座標を特定できない |
| 実スリープ・復帰／再ログイン | 未実施。本人操作後にOSイベント、セッションIDと描画を照合する |

プレビューの初回ログに出た出所不明のMutationObserverエラーは、アプリのシェーダー失敗とは特定していない。表示・給餌・停止再開は継続。ゼロエラーという主張はしない。

## 負荷実測

{chr(10).join(table)}

Balanced、同じ2画面接続。表示中は外部1789×1006を表示し、内蔵1665×1081はウィンドウで隠れた条件。被覆時はFinderで外部も覆った。一時停止はアプリ固有設定を保存して再起動し、最後に元へ復元。
CPUは帰属確認した本体＋4 WebKitプロセスの合計、100%=1コア。GPU使用率・電池持ちは測定していない。描画数は実際のレンダー投入カウンターで、ディスプレイの表示タイミング測定ではない。
停止・被覆とも両画面でフレーム・魚・水の時間増加ゼロ。表示中CPU差は一回ずつの測定差であり改善・退化の断定はしない。

{chr(10).join(memory)}

physical footprintは共有ページを含むためプロセス間で合算しない。開始直後の資源解放も含む。生データは evidence/v16-performance-summary.json と v16final-*.json。

## 導入・復旧・残る作業

- 導入日時：{manifest['installed_at']}。variant `{manifest['variant']}`。
- 上流固定：`{manifest['source_commit']}`。原本clean。Three.js r180。
- 正本：custom/realism-v16/。検査コピー：preview/veiled-guppy-v16-r1/。
- 前版の保存先：`{manifest['backup']}`。現行app：`{manifest['app']}`。
- 元の壁紙とmacOSアクセシビリティ設定はv14時点のハッシュと一致。アプリのみのpaused=0・Riverbedへ復元。
- 普段の操作・非破壊の自動起動解除と退避は README.md。本人操作の順序は SETUP-VERIFICATION.md。
- 残る作業：本人が実物候補を選ぶ→その実物の多角度・動画でヒレと泳ぎを再調整。水槽の選択済み構成は維持。ネイティブ操作・実スリープ・再ログインは実施結果を受けて記録する。

## 参照と表現上の限界

custom/realism-v16/REFERENCES.md に実物の写真・動画の観察を記録。写真をアプリへ転載せず、既存AI生成RGBA素材2枚を3D形状へマッピング。個別品種の科学的計測モデルではない。
背景は色画像と推定深度による2.5D。真の3D水草、完全な光学屈折・散乱・流体計算ではない。今後立体化する場合も本人が選んだ青・素材・左右の茂み・中央の砂道を基準とする。
照明比較は review/lighting-v16.html と evidence/natural-v16-metrics-lighting-*.png。弱い補助光（半球0.42、前0.50・後0.42）と現行（0.64、0.95・0.62）、主光2.8・露出1.06固定。中央は弱い補助光のまま主光の影だけを無効。魚単体なので水草等による他物体の影は含めない。影を消すより素材切替の差が大きいという定性的観察で、全色・全角度への一般化はしない。
旧v14のL*比較数値はシェーダーキャッシュ共有の不備で撤回済み。v16比較では版別キャッシュに修正したが、黒斑を除く身体領域の定量明度は再測定していない。旧数値は使わない。
'''
(root / 'V16-VERIFICATION.md').write_text(record)

html = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>水槽 v16 — 反映内容と確認結果</title>
<style>body{{margin:0;background:#edf5f6;color:#16323d;font:16px/1.8 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:36px 24px 80px}}h1{{font-size:clamp(26px,4vw,40px);line-height:1.4}}h2{{margin-top:48px;font-size:24px}}p{{max-width:850px}}.status{{padding:18px 22px;background:#fff4d9;border-left:5px solid #af7525;border-radius:6px}}figure{{margin:24px 0}}img,video{{display:block;width:100%;height:auto;background:#c5dfe9;border-radius:8px}}video{{max-height:680px}}figcaption,small{{color:#49616a;font-size:14px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}.scroll{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #cedee0}}a{{color:#075a78}}.links{{display:flex;gap:20px;flex-wrap:wrap}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}</style>
<main><small>DESKWORLDS · 2026年9月28日 · 現行 v16</small><h1>左右の茂みを戻し、<br>魚の銀肌・色・ヒレを調整。</h1>
<p class="status"><strong>反映済み。外観はまだ最終確定していません。</strong><br>水槽は本人が選んだv14の構成。魚は安価で交配しやすいグッピーの販売水槽を実写真で照合中です。v16を記憶の魚の再現として合格にはしていません。</p>
<figure><img src="../evidence/{native}" alt="左右の緑の茂み、中央の砂道、明るい青い水と24匹のグッピー"><figcaption>導入済みMacアプリの描画。WKWebView診断画像で、Dockやアイコンを含むデスクトップ合成画像ではありません。</figcaption></figure>
<h2>魚の比較</h2><p>銀色の頬と腹、局所的な紫・コバルト・ワインなどの発色を分けました。v15で小さすぎた尾・背びれを広げ、柔らかな遅れを付けています。最新の希望「細長い尾・小さめの背びれ」との一致は、実物選定後に詰めます。</p>
<figure><img src="../evidence/{comparison}" alt="同じ姿勢と光の魚比較"><figcaption>左：v14 ／ 中：採用撤回のv15 ／ 右：現行v16。同じ姿勢・照明・露出。</figcaption></figure>
<div class="grid"><figure><video controls preload="metadata" src="../evidence/{tank}" poster="../evidence/{native}"></video><figcaption>通常遊泳 約65秒。24匹、水草・水面・泡・砂の動き。</figcaption></figure><figure><video controls preload="metadata" src="../evidence/{turn}"></video><figcaption>8色の全周比較 約65秒。左v14・中v15・右v16。</figcaption></figure></div>
<h2>実機の負荷</h2><div class="scroll"><table><thead><tr><th>各90秒</th><th>v14 CPU</th><th>v16 CPU</th><th>v16 実描画</th></tr></thead><tbody>{''.join(html_rows)}</tbody></table></div>
<p><small>100%=CPU 1コア。表示中は外部画面を表示し内蔵画面は隠れた条件。被覆・停止とも描画と魚・水の時間増加ゼロ。GPU使用率・電池持ちは未測定。メモリは共有を重複合算せず、詳細記録にプロセス別で掲載。</small></p>
<h2>確認済みと残る確認</h2><p>構文・既存9テスト、形状と24匹の割当、プレビューの給餌／停止／再開、アプリのビルド・設定保持、Finderのウィンドウ操作を確認しました。元の壁紙とmacOSのアクセシビリティ設定も保持しています。</p>
<p class="status">Macメニュー・Dock・デスクトップドラッグ・実カーソル、実スリープ復帰・再ログインは未確認です。操作ツールでは対象を取得できない項目があり、本人の実操作結果と保存済みログを照合します。</p>
<p>魚は3D、水槽は写真風の色と推定深度を使った2.5Dです。模様の共通性やCGの輪郭は残ります。実物と区別不能という完成判定はしていません。</p>
<nav class="links"><a href="../SETUP-VERIFICATION.md">残る実操作の手順</a><a href="../V16-VERIFICATION.md">検証・メモリ実測・版の記録</a><a href="../README.md">普段の操作・元へ戻す</a></nav>
</main></html>'''
(root / 'review/V16-RESULTS.html').write_text(html)
print('Saved V16-VERIFICATION.md and review/V16-RESULTS.html')
