# Deskworlds — Macのグッピー水槽

2026-09-28 16:30に **Guppy Garden / textured-guppy-v8** を導入。24匹・5系統の色で、エビなし、Riverbed・Balanced・ログイン時起動を維持しています。

「本物そっくり」を目標に調整を続けています。今回は、AI生成の写実的な体表・尾膜の素材を、閉じた3Dの胴体と変形するヒレに組み込みました。頭と腹の輪郭を素材に合わせ、尾の規則的な折り目を弱めています。起動時に隠れている画面も、素材を読み込んでから最初の1枚を表示するよう修正しました。

**実魚の写真ではなく、完全な写実化も未達です。** 素材中の光沢、模様の共有、背面・腹側の細部、ヒレの流体表現、水草の薄さ・苔の粒・背面の平面感には調整の余地があります。水草・石・水・循環設備はv7の構成を維持しています。

比較は [review/V8-RESULTS.html](review/V8-RESULTS.html)。同じ倍率・照明の側面・斜め・正面と25秒の泳ぎ、全景、Macアプリの内部画像を保存しています。生成素材とプロンプト・由来は `custom/guppy/assets/` と `custom/guppy/photo-prompt-v8.txt`。画像生成は組み込みimage_genで実行し、元の透明度を保持しました。

Macアプリのウィンドウで新しい体表を目視し、両画面の素材読込成功も確認。1画面動作・もう1画面被覆停止の90秒測定は約30fps、CPU合計18.15%（1コア=100%）でした。デスクトップ全体の合成表示、ネイティブメニュー、アイコン・Dock操作、実スリープ・再ログインは未確認です。アプリ内画像をその確認の代わりにはしません。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。LaunchAgentが現在起動しているため、通常は手動起動不要です。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

アプリはクリックを受け取らず、カーソル位置を魚へ渡す設計です。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。カーソル反応・餌やり・Pause/Resumeはプレビューで一部確認していますが、ネイティブアプリのメニューからは未確認です。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。v8では1画面動作・もう1画面停止の状態を90秒測定しました。停止設定で再起動した状態の負荷測定はv7の履歴であり、v8の値として流用しません。CPUとphysical footprintの詳細・測定条件はVERIFICATION.mdを参照してください。両画面が完全に覆われた状態、GPU使用率、電池持ちは未測定です。

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
- 現在の導入記録: `evidence/manifest.json`（16:30導入、v8）
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。固定コミットは `3950c45ef5798ed2df9f78037994bcddacebbb01`。ビルド時に `custom/guppy/`、`scripts/customize.py`、`scripts/aquascape.py` をコピーへ適用します。移動・餌への反応は上流の処理を使います。変更した流木の形から衝突判定を生成し、苔とシダも共通座標で移動します。
- 今回の変更前v7アプリとLaunchAgentは `rollback/20260928T162824060202+0900/previous/`、ソースは `rollback/natural-v7-before-photo-20260928T162113/`。v8初回の起動待ち修正前は `rollback/20260928T163053631300+0900/previous/` に保存しました。
- 以前のv6アプリとLaunchAgentは `rollback/20260928T154014557728+0900/previous/`、v6ソースは `rollback/clearwater-v6-source-20260928T152125/` に保存しています。
- 以前の planted-tank-v3 は `rollback/20260928T085537088104+0900/previous/Deskworlds.app`、ソースは `rollback/planted-tank-v3-before-livebearer/` に保存しています。
- さらに前のnatural-v2アプリは `rollback/20260928T022407720836+0900/previous/Deskworlds.app`、ソースは `rollback/natural-v2-before-aquascape/` に保存しています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

検証記録は `VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
