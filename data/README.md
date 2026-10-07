# Data guide

[English](README.md) · [한국어](README.ko.md) · [Project README](../README.md)

The package includes the actual cleaned input and saved labeled output. Provider raw responses were not recovered from the research folder; these CSVs are not described as raw collection records.

## Data files

| File | Rows × columns | Role |
|---|---:|---|
| [tactical_analysis_cleaned.csv](processed/tactical_analysis_cleaned.csv) | 21,394 × 56 | RQ1 cleaned input · 정제 입력 |
| [rq1_final_data_14vars_hierarchical_4clusters.csv](../outputs/tables/rq1_final_data_14vars_hierarchical_4clusters.csv) | 21,394 × 30 | Saved labels for RQ2/RQ3 · 군집 결과 |

Copies are byte-identical to the reviewed originals; see [hashes and sizes](catalog/files.json). If GitHub limits the CSV table preview, use the file page’s Raw/download control.

## Browse by category

- [기간·리그·표본 / Period and coverage](catalog/coverage.md)
- [Possession and passing (2 columns)](catalog/possession.md)
- [Progression (2 columns)](catalog/progression.md)
- [Ball delivery and carrying (4 columns)](catalog/delivery.md)
- [Shooting (2 columns)](catalog/shooting.md)
- [Pressing and defensive actions (4 columns)](catalog/defense.md)
- [Match context and outcomes (11 columns)](catalog/context.md)
- [Additional match records (23 columns)](catalog/auxiliary.md)
- [Derived indicators and cluster labels (15 columns)](catalog/derived.md)

[All columns CSV / 전체 컬럼 사전](catalog/all_columns.csv) · [Schema](data_schema.json) · [Validation / 검증 기록](../docs/VALIDATION.md)

## Sources and interpretation

The thesis attributes match records to Sofascore and PPDA/DEEP to Understat. Original field mappings, collection timestamps, and cross-provider join provenance have not been recovered. Metric pages distinguish observed values from unresolved definitions.

There are 14 clustering inputs and 63 distinct columns across the two files. Auxiliary indicators, outcomes, and generated labels are identified separately. Two cluster counts differ from thesis Table 8; see the validation record.

Copies of the research data are included. Provider redistribution terms have not been established and no data license is newly asserted.
