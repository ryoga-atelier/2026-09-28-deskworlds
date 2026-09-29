from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];e=r/'evidence'
m=json.loads((e/'manifest.json').read_text());assert m['variant']=='guppy-v25'
d=json.loads((e/'v25-performance-summary.json').read_text());now=[x for x in d['rows'] if x['revision']=='v25final'];assert len(now)==3 and all(x['complete'] for x in now)
assert (e/'oval-v25-native.png').exists()
rows=[]
for state,label in [('running','表示中'),('covered','全面を隠した時'),('paused','一時停止')]:
 a=next(x for x in d['rows'] if x['revision']=='v21final' and x['state']==state);b=next(x for x in now if x['state']==state);w=next(x for x in b['windows'] if x['pixels']==[1789,1006])
 if state!='running':assert all(x['frames_delta']==x['water_delta']==x['fish_delta']==0 for x in b['windows'])
 rows.append([label,f"{a['cpu_percent_one_core']:.2f}%",f"{b['cpu_percent_one_core']:.2f}%",str(w['frames_delta']),f"{w['fps']:.3f}"])
headers=['状態','v21 CPU','v25 CPU','v25フレーム増加','fps']
table='<table><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
mdtable='|'+'|'.join(headers)+'|\n|---|---:|---:|---:|---:|\n'+'\n'.join('|'+'|'.join(row)+'|' for row in rows)
side=max(e.glob('natural-v18-metrics-oval25-side-7-photo*.png'),key=lambda p:p.stat().st_mtime).name
oblique=max(e.glob('natural-v18-metrics-oval25-oblique-7-photo*.png'),key=lambda p:p.stat().st_mtime).name
tank=max(e.glob('natural-v18-tank-oval25-*.webm'),key=lambda p:p.stat().st_mtime).name
turn=max(e.glob('natural-v18-turn-oval25-*.webm'),key=lambda p:p.stat().st_mtime).name
points='''- 白い腹の上端を体表の高さによる横線から、物体座標の楕円へ変更。上端も中央が上へ膨らむ曲線にした。
- 背中から頭の断面も、腹の中央上を頂点に肩と頭へ滑らかにつなぐ。初回の局所的な出っ張りは採用せず、周囲の断面を合わせたr2を採用。
- 前の指定も保持：淡い頭から尾へ深まる赤茶・藤色、細い鱗の線、ふくらんだ乳白色の腹、尾の黒根元・有色中央・透明外縁、背鰭と尻鰭の色と透明部。
- 眼の位置は変えず、共有断面から眼・鰓・ヒレの付け根と法線を生成。尻鰭の根元は腹の曲面に合わせた。
- 24匹・8色・Riverbed・Balanced・自動起動、水面・水草・泡・砂・泳ぎ・全画面露出は保持。'''
limits='''写真と同一の再現ではない。鱗と尾の筋はまだ規則的で、頭や鰓の質感・皮膚の色むら・角度に応じる反射には実写との差がある。透明なヒレの外縁は小さい表示や同系色の背景では見えにくい。今回の曲線は本人の追加指定に合わせた観察的な形状で、写真1枚から正確に3D復元した形ではない。外観の本人最終合格とは記録しない。'''
verification='''- 適用済みプレビューのnpm run check、既存npm test 9スイート成功（v25-r2-check.log、v25-r2-tests.log）。
- check-v25の腹・尾柄比、法線、8色配分、check-guppy-v17の600位相とヒレ根元、check-living-waterの砂・停止検査成功。旧版の寸法テストは書き換えず、今回の腹の変更範囲を別テストにした。
- 8色を横・斜め・正面・背面で描画し確認。素材なしの代替状態も描画。形状比較ページでシェーダーエラーなし。
- 通常遊泳と全周旋回を約65秒記録。代表姿勢を目視した記録であり、全フレームを連続目視して実写相当と合格した記録ではない。魚位置・カメラ・投影の比較結果はv25-video-metadata.json。
- Swiftビルド・署名・plist検査成功（v25-install.log）。インストール済み描画・素材55ファイルはプレビューと一致（v25-integrity.json）。
- 元の壁紙とmacOSアクセシビリティ設定のハッシュはv21と一致。上流原本は3950c45ef5798ed2df9f78037994bcddacebbb01、変更なし。
- ネイティブのWKWebView診断画像を保存。実際のフレーム進行は別途SIGUSR2の受動カウンターで検査した。診断画像をデスクトップ合成画像とは扱わない。'''
pending='''水槽メニューを開くイベントは記録されているが、Feed・Pause/Resume・Quitと画面結果の組は未確認。実カーソル反応、Dock・ドラッグ、実スリープ復帰、実再ログインも未確認。登録状態やアプリの普通の再起動で代用しない。SETUP-VERIFICATION.mdの本人操作結果と実イベント記録で照合する。全項目完了ではない。'''
md=f'''# v25 — 腹の上端と背中を曲線にする

導入: {m['installed_at']}。退避先: `{m['backup']}/previous/`。

## 変更と判断

{points}

## 写真との比較で訂正したこと

v22では「少し暗い鱗」を広い黒い面にし、本人の意図から外れた。v23で色のある地肌と細い鱗へ戻した。v24で尾へ向かう濃淡、透明なヒレ、丸い下腹と白い領域を追加。今回v25では白い腹の上端と背中も丸い曲線にした。

撮影とアプリでは照明・背景が違う。単純なRGB一致や黒白の二値化を外見の合格条件にしない。写真の中央上の個体と同程度の表示サイズで、色の位置・形・膜の透明部を比較した。

{limits}

## 検証済み

{verification}

## 実機負荷

各状態90秒、2画面・Balanced。外部1789×1006を表示、内蔵1665×1081は被覆。全面被覆では外部も検査用Finderで隠す。比較用ブラウザー描画は閉じた。CPUはアプリと専用WebKit 4プロセスを合算し、100%を1コア分とする。v21は同じ画面条件の保存済み基準。

{mdtable}

被覆・停止では両画面の描画・魚・水の時刻増加ゼロ。停止はアプリ固有の保存設定と再起動による検査で、メニュー実操作ではない。最後に元のpaused=0へ復元し、6秒のフレーム再増加を確認。v25final-restored-frames.json。

メモリはv25-performance-summary.jsonのプロセス別physical footprint開始・終了・最大値。共有ページの重複を避け合算しない。描画カウンターはCPU描画呼び出し数であり、画面提示時刻ではない。GPU・電池持ちは未測定。単発測定で性能改善を断定しない。

v22は表示中90秒のみ。v23・v24は追加修正が続いたため各状態90秒測定をしていない。過去版の負荷値をそれらの実測として流用しない。

## 残る確認

{pending}
'''
(r/'V25-VERIFICATION.md').write_text(md)
def crop(src,box,label,reference=False):
 return f'<figure><svg viewBox="{box}" role="img" aria-label="{label}"><image href="../evidence/{src}" width="{800 if reference else 1536}" height="{530 if reference else 450}"/></svg><figcaption>{label}</figcaption></figure>'
