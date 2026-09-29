"""Write the current mixed-guppy review from completed native measurements."""
from pathlib import Path
import json
from html import escape
root=Path(__file__).resolve().parents[1]
e=root/'evidence'
d=json.loads((e/'v17-performance-summary.json').read_text())
rows={(r['revision'],r['state']):r for r in d['rows']}
assert len(rows)==6 and all(r['complete'] for r in rows.values())
manifest=json.loads((e/'manifest.json').read_text())
assert manifest['variant']=='guppy-v17'
assert json.loads((e/'v17-integrity.json').read_text())['mismatches']==[]
refresh=json.loads((e/'v17final-refresh.json').read_text())
pause=json.loads((e/'v17final-pause-cycle.json').read_text())
assert refresh['preferences_preserved'] and pause['before']==pause['after']
labels={'running':'表示中','covered':'両画面をウィンドウで被覆','paused':'一時停止中'}
table=['| 各90秒 | v16 CPU | v17 CPU | v17 描画 |','|---|---:|---:|---|']
htmlrows=[]
for state,label in labels.items():
 a,b=rows['v16final',state],rows['v17final',state]
 if state!='running':assert all(w['frames_delta']==0 and w['fish_delta']==0 and w['water_delta']==0 for w in b['windows'])
 frames=' / '.join(f"{w['pixels'][0]}×{w['pixels'][1]}: {w['frames_delta']}枚 ({w['fps']:.2f}fps)"for w in b['windows'])
 cells=[label,f"{a['cpu_percent_one_core']:.2f}%",f"{b['cpu_percent_one_core']:.2f}%",frames]
 table.append('| '+' | '.join(cells)+' |');htmlrows.append('<tr>'+''.join('<td>'+escape(v)+'</td>'for v in cells)+'</tr>')
mem=['| 版・状態 | プロセス | footprint MiB 開始→終了（最大） |','|---|---|---:|']
for (rev,state),row in rows.items():
 for p in row['memory_per_pid']:mem.append(f"| {rev} {labels[state]} | {p['role']} PID{p['pid']} | {p['start_MiB']:.1f} → {p['end_MiB']:.1f} ({p['max_MiB']:.1f}) |")
