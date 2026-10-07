# Validation record / 검증 기록

Review date: 2026-10-08. This is a saved-artifact review, not a full model rerun.

## Confirmed / 확인한 사실

- Input `tactical_analysis_cleaned.csv`: 21,394 × 56. Labeled output: 21,394 × 30.
- The 14 clustering columns contain no missing or nonfinite values in either file. Other columns in the 56-column input do have missing values; the entire input is not described as missing-free.
- No duplicated complete rows or `(league, match_id, team)` keys in either file.
- One-to-one outer merge on those keys: 21,394 matched rows, no unmatched rows, and no differences in any of the 14 feature values.
- 10,697 `(league, match_id)` pairs, each with exactly two team rows. Team/opponent names, scores, home/away pairing, and dates are internally consistent in the saved input.
- Possession is within 0–100; no negative values across the 14 features; box shots never exceed total shots. These checks are not proof of source accuracy or absence of plausible-but-incorrect values.
- The 56 recalculated profile means match thesis Table 7 (printed p.23 / PDF p.32) when rounded to two decimals.
- All checks, source hashes, dtypes, and limitations are in [snapshot_audit.json](../outputs/review/snapshot_audit.json). [Coverage](../outputs/review/coverage.csv) and [feature ranges](../outputs/review/feature_ranges.csv) are included.

## Open discrepancies / 남아 있는 불일치

| Evidence | Thesis | Current saved artifact | Handling |
|---|---:|---:|---|
| Table 8, profile 2-1 | 4,017 (18.78%) | 4,122 (19.27%) | Show both; use current values only when explicitly labeled as the saved snapshot |
| Table 8, profile 2-2 | 8,035 (37.56%) | 7,930 (37.07%) | Same |
| Table 5, PCA k=2 silhouette | 0.422 | 0.421478 in saved silhouette CSV | Not identical at three decimals; do not silently treat as rounding equivalence |

Table 8 is printed p.24 / PDF p.33; Table 5 is printed p.20 / PDF p.29. The supplied PDF table pages were visually inspected. All three selected notebooks' stored outputs use 4,122 / 7,930. This supports a consistent current snapshot but does not establish why the paper differs. No row-level historical label file yielding 4,017 / 8,035 was established. Do not call the difference a confirmed typo, rerun difference, or 105 identified reassigned cases.

**한국어:** 논문과 현재 결과의 차이를 공개적으로 구분해야 합니다. 원인이 확인되기 전 논문을 오타라고 단정하거나 현재 데이터를 논문 수치에 맞춰 바꾸면 안 됩니다. 표 7 평균이 일치해도 표 8 사례 수가 자동 검증되는 것은 아닙니다.

## Notebook selection / 기준 후보 선택

[Notebook provenance](NOTEBOOK_PROVENANCE.json) records original relative paths and source/copy hashes. Cell indices below are zero-based in the original notebook JSON, before the new explanatory cell.

- **RQ1:** selected the user-named `06,22:` version. It contains the explicit `final_labels_4k` generation at cell 16 before use at cell 18. The undated copy uses that object without the equivalent creation cell. Selected version's saved nonempty code cells have sequential execution counts 127–144; this is evidence of a saved session, not a fresh-kernel test.
- **RQ2:** selected the named revised notebook. Multiple cells rewrite `rq2_mann_whitney_results.csv`; the final artifact depends on execution order. `compare_models_cv` selects by `_test_f1` in original cell 18. The exported model summary drops its comparison identifier from the displayed columns before concatenation; add an explicit comparison key in a future cleaned version. Do not present this file as an unambiguous standalone benchmark table.
- **RQ3:** selected the named revised copy. It reads RQ1's labeled output. Alternative persistence/diversity notebooks and output tables exist but are not part of the thesis's final three-question scope chosen here.
- Code-cell sources are unchanged in the public reference copies. Saved outputs, execution counts, and cell metadata were cleared; a review notice was added. This reduces stale-output confusion but does not repair or validate the models.

## Interpretation checks / 해석 검토

1. **Generated targets:** RQ2 recovers labels derived from the same match indicators. This is a surrogate explanation task, not independent validation of tactical classes.
2. **Selection on test performance:** The historical code selects on test F1. Use training cross-validation or nested/group-aware validation for model selection and reserve a separate final test if external generalization is a goal.
3. **Post-clustering inference:** Comparing the features used to create groups can describe separation, but small p-values are not independent proof of the taxonomy. Repeated teams and paired match records complicate row-independence assumptions.
4. **PCA scope:** Saved output reports 45.95% retained variance. It is recorded evidence only; original-feature-space stability and sensitivity should be evaluated before stronger taxonomy claims.
5. **PPDA wording:** In the README use “lower PPDA, consistent with stronger pressing activity.” The thesis p.23 phrase “pressing intensity is lowest” while interpreting stronger pressing is ambiguous; distinguish the metric's value from the construct.
6. **Distribution scope:** Recalculated season association is chi-square 149.178, df 15, p ≈ 3.51e-24, Cramér's V ≈ 0.0482. A small p-value and a small effect can coexist. The calculation does not resolve non-independence or identify a causal seasonal change.

## What has not been established / 확인하지 않은 것

Fresh-kernel execution of RQ1–RQ3; retrained models or SHAP outputs; original provider responses, scrape dates, joins, and exclusions; complete official fixture coverage; permission to redistribute row-level data; bootstrap stability from the original older notebook; and source-verification of every thesis reference.

현재 스냅샷에 대한 검증과 원자료 수집·전체 분석 재현을 구분합니다. 과거 출력의 높은 성능 수치와 부트스트랩 ARI를 이번에 검증한 성과로 재사용하지 않습니다.

## Release resolution / 정식 공개본으로 확정하는 순서

1. Preserve thesis and existing hashes; identify or document the unrecoverable historical Table 8 baseline.
2. Choose an explicit release: thesis archive with discrepancy note, or a newly rerun analysis with its own version and date. Never silently blend both.
3. Freeze input hashes, source-column mappings, exclusion rules, and dependencies.
4. Rerun notebooks in a separate copy from a fresh kernel; write outputs into a new versioned directory.
5. Rebuild RQ2 tables with comparison IDs and consistent effect-size definitions; revise evaluation claims.
6. Regenerate only the representative figures from the same labeled data, then validate captions and both READMEs.
