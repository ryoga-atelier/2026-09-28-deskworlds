"""Publish only recorded v26 results; missing checks stay explicitly pending."""
from pathlib import Path
import json
from html import escape

r = Path(__file__).resolve().parents[1]
e = r / 'evidence'
manifest = json.loads((e / 'manifest.json').read_text())
integrity = json.loads((e / 'v26-integrity.json').read_text())
assert manifest['variant'] == 'guppy-v26'
assert not integrity['runtime_mismatches']
assert (e / 'slender-v26-native.png').exists()
perf = json.loads((e / 'v26-performance-summary.json').read_text())
rows = perf['rows']
current = [x for x in rows if x['revision'] == 'v26final']
state_names = {'running':'表示中', 'covered':'ウィンドウで隠れた時', 'paused':'一時停止中'}
table = []
mdrows = []
for row in rows:
    frames = ' / '.join(f"{w['pixels']}: {w['frames_delta']}枚 ({w['fps']:.2f}fps)" for w in row['windows'])
    values = [row['revision'], state_names[row['state']], f"{row['seconds']:.1f}秒", f"{row['cpu_percent_one_core']:.2f}%", frames]
    table.append('<tr>' + ''.join('<td>'+escape(x)+'</td>' for x in values) + '</tr>')
    mdrows.append('| '+' | '.join(values)+' |')
missing = [state_names[s] for s in state_names if not any(x['state']==s and x['complete'] for x in current)]
perf_status = '現行版の3状態を各90秒測定済み。' if not missing else '現行版で未測定: '+ '、'.join(missing)+'。'

side = 'natural-v18-metrics-slim26-side-7-photo-detail1-20260928T160820Z.png'
tank = 'natural-v18-metrics-slim26-tank-v26-0-20260928T161218Z.png'
turn = 'natural-v18-turn-slim26-atlas-turn-7-20260928T161108Z.webm'
swim = 'natural-v18-tank-slim26-20260928T161225Z.webm'
for filename in [side,tank,turn,swim]:
    assert (e/filename).exists()

summary = '腹の曲線を残して体高を約28%、横幅を約15%絞りました。赤茶の一様な色面を弱め、灰紫を帯びる銀色、局所的な頬の桃色、頭から尾へ深まる濃淡に変更。細い鱗の縁と小さな反射を見えるようにしました。'
limits = '写真と比べ、尾の根元の暗色境界がまだ整いすぎ、鱗の配列と反射も規則的です。体の色・透け方は実魚の複雑さを再現しきれていません。8色系統は主にヒレと局所的な色差に表れ、胴全体は共通の銀色寄りです。魚は3Dですが水草と背景には2.5Dの表現が残ります。本人の最終的な外観合格は未確認です。'
checks = [
    ('コードと形状', 'npm run check / npm test、形状・24匹の色割当・遊泳・水草予算・砂の発生/静止/廃棄の検査が成功。法線は有限かつ単位長。'),
    ('比較描画', '8色の横・斜め・正面・背面、素材なしの代替描画を確認。全周旋回64.92秒、通常遊泳65.62秒を保存。通常遊泳は65サンプルで旧版と魚位置の差0、カメラと投影が一致。主要な姿勢を目視したが、動画の全フレームを目視検査したわけではない。'),
    ('Macへの反映', 'Swiftビルド・署名検査・LaunchAgent登録成功。インストール済みの実行資産55ファイルが検査用コピーと一致。実機WebViewの描画を保存し、受動カウンターで動作を確認。'),
    ('背景と設定', '元の壁紙とアクセシビリティ設定のハッシュはv21時点と一致。上流固定版は未変更。Riverbed、24匹、8色、Balanced、自動起動を維持。'),
    ('給餌とカーソル', 'シミュレーションの自動テストは成功。現行MacでのFeedと実カーソル操作の見た目は未確認。'),
    ('停止と再開', 'アプリ固有の保存設定と再起動を使って検証。停止中90秒の描画・魚・水の進行は0。元の再生設定へ戻した後、外部画面で6秒間180フレームの再開を確認。メニューのPause/Resume/Quitを実操作した合格とは区別する。'),
    ('Dock・ドラッグ・睡眠・ログイン', '実操作、実スリープ復帰、実再ログインは未確認。自動起動の登録状態を再ログイン成功とは扱わない。SETUP-VERIFICATION.mdの手順と既存イベント記録で照合する。'),
    ('ブラウザー診断', '単体魚比較のエラー/警告ログは0。水槽比較では従来と同じMutationObserverのDOMエラー1件（出典URLなし）がある。描画・動画保存は成功したが原因未確定。'),
]

