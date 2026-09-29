# Deskworlds — Macの水槽壁紙

2026-09-28 15:40に **Guppy Garden / natural-guppy-v7** を導入。24匹・5系統のグッピーが泳ぎ、エビは入れていません。専用LaunchAgentを登録し、Riverbed・Balancedで起動しています。

実物のグッピー写真を参考に、細い胴、小さい目、上向きの口、濃淡と不規則な尾模様へ調整しました。水草は左右で高さと密度を変え、石と流木を低く非対称にして、中央を広くしました。水の霞を増やさず背面の光を調整。循環フィルターは右奥に残し、吸水部・配管・戻り口・固定具をつなげています。

**まだ写真のような再現ではありません。** 尾膜の規則的な筋、滑らかな頭部、薄い葉や苔のちらつきにCGらしさが残ります。今回の比較は [review/V7-RESULTS.html](review/V7-RESULTS.html) に全景、側面・斜め・正面、25秒の泳ぎ動画をまとめています。前後は同じ画質・寸法・露出ですが、全景の魚の時刻と位置は異なります。

アプリに入れた18本のシーンJSは、検査・録画した最終プレビューと一致。Swiftビルド、署名、構文、上流9スイート、形状・フレーム計測の回帰検査が成功しています。Macの画面取得がタイムアウトしたため、デスクトップ全体の合成表示、ネイティブメニュー、アイコン・Dockの直接操作は今回確認できていません。内部描画やブラウザ確認を、その代わりの証拠として扱いません。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。LaunchAgentが現在起動しているため、通常は手動起動不要です。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

アプリはクリックを受け取らず、カーソル位置を魚へ渡す設計です。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。カーソル反応・餌やり・Pause/Resumeはプレビューで一部確認していますが、ネイティブアプリのメニューからは未確認です。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。v7では1画面動作・もう1画面停止と、停止設定で再起動した状態を各90秒測定しました。実描画は約30fps、停止中は0fpsです。CPUとphysical footprintの詳細・測定条件はVERIFICATION.mdを参照してください。両画面が完全に覆われた状態、GPU使用率、電池持ちは未測定です。

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
- 現在の導入記録: `evidence/manifest.json`（15:40導入、v7）
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。固定コミットは `3950c45ef5798ed2df9f78037994bcddacebbb01`。ビルド時に `custom/guppy/`、`scripts/customize.py`、`scripts/aquascape.py` をコピーへ適用します。移動・餌への反応は上流の処理を使います。変更した流木の形から衝突判定を生成し、苔とシダも共通座標で移動します。
- 今回の変更前v6アプリとLaunchAgentは `rollback/20260928T154014557728+0900/previous/`、v6ソースは `rollback/clearwater-v6-source-20260928T152125/` に保存しています。
- 以前の planted-tank-v3 は `rollback/20260928T085537088104+0900/previous/Deskworlds.app`、ソースは `rollback/planted-tank-v3-before-livebearer/` に保存しています。
- さらに前のnatural-v2アプリは `rollback/20260928T022407720836+0900/previous/Deskworlds.app`、ソースは `rollback/natural-v2-before-aquascape/` に保存しています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

検証記録は `VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
