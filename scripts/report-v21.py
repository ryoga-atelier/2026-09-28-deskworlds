"""Publish the local report only after all native measurements and capture exist."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
e = ROOT / 'evidence'
d = json.loads((e / 'v21-performance-summary.json').read_text())
assert (e / 'mixed-v21-native.png').exists()
current = [x for x in d['rows'] if x['revision'] == 'v21final']
assert len(current) == 3 and all(x['complete'] for x in current)
names = {'running': '表示中', 'covered': '全面を隠した時', 'paused': '一時停止'}
rows = []
for state, name in names.items():
    a = next(x for x in d['rows'] if x['revision'] == 'v19final' and x['state'] == state)
    b = next(x for x in current if x['state'] == state)
    w = next(x for x in b['windows'] if x['pixels'] == [1789, 1006])
    rows.append([name, f"{a['cpu_percent_one_core']:.2f}%", f"{b['cpu_percent_one_core']:.2f}%", str(w['frames_delta']), f"{w['fps']:.3f}"])
    if state != 'running':
        assert all(x['frames_delta'] == x['water_delta'] == x['fish_delta'] == 0 for x in b['windows'])
header = ['状態', 'v19 CPU', 'v21 CPU', 'v21フレーム増加', 'fps']
table = '<table><tr>' + ''.join('<th>' + x + '</th>' for x in header) + '</tr>'
table += ''.join('<tr>' + ''.join('<td>' + x + '</td>' for x in row) + '</tr>' for row in rows) + '</table>'
mdtable = '|' + '|'.join(header) + '|\n|---|---:|---:|---:|---:|\n'
mdtable += '\n'.join('|' + '|'.join(row) + '|' for row in rows)
mem = []
for row in d['rows']:
    for p in row['memory_per_pid']:
        mem.append('|'+ '|'.join([row['revision'], names[row['state']], f"{p['role']} ({p['pid']})", f"{p['start_MiB']:.1f}", f"{p['end_MiB']:.1f}", f"{p['max_MiB']:.1f}"])+'|')

md = '''# v19とv20を統合したv21 — 導入と検証

2026-09-29 00:16 JSTに導入。本人のv20導入承認に、直後の「19と20をミックスして写真へ近づける」という指定を反映した。v20単体は導入していない。以前のv19は rollback/20260929T001634244774+0900/previous/ に保存。

## 外観

v20の丸い腹と柔らかい尾、銀褐色・薄桃色の地肌を基礎に、v19の色を胴後方へ局所的に戻した。細い棒状に見えた後方胴に厚みを追加し、鼻先も写真の丸みへ寄せた。頭と眼・鰓・ヒレの座標、法線は同じ断面形状から生成する。

24匹、8色系統、Riverbed、Balanced、自動起動を維持。水面・植栽・砂・泡・泳ぎのコードはv19と同一。

写真の中央上の個体を主参照にし、添付画像を無加工で保存。画像はアプリ素材へ転用していない。裏面を測定した立体再構成ではなく、形と材質には写真との差が残る。本人による外観の最終合格とは記録しない。

## 確認したこと

- `v21-r2-check.log` と `v21-r2-tests.log`：構文・既存9スイート成功。
- `v21-r2-anatomy.log`：有限・単位法線、腹と尾柄の比率、24匹の8色配分に合格。
- `v21-r2-shape-swim.log`：インデックス、ヒレ形状、600フレームの位相、尾の根付きに合格。
- 横・斜め・正面・背面の8色を描画・目視。ブラウザーのシェーダーエラー記録なし。
- 全周64.95秒、全景64.93秒の比較動画を保存。65観測点で魚位置差ゼロ、カメラ・投影一致。固定時間刻みのブラウザー記録であり、Macのfps測定とは別。代表姿勢を観察した記録で、全フレームを連続目視した合格とはしない。
- Swiftビルド、署名検証、アプリとLaunchAgentのplist検査成功。`v21-install.log`。
- 比較候補とインストール済みアプリの描画・素材55ファイル一致。`v21-integrity.json`。
- 壁紙・macOSアクセシビリティ設定のSHA-256はv19時点と一致。上流原本は固定コミット3950c45ef5798ed2df9f78037994bcddacebbb01のまま、差分なし。
- Finderのメニュー、検査ウィンドウの作成・移動・全面表示・閉鎖を実操作。水槽メニューやDock、ドラッグの検査とは分ける。

## 実機負荷

各90秒、2画面接続、Balanced。外部1789×1006を表示、内蔵1665×1081は被覆。被覆検査時は外部もFinderで覆った。CPUはアプリと専用WebKit 4プロセスを合算、100%は1コア分。単発測定で性能改善の統計的主張はしない。

''' + mdtable + '''

被覆・停止では両画面の描画、魚・水の時間増加ゼロ。停止検査はアプリ保存設定と再起動で実施し、メニュークリックではない。ネイティブ停止はJSにfps=0を渡す実装なので、JS側pausedだけで判定しない。

最後に元のpaused=0 / riverscapeへ戻し、再開後の受動カウンターを6秒取得。`v21final-restored-frames.json`。表示・非表示の描画判定は実カウンターで行い、診断画像だけから判断しない。

CPU描画呼び出し数であり、画面への提示時刻・GPU使用率・電池消費は未測定。

### プロセス別physical footprint（MiB）

共有ページの重複を避け、メモリは合算しない。

|版|状態|プロセス|開始|終了|最大|
|---|---|---|---:|---:|---:|
''' + '\n'.join(mem) + '''

## 残る確認

水槽のMacメニューによるFeed/Pause/Resume/Quit、実カーソル反応、Dock、デスクトップドラッグ、実スリープ復帰、実再ログインは未確認。以前の操作ツールのタイムアウト・座標取得不可を解決した証拠はない。登録状態や通常のアプリ再起動を、実再ログイン成功の代用にしない。SETUP-VERIFICATION.md の本人操作結果と実イベント記録を照合する。

全項目完了ではない。魚の細かな材質と個体ごとの形、2.5Dの植栽・固定カメラ向けの光学近似には実写との差がある。操作と退避復旧はREADME.md。
'''
(ROOT / 'V21-VERIFICATION.md').write_text(md)

image = 'natural-v18-metrics-blend21-side-7-photo-detail1-20260928T151404Z.png'
figures = ''
for i, caption in enumerate(['v19：導入前', 'v20：写真参照の候補', 'v21：今回の統合版']):
    figures += f'<figure><div class="fishcrop"><img style="transform:translateX(-{i*100/3}%)" src="../evidence/{image}" alt="{caption}"></div><figcaption>{caption}</figcaption></figure>'
page = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v19とv20を混ぜたグッピー — 導入済みv21</title><link rel="stylesheet" href="report-v19.css"><style>.three{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.fishcrop{{overflow:hidden;aspect-ratio:512/450}}.fishcrop img{{width:300%;max-width:none;border-radius:0}}@media(max-width:700px){{.three{{display:block}}}}</style><main>
<h1>v19の色とv20の丸みを合わせました</h1><p class="notice">v21をMacへ導入済み。24匹・8色、透明な青い水、左右の茂みと中央の砂道を保持しています。以前のv19は退避保存しました。</p>
<h2>3版を同じ姿勢と光で</h2><div class="three">{figures}</div><p>v20の銀褐色と薄い桃色へ、v19の色を局所的に戻しました。腹の丸みと尾の曲線を保ち、尾の手前と鼻先にも厚みを追加しています。<a href="../evidence/{image}">横姿の比較を原寸で開く</a></p>
<details><summary>参照した写真と斜めの比較</summary><img style="max-width:800px" src="../evidence/user-selected-guppy-reference.png" alt="本人が指定したグッピー写真"><img src="../evidence/natural-v18-metrics-blend21-oblique-7-photo-detail1-20260928T151404Z.png" alt="左v19、中央v20、右v21の斜め姿"></details>
<h2>Macアプリの実際の描画</h2><figure><img src="../evidence/mixed-v21-native.png" alt="Macに導入したv21の水槽"><figcaption>アプリのWKWebView診断スナップショット。デスクトップ全体の合成画像ではありません。</figcaption></figure>
<h2>約65秒の遊泳記録</h2><video controls preload="metadata" src="../evidence/natural-v18-tank-blend21-20260928T151508Z.webm"></video><p>固定時間刻みで作ったブラウザーの比較記録です。Mac実機の負荷は以下で別に測定しています。</p><details><summary>8色の全周旋回</summary><video controls preload="metadata" src="../evidence/natural-v18-turn-blend21-atlas-turn-7-20260928T151512Z.webm"></video></details>
<h2>実機で各90秒を測定</h2>{table}<p>CPUの100%は1コア分。被覆・停止時は両画面の描画増加ゼロ。停止は保存設定による検査で、水槽メニューの実操作とは分けています。</p><p><a href="../V21-VERIFICATION.md">検証の詳細・メモリ実測</a></p>
<h2>残っていること</h2><p>写真にある肌の不規則さや柔らかい反射には差が残っています。水槽メニュー、実カーソル反応、Dock、ドラッグ、実スリープ・再ログインは未確認です。全項目完了にはしていません。</p><p><a href="../SETUP-VERIFICATION.md">残る実操作の確認手順</a> · <a href="../README.md">起動・餌やり・停止・元に戻す手順</a></p></main></html>'''
(ROOT / 'review/V21-RESULTS.html').write_text(page)
print('Saved V21-VERIFICATION.md and review/V21-RESULTS.html')