figs=crop('user-selected-guppy-reference.png','164 159 376 134','参照写真：丸い腹と、色のある地肌・細い鱗。',True)+crop(side,'615 150 330 134','直前v24：腹の上端と背中に水平な部分が残っていました。')+crop(side,'1127 150 330 134','今回v25：白い腹の上端は楕円、背中から頭も滑らかな弧に。')
html=f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>白い腹の上端と背中を丸く — v25</title><link rel="stylesheet" href="report-v19.css"><style>svg{{width:100%;display:block;border-radius:10px}}.compare{{max-width:760px;margin:auto}}figure{{margin:18px 0}}figcaption{{padding:8px 0}}.notice{{font-size:18px;line-height:1.8}}.scroll{{overflow:auto}}</style><main><h1>腹の上端と背中を、丸い曲線に</h1><p class="notice">白い部分を楕円の輪郭へ変更し、背中から頭もなだらかな弧にしました。v25をMacへ反映済みです。</p><div class="compare">{figs}</div><p>色補正なし。写真とアプリでは照明と背景が異なります。今回の丸みは、写真に加えて本人の追加指定を反映しています。</p><h2>今回の変更</h2><ul>{''.join('<li>'+x[2:]+'</li>' for x in points.splitlines())}</ul><details><summary>同じ姿勢・光で、v23 / v24 / v25を比較</summary><img src="../evidence/{side}" alt="左v23、中央v24、右v25"><img src="../evidence/{oblique}" alt="同じ順の斜め姿"></details><h2>Macに反映した水槽</h2><img src="../evidence/oval-v25-native.png" alt="導入済みv25の水槽"><p>アプリのWKWebView診断画像。デスクトップ全体の合成画像ではありません。</p><details><summary>通常遊泳と8色の全周（各約65秒）</summary><video controls preload="metadata" src="../evidence/{tank}"></video><video controls preload="metadata" src="../evidence/{turn}"></video></details><h2>まだ写真と違うところ</h2><p>{limits}</p><h2>実機で各90秒の負荷確認</h2><div class="scroll">{table}</div><p>CPUの100%は1コア分。被覆・停止時は両画面とも描画増加ゼロ。</p><p><a href="../V25-VERIFICATION.md">詳しい比較・検証記録</a> · <a href="../README.md">操作と元に戻す手順</a></p><h2>残る実操作</h2><p>{pending}</p><p><a href="../SETUP-VERIFICATION.md">実操作の確認手順</a></p></main></html>'''
(r/'review/V25-RESULTS.html').write_text(html)
print('Saved V25 report')
