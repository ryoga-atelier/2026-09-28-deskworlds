# Deskworlds — Macのグッピー水槽

2026-09-29 13:23 JSTに **guppy-v29 r12** を反映しました。腹の黒い斑を明瞭に戻し、明るい頭から濃い尾側への差を強めました。背中と後方の胴にも尾びれに合わせた8系統の色を重ねています。r11の腹の曲線・鱗・頬、体型、24匹、水景、Balanced、自動起動は保持。ロック解除後のMac実画面でも確認しました。

左右の明るい茂みと中央の砂道、水面・泡・砂・水草の動きはそのままです。魚は3D、植栽と背景は2.5Dです。

[最新のr11/r12写真比較](review/shape-v29-r12.html)、[検証記録](V29-VERIFICATION.md)、[残る実機操作](SETUP-VERIFICATION.md)。v22の広い黒い色面は不採用にし、その後の本人の指示に沿って修正しています。v29 r12は今回の実装候補で、本人の最終合格や写真と同じ写実性を得たとはしていません。

**全項目完了ではありません。** 今回の起動ログでは両ウィンドウの描画が進みました。長時間の全ディスプレイ確認は残ります。 外観の完全な実写再現、MacメニューのFeed/Pause/Resume/Quit、Dock、ドラッグ、実カーソル反応、実スリープ復帰と再ログイン、v29 r12の表示中・被覆中・停止中の負荷測定は残っています。

## 普段の使い方

- **起動**: Finderの「移動 → ホーム → Applications」で `Deskworlds.app` を開きます。LaunchAgentが現在起動しているため、通常は手動起動不要です。
- **餌やり**: 画面上部のDeskworldsアイコン → **Feed**。
- **一時停止 / 再開**: 同じメニューの **Pause / Resume**。
- **景色を変更**: **World → Riverbed / Coral reef / Betta**。選択は次回起動にも残ります。
- **終了**: **Quit**。元の壁紙が現れます。次回ログイン時には再び起動します。

アプリはクリックを受け取らず、カーソル位置を魚へ渡す設計です。デスクトップのクリックでは餌を与えません。ファイルの選択・ドラッグはFinderの操作です。餌やり・Pause/Resumeは過去版のプレビューとアプリ固有の保存設定、カーソル反応は自動テストで確認しています。v29 r12の実機操作は未確認で、過去版の結果をv29 r12の合格には数えていません。

画質はBalanced（上限30fps）。ウィンドウでほぼ隠れた時、低電力モード、画面ロック・画面スリープ中は描画を停止する設計です。停止中もアプリのメモリは保持されます。v29 r15では、ウィンドウで隠れた画面・眠った画面が60秒続くと水槽ページを手放し（メモリ解放）、見えたら作り直して再表示します。一時停止中は止まった水槽を表示したままにします。表示中・隠れた時・一時停止中の実測はV29-R15-VERIFICATION.mdを参照。電池持ちは未測定です。

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

自動起動を再び有効にする場合は、次を実行します。現行版を再ビルドし、既存物を保存退避して導入します。

```sh
python3 /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/scripts/provision.py install
```

## 元の魚へ戻す

魚と水槽全体を、作者の元のRiverbedに戻す場合:

```sh
python3 /Users/ryoga-atelier/workspace/apps/2026-09-28-deskworlds/scripts/provision.py install --variant original
```

現行グッピーへ戻す場合は `install --variant guppy-v29`（`guppy` は保存したv14）。どちらも既存のアプリを削除せずrollbackへ保存します。

## 出典と構成

