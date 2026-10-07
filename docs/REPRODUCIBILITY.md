# Reproduction status / 재현 상태

## Two distinct workflows / 구분해야 할 두 작업

**A. Executed snapshot audit.** `scripts/verify_snapshot.py` reads the two included CSVs, validates keys and features, compares 56 paper means and four cluster counts, and writes summaries. It has been executed. `requirements-audit.txt` records the package versions used for that audit; these are not recovered thesis-era versions.

**A. 실제 실행한 스냅샷 검증.** 포함된 CSV 두 개의 키·지표를 검사하고 논문 평균 56개·사례 수 4개를 비교한 뒤 집계를 저장했습니다. 감사용 의존성 버전은 원래 논문 실행 환경을 복원한 것이 아닙니다.

**B. Historical notebook pipeline.** RQ1 → RQ2 and RQ3. Reference copies are included with code-cell sources preserved, output cells cleared, and a review notice added. This pipeline has not been rerun in a fresh kernel in this package.

**B. 기존 연구 노트북.** RQ1 이후 RQ2와 RQ3를 실행하는 구조입니다. 코드 셀은 보존했고 출력은 제거했습니다. 이번 패키지에서 커널을 새로 시작해 전체 실행하지 않았습니다.

## Notebook order and dependencies / 실행 순서와 입력

| Order | Notebook | Input | Key output |
|---|---|---|---|
| 1 | `01_rq1_clustering.ipynb` | `data/processed/tactical_analysis_cleaned.csv` | `outputs/tables/rq1_final_data_14vars_hierarchical_4clusters.csv` |
| 2 | `02_rq2_profile_explanation.ipynb` | RQ1 labeled CSV | Difference tables, surrogate classifiers, SHAP figures |
| 3 | `03_rq3_league_season_distribution.ipynb` | Same RQ1 labeled CSV | League and season plots/tables |

These are historical execution directions, not a guarantee of current executability. Use a separate working copy and run with working directory at its root or `notebooks/`. Notebook path detection does not support arbitrary nested directories. Running them may rewrite their output files; do not point them at the only preserved original.

위 순서는 기존 코드에서 확인한 의존관계이며, 현재 환경에서 실행된다는 보증이 아닙니다. 원본이 아닌 별도 사본에서 실행하세요. 노트북의 경로 감지는 저장소 루트 또는 `notebooks/`를 기준으로 하며, 임의의 하위 경로를 지원하지 않습니다. 기존 코드가 산출물을 같은 이름으로 덮어쓰므로 원본 유일본에서 실행하지 마세요.

## Environment / 환경

The thesis states Python 3.11. Imports in the selected notebooks include NumPy, pandas, matplotlib, seaborn, SciPy, scikit-learn, XGBoost, SHAP, joblib, and IPython. RQ2 also contains an inline `!pip install scikit-posthocs` cell. This is valid notebook shell syntax, but it should be moved into an explicit environment definition in a future cleaned execution version. Do not mistake a plain Python AST parser rejecting `!pip` for a broken Jupyter notebook.

논문에는 Python 3.11로 기재되어 있습니다. 선택한 코드의 라이브러리와 버전은 추후 고정해야 합니다. RQ2의 `!pip install`은 노트북 문법으로는 유효하지만 실행 중 환경을 바꾸므로 정리된 실행본에서는 환경 파일로 분리하는 것이 좋습니다. 이번에는 원본 코드 보존을 위해 변경하지 않았습니다.

Korean figure fonts use AppleGothic on macOS and Malgun Gothic on Windows. A Linux environment may need a separately installed Korean font. This is a presentation dependency, not an analytical result.

## Before claiming full reproduction / 전체 재현을 주장하기 전

- Fix the input snapshot and reconcile the paper/current count difference.
- Freeze a clean environment, including model and SHAP compatibility.
- Execute each notebook from a fresh kernel in order, without relying on old variables.
- Prevent repeated exploratory cells from overwriting differently defined statistics under identical names.
- Rebuild result tables with comparison identifiers and consistent cluster names.
- Compare new outputs against the selected version, documenting any changes instead of overwriting paper claims.

No new clustering or classification performance result was produced by this packaging task.
