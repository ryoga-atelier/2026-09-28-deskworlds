# 出典・写真参照・権利の区分

## 元の水槽と水の参考

| 対象 | 原典 | 固定版・権利 |
|---|---|---|
| Deskworlds / Chase Lean | https://github.com/chaseleantj/deskworlds | 3950c45ef5798ed2df9f78037994bcddacebbb01、MIT |
| 発端のX投稿 | https://x.com/chaseleantj/status/2100663203076128908 | 投稿の出典。本文の再配布物は含めない |
| caustic-volume / Scottie | https://github.com/ScottieFox/caustic-volume | d87351bff19831aa9d11c0679605fad6797b133f、MIT |
| Three.js | 上流のvendor/ | 上流同梱のMIT表記を保持 |
| 上流の水槽テクスチャ | Poly Haven、上流READMEと各素材の記録 | CC0。上流の由来を保持 |

Deskworldsとcaustic-volumeのLICENSE原文は `licenses/` に保存し、上流のsubmodule内でも保持します。追加コードや生成画像と、第三者の原典の権利を一括して扱いません。独自追加部分の新しい公開ライセンスは今回設定していません。

## 本人指定の実魚写真

- 商品ページ: https://www.petballoon.net/product/65143
- 指定された画像: https://www.petballoon.net/data/petballoon3/product/zc22-91018981_2.jpg
- セッション中に保存した参照コピー: `evidence/user-selected-guppy-reference.png`
- 権利: 第三者の写真。再配布許諾やCC0とは確認していません。セッション中に本人が提示した観察・比較用の参照として保存したもので、アプリへ組み込まず、魚のテクスチャへ転用していません。リポジトリの公開は、この写真の権利移転や写真素材としての利用許諾を意味しません。
- 魚の品種・性別の厳密な同定はしていません。特定品種の忠実な再現を保証しません。

写真で本人が重視した特徴は、細身で口先がやや上向きの輪郭、小さい目、湾曲する真珠色の腹、腹の後端の丸い暗色、エラの別の色と切れ込み、明るい頭から濃い尾柄への色、細い鱗の境界です。尾は暗い根元・青い中央・薄く透ける縁、背鰭と尻鰭には着色と薄い透明層が見えます。写真の照明を正確な体色の測色値とは扱っていません。

初期の追加参照は `custom/guppy/REFERENCES.md`。Wikipediaの説明・品種写真は観察用で、第三者写真をアプリ素材として同梱していません。

## AI生成素材

魚の初期色素素材、葉、水槽背景・深度は `custom/guppy/assets/` に収録しています。同じ場所のprompt・provenanceファイルに生成経路、入力、SHA-256を記録しています。これらは実魚の写真ではありません。r15以降、胴の粒感に使っていた2枚の色素画像は読み込みを停止しましたが、過去版の再現のため残しています。
