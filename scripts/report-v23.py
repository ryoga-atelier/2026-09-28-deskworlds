"""Build the photo analysis and measured report from saved, inspected artifacts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];e=ROOT/'evidence'
manifest=json.loads((e/'manifest.json').read_text());assert manifest['variant']=='guppy-v23'
d=json.loads((e/'v23-performance-summary.json').read_text());current=[x for x in d['rows'] if x['revision']=='v23final']
assert len(current)==3 and all(x['complete'] for x in current)
assert (e/'warm-v23-native.png').exists()
side=max(e.glob('natural-v18-metrics-warm23-side-7-photo*.png'),key=lambda p:p.stat().st_mtime).name
oblique=max(e.glob('natural-v18-metrics-warm23-oblique-7-photo*.png'),key=lambda p:p.stat().st_mtime).name
tank=max(e.glob('natural-v18-tank-warm23-*.webm'),key=lambda p:p.stat().st_mtime).name
turn=max(e.glob('natural-v18-turn-warm23-*.webm'),key=lambda p:p.stat().st_mtime).name
rows=[];names={'running':'表示中','covered':'全面を隠した時','paused':'一時停止'}
for state,name in names.items():
 a=next(x for x in d['rows'] if x['revision']=='v21final' and x['state']==state);b=next(x for x in current if x['state']==state)
 w=next(x for x in b['windows'] if x['pixels']==[1789,1006])
 if state!='running':assert all(x['frames_delta']==x['water_delta']==x['fish_delta']==0 for x in b['windows'])
 rows.append([name,f"{a['cpu_percent_one_core']:.2f}%",f"{b['cpu_percent_one_core']:.2f}%",str(w['frames_delta']),f"{w['fps']:.3f}"])
headers=['状態','v21 CPU','v23 CPU','v23フレーム増加','fps']
table='<table><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
mdtable='|'+'|'.join(headers)+'|\n|---|---:|---:|---:|---:|\n'+'\n'.join('|'+'|'.join(row)+'|' for row in rows)
analysis=[
 ('背中・体側','薄い赤茶・藤色・黄みのある地肌に、細い鱗の縁が重なる。上半身全体が黒いわけではない。','広い暗い帯と銀色の下半身になり、色のある地肌が隠れた。','暗い面を撤去。赤茶・藤色の地肌へ、細い茶紫の鱗の縁を重ねた。'),
 ('お腹','前腹部の丸みに沿った乳白色の領域。周囲に金色・桃色が残る。','白・銀色が下半身へ広がり、暗い上半身との二色分割に見えた。','白を前腹部の曲線に限定。周囲に黄み、頬に桃色を残した。'),
 ('鱗・反射','薄い網目と小さな反射。厚い板が並んでいるようには見えない。','大きな鱗の凹凸と金属的な反射が強く、鎧のように見えた。','凹凸を浅く、線を細かくし、金属反射を弱めた。'),
 ('目・頭','黒い瞳の周囲には明るい輪があり、頭は桃色と黄みのある地肌。','顔全体に暗い膜を重ね、頭が灰黒色に見えた。','暗色を目のすぐ周囲へ限定。顔を地肌の色へ戻した。'),
 ('ヒレ','背鰭・尻鰭は薄い青と透明部。尾は丸い黒い付け根、青い中央、薄い透明縁。','青と透明の分離は改善したが、黒い付け根が直線的で、先端を広く薄くしすぎた。','尾の根元を丸い範囲へ絞り、中央の青を残して外縁を透かす。背鰭・尻鰭の色層は保持。')]
md='''# 写真との比較・修正 v23

## 判定

v22の「暗い上半身と白い下半身」は、本人の意図と写真から外れていた。暗さの種類を、地肌に重なる細い鱗の線と、広い黒い色面で取り違えた。実装済み・シェーダー成功という事実は外見の合格を意味しない。

v23はこの色の構造を修正した版であり、写真そっくりの完成版・本人の最終合格ではない。写真の中央上の個体を参照。撮影照明とアプリの照明は異なるため、RGBの単純一致や黒白二値化を合格条件にしない。

|部位|写真|v22の違い|v23での修正|
|---|---|---|---|
'''+ '\n'.join('|'+ '|'.join(row)+'|' for row in analysis)+'''

## 残る見た目の差

- 頭・鰓の輪郭は写真より硬い。腹から頬・口へつながる形にはまだ差がある。
- 鱗とヒレの筋は写真より規則的。地肌の色むらと小さな透け・反射の変化は近似にとどまる。
- 側面写真1枚から裏面や全周の形を正確に復元したものではない。
- 背景の植栽は2.5D、魚は3D。色の面を直しただけで実写と同一とは言わない。

## 導入と検証

'''+f"導入時刻: {manifest['installed_at']}。保存退避: `{manifest['backup']}/previous/`。\n\n"+'''
- v21の形状、24匹・8色、泳ぎ、水面・水草・泡・砂、照明・露出を保持。今回の魚の変更はphoto-material.js。
- `v23-check.log`、`v23-tests.log`：構文と既存9スイート成功。
- `v23-shape-swim.log`、`v23-anatomy.log`、`v23-living-water.log`：形状・法線・色割当・600位相・砂と停止の検査成功。
- 8色を横・斜め・正面・背面で描画して確認。素材なしの代替状態も描画。比較ページのシェーダーエラーなし。
- 全周と通常遊泳を約65秒ずつ記録。代表姿勢を目視したもので、全フレームを連続目視して実写相当と合格した記録ではない。通常遊泳の同時比較は魚位置・カメラ・投影が一致。
- Swiftビルド・署名・plist検査成功。`v23-install.log`。
- 導入前プレビューとアプリの描画・素材は一致。`v23-integrity.json`。
- 元の壁紙とmacOSアクセシビリティのファイルハッシュはv21と一致。上流は固定コミット3950c45ef5798ed2df9f78037994bcddacebbb01のまま変更なし。
- v22は本人が色面を不採用と指摘。表示中90秒だけ実測し、被覆と停止の測定は中止した。v22を全項目合格として扱わない。

## 実機負荷

各90秒・2画面・Balanced。v21と同じ画面条件。CPUはアプリと専用WebKit 4プロセス、100%は1コア分。外部1789×1006は表示、内蔵1665×1081は他ウィンドウで被覆。被覆測定は外部も検査用Finderで覆う。ブラウザーの比較描画は閉じて測定。

'''+mdtable+'''

被覆・停止では両画面の描画と魚・水の時刻増加はゼロ。停止はアプリ固有の保存設定と再起動で検査し、メニュークリックと混同しない。最後に元のpaused=0へ戻して6秒のフレーム増加を確認。

メモリは `evidence/v23-performance-summary.json` の各プロセスのphysical footprint開始・終了・最大値に記録。共有メモリがあるため合算しない。GPU負荷・電池持ち・画面への実提示時刻は未測定。単発の測定から性能改善を断定しない。

## 実操作の未確認

水槽メニューを開くイベントは記録されているが、Feed・Pause/Resume・Quitの操作と画面結果の組は未確認。実カーソル反応、Dock、ドラッグ、実スリープ復帰、実再ログインは未確認。SETUP-VERIFICATION.mdの手順と実イベントで照合する。登録状態は実再ログインの代わりにしない。全項目完了ではない。
'''
(ROOT/'V23-VERIFICATION.md').write_text(md)
def crop(src,viewbox,label):
 return f'<figure><svg viewBox="{viewbox}" role="img" aria-label="{label}"><image href="../evidence/{src}" width="{800 if src.startswith("user-") else 1536}" height="{530 if src.startswith("user-") else 450}"/></svg><figcaption>{label}</figcaption></figure>'
photos=crop('user-selected-guppy-reference.png','164 159 376 134','参照写真：色のある地肌に細い鱗。白い部分はお腹に限られる。')+crop(side,'615 153 330 130','v22：暗い面が広すぎた版。本人の指摘で不採用。')+crop(side,'1127 153 330 130','v23：広い黒い帯を外し、地肌・鱗の線・白い腹を分けた修正版。')
atable='<table><tr>'+''.join('<th>'+x+'</th>' for x in ['部位','写真','v22との違い','修正'])+'</tr>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in analysis)+'</table>'
page=f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>写真とグッピーの違い — 地肌と鱗を修正したv23</title><link rel="stylesheet" href="report-v19.css"><style>svg{{width:100%;display:block;border-radius:10px}}.compare{{max-width:760px;margin:auto}}figure{{margin:18px 0}}figcaption{{padding:9px 0}}.scroll{{overflow:auto}}td{{min-width:150px}}td:first-child{{min-width:90px}}.notice{{font-size:18px;line-height:1.8}}</style><main>
<h1>黒い面ではなく、色のある地肌と細い鱗</h1><p class="notice">ご指摘の通り、v22は暗い背中と白い腹へ分けすぎていました。写真では薄い赤茶・藤色・黄みのある地肌に細い鱗が重なり、お腹だけが乳白色です。その解釈へ直したv23をMacに反映しました。</p>
<h2>同じくらいの大きさで比較</h2><div class="compare">{photos}</div><p>色補正はしていません。写真とアプリでは照明と背景が異なります。比較は色の面積と配置、鱗の細さを中心に見ています。</p><details><summary>写真全体と、同じ光で描いたv21・v22・v23</summary><img src="../evidence/user-selected-guppy-reference.png" alt="参照写真全体"><img src="../evidence/{side}" alt="左v21、中央v22、右v23"><img src="../evidence/{oblique}" alt="同じ3版を斜めから"></details>
<h2>何を取り違えていたか</h2><div class="scroll">{atable}</div>
<h2>まだ写真と違うところ</h2><p>頭・鰓の輪郭が硬く、鱗や尾の筋も写真より規則的です。地肌の細かい色むら、角度で変わる柔らかな反射・透け感にも差が残ります。今回直したのは色の構造であり、「本物そっくりに完成」とは判定していません。</p>
<h2>Macに反映した水槽</h2><img src="../evidence/warm-v23-native.png" alt="導入済みv23の実機描画"><p>アプリのWKWebView診断画像。デスクトップ全体の合成画像ではありません。水槽の背景・24匹・8色・Balanced・自動起動を保持。</p>
<details><summary>通常遊泳と8色の全周記録（各約65秒）</summary><video controls preload="metadata" src="../evidence/{tank}"></video><video controls preload="metadata" src="../evidence/{turn}"></video></details>
<h2>実機で各90秒の負荷確認</h2>{table}<p>CPUの100%は1コア分。被覆・停止中の両画面の描画増加はゼロ。メニュー実操作とは分けた検査です。</p><p><a href="../V23-VERIFICATION.md">比較分析・実測・確認範囲</a> · <a href="../README.md">普段の操作と元に戻す手順</a></p><p>Feed/Pause/Resume/Quit、実カーソル、Dock・ドラッグ、実スリープ・再ログインの確認は残っています。<a href="../SETUP-VERIFICATION.md">確認手順</a></p></main></html>'''
(ROOT/'review/V23-RESULTS.html').write_text(page)
print('Saved V23-VERIFICATION.md and review/V23-RESULTS.html')
