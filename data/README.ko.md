# 데이터 안내

[English](README.md) · [한국어](README.ko.md) · [Project README](../README.ko.md)

실제 분석에 사용한 정제 입력과 군집 라벨 결과를 포함했습니다. 제공처의 원본 응답 파일은 현재 연구 폴더에서 확보하지 못했으므로, 두 CSV를 수집 원본이라고 부르지 않습니다.

## 데이터 파일

| File | Rows × columns | Role |
|---|---:|---|
| [tactical_analysis_cleaned.csv](processed/tactical_analysis_cleaned.csv) | 21,394 × 56 | RQ1 cleaned input · 정제 입력 |
| [rq1_final_data_14vars_hierarchical_4clusters.csv](../outputs/tables/rq1_final_data_14vars_hierarchical_4clusters.csv) | 21,394 × 30 | Saved labels for RQ2/RQ3 · 군집 결과 |

파일은 원본과 바이트 단위로 동일한 사본입니다. [해시·용량](catalog/files.json)으로 확인할 수 있습니다. GitHub에서 큰 CSV의 표 미리보기가 제한되면 파일 페이지의 Raw/다운로드로 열 수 있습니다.

## 카테고리별 보기

- [기간·리그·표본 / Period and coverage](catalog/coverage.ko.md)
- [점유·패스 (2 columns)](catalog/possession.ko.md)
- [공격지역 진입 (2 columns)](catalog/progression.ko.md)
- [공격 전개 (4 columns)](catalog/delivery.ko.md)
- [슈팅 (2 columns)](catalog/shooting.ko.md)
- [압박·수비 (4 columns)](catalog/defense.ko.md)
- [경기 정보·결과 (11 columns)](catalog/context.ko.md)
- [보조 경기기록 (23 columns)](catalog/auxiliary.ko.md)
- [파생 지표·군집 라벨 (15 columns)](catalog/derived.ko.md)

[All columns CSV / 전체 컬럼 사전](catalog/all_columns.csv) · [Schema](data_schema.json) · [Validation / 검증 기록](../docs/VALIDATION.md)

## 출처와 해석

논문에는 Sofascore 경기기록과 Understat의 PPDA·DEEP를 사용했다고 기재되어 있습니다. 원필드 매핑·수집 시각·제공처 간 결합 이력은 아직 복원하지 못했습니다. 지표별로 확인한 범위와 미확인 정의를 구분했습니다.

군집 입력은 14개이며, 파일별 컬럼의 합집합은 63개입니다. 보조 지표·경기 결과·라벨을 군집 입력과 구분해서 읽으세요. 현재 두 군집의 사례 수는 논문 표 8과 다릅니다. 자세한 내용은 검증 기록에 있습니다.

연구에 사용한 데이터 사본을 포함했습니다. 제공처의 재배포 조건을 확정하거나 데이터 라이선스를 새로 부여한 것은 아닙니다.
