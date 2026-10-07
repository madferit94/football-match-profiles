# Problem definition / 문제 정의

[English README](../README.md) · [한국어 README](../README.ko.md)

## Decision boundary / 분석의 경계

**Practical problem:** Final scores and season averages give limited descriptions of how individual team performances differ. A reusable match-record profile can organize comparison and direct further video investigation.

**현실 문제:** 결과와 시즌 평균만으로는 경기마다 다른 운영 양상을 설명하기 어렵습니다. 경기별 유형을 만들어 비교 대상을 정리하고, 이후 영상 확인의 출발점을 제공합니다.

**Central question:** What interpretable match-record profiles emerge across Europe's five major leagues, what distinguishes them, and how are they distributed across leagues and seasons?

**중심 질문:** 유럽 5대 리그의 경기기록에서 어떤 유형이 나타나며, 무엇으로 구별되고, 리그·시즌에 따라 어떻게 분포하는가?

이 연구는 경기기록에서 유형을 찾고 그 특징과 분포를 설명하는 데 초점을 둡니다.

## Research questions and analysis / 연구 질문과 분석

| Research question / 연구 질문 | Subquestions / 세부 질문 | Method / 방법 | Interpretation / 해석 범위 |
|---|---|---|---|
| RQ1: Derive / 유형 도출 | What is one observation? Which indicators are available? How many groups and what partition? / 한 행·입력 지표·군집 수·분할 방식은? | Cohort checks, scaling, PCA, silhouette, recursive K-means | Fix labels here. Do not rank their success. / 유형을 확정하며 성과 순위를 매기지 않음 |
| RQ2: Explain / 유형 설명 | Which distributions differ? How large are the differences? Which inputs does the surrogate classifier use? / 어떤 지표가 얼마나 다르고, 라벨 설명 모델은 무엇을 사용하는가? | Means/distributions, Mann–Whitney U, effect sizes, classifier comparison, SHAP | Describe existing labels; do not redefine groups from explanations. / 기존 유형을 설명하며 SHAP로 군집을 다시 정의하지 않음 |
| RQ3: Locate / 분포 비교 | Where: league shares. When: season shares. Combined context: league-by-season shares. / 어느 리그·어느 시즌·리그 내 시즌별 비중인가? | Counts, denominator-aware percentages, exploratory association | Reuse fixed labels and denominators; do not infer league strength or causes. / 같은 라벨·분모로 비교하며 우열·원인을 추론하지 않음 |

The profiles derived in RQ1 provide the common basis for RQ2 and RQ3: the same labels are used to explain feature differences and compare league and season distributions.

RQ1에서 도출한 유형을 공통 기준으로 사용합니다. RQ2에서는 유형별 지표 차이를 설명하고, RQ3에서는 같은 유형의 비중을 리그와 시즌별로 비교합니다.

## Indicator organization / 지표 배치

The 14 indicators describe possession, progression, ball delivery and carrying, shooting, and defensive activity. These aspects are related and are interpreted together.

14개 지표는 점유·패스, 공격지역 진입, 전개 방식, 슈팅, 압박·수비 행동을 살펴봅니다. 서로 연관된 지표를 함께 해석하여 경기 운영 특성을 설명합니다.

| Reporting group / 설명 범주 | Columns | Count |
|---|---|---:|
| Possession and passing / 점유·패스 | `possession`, `passes` | 2 |
| Progression / 공격지역 진입 | `final_third_entries`, `DEEP` | 2 |
| Ball delivery and carrying / 전개 방식 | `long_balls`, `goalkeeping_goal_kicks`, `crosses`, `dribbles` | 4 |
| Shooting / 슈팅 | `shots`, `box_shots` | 2 |
| Pressing and defensive actions / 압박·수비 행동 | `ppda_val`, `tackles`, `interceptions`, `clearances` | 4 |
| Total / 합계 | Clustering indicators / 군집 입력 지표 | 14 |

Goal kicks are included as recorded actions, not as a direct measure of goal-kick strategy. A match-level record cannot identify transitions, defensive shape, or off-ball movement in detail.

골킥은 기록된 횟수이며, 골킥 전술 그 자체를 나타내지 않습니다. 경기 합계만으로 공수 전환·수비 대형·공 없는 움직임을 세밀하게 분리할 수 없습니다.

## Metric definitions / 산식

- Profile share within group = profile team-match rows / all retained team-match rows in that league or season × 100.
- Cluster profile mean = sum of indicator values within the cluster / team-match rows in that cluster.
- 군집 비중 = 해당 유형 팀-경기 수 ÷ 같은 리그 또는 시즌의 전체 유지된 팀-경기 수 × 100.
- 군집 평균 = 군집 내 지표 합계 ÷ 군집의 팀-경기 수.

Compare percentages rather than counts when league/season sample sizes differ. Counts must still be reported to show the denominator. A profile count is not a count of unique teams.

리그·시즌의 표본 크기가 다르므로 비중을 비교하되 분모를 함께 제시합니다. 군집 사례 수는 서로 다른 팀의 수가 아닙니다.

## Claims to use / 권장 표현

- Use: “The high-possession profile has a higher mean shot count in this sample.” / “이 표본에서 고점유 유형은 평균 슈팅 수가 높았습니다.”
- Avoid: “Possession tactics cause more shots or wins.” / “점유 전술이 슈팅과 승리를 증가시킵니다.”
- Use: “SHAP explains a classifier recovering the generated labels.” / “SHAP은 생성된 라벨을 구분하는 분류 모델을 설명합니다.”
- Avoid: “SHAP proves the tactical importance or causal impact of possession.” / “SHAP이 점유율의 전술적·인과적 영향력을 증명합니다.”
- Use: “The profile share differs in the retained league samples.” / “유지된 리그 표본에서 유형 비중이 달랐습니다.”
- Avoid: “This proves one league is tactically superior.” / “특정 리그의 전술적 우월성을 입증합니다.”

## Portfolio contribution / 포트폴리오에서 보여주는 역량

Problem framing, observation design, multi-source data organization, interpretable unsupervised analysis, numerical verification, and honest communication of limitations. Collection reproducibility and external validation remain separate deliverables to complete; neither is established by this README.

문제 정의, 분석 단위 설계, 여러 출처의 자료 구성, 해석 가능한 비지도 분석, 숫자 검증, 한계 전달을 보여줍니다. 수집 재현성과 외부 검증은 추가로 완성해야 할 결과물이며 README만으로 입증되지 않습니다.
