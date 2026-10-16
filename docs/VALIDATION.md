# Validation record / 검증 기록

Review date: 2026-10-08. This is a saved-artifact review, not a full model rerun.

검토일: 2026-10-08. 저장된 결과물을 검토한 것이며, 모델 전체를 다시 실행한 것은 아닙니다.

## Confirmed / 확인한 사실

- Input `tactical_analysis_cleaned.csv`: 21,394 × 56. Labeled output: 21,394 × 30.
- The 14 clustering columns contain no missing or nonfinite values in either file. Other columns in the 56-column input do have missing values; the entire input is not described as missing-free.
- No duplicated complete rows or `(league, match_id, team)` keys in either file.
- One-to-one outer merge on those keys: 21,394 matched rows, no unmatched rows, and no differences in any of the 14 feature values.
- 10,697 `(league, match_id)` pairs, each with exactly two team rows. Team/opponent names, scores, home/away pairing, and dates are internally consistent in the saved input.
- Possession is within 0–100; no negative values across the 14 features; box shots never exceed total shots. These checks are not proof of source accuracy or absence of plausible-but-incorrect values.
- The 56 recalculated profile means match thesis Table 7 (printed p.23 / PDF p.32) when rounded to two decimals.
- All checks, source hashes, dtypes, and limitations are in [snapshot_audit.json](../outputs/review/snapshot_audit.json). [Coverage](../outputs/review/coverage.csv) and [feature ranges](../outputs/review/feature_ranges.csv) are included.

**한국어:**

- 입력 `tactical_analysis_cleaned.csv`: 21,394 × 56. 라벨 결과: 21,394 × 30.
- 군집에 쓴 14개 열은 두 파일 모두 결측값이나 무한값이 없습니다. 56개 열 입력의 다른 열에는 결측값이 있으므로, 입력 전체에 결측이 없다고 설명하지 않습니다.
- 두 파일 모두 완전히 같은 행이나 `(league, match_id, team)` 키 중복이 없습니다.
- 이 키로 1:1 외부 결합한 결과 21,394행이 모두 짝을 이루었고, 짝이 없는 행이나 14개 지표 값의 차이는 없습니다.
- `(league, match_id)` 조합은 10,697개이며, 모두 팀 행이 정확히 두 개입니다. 저장된 입력에서 팀·상대 이름, 스코어, 홈·원정 짝, 날짜가 서로 맞습니다.
- 점유율은 0~100 범위이고, 14개 지표에 음수가 없으며, 박스 안 슈팅이 전체 슈팅보다 많은 경우가 없습니다. 이 점검이 원천 자료의 정확성이나, 그럴듯하지만 틀린 값이 없다는 것을 증명하지는 않습니다.
- 다시 계산한 유형별 평균 56개는 소수 둘째 자리 반올림 기준으로 논문 표 7(인쇄 p.23 / PDF p.32)과 일치합니다.
- 모든 점검, 원본 해시, 자료형, 한계는 [snapshot_audit.json](../outputs/review/snapshot_audit.json)에 있습니다. [범위](../outputs/review/coverage.csv)와 [지표 범위](../outputs/review/feature_ranges.csv)도 포함했습니다.

## Open discrepancies / 남아 있는 불일치

| Evidence / 근거 | Thesis / 논문 | Current saved artifact / 현재 저장 결과 | Handling / 처리 |
|---|---:|---:|---|
| Table 8, profile 2-1 | 4,017 (18.78%) | 4,122 (19.27%) | Show both; use current values only when explicitly labeled as the saved snapshot / 두 값을 모두 표시하고, 현재 값은 저장 스냅샷이라고 밝힐 때만 사용 |
| Table 8, profile 2-2 | 8,035 (37.56%) | 7,930 (37.07%) | Same / 같음 |
| Table 5, PCA k=2 silhouette | 0.422 | 0.421478 in saved silhouette CSV | Not identical at three decimals; do not silently treat as rounding equivalence / 소수 셋째 자리에서 다르므로 반올림 차이로 조용히 넘기지 않음 |

Table 8 is printed p.24 / PDF p.33; Table 5 is printed p.20 / PDF p.29. The supplied PDF table pages were visually inspected. All three selected notebooks' stored outputs use 4,122 / 7,930. The author reports that the saved results come from a notebook rerun after the thesis analysis. This author-provided run history is distinguished from verified configuration provenance: no historical row-level label file yielding 4,017 / 8,035, or run-specific record of the original seed, was established. The published RQ1 code specifies `random_state=42` and `n_init=10`. The review does not attribute the difference to a specific seed change or identify 105 reassigned cases. Multiple-seed stability testing remains follow-up work; it is not reported as a completed experiment.

