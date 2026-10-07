# Match-record profiles in European football

**How can team performances be grouped beyond the final score, and how do those profiles vary across leagues and seasons?**

[한국어](README.ko.md) · [Research questions](docs/PROBLEM_DEFINITION.md) · [Validation](docs/VALIDATION.md) · [Publication plan](docs/PUBLICATION_PLAN.ko.md)

A research project deriving and comparing team-match profiles across Europe’s Big Five leagues. This repository shares the **problem framing → data preparation → clustering → feature interpretation → league and season comparisons** through code, data, and result tables.

The study groups **team-match observations**, explains the resulting profiles, and compares their distributions across leagues and seasons. The profiles refer to statistical patterns in match records; the labels do not directly measure formations, coaching intent, or tactical effectiveness.

> **Validation status — 8 October 2026.** The saved CSVs were audited and their summaries recalculated. The three historical notebooks have not been rerun end to end. Two cluster counts differ from thesis Table 8; both versions are documented below. End-to-end rerunning remains pending.

## Explore

| Category | Contents |
|---|---|
| [Data files](data/README.md) | Actual cleaned input and saved labels |
| [Period and coverage](data/catalog/coverage.md) | Match counts and dates by league and season |
| [Metric guide](data/README.md#browse-by-category) | 14 clustering inputs and all auxiliary/derived columns |
| [Research questions](docs/PROBLEM_DEFINITION.md) | Derive, explain, and compare profiles |
| [Analysis code](notebooks/) | RQ1, RQ2, and RQ3 notebooks |
| [Results](outputs/README.md) | Profile means and league/season shares |
| [Validation and limitations](docs/VALIDATION.md) | Data checks and paper discrepancies |

## Problem

Scores describe outcomes but do not fully describe how teams possessed the ball, progressed attacks, generated shots, or defended. Assigning a single permanent style to a club also hides differences between its matches.

This project asks whether a common set of match records can provide an interpretable basis for comparing **how teams played in individual matches** across five leagues and six seasons.

## Research questions

The analysis first derives profiles from match records, then explains their characteristics and compares their distributions across leagues and seasons.

| Question | Responsibility | Deliverable |
|---|---|---|
| **RQ1 — What profiles emerge?** | Define the observation and indicators; derive groups from similarities in match records. | Two-stage K-means grouping and four profile labels. |
| **RQ2 — What distinguishes the profiles?** | Describe feature differences and explain a classifier trained to recover the generated labels. | Profile means, distribution comparisons, effect sizes, and SHAP interpretation. |
| **RQ3 — Where and when do profiles occur?** | Compare the fixed profile definitions across leagues and seasons. | Within-league and within-season shares. |

## Data

| Item | Scope |
|---|---|
| Leagues | Premier League, LaLiga, Bundesliga, Serie A, Ligue 1 |
| Seasons | 2019/20–2024/25 |
| Observation | One team in one match; a retained match contributes two rows |
| Retained sample | **21,394 team-match rows / 10,697 distinct league–match IDs** |
| Dates in the saved data | 9 August 2019–25 May 2025 |
| Providers reported in the thesis | Sofascore; Understat for PPDA and DEEP |
| Clustering inputs | 14 indicators; goals, match results, and xG are not clustering inputs |

The distinct-match count was verified from the saved data, including reciprocal team/opponent and score checks. It is **not a claim of complete fixture coverage**. Raw collection records and provider-join provenance were not reconstructed in this review. The cleaned input and saved labels are included; see [data files and definitions](data/README.md). These files are distinct from raw provider responses.

## Method

1. Restrict the input to the six target seasons and retain rows complete on the 14 indicators.
2. Standardize the indicators, then apply principal component analysis (PCA) to obtain two coordinates.
3. Compare first-stage K-means solutions for `k=2…9`; split each of the two selected parent groups into two subgroups after examining `k=2…5` within each parent.
4. Interpret the four groups using the original indicator values. These names are post-hoc descriptions.
5. Compare profile distributions using descriptive statistics, Mann–Whitney U tests, and effect sizes. Compare tree classifiers and use SHAP to explain label separation.
6. Compare profile shares by league and season.

This is **recursive 2×2 K-means partitioning**, not agglomerative hierarchical clustering and not a globally selected `k=4` solution. The saved RQ1 output reports 45.95% variance retained by two PCs; this figure was not recomputed by fitting PCA during this review.

## Findings from the current saved snapshot

The values below were recalculated from the existing labeled CSV, without refitting the clustering model. The 14-feature means for all four groups match thesis Table 7 at its displayed two-decimal precision.

| Profile | Interpretation label | Team-match rows | Share | Possession (%) | Shots | PPDA |
|---|---|---:|---:|---:|---:|---:|
| 1-1 | Possession build-up | 6,487 | 30.32% | 56.48 | 14.42 | 9.85 |
| 1-2 | High-possession dominance | 2,855 | 13.34% | 65.50 | 19.98 | 8.22 |
| 2-1 | Low-possession defensive | 4,122 | 19.27% | 35.60 | 7.82 | 20.59 |
| 2-2 | Defensive build-up | 7,930 | 37.07% | 46.60 | 10.70 | 12.33 |

- The high-possession profile has the highest mean shot volume and the lowest PPDA. Lower PPDA is an indirect indication of stronger pressing activity, not evidence of pressing success.
- The low-possession defensive profile combines fewer shots with more clearances. This describes observed match records, not a deliberate defensive strategy in every match.
- The high-possession profile accounts for **17.13%** of retained EPL team-match rows and **10.82%** of LaLiga rows. These unadjusted sample shares do not rank league quality.
- The recalculated season–profile association has **Cramér's V = 0.0482**. The statistically small p-value should not be presented as a large practical change; the effect-size measure is small, and rows also contain repeated teams and paired opponents.

Evidence: [counts](outputs/review/cluster_counts.csv), [all profile means](outputs/review/cluster_profile.csv), [league shares](outputs/review/league_cluster_share.csv), [season shares](outputs/review/season_cluster_share.csv), and [audit record](outputs/review/snapshot_audit.json).

### Analysis versions and reproducibility settings

The 14 indicators were selected by reviewing match-record categories used in prior research and considering data availability. Candidate cluster counts were examined using silhouette scores, as documented in the study's variable-selection and clustering procedures.

According to the author, the thesis reports results from the writing-stage analysis, while this repository contains results from a subsequent notebook rerun. Thesis Table 8 reports **4,017 / 8,035** observations for profiles 2-1 / 2-2; the current saved data contain **4,122 / 7,930**. Both versions total 21,394 observations.

The published RQ1 code specifies `random_state=42` and `n_init=10`. Run-specific configuration records linking the thesis analysis to the current snapshot have not been established, so the count difference is not attributed to a particular seed change. Stability comparisons across multiple random seeds are identified as follow-up validation. See the [validation record](docs/VALIDATION.md).

## Interpretation and use

In this sample, the four profiles differ in combinations of possession, danger-area passing, shots, PPDA, and clearances. For example, the two possession-based profiles average 14.42 versus 19.98 shots and 7.45 versus 12.56 DEEP. This allows a description such as “possession-based” to be specified further through progression and shooting records. Superiority over a possession-only grouping has not been tested.

A proposed next use is to inspect a team's profile mix and select matches that depart from its usual pattern for contextual video review. This application has not been evaluated for analyst time savings or decision quality. The analysis does not establish which profile causes wins or which tactic a coach should choose.

## Limitations

- The labels are generated from the same indicators later used to explain them. Classifier accuracy measures recovery of those labels, not externally validated tactical truth or match-result prediction.
- The historical RQ2 code selects the model using test F1. That set is therefore part of model selection, not an untouched final performance test. PCA/clusters were also derived before this split.
- Random row splits do not isolate future seasons, unseen teams, or both opponents in the same match. Tests on repeated team-match rows require care about independence.
- Tests on clustering inputs are descriptive post-clustering comparisons, not independent confirmation that the groups exist. Multiple comparisons and effect sizes also need attention.
- Two PCs retain only part of the input variation. Higher silhouette scores in a different-dimensional space do not alone prove a better football taxonomy.
- Counts are not adjusted for possession, opponent strength, home/away status, score state, or provider differences. The 14 indicators are correlated and do not exhaust football tactics.
- End-to-end collection, notebook execution, and the thesis-count discrepancy remain unresolved.

## Repository guide

| Path | Purpose |
|---|---|
| `notebooks/01_rq1_clustering.ipynb` | Selected historical clustering code; outputs cleared |
| `notebooks/02_rq2_profile_explanation.ipynb` | Selected historical comparison/classifier/SHAP code; outputs cleared |
| `notebooks/03_rq3_league_season_distribution.ipynb` | Selected historical distribution analysis; outputs cleared |
| `scripts/verify_snapshot.py` | Executed read-only audit of local CSV snapshots |
| `outputs/review/` | Summaries recalculated for the publication review |
| `data/` | Cleaned input, coverage tables, and category-based metric documentation |
| `docs/` | Problem decomposition, evidence, file decisions, and notebook provenance |

## Python scripts

Companion `.py` files sit beside the notebooks in `notebooks/`, preserving code-cell order and analysis logic.

| Analysis | Notebook | Python script |
|---|---|---|
| RQ1 profile derivation | [Notebook](notebooks/01_rq1_clustering.ipynb) | [Python](notebooks/01_rq1_clustering.py) |
| RQ2 profile explanation | [Notebook](notebooks/02_rq2_profile_explanation.ipynb) | [Python](notebooks/02_rq2_profile_explanation.py) |
| RQ3 distribution comparison | [Notebook](notebooks/03_rq3_league_season_distribution.ipynb) | [Python](notebooks/03_rq3_league_season_distribution.py) |

The exports add an explicit `display` import and replace the notebook's inline `!pip install` with a separate-installation comment. Code-cell equivalence and Python syntax were checked; the full analysis was not rerun. See [execution notes](docs/REPRODUCIBILITY.md#python-companion-scripts--파이썬-사본).

## Reproduce the snapshot audit

The audit requires Python, pandas, NumPy, and SciPy. From this repository root:

```bash
python -m pip install -r requirements-audit.txt
python scripts/verify_snapshot.py \
  --source-root . \
  --output-dir ../football-match-profiles-audit-new
```

Both CSVs are bundled, so `--source-root .` reads this repository. The audit refuses to replace existing review outputs or write inside the source folder. It does **not** reproduce collection, clustering, classifiers, or SHAP. For the historical notebook order and prerequisites, see [reproduction status](docs/REPRODUCIBILITY.md).

## Author and contact

**Minseob Eom · 엄민섭**

- Email: [wowzc@naver.com](mailto:wowzc@naver.com)
- LinkedIn: [Minseob Eom](https://www.linkedin.com/in/minseob-eom-97b410375/)
- Instagram: [@madferit94](https://www.instagram.com/madferit94/)
- GitHub: [@madferit94](https://github.com/madferit94)

## Research background and data sources

This project shares data, analytical steps, and results developed during master's research. Related study: *Clustering Tactical Types and Analyzing Type-Specific Match Characteristics in Football: Evidence from Europe’s Big Five Leagues* (2026). The thesis PDF is not published here.

Data sources are Sofascore and Understat. The scope of verified field definitions and collection provenance is documented in the [data guide](data/README.md). No license is asserted over provider data.
