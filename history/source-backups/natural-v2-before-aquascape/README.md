# Deskworlds — Macの水槽壁紙

2026-09-28に導入。現在は **自然な質感のグッピー版（Guppy Garden / natural-v2）** です。水草の景色の中を、赤・金・青の尾びれを持つ24匹が泳ぎます。ログイン時に自動起動します。

実物の観賞用グッピー写真を参考に、細い体、控えめな大きさの目、上向きの口、鱗の光沢、尾びれの不規則な模様と半透明の縁を調整したローカルの3Dモデルです。レッドグラス・ゴールデンスネークスキン・ブルーグラスを参考にしていますが、特定の血統を正確に再現したモデルではありません。写真や動画の貼り付けではなく、魚ごとに異なる模様を描いて泳がせています。メニューバーでは従来の **World → Riverbed** を選びます。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

カーソルを魚へ近づけると反応します。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。上流メニューが表示するフレーム数はネイティブ側の要求値で、Balanced側の実際の上限とは異なる場合があります。

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

水草の景色を保ち、作者の元のテトラに戻す場合:

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
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。ビルド時に `custom/guppy/fish-anatomy.js` と `scripts/customize.py` でグッピーの見た目を適用します。移動・餌への反応は上流の処理を使い、尾びれの縁に柔らかな揺れを加えています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

検証記録は `VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