md = f'''# v26-r2 — 細身の輪郭、銀色の地肌、細い鱗

導入: {manifest['installed_at']}。固定版: `{manifest['source_commit']}`。
正本: `custom/realism-v26/`。検査用コピー: `preview/slender-pearl-guppy-v26-r2/`。
直前のv25とLaunchAgentは `{Path(manifest['backup']).relative_to(r)}/previous/` に保存。

{summary}

測定上の前腹部の体高はv25の0.251337から0.180513、横幅は0.098273から0.083064。これはモデル内の寸法であり、写真を較正して測った生物学的な数値ではありません。

## 検証

''' + '\n\n'.join(f'**{a}**: {b}' for a,b in checks) + f'''

## 現行と比較基準の負荷

{perf_status} CPUは1コア=100%。接続中の2画面、Balanced、アプリと4個のWebKitプロセスをPIDで帰属。フレームは実描画の送信カウンターで、ディスプレイの提示フレームそのものではありません。GPUと電池持ちは未測定。

| 版 | 状態 | 時間 | CPU | 画面ごとの描画 |
|---|---|---|---|---|
''' + '\n'.join(mdrows) + f'''

メモリは `evidence/v26-performance-summary.json` の `memory_per_pid` に開始/終了/最大のphysical footprintを保存。共有領域があるためPID間の単純合計はしません。

## 表現上の残り

{limits}

[写真・前版・現行の比較、実機画像、動画](review/V26-RESULTS.html)。[残る実機操作](SETUP-VERIFICATION.md)。
'''
(r/'V26-VERIFICATION.md').write_text(md)

def fish_crop(file, box, width, height):
    return f'<svg viewBox="{box}" role="img"><image href="../evidence/{file}" width="{width}" height="{height}"/></svg>'

html = '''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>グッピー v26｜細身・銀色・鱗の比較</title>
<style>body{margin:0;background:#eef5f7;color:#19343e;font:16px/1.8 system-ui}main{max-width:1120px;margin:auto;padding:36px 24px}h1{font-size:32px;line-height:1.4}h2{margin-top:36px;font-size:23px}.intro{max-width:850px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}figure{margin:0;background:white;border-radius:10px;overflow:hidden}figcaption{padding:9px 14px;font-weight:650}svg{width:100%;display:block;aspect-ratio:2.6}img,video{width:100%;display:block}a{color:#176889}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;border-bottom:1px solid #c9dbe2;padding:9px}.scroll{overflow:auto}.note{background:#fff3db;padding:16px;border-radius:8px}.meta{font-size:14px;color:#47616a}.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}details{margin:16px 0}li{margin:8px 0}@media(max-width:700px){.grid,.two{grid-template-columns:1fr}h1{font-size:25px}}</style><main>
<p class="meta">Deskworlds · 写真を基準にした調整 · v26-r2</p><h1>丸みを残して、スリムなグッピーへ</h1>'''
html += f'<p class="intro">{summary}</p><p class="meta">導入日時: {manifest["installed_at"]}。前版v25は保存退避済み。</p>'
html += '<div class="grid"><figure>'+fish_crop('user-selected-guppy-reference.png','164 159 376 134',800,530)+'<figcaption>参考写真</figcaption></figure><figure>'+fish_crop(side,'615 150 330 134',1536,450)+'<figcaption>前版 v25 — 太かった腹</figcaption></figure><figure>'+fish_crop(side,'1127 150 330 134',1536,450)+'<figcaption>現行 v26 — 細身・銀色・鱗</figcaption></figure></div>'
html += '<p class="meta">前版と現行は同じ個体・姿勢・照明・カメラ。画像の色補正はしていません。写真は撮影条件が異なり、輪郭と色の構造の参考です。</p>'
html += f'<h2>水槽全体とMacでの表示</h2><figure><img src="../evidence/{tank}" alt="v26の明るい青い水槽全景"><figcaption>現行の描画 · 左右の茂みと中央の砂道を保持</figcaption></figure><details><summary>Macアプリの実描画を見る</summary><img src="../evidence/slender-v26-native.png" alt="Macアプリの実WebViewの描画"><p class="meta">アプリ内のWebViewスナップショット。Dockやメニューを含む画面全体の証拠ではありません。</p></details>'
html += f'<h2>動きの記録</h2><div class="two"><figure><video controls preload="none" src="../evidence/{turn}"></video><figcaption>8色の全周旋回 · 64.92秒</figcaption></figure><figure><video controls preload="none" poster="../evidence/{tank}" src="../evidence/{swim}"></video><figcaption>通常遊泳 · 65.62秒</figcaption></figure></div>'
html += '<h2>検証済みと未確認</h2><ul>'+''.join(f'<li><b>{a}</b> — {b}</li>' for a,b in checks)+'</ul>'
html += f'<h2>負荷の実測</h2><p>{perf_status} CPUは1コア=100%。2画面・Balanced。メモリのPID別記録は<a href="../evidence/v26-performance-summary.json">測定JSON</a>にあります。GPU・電池持ちは未測定です。</p><div class="scroll"><table><thead><tr><th>版</th><th>状態</th><th>時間</th><th>CPU</th><th>描画枚数 / fps</th></tr></thead><tbody>'+''.join(table)+'</tbody></table></div>'
html += f'<h2>写真との差として残る点</h2><p class="note">{limits}</p><p><a href="../V26-VERIFICATION.md">詳しい検証記録</a> · <a href="../SETUP-VERIFICATION.md">残る実機操作の手順</a> · <a href="../README.md">起動・餌やり・停止・元に戻す手順</a></p><p class="meta">上流固定コミット: {manifest["source_commit"]}。本人指定の写真は比較参照のみで、アプリにテクスチャとして同梱していません。</p></main></html>'
(r/'review/V26-RESULTS.html').write_text(html)
print('Wrote V26-VERIFICATION.md and review/V26-RESULTS.html')