**한국어:** 표 8은 인쇄 p.24 / PDF p.33, 표 5는 인쇄 p.20 / PDF p.29이며, 제공된 PDF의 표 페이지를 눈으로 확인했습니다. 선택한 노트북 3개의 저장 출력은 모두 4,122 / 7,930을 사용합니다. 저자 설명에 따르면 논문 작성 당시 결과와 이후 노트북 재실행 결과의 차이입니다. 당시 실행 설정과 현재 결과를 연결하는 기록은 확보되지 않았으므로, 특정 난수 시드 변경이 원인이라고 확정하지 않습니다. 공개 RQ1 코드는 `random_state=42`, `n_init=10`이며 다중 시드 안정성 비교는 후속 검증으로 구분합니다. 어떤 105개 사례가 다른 유형으로 옮겨졌는지도 특정하지 않습니다. 표 7 평균의 일치와 표 8 사례 수의 버전 차이는 별도로 기록합니다.

## Notebook selection / 기준 후보 선택

[Notebook provenance](NOTEBOOK_PROVENANCE.json) records original relative paths and source/copy hashes. Cell indices below are zero-based in the original notebook JSON, before the new explanatory cell.

- **RQ1:** selected the user-named `06,22:` version. It contains the explicit `final_labels_4k` generation at cell 16 before use at cell 18. The undated copy uses that object without the equivalent creation cell. Selected version's saved nonempty code cells have sequential execution counts 127–144; this is evidence of a saved session, not a fresh-kernel test.
- **RQ2:** selected the named revised notebook. Multiple cells rewrite `rq2_mann_whitney_results.csv`; the final artifact depends on execution order. `compare_models_cv` selects by `_test_f1` in original cell 18. The exported model summary drops its comparison identifier from the displayed columns before concatenation; add an explicit comparison key in a future cleaned version. Do not present this file as an unambiguous standalone benchmark table.
- **RQ3:** selected the named revised copy. It reads RQ1's labeled output. Alternative persistence/diversity notebooks and output tables exist but are not part of the thesis's final three-question scope chosen here.
- Code-cell sources are unchanged in the public reference copies. Saved outputs, execution counts, and cell metadata were cleared; a review notice was added. This reduces stale-output confusion but does not repair or validate the models.

**한국어:** [노트북 출처 기록](NOTEBOOK_PROVENANCE.json)에 원래 상대 경로와 원본·사본 해시가 있습니다. 아래 셀 번호는 새 설명 셀을 넣기 전 원본 노트북 JSON 기준이며 0부터 셉니다.

- **RQ1:** 사용자가 지정한 `06,22:` 버전을 선택했습니다. 셀 16에서 `final_labels_4k`를 만든 뒤 셀 18에서 사용합니다. 날짜가 없는 사본은 이 생성 셀 없이 같은 객체를 사용합니다. 선택한 버전의 비어 있지 않은 코드 셀 실행 번호는 127–144로 이어지며, 이는 저장된 세션의 흔적일 뿐 새 커널 실행 검증은 아닙니다.
- **RQ2:** 이름이 지정된 수정 노트북을 선택했습니다. 여러 셀이 `rq2_mann_whitney_results.csv`를 다시 쓰므로 최종 파일은 실행 순서에 따라 달라집니다. 원본 셀 18의 `compare_models_cv`는 `_test_f1` 기준으로 모델을 고릅니다. 내보낸 모델 요약은 합치기 전에 비교 식별자 열을 빼므로, 정리된 버전에서는 비교 키를 명시해야 합니다. 이 파일을 단독으로 해석 가능한 성능 비교표로 제시하지 마세요.
- **RQ3:** 이름이 지정된 수정 사본을 선택했습니다. RQ1의 라벨 결과를 읽습니다. 다른 지속성·다양성 노트북과 결과표도 있지만, 여기서 정한 논문의 최종 세 질문 범위에는 포함하지 않습니다.
- 공개 참고본의 코드 셀 내용은 바꾸지 않았습니다. 저장 출력, 실행 번호, 셀 메타데이터는 지우고 검토 안내를 추가했습니다. 오래된 출력으로 인한 혼동은 줄지만, 모델을 고치거나 검증한 것은 아닙니다.

## Interpretation checks / 해석 검토

1. **Generated targets:** RQ2 recovers labels derived from the same match indicators. This is a surrogate explanation task, not independent validation of tactical classes.
2. **Selection on test performance:** The historical code selects on test F1. Use training cross-validation or nested/group-aware validation for model selection and reserve a separate final test if external generalization is a goal.
3. **Post-clustering inference:** Comparing the features used to create groups can describe separation, but small p-values are not independent proof of the taxonomy. Repeated teams and paired match records complicate row-independence assumptions.
4. **PCA scope:** Saved output reports 45.95% retained variance. It is recorded evidence only; original-feature-space stability and sensitivity should be evaluated before stronger taxonomy claims.
5. **PPDA wording:** In the README use “lower PPDA, consistent with stronger pressing activity.” The thesis p.23 phrase “pressing intensity is lowest” while interpreting stronger pressing is ambiguous; distinguish the metric's value from the construct.
6. **Distribution scope:** Recalculated season association is chi-square 149.178, df 15, p ≈ 3.51e-24, Cramér's V ≈ 0.0482. A small p-value and a small effect can coexist. The calculation does not resolve non-independence or identify a causal seasonal change.

