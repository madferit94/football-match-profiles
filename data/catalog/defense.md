# Pressing and defensive actions

[데이터 목차 / Data index](../README.md)

Scope: **2019/20–2024/25**, match dates **2019-08-09–2025-05-25**. Ranges and missing counts are computed from the included files.

Labels follow the thesis, code, and column names. A provider-field mapping has not been recovered. Attempted versus successful passes, long balls, crosses, dribbles, tackles, and spatial definitions of progression require source verification.

## `ppda_val` — PPDA: passes allowed per defensive action

- Meaning: PPDA: passes allowed per defensive action
- Unit/encoding: ratio
- Clustering input: yes
- File: input + labeled
- Stored dtype: `float64`
- Observed range: 2 – 193
- Missing: 0 / 21,394 rows
- Lower values suggest stronger pressing activity. This is not pressing success; the provider zone and action denominator remain to be verified.

## `tackles` — Tackles

- Meaning: Tackles
- Unit/encoding: count
- Clustering input: yes
- File: input + labeled
- Stored dtype: `float64`
- Observed range: 1 – 46
- Missing: 0 / 21,394 rows

## `interceptions` — Interceptions

- Meaning: Interceptions
- Unit/encoding: count
- Clustering input: yes
- File: input + labeled
- Stored dtype: `float64`
- Observed range: 0 – 33
- Missing: 0 / 21,394 rows

## `clearances` — Clearances

- Meaning: Clearances
- Unit/encoding: count
- Clustering input: yes
- File: input + labeled
- Stored dtype: `float64`
- Observed range: 0 – 76
- Missing: 0 / 21,394 rows

