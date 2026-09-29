# Deskworlds — Macのグッピー水槽

2026-09-28 20:55に **Guppy Garden / pearl-guppy-v14** を導入。明るい体色・自然な厚み・8色24匹へ更新しました。Riverbed、Balanced、ログイン時起動を保持しています。

薄紫4・シャンパン4・淡い黄土色3・水色3・青緑2・桃色2・赤3・濃い青3。陰側にも柔らかい光を回し、前腹部を約12%、横幅を最大18%増やしています。透明な青い水、水面・水草・泡・砂の動きはv13を保ちました。

[65秒の動画と比較](review/V14-RESULTS.html)、[今回の検証記録](V14-VERIFICATION.md)、[見た目の判断](VISUAL-REVIEW.md)を保存しています。8色4方向・全周旋回・通常遊泳、既存9テスト、形状・配色・給餌・停止再開を検査し、Macでの表示も確認しました。導入した104ファイルは採用候補r3と一致しています。

**魚の変更は反映済み。操作確認は一部未完了です。** Finder操作とアイコン選択は観測しました。Macメニュー・Dockは操作ツールの応答が得られず、ドラッグ位置も取得できませんでした。実カーソル反応、実スリープ復帰、再ログインを含め、[残る確認手順](SETUP-VERIFICATION.md)で本人操作後に記録を照合します。未実施を合格扱いにしません。

魚は3Dモデルと2枚の色素素材、背景は写真風2.5Dです。模様の共通性やヒレ・屈折の近似は残り、実物と区別不能な再現とはしていません。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。LaunchAgentが現在起動しているため、通常は手動起動不要です。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

アプリはクリックを受け取らず、カーソル位置を魚へ渡す設計です。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。餌やり・Pause/Resumeはv14のプレビューとアプリ固有の保存設定で確認し、カーソル反応の自動テストも通っています。実カーソル操作の確認は別途必要です。ネイティブアプリのメニューからは未確認です。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。v14の変更前後を各状態90秒で測った結果はV14-VERIFICATION.mdに記録します。過去版の数値を現行値として流用しません。CPUとphysical footprintの詳細・測定条件はVERIFICATION.mdを参照してください。ウィンドウで両画面を覆った場合も受動の描画カウンターで確認します。GPU使用率、電池持ちは未測定です。

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
- 現在の導入記録: `evidence/manifest.json`（20:55導入、v14 + 実機確認用の記録）
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。固定コミットは `3950c45ef5798ed2df9f78037994bcddacebbb01`。ビルド時に `custom/guppy/`、`scripts/customize.py`、`scripts/aquascape.py`、`scripts/natural_tank.py`、`scripts/photo_habitat.py` をコピーへ適用します。餌と警戒反応は上流の処理を使い、群れの間隔・同調・探索数はグッピー用に変更しています。変更した流木の形から衝突判定を生成し、苔とシダも共通座標で移動します。
- 今回の変更前v13アプリとLaunchAgentは `rollback/20260928T205506131351+0900/previous/`、コード・文書は `rollback/v13-before-pearl-20260928T203313/` に保存。
- 以前の変更前v12アプリとLaunchAgentは `rollback/20260928T193148710980+0900/previous/`、コードと文書は `rollback/v12-before-living-water-20260928T191855/` に保存しています。
- v11アプリとLaunchAgentは `rollback/20260928T191345139232+0900/previous/`、コードと文書は `rollback/v11-before-brighter-rear-20260928T190553/` に保存しています。
- 以前のv10アプリとLaunchAgentは `rollback/20260928T175718361798+0900/previous/`、編集前ソース・文書は `rollback/v10-before-comprehensive-20260928T175230/` に保存しています。
- 前回の変更前v8アプリとLaunchAgentは `rollback/20260928T171540657669+0900/previous/`、編集前ソース・文書は `rollback/v8-before-natural-tank-20260928T164903/` に保存しています。
- 以前のv7アプリとLaunchAgentは `rollback/20260928T162824060202+0900/previous/`、ソースは `rollback/natural-v7-before-photo-20260928T162113/`。v8初回の起動待ち修正前は `rollback/20260928T163053631300+0900/previous/` に保存しました。
- 以前のv6アプリとLaunchAgentは `rollback/20260928T154014557728+0900/previous/`、v6ソースは `rollback/clearwater-v6-source-20260928T152125/` に保存しています。
- 以前の planted-tank-v3 は `rollback/20260928T085537088104+0900/previous/Deskworlds.app`、ソースは `rollback/planted-tank-v3-before-livebearer/` に保存しています。
- さらに前のnatural-v2アプリは `rollback/20260928T022407720836+0900/previous/Deskworlds.app`、ソースは `rollback/natural-v2-before-aquascape/` に保存しています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

検証記録は `VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
