# Derived indicators and cluster labels

[데이터 목차 / Data index](../README.md)

Scope: **2019/20–2024/25**, match dates **2019-08-09–2025-05-25**. Ranges and missing counts are computed from the included files.

Labels follow the thesis, code, and column names. A provider-field mapping has not been recovered. Attempted versus successful passes, long balls, crosses, dribbles, tackles, and spatial definitions of progression require source verification.

## `long_ball_ratio` — Long balls relative to passes

- Meaning: Long balls relative to passes
- Unit/encoding: %
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 2.06186 – 106.25
- Missing: 0 / 21,394 rows
- Formula checked against data: `long_balls / passes * 100`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `final_third_entry_ratio` — Final-third entries relative to passes

- Meaning: Final-third entries relative to passes
- Unit/encoding: %
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 3.25733 – 82.7957
- Missing: 0 / 21,394 rows
- Formula checked against data: `final_third_entries / passes * 100`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `dribble_ratio` — Dribbles relative to passes

- Meaning: Dribbles relative to passes
- Unit/encoding: %
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0.25 – 23.3202
- Missing: 0 / 21,394 rows
- Formula checked against data: `dribbles / passes * 100`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `cross_ratio` — Crosses relative to passes

- Meaning: Crosses relative to passes
- Unit/encoding: %
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0 – 26.0417
- Missing: 0 / 21,394 rows
- Formula checked against data: `crosses / passes * 100`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `dispossessed_ratio` — Dispossessions relative to passes

- Meaning: Dispossessions relative to passes
- Unit/encoding: %
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0 – 19.0083
- Missing: 0 / 21,394 rows
- Formula checked against data: `dispossessed / passes * 100`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `tackles_padj` — Possession-adjusted tackles

- Meaning: Possession-adjusted tackles
- Unit/encoding: adjusted count
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0.925926 – 69.5652
- Missing: 0 / 21,394 rows
- Formula checked against data: `tackles * 50 / (100 - possession)`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `interceptions_padj` — Possession-adjusted interceptions

- Meaning: Possession-adjusted interceptions
- Unit/encoding: adjusted count
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0 – 40.7407
- Missing: 0 / 21,394 rows
- Formula checked against data: `interceptions * 50 / (100 - possession)`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `clearances_padj` — Possession-adjusted clearances

- Meaning: Possession-adjusted clearances
- Unit/encoding: adjusted count
- Clustering input: no
- File: input
- Stored dtype: `float64`
- Observed range: 0 – 83.8235
- Missing: 0 / 21,394 rows
- Formula checked against data: `clearances * 50 / (100 - possession)`; all rows match: True.
- Numeric agreement does not reconstruct the original collection/transformation provenance.

## `PC1` — First principal component score

- Meaning: First principal component score
- Unit/encoding: score
- Clustering input: no
- File: labeled
- Stored dtype: `float64`
- Observed range: -10.2461 – 9.37346
- Missing: 0 / 21,394 rows

## `PC2` — Second principal component score

- Meaning: Second principal component score
- Unit/encoding: score
- Clustering input: no
- File: labeled
- Stored dtype: `float64`
- Observed range: -11.7001 – 5.42577
- Missing: 0 / 21,394 rows

## `cluster_stage1` — Parent cluster ID

- Meaning: Parent cluster ID
- Unit/encoding: 0/1
- Clustering input: no
- File: labeled
- Stored dtype: `int64`
- Observed range: 0 – 1
- Missing: 0 / 21,394 rows

## `cluster_final_num` — Final numeric cluster ID

- Meaning: Final numeric cluster ID
- Unit/encoding: 0–3
- Clustering input: no
- File: labeled
- Stored dtype: `int64`
- Observed range: 0 – 3
- Missing: 0 / 21,394 rows

## `cluster_final_hier` — Final profile code

- Meaning: Final profile code
- Unit/encoding: 1-1/1-2/2-1/2-2
- Clustering input: no
- File: labeled
- Stored dtype: `object`
- Example values: 1-1, 2-2, 1-2, 2-1
- Missing: 0 / 21,394 rows

## `cluster_label` — Stored English profile label

- Meaning: Stored English profile label
- Unit/encoding: label
- Clustering input: no
- File: labeled
- Stored dtype: `object`
- Example values: Progressive Possession, Defensive Direct, High-Possession Control, Low-Possession Defensive
- Missing: 0 / 21,394 rows

## `cluster_label_kr` — Stored Korean profile label

- Meaning: Stored Korean profile label
- Unit/encoding: label
- Clustering input: no
- File: labeled
- Stored dtype: `object`
- Example values: 점유 전개형, 수비적 전개형, 고점유 지배형, 저점유 수비형
- Missing: 0 / 21,394 rows

