# v29 r12 — 黒い斑・頭から尾の濃淡・背中の色

更新: 2026-09-29T13:25:07.767715+09:00  
状態: Macへ反映。本人のロック解除後、実機WKWebViewの外観を確認。今回の色調整と全セットアップの検証を区別する。

## 今回の修正

r11の黒が薄すぎるという本人の訂正を反映した。腹の曲線、半円の大きさ、鱗、頬の細部は保ち、色の配分だけを調整。

- 腹の斑を、r8で使った暗い灰黒色と混合係数へ戻した。白と共通の外枠、内側へ湾曲する境界はr11を維持。
- 黒い斑から透過する補助光を減らし、局所的な反射も抑えた。鱗と濃淡が残るよう色面の微細な変化は維持。
- 明るい頭から濃い尾柄への明度差を強化。後方の胴に回る透過光も抑え、明るい腹は別の層として保持。全画面の露出・水・砂・照明は変更していない。
- 共通パレットから尾の色を背中と後方の胴へ薄く重ねた。水色・赤・シャンパン・青緑・桃色・薄紫・黄土色・青が、尾だけでなく胴にも現れる。
- 鱗にかけていた共通の茶色を局所の体色に置き換え、重ね塗りで8色が同じ茶色へ戻るのを防いだ。
- 変更した場面ソースはphoto-material.jsのみ。体型、目・口・ヒレの形、24匹・8色の割当、水草・泡・水・砂の動作は変更なし。

## 見た目と数値

- 比較: review/shape-v29-r12.html（左r11、右r12）。同じ光・個体・姿勢。
- 横: evidence/bronze-gradient-v29-side-7-photo-detail1-20260929T042111Z.png
- 横の抜粋: evidence/v29-r12-final-comparison.png（上下の余白のみ除去）。
- 8色の横: evidence/bronze-gradient-v29-atlas-7-photo-detail1-20260929T042140Z.png
- 素材なし・8色の斜め: evidence/bronze-gradient-v29-atlas-oblique-7-fallback-detail1-20260929T042222Z.png
- 8色全周動画: evidence/bronze-gradient-v29-turn-7-20260929T042339Z.webm。64.949秒、1868フレーム、1536×1536。代表4コマを確認し、左右の胴の色・斑・斜めの陰影に明らかな破綻なし。連続65秒の実機目視確認とは扱わない。
- 青い1匹の横比較画像で、同じ位置の矩形から線形sRGB輝度の中央値を採取。頭／後方胴の比は2.02→3.77、白い腹／黒斑は4.06→11.99。これは今回の指定部分の測定であり、全個体・実機全体・アクセシビリティ比の測定ではない。座標と方法: evidence/v29-r12-render-contrast.json。
- Mac実画面で、黒い腹の斑、後方胴の青・紫・桃色・黄系の違い、頭から尾の濃淡を観測。ネイティブ画像ファイルの保存はしていない。

## 検査・導入

- 適用済みプレビューでnpm run check、npm test、check-photo-guppy-v29、check-photo-guppy-v28、check-guppy-v17、check-v17、check-living-water成功。WebGLエラーは観測なし。
- 版: bronze-gradient-guppy-v29-r12
- 上流: 3950c45ef5798ed2df9f78037994bcddacebbb01、作業ツリー変更なし。
- ビルド: /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/build/20260929T132302760260+0900/Deskworlds.app
- r11のアプリとLaunchAgent退避先: /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/rollback/20260929T132305333986+0900/previous/
- PID（検証時）: 37922。署名・ソース12ファイル一致・LaunchAgent稼働・RunAtLoadを確認。Riverbed、停止設定0、Balancedを保持。
- 起動時の2つのウィンドウ: 544フレーム／18.177秒、362フレーム／12.005秒で、ともに30fps設定・running true。一方が1フレームのままという過去の状態は今回の起動標本では再現していない。長時間・全ディスプレイの連続動作までの証明ではない。
- 導入確認: evidence/v29-r12-final-integrity.json。差分: evidence/v29-r12-material.patch。前回記録: evidence/V29-R11-VERIFICATION.md。

## 残る確認

MacメニューのFeed/Pause/Resume/Quit、Dock・ドラッグ・実カーソル反応、実スリープ・再ログイン、長時間の全ディスプレイ確認、表示中・被覆中・停止中の各90秒負荷比較は未完了。今回の実画面の外観確認を、これらの合格や本人の最終合格とは数えない。

写真そのものの再現にはまだ限界がある。鱗の反復や近接時の形状分割、遠景での細かな頬の反射の見え方は手続き的な3D表現である。
