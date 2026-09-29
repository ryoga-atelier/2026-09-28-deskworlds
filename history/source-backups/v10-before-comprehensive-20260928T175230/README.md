# Deskworlds — Macのグッピー水槽

2026-09-28 17:15に **Guppy Garden / photo-depth-v10** を導入。24匹・5系統の色、エビなし、Riverbed・Balanced・ログイン時起動を保持しています。

今回、水草・石・砂・水中の光を含む背景を作り直しました。写実的にAI生成した水槽の色画像と、おおよその奥行き画像を組み合わせています。微かな葉の揺れと水底の光を加え、魚が植物の奥へ入ると隠れる構成です。魚は閉じた3D胴体と変形するヒレのまま、赤系モザイクと青系グラスの2素材を使って泳ぎます。

**背景は2.5D、魚は操作に反応する3Dです。** 実写映像のループや、すべての水草を立体化したシミュレーションではありません。生成素材の光沢、奥行きと障害物判定の近似、模様の共有、ヒレの流体表現には限界があります。「利用者のイメージに到達した」という受領確認はまだ得ていません。

[review/V10-RESULTS.html](review/V10-RESULTS.html) に、前後の全景と25秒の泳ぎ・給餌映像を保存。Macのアプリウィンドウでも表示を確認しています。デスクトップ全体の合成表示、ネイティブメニュー、アイコン・Dock操作、実スリープ・再ログインの確認とは分けています。採用版・テスト・実測は [VERIFICATION.md](VERIFICATION.md)、見た目の判断は [VISUAL-REVIEW.md](VISUAL-REVIEW.md) に記録しています。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。LaunchAgentが現在起動しているため、通常は手動起動不要です。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

アプリはクリックを受け取らず、カーソル位置を魚へ渡す設計です。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。カーソル反応・餌やり・Pause/Resumeはプレビューで一部確認していますが、ネイティブアプリのメニューからは未確認です。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。現行v10の状態別実測はVERIFICATION.mdの先頭に記録しています。過去版の数値を現行値として流用しません。CPUとphysical footprintの詳細・測定条件はVERIFICATION.mdを参照してください。両画面が完全に覆われた状態、GPU使用率、電池持ちは未測定です。

## 動かない時

1. 他のウィンドウで壁紙が隠れていないか確認します。
2. メニューにResumeがあれば選びます。一時停止の選択は再起動後にも残ります。
3. 低電力モードでは描画が停止します。
4. メニューバーのアイコンが見つからない場合、Finderを手前にすると左側のメニューが短くなります。それでも見つからない場合は下のコマンドで停止できます。

macOSの「視差効果を減らす」など、システム全体の設定は変更していません。元の壁紙画像も変更していません。

## 自動起動をやめる / 元へ戻す

ターミナルで次を実行すると、実行中の水槽を停止し、自動起動設定を案件のrollbackへ退避します。アプリは残るので手動で起動できます。

```sh
python3 /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/scripts/provision.py disable-autostart
```

アプリも使わなくなった場合は、先にメニューのQuitで終了してから次を実行します。アプリと自動起動設定を削除せずrollbackへ移します。

```sh
python3 /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/scripts/provision.py retire
```

自動起動を再び有効にする場合は、次を実行します。確認済み版を再ビルドし、既存物を保存退避して導入します。

```sh
python3 /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/scripts/provision.py install
```

## 元の魚へ戻す

魚と水槽全体を、作者の元のRiverbedに戻す場合:

```sh
python3 /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/scripts/provision.py install --variant original
```

グッピーへ戻す場合は `install --variant guppy`。どちらも既存のアプリを削除せずrollbackへ保存します。

## 出典と構成

- 元投稿: https://x.com/chaseleantj/status/2100663203076128908
- 作者のソース: https://github.com/chaseleantj/deskworlds
- 固定コミット: `3950c45ef5798ed2df9f78037994bcddacebbb01`
- ライセンス: 上流とThree.jsはMIT、上流同梱テクスチャはPoly HavenのCC0。今回の魚・葉・水槽の追加素材はAI生成で、由来・プロンプトを `custom/guppy/assets/` に保存。アプリ内に上流ライセンスとREADMEを同梱しています。
- インストール先: `/Users/ryoga-atelier/Applications/Deskworlds.app`
- 自動起動: `/Users/ryoga-atelier/Library/LaunchAgents/com.chaselean.deskworlds.plist`
- 現在の導入記録: `evidence/manifest.json`（17:15導入、v10）
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。固定コミットは `3950c45ef5798ed2df9f78037994bcddacebbb01`。ビルド時に `custom/guppy/`、`scripts/customize.py`、`scripts/aquascape.py`、`scripts/natural_tank.py`、`scripts/photo_habitat.py` をコピーへ適用します。移動・餌への反応は上流の処理を使います。変更した流木の形から衝突判定を生成し、苔とシダも共通座標で移動します。
- 今回の変更前v8アプリとLaunchAgentは `rollback/20260928T171540657669+0900/previous/`、編集前ソース・文書は `rollback/v8-before-natural-tank-20260928T164903/` に保存しています。
- 以前のv7アプリとLaunchAgentは `rollback/20260928T162824060202+0900/previous/`、ソースは `rollback/natural-v7-before-photo-20260928T162113/`。v8初回の起動待ち修正前は `rollback/20260928T163053631300+0900/previous/` に保存しました。
- 以前のv6アプリとLaunchAgentは `rollback/20260928T154014557728+0900/previous/`、v6ソースは `rollback/clearwater-v6-source-20260928T152125/` に保存しています。
- 以前の planted-tank-v3 は `rollback/20260928T085537088104+0900/previous/Deskworlds.app`、ソースは `rollback/planted-tank-v3-before-livebearer/` に保存しています。
- さらに前のnatural-v2アプリは `rollback/20260928T022407720836+0900/previous/Deskworlds.app`、ソースは `rollback/natural-v2-before-aquascape/` に保存しています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

検証記録は `VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
