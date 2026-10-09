# 評估結果

所有數字皆為本批測試集的觀察值；exact match 附 95% bootstrap CI，CI 重疊時不宣稱差異。

## 整體指標

| run | split | n | exact match [95% CI] | JSON 合法 | schema 合法 | action 準確 | tool F1 | 干擾項誤用 | 字面參數 | 引用參數 | 相依 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zeroshot | test_id | 121 | 0.413 [0.322, 0.504] | 0.975 | 0.917 | 0.868 | 0.793 | 0.090 | 0.617 | 0.190 | 0.510 |
| zeroshot | test_ood | 149 | 0.208 [0.141, 0.275] | 0.953 | 0.826 | 0.664 | 0.727 | 0.280 | 0.705 | 0.353 | 0.430 |
| fewshot | test_id | 121 | 0.612 [0.521, 0.702] | 0.959 | 0.909 | 0.876 | 0.853 | 0.070 | 0.778 | 0.443 | 0.780 |
| fewshot | test_ood | 149 | 0.215 [0.148, 0.275] | 0.960 | 0.899 | 0.638 | 0.760 | 0.270 | 0.846 | 0.433 | 0.590 |
| qlora-r16 | test_id | 121 | 0.992 [0.975, 1.000] | 1.000 | 1.000 | 1.000 | 0.998 | 0.000 | 0.994 | 0.975 | 0.990 |
| qlora-r16 | test_ood | 149 | 0.443 [0.362, 0.517] | 1.000 | 0.993 | 0.953 | 0.920 | 0.170 | 0.948 | 0.520 | 0.690 |

## 依任務類型的 exact match

| run | split | single | parallel | chain | dag | clarify | refuse |
|---|---|---|---|---|---|---|---|
| zeroshot | test_id | 0.73 (n=22) | 0.46 (n=26) | 0.21 (n=33) | 0.00 (n=19) | 0.00 (n=4) | 0.88 (n=17) |
| zeroshot | test_ood | — | 0.20 (n=25) | 0.12 (n=50) | 0.00 (n=25) | 0.00 (n=24) | 0.80 (n=25) |
| fewshot | test_id | 0.86 (n=22) | 0.58 (n=26) | 0.58 (n=33) | 0.21 (n=19) | 0.25 (n=4) | 0.94 (n=17) |
| fewshot | test_ood | — | 0.68 (n=25) | 0.30 (n=50) | 0.00 (n=25) | 0.00 (n=24) | 0.00 (n=25) |
| qlora-r16 | test_id | 1.00 (n=22) | 1.00 (n=26) | 0.97 (n=33) | 1.00 (n=19) | 1.00 (n=4) | 1.00 (n=17) |
| qlora-r16 | test_ood | — | 1.00 (n=25) | 0.46 (n=50) | 0.00 (n=25) | 0.00 (n=24) | 0.72 (n=25) |

## 錯誤類型（筆數，一筆可有多個 tag）

| run | split | dependency | distractor | extra_step | format | hallucinated_args | literal_arg | missed_refuse | missing_step | other | ref_arg | wrong_missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zeroshot | test_id | 39 | 9 | 2 | 10 | 4 | 28 | 2 | 31 | 8 | 40 | 0 |
| zeroshot | test_ood | 36 | 28 | 0 | 26 | 19 | 21 | 5 | 11 | 4 | 55 | 0 |
| fewshot | test_id | 11 | 7 | 0 | 11 | 3 | 12 | 1 | 10 | 5 | 21 | 0 |
| fewshot | test_ood | 32 | 27 | 0 | 15 | 16 | 19 | 23 | 14 | 0 | 53 | 4 |
| qlora-r16 | test_id | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| qlora-r16 | test_ood | 31 | 17 | 0 | 1 | 0 | 17 | 6 | 17 | 0 | 49 | 24 |

## action 混淆矩陣（列 = gold，欄 = 預測；test_id + test_ood 合計）

**zeroshot**

| gold \ pred | plan | clarify | refuse | invalid |
|---|---|---|---|---|
| plan | 169 | 0 | 0 | 31 |
| clarify | 23 | 0 | 0 | 5 |
| refuse | 6 | 1 | 35 | 0 |

**fewshot**

| gold \ pred | plan | clarify | refuse | invalid |
|---|---|---|---|---|
| plan | 180 | 0 | 0 | 20 |
| clarify | 19 | 5 | 0 | 4 |
| refuse | 24 | 0 | 16 | 2 |

**qlora-r16**

| gold \ pred | plan | clarify | refuse | invalid |
|---|---|---|---|---|
| plan | 200 | 0 | 0 | 0 |
| clarify | 0 | 28 | 0 | 0 |
| refuse | 6 | 0 | 35 | 1 |

