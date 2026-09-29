# Deskworlds v7 process probe

実装・自己検証: 2026-09-28（macOS 26.6.2 / arm64）。
担当: `01a0e6aa-a83e-7473-ab8a-305cfe10d3ab`。
親: `01a0e3a9-82bc-7353-be3f-dacf575f7cea`。
選択値: 親から継承。親・担当のthread metadataと担当のturn_contextで `gpt-6-astra / xhigh` を観測。設定変更なし。

## 担当範囲と取得方法

変更は `scripts/measure-v7.py` とこのファイルだけ。アプリ、UI、魚・水槽ソース、既存 `measure-states.py` は操作・変更していない。別エージェント、モデルCLI、課金、認証、権限変更、外部送信なし。

Python標準ライブラリのctypesからmacOSの非特権API `libproc.proc_pid_rusage(pid, RUSAGE_INFO_V0, buffer)` を呼ぶ。構造体はローカルSDKの `sys/resource.h`（`rusage_info_v0`, 96 bytes）と `libproc.h` に照合した。`vmmap` / `footprint` コマンドの生出力は取得しない。

- CPU: `ri_user_time` と `ri_system_time` の累積Mach tickを `mach_timebase_info` の `numer/denom` でナノ秒に変換し、実際の観測時刻間の差分を取る。`100 * ΔCPU秒 / Δ実時間秒`。100%は1コア分で、マルチスレッドなら100%を超え得る。ホスト全コア数では割らない。
- メモリ: PIDごとの `ri_phys_footprint` をbytesで保存する。RSSではなく、PID間のメモリ合計も出さない。
- GPU: 常に `{"status":"unknown","value":null,"reason":"not_measured"}`。CPUやfootprintからGPU負荷・電力を推定しない。
- プロセス名・引数・環境変数・実行ファイルパス・メモリ内容は読まない。APIの集計値、時刻、PID、非機密label、固定理由コードだけを保存する。画像UUIDは同一性の内部照合だけに使い出力しない。

初回の自己テストでCPUの単位を検証した。Mach tickをナノ秒と仮定すると0.014950571秒に見えたが、このホストの `numer=125, denom=3` で変換すると0.622940458秒となり、子自身の0.622884秒と一致した。実装はこの変換を行い、自己テストで `time.process_time_ns()` と比較する。

## コマンド例

案件ディレクトリで実行する。下のPIDは例示値であり、**親が帰属を確定したPIDにだけ置き換える**。新しいヘルパーや再起動後のPIDを自動探索しない。labelには非機密の状態名だけを入れる。

```sh
python3 -B scripts/measure-v7.py --self-test

python3 -B scripts/measure-v7.py \
  --pids 12345,12346 \
  --label aquarium-v7-running \
  --duration 30 --interval 1 \
  --output evidence/v7-running-20260928-01.json

python3 -B scripts/measure-v7.py \
  --pids 12345 12346 \
  --label aquarium-v7-paused \
  --duration 30 --interval 1 \
  --output -
```

`--pids` は空白・カンマ区切りを受け付け、重複・0・負数・int32範囲外を拒否する。duration / intervalは有限の正数が必要。5引数は通常実行ですべて必須。`--self-test` は単独使用で、生成する子は自身で開始・終了し、ファイルを作らずstdoutに集計結果を返す。

ファイル出力は新規作成専用（`open(..., "x")`）。既存ファイルや同名symlinkを上書きせず、親ディレクトリも自動作成しない。`--output -` はstdout。Ctrl-Cでは取得済みのJSONを出して終了コード130。通常終了コード0は測定ループ完了を意味し、PID取得成功の保証ではない。必ず各PIDの `summary.processes[].complete` と欠測理由を確認する。

## JSONの読み方・欠測契約

`started_at_utc` / `ended_at_utc` と `actual_duration_seconds` が実行窓。開始・終了を含む各観測は `samples` に入り、各PIDに実測の `elapsed_seconds` とAPI呼出時間がある。CPU間隔計算にはそのPIDの実時刻を使う。要求間隔を守れないときは追いつき用の連続観測をせず、次のtickへ進み、`scheduled_elapsed_seconds` と `sampling_lag_seconds` を記録する。最終観測はduration時点に要求するが、OSのスケジューリングやAPI呼出で実際には遅れ得る。

各PIDの `summary.processes[]`:

| 値 | 意味 |
|---|---|
| `cpu.start_total_ns`, `end_total_ns` | 観測窓の両端の累積CPU。欠測端はnull |
| `cpu.delta_seconds`, `mean_percent_one_core` | 全観測が有効なときだけ、窓全体の差分と平均 |
| `physical_footprint.start_bytes`, `end_bytes` | 窓両端の実測footprint。後の有効値で欠測端を置換しない |
| `min_bytes`, `max_bytes` | 有効観測だけでの最小・最大。欠測があっても観測値として残す |
| `delta_bytes`, `endpoint_bytes_per_second` | 全観測が有効なときだけ両端差・両端差/秒 |
| `ols_bytes_per_second`, `trend` | 実時刻に対する最小二乗直線の傾きと、その符号（increasing / decreasing / flat）。欠測時はnull / unknown |
| `valid_sample_count`, `missing_sample_count`, `missing_reasons` | 観測数と固定理由コード |