native='mixed-v17-native.png';comparison='natural-v17-metrics-side-7-photo-20260928T134759Z.png'
tank='natural-v17-tank-after-20260928T134616Z.webm';turn='natural-v17-turn-atlas-turn-7-20260928T134722Z.webm'
report=f'''# v17 — 本人が選んだミックスグッピーへの調整

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

![インストール済みMacアプリの描画](evidence/{native})

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

{chr(10).join(table)}

2画面・Balanced。表示中は外部画面1789×1006が表示、内蔵1665×1081は隠れた条件。被覆時はFinderで外部も覆った。停止はアプリ固有設定で行い、最後にpaused=0とRiverbedへ復元。CPU100%=1コア。本体＋専用WebKit4プロセスのlibproc実測。実描画はレンダー投入数で、モニターの表示時刻ではない。GPU使用率と電池持ちは未測定。

{chr(10).join(mem)}

メモリはphysical footprint。共有ページを含むのでPID間で合算しない。各1回90秒の結果で長期リークや負荷差の有意性を断定しない。生データはv17-performance-summary.json、v17final-*.json。

## 版と復旧

- 導入：{manifest['installed_at']}。`{manifest['variant']}`。
- 上流固定：`{manifest['source_commit']}`、原本clean。Three.js r180。
- 正本 custom/realism-v17/。検査コピー preview/mixed-guppy-v17-r2/。
- アプリ `{manifest['app']}`。旧v16の退避 `{manifest['backup']}`。
- 元の壁紙・macOSアクセシビリティ設定はv16時点のハッシュと一致。
- 起動・Feed・Pause/Resume・Quitと非破壊の退避はREADME.md。残る本人操作はSETUP-VERIFICATION.md。
- 参照・権利：custom/realism-v17/REFERENCES.md。店の写真は観察のみでアプリへ転載していない。
'''
(root/'V17-VERIFICATION.md').write_text(report)
html=f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ミックスグッピー v17 — 調整と検証</title><style>body{{margin:0;background:#edf5f6;color:#17353d;font:16px/1.8 system-ui}}main{{max-width:1100px;margin:auto;padding:36px 24px 80px}}h1{{font-size:clamp(26px,4vw,40px);line-height:1.4}}h2{{margin-top:40px}}p{{max-width:850px}}.note{{background:#fff4da;border-left:5px solid #b88739;padding:16px 20px}}img,video{{display:block;width:100%;border-radius:8px}}video{{max-height:660px;background:#c0dbe6}}figure{{margin:24px 0}}figcaption,small{{font-size:14px;color:#4a6670}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}.scroll{{overflow-x:auto}}table{{border-collapse:collapse;background:#fff;width:100%}}td,th{{border-bottom:1px solid #cadadc;padding:12px;text-align:left}}a{{color:#075c7d}}nav{{display:flex;gap:20px;flex-wrap:wrap}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}</style><main><small>2026年9月28日 · インストール済み v17</small><h1>身近なミックスグッピーへ。</h1>
<p>選んでもらった<a href="https://www.petballoon.net/product/65143">実物の写真</a>を基準に、細すぎる尾の付け根と大きすぎるヒレを調整。銀色の胴に色柄が乗る、青・黄・紫などの24匹へ。</p><p class="note">左右の茂みと中央の砂道は保持。技術検証は下記の範囲で済みました。外観の本人による最終確認、Macメニュー・Dock・ドラッグ・実スリープ・再ログインは完了扱いにしていません。</p>
<figure><img src="../evidence/{native}" alt="左右の明るい茂みと透明な青い水を泳ぐミックスグッピー"><figcaption>導入済みアプリの描画。WKWebView診断画像で、Dockやアイコンは含みません。</figcaption></figure>
<h2>代表個体の形を合わせる</h2><figure><img src="../evidence/{comparison}" alt="左が旧版、中央が新しい魚、右が小さく表示した新しい魚"><figcaption>左v16 ／ 中v17 ／ 右v17の壁紙に近いサイズ。同じ光・姿勢・露出。</figcaption></figure>
<p>胴から尾へ厚みをつなぎ、小ぶりの丸い尾と控えめな背びれへ。色の薄い魚と後半に模様が入る魚を混ぜています。写真と完全一致する模型ではなく、鱗・透け・体型差には近似が残ります。</p>
<div class="grid"><figure><video controls preload="metadata" poster="../evidence/{native}" src="../evidence/{tank}"></video><figcaption>通常遊泳 約65秒。24匹と水槽の動き。</figcaption></figure><figure><video controls preload="metadata" src="../evidence/{turn}"></video><figcaption>8色の全周比較 約65秒。左v16、中・右v17。</figcaption></figure></div>
<h2>実機の負荷</h2><div class="scroll"><table><tr><th>各90秒</th><th>旧v16 CPU</th><th>v17 CPU</th><th>v17実描画</th></tr>{''.join(htmlrows)}</table></div><p><small>CPU100%=1コア。被覆・停止時は魚と水の時間増加もゼロ。GPU使用率・電池持ちは未測定。メモリのPID別実測は検証記録に掲載。</small></p>
<h2>確認できたこと・まだ必要なこと</h2><p>既存9テスト、構文、形状・ヒレ接続・24匹の割当、プレビュー給餌・停止再開、Macのビルド・表示・再起動時の設定保持を確認。給餌は10粒のうち7粒を捕食しました。</p><p class="note">メニュー・Dock・デスクトップドラッグ・実カーソルは操作ツールの取得制約があり本人操作待ち。実スリープ復帰と再ログインも未実施です。<a href="../SETUP-VERIFICATION.md">残る操作の手順</a>から結果を照合します。</p>
<p>魚は3D、水草を含む背景は色画像と推定深度の2.5Dです。水槽の完全な立体化や、実物と区別不能という判定はしていません。</p><nav><a href="../V17-VERIFICATION.md">全検証・版・メモリ実測</a><a href="../README.md">使い方・元へ戻す</a><a href="../SETUP-VERIFICATION.md">残る実操作</a></nav></main></html>'''
(root/'review/V17-RESULTS.html').write_text(html)
print('Saved v17 review and verification')
