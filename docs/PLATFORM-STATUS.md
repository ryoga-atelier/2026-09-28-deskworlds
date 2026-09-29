# 対応状況と検証の区分

2026-09-30。採用版はv29-r16（24fps）。

| 項目 | Mac | Windows |
|---|---|---|
| ソースからの環境診断・準備 | 手元MacとGitHub macOSランナーで成功 | GitHub Windowsランナーで新規取得から成功 |
| 描画 | 導入済みMacアプリの過去記録、新規ネイティブビルド成功 | Windows用IIFEパッケージをWindows上のChromiumでも実描画確認 |
| 給餌、ホスト停止、本人の停止維持、再開 | 既存検査と過去記録 | パッケージのブラウザー試験で成功 |
| デスクトップ壁紙としての表示 | 導入済み | Lively実機は未確認 |
| メニュー・Dock/タスクバー・ドラッグ | 未確認項目あり | 未確認 |
| 実スリープ復帰・再ログイン | 未確認 | 未確認 |
| CPU/GPU/メモリ | V29-R15-VERIFICATION.mdの既存実測 | 未測定。Macの値を転用しない |

## セットアップの検査結果

[GitHub Actions 36602825539](https://github.com/ryoga-atelier/2026-09-28-deskworlds/actions/runs/36602825539) は、macos-15とwindows-latestの両方で成功しました。検査したソースは `5f772f10cd8f8274cedabc964a1c2e3656bf5571` です。

- 上流submodule未取得のcloneから固定版を取得し、既存の構文・挙動・魚形状・配色・水の検査が成功。
- 新しいPython検査5件、ホスト停止と本人停止を分けるJavaScript検査3件が成功。
- 両OSでWindows用ZIPを構築し、欠けた素材の要求やJavaScript例外がないこと、描画・給餌・24fps設定・停止中のフレーム増加ゼロ・本人の停止維持・再開をChromiumで確認。
- Windowsで `setup-windows.cmd doctor` が成功。Mac（Apple Silicon）で専用アプリのコンパイル・署名検査が成功。Intel Macの実行は未確認。

Windowsのソフトウェア描画検査では、専用headless-shellの撮影処理が停止したため、通常版Chromiumで検査し、低速なソフトウェア描画に合わせてフレーム完了の待機時間を設定しています。水槽のソースや見た目は変更していません。この検査は機能確認であり、24fpsの実効速度やGPU負荷の測定ではありません。

検査記録は [portable-ci-20260930.json](../evidence/portable-ci-20260930.json)、Windowsランナーで描いた画像は [portable-windows-ci.png](../evidence/portable-windows-ci.png) です。配布ZIPは [Release](https://github.com/ryoga-atelier/2026-09-28-deskworlds/releases/tag/v29-r16-portable.2) に保存し、SHA-256と構築元も同梱します。ホステッドランナーでの成功はLivelyの実デスクトップの合格ではありません。

初回Lively導入後は、24匹の水槽表示、カスタマイズのFeedとPlaying、デスクトップアイコン操作、他のアプリに隠れた時の停止・復帰を本人のPCで確認してください。元の壁紙へ戻ること、自動起動の登録と実ログインも分けて記録します。
