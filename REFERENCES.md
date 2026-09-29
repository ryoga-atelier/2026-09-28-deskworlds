# 参照帳

現行は末尾のv14条件。以下のv12/v13条件は履歴です。

## 履歴: v12

- 利用者の今回の指摘：奥が暗く、真っ黒に見える。グッピーの方向性は改善しているが、調整と未確認部分の点検を続ける。
- 編集対象：custom/guppy/assets/aquarium-photo-v10.png。構図・岩・砂・流木・濾過設備の位置を保持し、背景の照明を変更する。
- 魚の資料：custom/guppy/REFERENCES.md。実写資料は観察用で、今回の素材には転用しない。
- 前回の判定と不足：VISUAL-REVIEW.md、VERIFICATION.md。v11の採用判断では後景の黒さを許容しすぎていた。
- 変更しない条件：上流固定コミット、魚のv11形状・行動、OS壁紙、全体アクセシビリティ、自動起動登録。

## v13の参照条件

2026-09-28 利用者の具体像：透明度の高いミネラルウォーターのように透き通った青い水。水草の揺れ・魚に伴う薄い砂煙・水面の揺れ・泡。v12の灰緑の静止面は不採用。新しい背景は配置を維持し、動きは実時間の描画で加える。

## v14の参照条件

今回の承認済み計画：明度を上げ、適度な彩度と真珠のような反射、自然な前腹部、薄紫・シャンパン・淡い黄土色中心の8色24匹。背景はv13固定。写真資料は観察用で転用せず、既存のAI色素PNG2枚を維持。地色・ヒレ・代替描画を共通の `custom/guppy/guppy-palette.js` から構成する。今回追加の画像生成や外部素材取得はない。

## 最新の一次資料と再制作の基準

- 利用者指定X: https://x.com/tetumemo/status/2104131601663930588?s=20
- ScottieFox公開: https://scottiefox.github.io/caustic-volume/
- ソース: https://github.com/ScottieFox/caustic-volume
- 軽量版: https://scottiefox.github.io/caustic-volume/lite/index.html
- サイドからの引継ぎ: Lite Three.js r186、MIT、水面高さ/傾き、GPU波紋、反射・屈折・全反射・距離吸収・集光。こちらではこれから原本と実表示を照合する。Full動作・負荷とMac統合は未確認。
- 実魚の側面・斜め・正面・泳ぎは新たに一次資料へ照合し、品種と利用条件を記録する。生成画像を生物の正解にしない。


## v27 visual cues (2026-09-29)

The owner-selected `evidence/user-selected-guppy-reference.png` remains the primary visual reference. For this correction, compare the body scale arcs from opercle to caudal peduncle, the small diffuse shadow within the pale posterior belly, and the blue-tinted transparent fin membrane with readable radial rays. Do not infer calibrated colour from this aquarium exposure. Reference stays outside packaged textures.