- 元投稿: https://x.com/chaseleantj/status/2100663203076128908
- 作者のソース: https://github.com/chaseleantj/deskworlds
- 固定コミット: `3950c45ef5798ed2df9f78037994bcddacebbb01`
- ライセンス: 上流とThree.jsはMIT、上流同梱テクスチャはPoly HavenのCC0。今回の魚・葉・水槽の追加素材はAI生成で、由来・プロンプトを `custom/guppy/assets/` に保存。アプリ内に上流ライセンスとREADMEを同梱しています。
- インストール先: `/Users/ryoga-atelier/Applications/Deskworlds.app`
- 自動起動: `/Users/ryoga-atelier/Library/LaunchAgents/com.chaselean.deskworlds.plist`
- 現在の導入記録: `evidence/manifest.json` と `evidence/v29-r12-final-integrity.json`
- 導入スクリプト: `scripts/provision.py`。上流の削除付きinstall/uninstallは実行していません。
- 上流原本は変更していません。固定コミットは `3950c45ef5798ed2df9f78037994bcddacebbb01`。ビルド時に `custom/guppy/`、`scripts/customize.py`、`scripts/aquascape.py`、`scripts/natural_tank.py`、`scripts/photo_habitat.py` をコピーへ適用します。餌と警戒反応は上流の処理を使い、群れの間隔・同調・探索数はグッピー用に変更しています。変更した流木の形から衝突判定を生成し、苔とシダも共通座標で移動します。
- 直前r11のアプリとLaunchAgentは `rollback/20260929T132305333986+0900/previous/` に保存。
- r10のアプリとLaunchAgentは `rollback/20260929T125244773591+0900/previous/` に保存。
- r9のアプリとLaunchAgentは `rollback/20260929T122931884288+0900/previous/` に保存。
- r8のアプリとLaunchAgentは `rollback/20260929T122207070102+0900/previous/` に保存。
- r7のアプリとLaunchAgentは `rollback/20260929T120959741663+0900/previous/` に保存。
- r6のアプリとLaunchAgentは `rollback/20260929T113154110446+0900/previous/` に保存。ヒレ修正前のr7は `rollback/20260929T114432347435+0900/previous/`。
- v28直前のv27アプリとLaunchAgentは `rollback/20260929T094751332461+0900/previous/` に保存。v27直前のv26は `rollback/20260929T014855479463+0900/previous/`。v26直前のv25は `rollback/20260929T011047428474+0900/previous/`。
- v25直前のv24は `rollback/20260929T005458906470+0900/previous/`。v24直前のv23は `rollback/20260929T004800155740+0900/previous/`。v23直前のv22は `rollback/20260929T004127154070+0900/previous/`。
- v22直前のv21は `rollback/20260929T003419463540+0900/previous/`。v21直前のv19は `rollback/20260929T001634244774+0900/previous/`。
- v19直前の不採用v18-r8は `rollback/20260928T234505917593+0900/previous/`。v18直前のv17は `rollback/20260928T233416852733+0900/previous/`。
- v17直前のv16アプリとLaunchAgentは `rollback/20260928T224640180929+0900/previous/`。
- v16直前のv15アプリとLaunchAgentは `rollback/20260928T221914686599+0900/previous/`。v14は `rollback/20260928T220248204363+0900/previous/` に保存。
- 以前のv13アプリとLaunchAgentは `rollback/20260928T205506131351+0900/previous/`、コード・文書は `rollback/v13-before-pearl-20260928T203313/` に保存。
- 以前の変更前v12アプリとLaunchAgentは `rollback/20260928T193148710980+0900/previous/`、コードと文書は `rollback/v12-before-living-water-20260928T191855/` に保存しています。
- v11アプリとLaunchAgentは `rollback/20260928T191345139232+0900/previous/`、コードと文書は `rollback/v11-before-brighter-rear-20260928T190553/` に保存しています。
- 以前のv10アプリとLaunchAgentは `rollback/20260928T175718361798+0900/previous/`、編集前ソース・文書は `rollback/v10-before-comprehensive-20260928T175230/` に保存しています。
- 前回の変更前v8アプリとLaunchAgentは `rollback/20260928T171540657669+0900/previous/`、編集前ソース・文書は `rollback/v8-before-natural-tank-20260928T164903/` に保存しています。
- 以前のv7アプリとLaunchAgentは `rollback/20260928T162824060202+0900/previous/`、ソースは `rollback/natural-v7-before-photo-20260928T162113/`。v8初回の起動待ち修正前は `rollback/20260928T163053631300+0900/previous/` に保存しました。
- 以前のv6アプリとLaunchAgentは `rollback/20260928T154014557728+0900/previous/`、v6ソースは `rollback/clearwater-v6-source-20260928T152125/` に保存しています。
- 以前の planted-tank-v3 は `rollback/20260928T085537088104+0900/previous/Deskworlds.app`、ソースは `rollback/planted-tank-v3-before-livebearer/` に保存しています。
- さらに前のnatural-v2アプリは `rollback/20260928T022407720836+0900/previous/Deskworlds.app`、ソースは `rollback/natural-v2-before-aquascape/` に保存しています。
- 起動時にネット接続・Node.js・ターミナルは不要です。

現行の検証記録は `V29-VERIFICATION.md` と `evidence/`。将来のアップデートは別途確認してから行い、この固定版を自動更新しません。
