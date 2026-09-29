# Deskworlds — Macの水槽壁紙

2026-09-28に導入。現在のインストール版は **Guppy Garden / clearwater-guppy-v6** です。24匹のグッピーが泳ぎ、エビは入れていません。5系統の色に個体ごとの模様を付けています。専用LaunchAgentは登録され、現在実行中です。

水の灰緑の霞を弱め、奥の色を中立にして、控えめな水面光と広い遊泳路を設けました。画面全体の実描画はアプリ内診断画像と20秒動画で確認しています。左右の草の密度と尾模様にはまだ作り物らしさが残り、魚と水草は写真ではなく手続き生成の3Dモデルです。

比較ページは `review/clearwater-v5.html`。変更前は `evidence/clearwater-shrimp-v5-20260928T025313Z-before.png`、水の調整後は `evidence/clearwater-guppy-v6-20260928T025339Z-after.png`、現在のアプリ内診断画像は `evidence/clearwater-guppy-v6-native-20260928T121756.png`、遊泳動画は `evidence/clearwater-guppy-v6-20260928T025441Z-swim.webm` です。診断画像はWebView内部の描画で、デスクトップ全体の合成表示を確認した証拠ではありません。実機での背景合成とネイティブメニュー操作は未確認です。残る見た目の差は `VISUAL-REVIEW.md` に記録しています。

グッピーの参考写真と泳ぐ映像を見て調整したローカルの3Dモデルです。実写素材の貼り付けではなく、特定品種を正確に再現したものでもありません。尾びれ模様と表面にCGらしさが残ります。アプリ内の世界名は **World → Riverbed** です。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。LaunchAgentが現在起動しているため、通常は手動起動不要です。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

アプリはクリックを受け取らず、カーソル位置を魚へ渡す設計です。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。カーソル反応・餌やり・Pause/Resumeはプレビューで一部確認していますが、ネイティブアプリのメニューからは未確認です。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。今回のv6では状態別のCPU・メモリを測り直していません。前版の数値をv6の実測として扱わないでください。

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
- ライセンス: MIT。Three.jsはMIT、テクスチャはPoly HavenのCC0。アプリ内に上流ライセンスとREADMEを同梱しています。
- インストール先: `/Users/ryoga-atelier/Applications/Deskworlds.app`
- 自動起動: `/Users/ryoga-atelier/Library/LaunchAgents/com.chaselean.deskworlds.plist`
- 現在の導入記録: `evidence/manifest.json`（12:17導入、プロセスrunning）
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。固定コミットは `3950c45ef5798ed2df9f78037994bcddacebbb01`。ビルド時に `custom/guppy/`、`scripts/customize.py`、`scripts/aquascape.py` をコピーへ適用します。移動・餌への反応は上流の処理を使います。変更した流木の形から衝突判定を生成し、苔とシダも共通座標で移動します。
- 今回の変更前 planted-tank-v3 は `rollback/20260928T085537088104+0900/previous/Deskworlds.app`、ソースは `rollback/planted-tank-v3-before-livebearer/` に保存しています。
- さらに前のnatural-v2アプリは `rollback/20260928T022407720836+0900/previous/Deskworlds.app`、ソースは `rollback/natural-v2-before-aquascape/` に保存しています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

検証記録は `VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