開始時に同一性を取れないPIDは、その後も欠測にする。初回の権限・API失敗後は `baseline_identity_unavailable`、終了・消失の検出後はその理由を保持する。確定した同一性の基準は開始Mach時刻と画像UUID。途中で終了・消失・PID再利用・別画像へのexec・CPUカウンタ巻き戻りを検出すると、そのPIDは残りの実行窓で欠測に固定する。終了済みプロセスのrusageが取得できても `ri_proc_exit_abstime` が立っていれば欠測。差分を別プロセスにまたがせない。

権限拒否は `permission_denied` とerrno、API不可・不明は固定理由とnullを記録する。開始同一性が確定した後の一時的取得失敗は復帰時に同一性を再照合し、欠測をまたぐCPU間隔差を計算しない。全窓のCPU差・メモリ差・傾きは、どこか1回でも欠測があればnullと `missing_samples`。初回観測のCPU間隔値は差分元がないためnull / `baseline`。中断時は全窓集計をnull / `run_interrupted` とする。

## 実行済み検証

1. `python3 -B scripts/measure-v7.py --self-test`: **13項目合格、終了0**。既知のCPU差/傾き、権限拒否、欠測またぎ禁止、基準同一性不明、終了・PID再利用・画像変更・CPU巻き戻り、API不可、中断、不正引数を合成データで検証。実子でCPU・footprint・終了を検証。
2. AST構文解析と `--help`: 合格。`-B`を使いbytecodeファイルは作らない。
3. 自分で開始した2つのPython子（sleep 2秒 / 0.28秒）を、実CLIでduration 0.65秒、interval 0.1秒、8観測。長い子は8/8有効。短い子は3有効・5欠測、理由 `process_exited`、終了CPU・footprintはnull、全窓差と傾きもnull。
4. 上記CLIのJSONを、この担当ノートのパスへ一時保存してJSONとして再読込。終了0、stdoutへの重複出力なし。再度同じ出力先を指定すると終了2となり、SHA-256が変わらないことを確認。この文書への書換え後も、他の証拠ファイルは作っていない。
5. 実CLIで `duration=nan` / `interval=0` / 重複PIDを指定し、いずれも終了2で拒否。
6. 自分が起動した測定CLIだけにSIGINTを送り、4観測のJSONがstdoutへ保存され、`completed=false`、集計理由 `run_interrupted`、終了130を確認。アプリにはシグナルを送っていない。
7. 合成readerでduration 0.01秒、interval 10秒を指定し、開始・終了の2観測とflat傾向を確認。指定間隔が測定時間より長くても両端を記録する。担当2ファイルの再読込・構文・空白検査も実施。

自己テストの代表実測（子PID 43009、10観測）:

```json
{
  "mach_timebase": {"numer": 125, "denom": 3},
  "child_cpu_seconds": 0.644511,
  "probe_cpu_delta_seconds": 0.644558626,
  "difference_seconds": 0.000047626,
  "mean_percent_one_core": 71.4471640062671,
  "physical_footprint_start_bytes": 7438720,
  "physical_footprint_end_bytes": 24363416,
  "physical_footprint_delta_bytes": 16924696,
  "ols_bytes_per_second": 18225693.981391437,
  "trend": "increasing",
  "gpu": "unknown"
}
```

## 限界・親への引継ぎ

- 実機検証はこのmacOS/arm64の自分の子だけ。Deskworlds / WebKit / 他ユーザーPIDの権限可否・実負荷は未確認。権限拒否は合成検証であり、権限変更による実証はしていない。
- PID再利用・別画像へのexec・巻き戻りは合成データで検証。実PIDを意図的に再利用させてはいない。同じPIDで同じ画像へexecし、開始時刻・画像UUID・CPUカウンタが連続する場合は検出できない。既知の再起動があった測定窓は親が破棄してPIDを再確定する。
- process physical footprintはOSのメモリ計上指標であり、物理RAM総量やプロセス間で重複を除いた専有量ではない。子孫を自動加算しない。OSの共有・圧縮等の帰属に従う。GPU使用率・電力・実描画fps・画面状態はこの道具の対象外。
- 短時間の傾きは一時的な確保や圧縮・回収でも変化する。正の傾きだけでリークと断定しない。必要なら親が同一条件・十分なdurationで複数回比較する。
- PID間は逐次観測で完全同時ではない。短いintervalや多PIDによる計測側の負荷・観測間隔の遅れを確認する。`complete=true` は実際に採れた観測が全て有効という意味で、OS都合の遅延や飛ばしたtickがゼロという保証ではない。
- この担当によるv7のアプリ性能判定は未実施。親は確定PID・状態label・測定窓を、別担当のUI実フレーム間隔と対応させて判断する。

保存・再読込した途中終了テストの証跡（開始UTC `2026-09-28T06:28:14.384+00:00`）:

```json
{
  "pid": 43156,
  "sample_count": 8,
  "valid_sample_count": 3,
  "missing_sample_count": 5,
  "missing_reasons": [
    "process_exited"
  ],
  "complete": false,
  "observed_span_seconds": 0.658478625,
  "start_elapsed_seconds": 3.1812e-05,
  "end_elapsed_seconds": 0.658510437,
  "cpu": {
    "start_total_ns": 13781499,
    "end_total_ns": null,
    "delta_seconds": null,
    "mean_percent_one_core": null,
    "reason": "missing_samples"
  },
  "physical_footprint": {
    "start_bytes": 6914456,
    "end_bytes": null,
    "min_bytes": 6914456,
    "max_bytes": 6914456,
    "delta_bytes": null,
    "endpoint_bytes_per_second": null,
    "ols_bytes_per_second": null,
    "trend": "unknown",
    "reason": "missing_samples"
  }
}
```
