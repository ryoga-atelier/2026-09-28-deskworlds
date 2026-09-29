# 実物基準のv15 — 参照帳

Status: 検査用試作。Macへ未導入。

- 側面: Przemysław Malkowski, Guppy red male.jpg, 2006. https://commons.wikimedia.org/wiki/File:Guppy_red_male.jpg 。CC BY-SA 3.0。Commonsの原寸写真をブラウザで観察。写真素材をアプリへ同梱・テクスチャ転用していない。頬/腹の銀色、局所的な赤い色素、丸い鰓室、眼の明るい虹彩、細い尾柄、放射するヒレ条と凸状で不均一な尾縁を参照。写真の明るい部分にはフラッシュ反射があり、露出の目標値にはしない。品種名は資料にGuppy maleのみで確定していない。
- 動き・角度: The Nature Box, Guppies (Poecilia reticulata) in an aquarium.webm, 2016-07-04. https://commons.wikimedia.org/wiki/File:Guppies_(Poecilia_reticulata)_in_an_aquarium.webm 。CC BY 4.0、Own work、121.211秒。Commons原動画を再生・再観察。資料のroundtail variety?は推定表記。ネオンテトラ等も混泳しているため対象を混同しない。小さな胸びれによる姿勢維持、短い前進と方向転換、正面時の細い断面を参照。低解像/動体ブレのため細いヒレの拍数の定量根拠にはしない。
- 水: ScottieFox / CAUSTIC//VOLUME、MIT。取得した固定commit d87351bff19831aa9d11c0679605fad6797b133f、原本 upstream/caustic-volume。利用するコードにはLICENSEを同梱。LiteはThree r186.1、既存水槽はr180。水面統合RT・屈折した光線の着地点・面積比の集光を検査対象にする。原デモ固有のduck/floor/wallレイトレースをそのまま魚に使わない。

形状のstationsは写真を見て作る試作値で、生物の計測論文由来ではない。生成PNGは色素の微細な参考として残し、生物の輪郭・眼・ヒレの正解にはしない。

- 給餌時の実写: 5snake5, Feeding of Poecilia reticulata.ogv, 2021-03-16, Own work, CC0 1.0. https://commons.wikimedia.org/wiki/File:Feeding_of_Poecilia_reticulata.ogv 。公開480p VP9版をブラウザで再生。餌タブレット前で各魚が独立して進退し、銀色/青色の側面が向きで強く変わる様子、正面の細い頭・眼・半透明の尾を観察。群れ密度と黄味の水槽色は今回の展示構図の目標にはしない。

## 発色と透明な尾の追加観察（2026-09-28 21:53 JST）

- LiveAquaria「Purple Delta Guppy, Male」 https://www.liveaquaria.com/products/purple-delta-guppy-male をブラウザで開き、拡大商品写真を実見。前側の銀色、部分的な橙色、後方の青紫、尾の細い放射状の筋と透ける縁を観察。写真は照明・撮影条件不明、絶対色の校正資料ではない。利用者がこの品種を選んだという意味ではない。写真は転載・組込みせず観察だけ。
- 利用者の追加記憶は「紫、コバルトブルー、ワインレッドのような赤、ライムイエロー、パステルパープル」「透明感のある尾に線状の色」。全身パステルという解釈を撤回。24匹と8系統の配分は維持し、各系統の個体差に深い色・淡い色を混在させる。部位・品種指定とは解釈しない。
- 透明な膜と細い色の筋は別のシェーダー成分へ。現実のヒレ条・色素そのものを科学的に同定したとはしない。
