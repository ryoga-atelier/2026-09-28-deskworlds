# v15 の試作と採用撤回

2026-09-28 22:02に実機へ導入し表示を確認。銀肌と局所色素、細い透明膜、16波の共通水面、4層の集光、実シーンの平面反射、3D植栽を実装した。CAUSTIC//LITEのMIT許諾を同梱。上流Three r180を維持。

その後の本人評価で、ヒレが小さく薄いため細長い魚に見える、水草は前版の明るい左右の茂みが好み、と判明。外観合格を撤回。v16は好みのv14背景と大きめの尾・背びれを組み合わせる。v15の3D水槽は `preview/exhibit-guppy-v15-r3` と `custom/realism-v15` に保存。

v15の表示中90秒だけは計測した。evidence/v15final-load-running.json と同 frames-running.json。この値をv16の負荷に流用しない。covered/pausedはv15では未実施。

候補全周・通常遊泳は約65秒のWebMへ保存し、ブラウザ再生完走を確認。見た目の合格を意味しない。実機画像 exhibit-v15-r3-native.png はWKWebView診断画像でデスクトップ合成全体ではない。