**한국어:**

1. **생성된 정답값:** RQ2는 같은 경기 지표로 만든 라벨을 다시 맞히는 대리 설명 과제입니다. 전술 유형을 독립적으로 검증한 것이 아닙니다.
2. **테스트 성능으로 모델 선택:** 기존 코드는 테스트 F1로 모델을 고릅니다. 모델 선택에는 학습 데이터 교차검증이나 중첩·그룹 검증을 쓰고, 외부 일반화를 보려면 최종 테스트를 따로 남겨야 합니다.
3. **군집 후 추론:** 군집을 만든 지표끼리 비교하면 분리 정도는 설명할 수 있지만, 작은 p값이 유형 체계의 독립적 증명은 아닙니다. 같은 팀이 반복 등장하고 경기당 두 행이 짝을 이루므로 행 독립 가정도 성립하기 어렵습니다.
4. **PCA 범위:** 저장된 출력의 설명 분산은 45.95%입니다. 기록된 근거일 뿐이며, 더 강한 유형 주장을 하려면 원래 지표 공간에서의 안정성과 민감도를 먼저 평가해야 합니다.
5. **PPDA 표현:** README에서는 “PPDA가 낮음, 즉 더 강한 압박 활동과 일치”라고 씁니다. 더 강한 압박을 해석하면서 “압박 강도가 가장 낮다”고 쓴 논문 p.23의 표현은 모호하므로, 지표 값과 개념을 구분합니다.
6. **분포 범위:** 다시 계산한 시즌 연관성은 카이제곱 149.178, 자유도 15, p ≈ 3.51e-24, Cramér's V ≈ 0.0482입니다. p값이 작아도 효과는 작을 수 있습니다. 이 계산으로 비독립성 문제가 해결되거나 시즌별 인과 변화가 확인되지는 않습니다.

## What has not been established / 확인하지 않은 것

Fresh-kernel execution of RQ1–RQ3; retrained models or SHAP outputs; original provider responses, scrape dates, joins, and exclusions; complete official fixture coverage; permission to redistribute row-level data; bootstrap stability from the original older notebook; and source-verification of every thesis reference.

RQ1–RQ3의 새 커널 실행, 모델·SHAP 재학습 결과, 원 제공처 응답·수집 날짜·결합·제외 기준, 공식 경기 일정 전체 범위, 행 단위 데이터 재배포 허락, 기존 구 노트북의 부트스트랩 안정성, 논문 참고문헌 전체의 출처 확인은 확인하지 않았습니다.

현재 스냅샷에 대한 검증과 원자료 수집·전체 분석 재현을 구분합니다. 과거 출력의 높은 성능 수치와 부트스트랩 ARI를 이번에 검증한 성과로 재사용하지 않습니다.

## Release resolution / 정식 공개본으로 확정하는 순서

1. Preserve thesis and existing hashes; identify or document the unrecoverable historical Table 8 baseline.
2. Choose an explicit release: thesis archive with discrepancy note, or a newly rerun analysis with its own version and date. Never silently blend both.
3. Freeze input hashes, source-column mappings, exclusion rules, and dependencies.
4. Rerun notebooks in a separate copy from a fresh kernel; write outputs into a new versioned directory.
5. Rebuild RQ2 tables with comparison IDs and consistent effect-size definitions; revise evaluation claims.
6. Regenerate only the representative figures from the same labeled data, then validate captions and both READMEs.

**한국어:**

1. 논문과 기존 해시를 보존하고, 복원할 수 없는 과거 표 8 기준값을 찾거나 그 사실을 기록합니다.
2. 공개본을 분명히 고릅니다. 불일치 안내를 붙인 논문 보관본이거나, 자체 버전과 날짜를 가진 새 재실행 분석입니다. 둘을 조용히 섞지 않습니다.
3. 입력 해시, 원천 열 매핑, 제외 규칙, 의존성을 고정합니다.
4. 별도 사본에서 새 커널로 노트북을 다시 실행하고, 결과는 버전이 붙은 새 폴더에 씁니다.
5. 비교 ID와 일관된 효과크기 정의로 RQ2 표를 다시 만들고, 평가 관련 주장을 고칩니다.
6. 같은 라벨 데이터로 대표 그림만 다시 만들고, 캡션과 두 README를 확인합니다.
