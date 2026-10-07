# 분석 결과 보기

[Project README](../README.ko.md) · [Data guide](../data/README.ko.md)

아래 표는 기존 라벨 CSV를 이번 검토에서 다시 집계한 결과입니다. 모델 재학습 결과가 아니며, 논문 표 8과 다른 두 군집 사례 수는 구분해 표시했습니다.

| Category / 분류 | File / 파일 |
|---|---|
| Profile counts / 유형 수·비중 | [cluster_counts.csv](review/cluster_counts.csv) |
| 14-feature means / 14개 지표 평균 | [cluster_profile.csv](review/cluster_profile.csv) |
| League shares / 리그별 비중 | [league_cluster_share.csv](review/league_cluster_share.csv) |
| Season shares / 시즌별 비중 | [season_cluster_share.csv](review/season_cluster_share.csv) |
| Sample sizes / 표본 수 | [coverage.csv](review/coverage.csv) |
| Value ranges / 값 범위 | [feature_ranges.csv](review/feature_ranges.csv) |
| Audit / 검사 기록 | [snapshot_audit.json](review/snapshot_audit.json) |
| Team-match labels / 행별 군집 결과 | [Labeled CSV](tables/rq1_final_data_14vars_hierarchical_4clusters.csv) |
