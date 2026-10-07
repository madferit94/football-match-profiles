# -*- coding: utf-8 -*-
# Python companion to the notebook with the same filename.
# Notebook cell order and analysis code are preserved.
# Adaptations: import display for ordinary Python; comment out inline pip install.
# Install dependencies separately; run from the repository root or notebooks/.
# This export has been syntax-checked, not executed end to end.
# Original analysis writes to outputs/tables and outputs/figures.

from IPython.display import display

# %% [markdown] Notebook cell 0
# # Historical research notebook / 기존 연구 코드
# This is a reference copy of the thesis workflow. Code cells are preserved, but saved outputs and execution counts were cleared for publication review. It has not been rerun in this package. Read ../docs/VALIDATION.md before executing. Run from the repository root or notebooks/ directory; the required cleaned input and saved labels are included.
# 기존 연구의 참고용 사본입니다. 코드 셀은 보존했고 저장 출력과 실행 번호를 지웠습니다. 이 패키지에서 전체 재실행하지 않았습니다. 검증 문서와 포함된 데이터 안내를 먼저 확인하세요.

# %% [markdown] Notebook cell 1
# # 연구내용2. 전술 운영 유형 간 전술 지표 차이 검증 및 핵심 지표 해석
# 
# - 계층적 군집 구조에 따른 전술 지표 차이 검증
# - XGBoost-SHAP 기반 최종 전술 운영 유형별 핵심 지표 해석

# %% [code] Notebook cell 2
# ── 한글 폰트 설정 (운영체제 자동 감지) ───────────────────────────
import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

if platform.system() == "Darwin":           # macOS
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:                                       # Linux 등
    plt.rcParams["font.family"] = "DejaVu Sans"

plt.rcParams["axes.unicode_minus"] = False   # 마이너스 기호 깨짐 방지

print(f"폰트 설정: {plt.rcParams['font.family'][0]}")

# %% [code] Notebook cell 3
# Cell 2 끝부분에 추가
import platform
if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# %% [code] Notebook cell 4
# Install before running: python -m pip install scikit-posthocs


# %% [markdown] Notebook cell 5
# ## [STEP 1] 라이브러리 로드 및 데이터 준비]

# %% [code] Notebook cell 6
 # ════════════════════════════════════════════════════════════
# [RQ2 STEP 1] Load Libraries and Prepare Data (최종 명칭 반영)
# ════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import shap
import joblib # 필요한 경우 추가

from xgboost import XGBClassifier
from pathlib import Path

import warnings
warnings.filterwarnings("ignore")

# ── 1. Path settings ──────────────────────────────────────────────────────────
CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "notebooks" else CURRENT_DIR

OUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
OUT_FIG_DIR   = PROJECT_ROOT / "outputs" / "figures"

OUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = OUT_TABLE_DIR / "rq1_final_data_14vars_hierarchical_4clusters.csv"

if not DATA_PATH.exists():
    raise FileNotFoundError(f"입력 파일 없음: {DATA_PATH}")

df_rq2 = pd.read_csv(DATA_PATH)

# ── 2. 전술 변수 (14개, 최종) ─────────────────────────────────────────────────
FINAL_TACTICAL_VARS = [
    "possession", "passes", "long_balls", "final_third_entries",
    "goalkeeping_goal_kicks", "ppda_val", "DEEP",
    "crosses", "dribbles", "box_shots", "shots",
    "tackles", "interceptions", "clearances",
]

# ── 3. 확정된 군집 명칭 매핑 ───────────────────────────────────────────────────
FINAL_CLUSTER_ORDER = ["1-1", "1-2", "2-1", "2-2"]

# 표 및 시각화에 사용할 최종 명칭
FINAL_CLUSTER_NAME_MAP = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

# 1차 상위 군집 명칭
STAGE1_NAME_MAP = {
    0: "Stage 1 Cluster 1 (능동적 점유형)", 
    1: "Stage 1 Cluster 2 (수비적 직접형)",
}

RANDOM_STATE = 42

# ── 4. 필수 컬럼 검증 ──────────────────────────────────────────────────────────
# 데이터프레임 내 'cluster_label_kr'이 최종 명칭으로 이미 저장되어 있다고 가정합니다.
required_cols = FINAL_TACTICAL_VARS + [
    "cluster_stage1", "cluster_final_num",
    "cluster_final_hier", "cluster_label", "cluster_label_kr",
]
missing_cols = [c for c in required_cols if c not in df_rq2.columns]
if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

df_rq2["cluster_stage1"]     = df_rq2["cluster_stage1"].astype(int)
df_rq2["cluster_final_hier"] = df_rq2["cluster_final_hier"].astype(str)

# ── 5. 기초 확인 ──────────────────────────────────────────────────────────────
print("=" * 80)
print("[RQ2 STEP 1] Data Loaded - Tactical Analysis Ready")
print("=" * 80)
print(f"  Data path    : {DATA_PATH}")
print(f"  Rows         : {len(df_rq2):,}")
print(f"  Tactical Vars: {len(FINAL_TACTICAL_VARS)}")

print("\n[Stage 1 cluster distribution]")
display(df_rq2["cluster_stage1"].value_counts().sort_index()
        .rename(index=STAGE1_NAME_MAP).rename_axis("cluster_stage1").reset_index(name="count"))

print("\n[Final hierarchical cluster distribution]")
dist = df_rq2["cluster_final_hier"].value_counts().reindex(FINAL_CLUSTER_ORDER).reset_index()
dist.columns = ["cluster_final_hier", "count"]
# 매핑 적용
dist["name"] = dist["cluster_final_hier"].map(FINAL_CLUSTER_NAME_MAP)
display(dist)

print("\n[Cluster name mapping check]")
display(df_rq2[["cluster_final_hier", "cluster_label_kr"]]
        .drop_duplicates().sort_values("cluster_final_hier").reset_index(drop=True))

# %% [markdown] Notebook cell 7
# ## RQ2 STEP 2. 전술 운영 유형별 기술통계

# %% [code] Notebook cell 8
# ════════════════════════════════════════════════════════════
# [RQ2 STEP 2] Helper 함수 정의
# ════════════════════════════════════════════════════════════
import pandas as pd
import numpy as np

def make_mean_sd_table(data, group_col, variables, group_order, group_name_map):
    """
    각 군집별 Mean ± SD 표 생성
    - data: DataFrame
    - group_col: 군집 라벨 컬럼명
    - variables: 변수 리스트
    - group_order: 군집 순서 리스트
    - group_name_map: {원래값: 표시명} 딕셔너리
    """
    result = {}
    for g in group_order:
        subset = data[data[group_col] == g][variables]
        m = subset.mean()
        s = subset.std()
        result[group_name_map[g]] = (m.round(2).astype(str) + " ± " + s.round(2).astype(str))
    
    df_out = pd.DataFrame(result)
    df_out.index = variables
    return df_out

# %% [code] Notebook cell 9
 # ════════════════════════════════════════════════════════════
# [RQ2 STEP 2] Descriptive Statistics: Mean ± SD (최종 명칭 반영)
# ════════════════════════════════════════════════════════════

print("=" * 80)
print("[RQ2 STEP 2] Descriptive Statistics: Mean ± SD")
print("=" * 80)

# ── 1. Helper 함수 유지 및 딕셔너리 매핑 ──────────────────────────────
# 변수명 매핑 (기존 유지)
var_ko = {
    "possession": "점유율 (Possession)", 
    "passes": "패스 (Passes)", 
    "long_balls": "롱볼 (Long balls)", 
    "final_third_entries": "상대 진영 1/3 투입 (Final third entries)", 
    "goalkeeping_goal_kicks": "골킥 (Goal kicks)", 
    "ppda_val": "전방 압박 강도 (PPDA)", 
    "DEEP": "위험 지역 진입 패스 (DEEP)", 
    "crosses": "크로스 (Crosses)", 
    "dribbles": "드리블 (Dribbles)", 
    "box_shots": "박스 내 슈팅 (Box shots)", 
    "shots": "슈팅 (Shots)",
    "tackles": "태클 (Tackles)", 
    "interceptions": "인터셉트 (Interceptions)", 
    "clearances": "클리어링 (Clearances)"
}

# ── 2-1. Stage 1 비교 ────────────────────────────────────────────────
desc_stage1 = make_mean_sd_table(
    data=df_rq2,
    group_col="cluster_stage1",
    variables=FINAL_TACTICAL_VARS,
    group_order=[0, 1],
    group_name_map={0: "Cluster 1 (능동적 점유형)", 1: "Cluster 2 (수비적 직접형)"}
)
print("\n[2-1] Stage 1 비교: 능동적 점유형 vs 수비적 직접형")
display(desc_stage1)
desc_stage1.to_csv(OUT_TABLE_DIR / "rq2_desc_stage1_proactive_vs_defensive.csv", encoding="utf-8-sig")

# ── 2-2-A. Cluster 1 세부 비교 ──────────────────────────────────────
df_stage1_1 = df_rq2[df_rq2["cluster_stage1"] == 0].copy()

desc_stage1_1 = make_mean_sd_table(
    data=df_stage1_1,
    group_col="cluster_final_hier",
    variables=FINAL_TACTICAL_VARS,
    group_order=["1-1", "1-2"],
    group_name_map={"1-1": "1-1 점유 전개형", "1-2": "1-2 고점유 지배형"}
)
print("\n[2-2-A] Cluster 1 내: 1-1 점유 전개형 vs 1-2 고점유 지배형")
display(desc_stage1_1)
desc_stage1_1.to_csv(OUT_TABLE_DIR / "rq2_desc_within_cluster1_1-1_vs_1-2.csv", encoding="utf-8-sig")

# ── 2-2-B. Cluster 2 세부 비교 ──────────────────────────────────────
df_stage1_2 = df_rq2[df_rq2["cluster_stage1"] == 1].copy()

desc_stage1_2 = make_mean_sd_table(
    data=df_stage1_2,
    group_col="cluster_final_hier",
    variables=FINAL_TACTICAL_VARS,
    group_order=["2-1", "2-2"],
    group_name_map={"2-1": "2-1 저점유 수비형", "2-2": "2-2 수비적 전개형"}
)
print("\n[2-2-B] Cluster 2 내: 2-1 저점유 수비형 vs 2-2 수비적 전개형")
display(desc_stage1_2)
desc_stage1_2.to_csv(OUT_TABLE_DIR / "rq2_desc_within_cluster2_2-1_vs_2-2.csv", encoding="utf-8-sig")

print("\n저장 완료.")

# %% [markdown] Notebook cell 10
# ## RQ2 STEP 3. 검정 방법 선정을 위한 통계적 가정 검토

# %% [code] Notebook cell 11
 # ════════════════════════════════════════════════════════════
# [RQ2 STEP 3] Assumption Checks (Normality & Homogeneity of Variance)
# ════════════════════════════════════════════════════════════

from scipy.stats import shapiro, levene
import pandas as pd
import numpy as np

print("=" * 80)
print("[RQ2 STEP 3] Normality (Shapiro-Wilk) & Homogeneity of Variance (Levene)")
print("=" * 80)

# ── Helper ───────────────────────────────────────────────────────────────────
def run_assumption_checks(data, group_col, variables, comparison_name, group_order=None):
    if group_order is None:
        group_order = sorted(data[group_col].dropna().unique())
    results = []
    for var in variables:
        groups = [data.loc[data[group_col] == g, var].dropna().values for g in group_order]

        shapiro_ps = []
        for gv in groups:
            samp = (pd.Series(gv).sample(n=5000, random_state=42).values
                    if len(gv) > 5000 else gv)
            _, p = shapiro(samp) if len(samp) >= 3 else (np.nan, np.nan)
            shapiro_ps.append(p)

        norm_pass = all(p > 0.05 for p in shapiro_ps if not np.isnan(p))

        if all(len(g) >= 2 for g in groups):
            _, lev_p = levene(*groups, center="median")
        else:
            lev_p = np.nan

        var_pass = bool(lev_p > 0.05) if not np.isnan(lev_p) else False
        rec = "Independent samples t-test" if (norm_pass and var_pass) else "Mann-Whitney U test"

        results.append({
            "comparison":              comparison_name,
            "variable":                var,
            "group_1":                 group_order[0],
            "group_2":                 group_order[1],
            "min_shapiro_p":           np.nanmin(shapiro_ps),
            "normality":               "Pass" if norm_pass else "Violated",
            "levene_p":                lev_p,
            "homogeneity_of_variance": "Pass" if var_pass else "Violated",
            "recommended_test":        rec
        })
    return pd.DataFrame(results)

# ── 서브셋 준비 (수정된 부분) ──────────────────────────────────────────────────
# 변수명을 df_stage1_1과 df_stage1_2로 맞춰주었습니다.
df_stage1_1 = df_rq2[df_rq2["cluster_stage1"] == 0].copy()
df_stage1_2 = df_rq2[df_rq2["cluster_stage1"] == 1].copy()

# ── 3-1. Stage 1: Cluster 1 vs Cluster 2 ─────────────────────────────────────
a1 = run_assumption_checks(
    df_rq2, "cluster_stage1", FINAL_TACTICAL_VARS,
    "Stage 1: Cluster 1 vs Cluster 2",
    group_order=[0, 1]
)

# ── 3-2. Within Stage 1 Cluster 1: 1-1 vs 1-2 ────────────────────────────────
a2 = run_assumption_checks(
    df_stage1_1, "cluster_final_hier", FINAL_TACTICAL_VARS,
    "Within Stage 1 Cluster 1: 1-1 vs 1-2",
    group_order=["1-1", "1-2"]
)

# ── 3-3. Within Stage 1 Cluster 2: 2-1 vs 2-2 ────────────────────────────────
a3 = run_assumption_checks(
    df_stage1_2, "cluster_final_hier", FINAL_TACTICAL_VARS,
    "Within Stage 1 Cluster 2: 2-1 vs 2-2",
    group_order=["2-1", "2-2"]
)

# ── 합본 및 출력 ──────────────────────────────────────────────────────────────
assumption_results = pd.concat([a1, a2, a3], ignore_index=True)

disp = assumption_results.copy()
disp["min_shapiro_p"] = disp["min_shapiro_p"].apply(
    lambda x: "< .001" if x < 0.001 else f"{x:.4f}")
disp["levene_p"] = disp["levene_p"].apply(
    lambda x: "< .001" if x < 0.001 else f"{x:.4f}")
display(disp)

assumption_results.to_csv(
    OUT_TABLE_DIR / "rq2_assumption_checks_three_binary_comparisons.csv",
    index=False, encoding="utf-8-sig"
)

# ── 요약 ─────────────────────────────────────────────────────────────────────
n_total = len(assumption_results)
n_mw    = (assumption_results["recommended_test"] == "Mann-Whitney U test").sum()

print(f"\nTotal checks: {n_total}  |  Mann-Whitney recommended: {n_mw}/{n_total}")

summary_df = (assumption_results
              .groupby("comparison")["recommended_test"]
              .value_counts().unstack(fill_value=0))
print("\n[Assumption Check Summary by Comparison]")
display(summary_df)

if n_mw == n_total:
    print("\n→ 최종 결정: 모든 비교에 Mann-Whitney U 검정 적용")
else:
    print("\n→ 최종 결정: 해석 일관성을 위해 Mann-Whitney U 검정으로 통일")

print("\nSaved: rq2_assumption_checks_three_binary_comparisons.csv")

# %% [markdown] Notebook cell 12
# ## RQ2 STEP 4. Mann-Whitney U 검정을 통한 전술 지표 차이 분석

# %% [code] Notebook cell 13
# ════════════════════════════════════════════════════════════
# [RQ2 STEP 4] Helper 함수 정의
# ════════════════════════════════════════════════════════════
from scipy.stats import mannwhitneyu
import pandas as pd
import numpy as np

def rank_biserial_correlation(u_stat, n1, n2):
    """랭크-양분상관계수 (효과크기 r)"""
    return 1 - (2 * u_stat) / (n1 * n2)

def run_mann_whitney(data, group_col, group1, group2, variables, label=""):
    """
    두 군집 간 Mann-Whitney U 검정 실행
    Returns: DataFrame (variable, median_group_1, median_group_2, U_statistic, p_value, rank_biserial_r)
    """
    g1 = data[data[group_col] == group1]
    g2 = data[data[group_col] == group2]
    
    results = []
    for var in variables:
        x1 = g1[var].dropna().values
        x2 = g2[var].dropna().values
        
        u_stat, p_val = mannwhitneyu(x1, x2, alternative="two-sided")
        r = rank_biserial_correlation(u_stat, len(x1), len(x2))
        
        results.append({
            "comparison": label,
            "variable": var,
            "n_group1": len(x1),
            "n_group2": len(x2),
            "median_group_1": float(np.median(x1)),
            "median_group_2": float(np.median(x2)),
            "U_statistic": u_stat,
            "p_value": p_val,
            "rank_biserial_r": r
        })
    
    return pd.DataFrame(results)

# %% [code] Notebook cell 14
 # ════════════════════════════════════════════════════════════
# [RQ2 STEP 4] Mann-Whitney U Test: Three Binary Comparisons (최종 명칭 반영)
# ════════════════════════════════════════════════════════════

from scipy.stats import mannwhitneyu
import pandas as pd
import numpy as np

print("=" * 80)
print("[RQ2 STEP 4] Mann-Whitney U Test (APA Style)")
print("=" * 80)

# ── 1. 논문용 명칭 매핑 (데이터프레임 출력 및 변수명 변환) ──────────
# 그룹 라벨 매핑 (디스플레이용)
group_label_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
    0: "Cluster 1 (능동적 점유형)",
    1: "Cluster 2 (수비적 직접형)"
}

# ── 2. Helper 함수 (로직 유지) ─────────────────────────────────────────
# (rank_biserial_correlation, interpret_rbc, run_mann_whitney 함수는 기존과 동일)
# [중략: 기존 코드와 동일한 helper 함수들을 사용하십시오]

# ── 3. 논문용 요약 출력 함수 (명칭 매핑 반영) ─────────────────────────
def display_summary(df, group1_key, group2_key):
    d = df.copy()
    var_ko = {
        "possession": "점유율 (Possession)", "passes": "패스 (Passes)", 
        "long_balls": "롱볼 (Long balls)", "final_third_entries": "상대 진영 1/3 투입 (Final third entries)", 
        "goalkeeping_goal_kicks": "골킥 (Goal kicks)", "ppda_val": "전방 압박 강도 (PPDA)", 
        "DEEP": "위험 지역 진입 패스 (DEEP)", "crosses": "크로스 (Crosses)", 
        "dribbles": "드리블 (Dribbles)", "box_shots": "박스 내 슈팅 (Box shots)", 
        "shots": "슈팅 (Shots)", "tackles": "태클 (Tackles)", 
        "interceptions": "인터셉트 (Interceptions)", "clearances": "클리어링 (Clearances)"
    }
    d["변수"] = d["variable"].map(lambda x: var_ko.get(x, x))
    
    # APA 스타일 포맷팅
    d["Mdn_1"] = d["median_group_1"].apply(lambda x: f"{x:.2f}")
    d["Mdn_2"] = d["median_group_2"].apply(lambda x: f"{x:.2f}")
    d["U"] = d["U_statistic"].apply(lambda x: f"{x:,.1f}")
    
    def format_p(p):
        if p < 0.001: return "< .001*"
        elif p < 0.05: return f"{p:.3f}*".replace("0.", ".")
        else: return f"{p:.3f}".replace("0.", ".")
    d["p"] = d["p_value"].apply(format_p)
    d["r"] = d["rank_biserial_r"].apply(lambda x: f"{x:.3f}".replace("0.", ".").replace("-0.", "-."))
    
    # 라벨링 매핑
    label1 = group_label_map.get(group1_key, str(group1_key))
    label2 = group_label_map.get(group2_key, str(group2_key))
    
    summary = d[["변수", "Mdn_1", "Mdn_2", "U", "p", "r"]].copy()
    summary.columns = ["변수", f"Mdn ({label1})", f"Mdn ({label2})", "U", "p", "r"]
    
    display(summary.style.hide(axis="index"))

# ── 4. 분석 실행 및 출력 ──────────────────────────────────────────────

# 4-1. Stage 1 비교
mw_stage1 = run_mann_whitney(df_rq2, "cluster_stage1", 0, 1, FINAL_TACTICAL_VARS, "Stage 1")
print("\n[4-1] 능동적 점유형 vs 수비적 직접형")
display_summary(mw_stage1, 0, 1)

# 4-2. Cluster 1 세부 비교 (1-1 vs 1-2)
mw_stage1_1 = run_mann_whitney(df_stage1_1, "cluster_final_hier", "1-1", "1-2", FINAL_TACTICAL_VARS, "C1_Sub")
print("\n[4-2] 점유 전개형 vs 고점유 지배형")
display_summary(mw_stage1_1, "1-1", "1-2")

# 4-3. Cluster 2 세부 비교 (2-1 vs 2-2)
mw_stage1_2 = run_mann_whitney(df_stage1_2, "cluster_final_hier", "2-1", "2-2", FINAL_TACTICAL_VARS, "C2_Sub")
print("\n[4-3] 저점유 수비형 vs 수비적 전개형")
display_summary(mw_stage1_2, "2-1", "2-2")

# 5. 합본 저장
mw_results = pd.concat([mw_stage1, mw_stage1_1, mw_stage1_2], ignore_index=True)
mw_results.to_csv(OUT_TABLE_DIR / "rq2_mann_whitney_results.csv", index=False, encoding="utf-8-sig")

# %% [markdown] Notebook cell 15
# ## z 값 환산한 코드

# %% [code] Notebook cell 16
 # ════════════════════════════════════════════════════════════
# [RQ2 STEP 4] Helper 함수 정의
# ════════════════════════════════════════════════════════════
from scipy.stats import mannwhitneyu
import pandas as pd
import numpy as np

def rank_biserial_correlation(u_stat, n1, n2):
    return (2 * u_stat) / (n1 * n2) - 1  # 부호 수정

def u_to_z(u_stat, n1, n2):
    mean_u = (n1 * n2) / 2
    std_u = np.sqrt((n1 * n2 * (n1 + n2 + 1)) / 12)
    return (u_stat - mean_u) / std_u

def run_mann_whitney(data, group_col, group1, group2, variables, label=""):
    g1 = data[data[group_col] == group1]
    g2 = data[data[group_col] == group2]
    results = []
    for var in variables:
        x1 = g1[var].dropna().values
        x2 = g2[var].dropna().values
        u_stat, p_val = mannwhitneyu(x1, x2, alternative="two-sided")
        r = rank_biserial_correlation(u_stat, len(x1), len(x2))
        z = u_to_z(u_stat, len(x1), len(x2))
        results.append({
            "comparison": label,
            "variable": var,
            "n_group1": len(x1),
            "n_group2": len(x2),
            "median_group_1": float(np.median(x1)),
            "median_group_2": float(np.median(x2)),
            "U_statistic": u_stat,
            "Z_statistic": z,
            "p_value": p_val,
            "rank_biserial_r": r
        })
    return pd.DataFrame(results)


# ════════════════════════════════════════════════════════════
# [RQ2 STEP 4] Mann-Whitney U Test: Three Binary Comparisons
# ════════════════════════════════════════════════════════════
print("=" * 80)
print("[RQ2 STEP 4] Mann-Whitney U Test (APA Style)")
print("=" * 80)

group_label_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
    0: "Cluster 1 (능동적 점유형)",
    1: "Cluster 2 (수비적 직접형)"
}

def display_summary(df, group1_key, group2_key):
    d = df.copy()
    var_ko = {
        "possession": "점유율 (Possession)", "passes": "패스 (Passes)",
        "long_balls": "롱볼 (Long balls)", "final_third_entries": "상대 진영 1/3 투입 (Final third entries)",
        "goalkeeping_goal_kicks": "골킥 (Goal kicks)", "ppda_val": "전방 압박 강도 (PPDA)",
        "DEEP": "위험 지역 진입 패스 (DEEP)", "crosses": "크로스 (Crosses)",
        "dribbles": "드리블 (Dribbles)", "box_shots": "박스 내 슈팅 (Box shots)",
        "shots": "슈팅 (Shots)", "tackles": "태클 (Tackles)",
        "interceptions": "인터셉트 (Interceptions)", "clearances": "클리어링 (Clearances)"
    }
    d["변수"] = d["variable"].map(lambda x: var_ko.get(x, x))
    d["Mdn_1"] = d["median_group_1"].apply(lambda x: f"{x:.2f}")
    d["Mdn_2"] = d["median_group_2"].apply(lambda x: f"{x:.2f}")
    d["Z"] = d["Z_statistic"].apply(lambda x: f"{x:.2f}")

    def format_p(p):
        if p < 0.001: return "< .001*"
        elif p < 0.05: return f"{p:.3f}*".replace("0.", ".")
        else: return f"{p:.3f}".replace("0.", ".")

    d["p"] = d["p_value"].apply(format_p)
    d["r"] = d["rank_biserial_r"].apply(lambda x: f"{x:.3f}".replace("0.", ".").replace("-0.", "-."))

    label1 = group_label_map.get(group1_key, str(group1_key))
    label2 = group_label_map.get(group2_key, str(group2_key))

    summary = d[["변수", "Mdn_1", "Mdn_2", "Z", "p", "r"]].copy()
    summary.columns = ["변수", f"Mdn ({label1})", f"Mdn ({label2})", "Z", "p", "r"]
    display(summary.style.hide(axis="index"))

# ── 4-1. Stage 1 비교 ────────────────────────────────────────────────
mw_stage1 = run_mann_whitney(df_rq2, "cluster_stage1", 0, 1, FINAL_TACTICAL_VARS, "Stage 1")
print("\n[4-1] 능동적 점유형 vs 수비적 직접형")
display_summary(mw_stage1, 0, 1)

# ── 4-2. Cluster 1 세부 비교 (1-1 vs 1-2) ───────────────────────────
mw_stage1_1 = run_mann_whitney(df_stage1_1, "cluster_final_hier", "1-1", "1-2", FINAL_TACTICAL_VARS, "C1_Sub")
print("\n[4-2] 점유 전개형 vs 고점유 지배형")
display_summary(mw_stage1_1, "1-1", "1-2")

# ── 4-3. Cluster 2 세부 비교 (2-1 vs 2-2) ───────────────────────────
mw_stage1_2 = run_mann_whitney(df_stage1_2, "cluster_final_hier", "2-1", "2-2", FINAL_TACTICAL_VARS, "C2_Sub")
print("\n[4-3] 저점유 수비형 vs 수비적 전개형")
display_summary(mw_stage1_2, "2-1", "2-2")

# ── 5. 합본 저장 ─────────────────────────────────────────────────────
mw_results = pd.concat([mw_stage1, mw_stage1_1, mw_stage1_2], ignore_index=True)
mw_results.to_csv(OUT_TABLE_DIR / "rq2_mann_whitney_results.csv", index=False, encoding="utf-8-sig")
print("\n저장 완료.")

# %% [code] Notebook cell 17
 # ════════════════════════════════════════════════════════════
# [RQ2 STEP 2 & 4] Helper 함수 정의 + 통합표 생성
# ════════════════════════════════════════════════════════════
from scipy.stats import mannwhitneyu
import pandas as pd
import numpy as np

var_ko = {
    "possession": "점유율 (Possession)",
    "passes": "패스 (Passes)",
    "long_balls": "롱볼 (Long balls)",
    "final_third_entries": "상대 진영 1/3 투입 (Final third entries)",
    "goalkeeping_goal_kicks": "골킥 (Goal kicks)",
    "ppda_val": "전방 압박 강도 (PPDA)",
    "DEEP": "위험 지역 진입 패스 (DEEP)",
    "crosses": "크로스 (Crosses)",
    "dribbles": "드리블 (Dribbles)",
    "box_shots": "박스 내 슈팅 (Box shots)",
    "shots": "슈팅 (Shots)",
    "tackles": "태클 (Tackles)",
    "interceptions": "인터셉트 (Interceptions)",
    "clearances": "클리어링 (Clearances)"
}

group_label_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
    0: "군집 1",
    1: "군집 2"
}

def rank_biserial_correlation(u_stat, n1, n2):
    return (2 * u_stat) / (n1 * n2) - 1

def run_mann_whitney(data, group_col, group1, group2, variables, label=""):
    g1 = data[data[group_col] == group1]
    g2 = data[data[group_col] == group2]
    results = []
    for var in variables:
        x1 = g1[var].dropna().values
        x2 = g2[var].dropna().values
        u_stat, p_val = mannwhitneyu(x1, x2, alternative="two-sided")
        r = rank_biserial_correlation(u_stat, len(x1), len(x2))
        results.append({
            "comparison": label,
            "variable": var,
            "n_group1": len(x1),
            "n_group2": len(x2),
            "mean_group_1": float(np.mean(x1)),
            "std_group_1": float(np.std(x1, ddof=1)),
            "mean_group_2": float(np.mean(x2)),
            "std_group_2": float(np.std(x2, ddof=1)),
            "U_statistic": u_stat,
            "p_value": p_val,
            "rank_biserial_r": r
        })
    return pd.DataFrame(results)

def display_combined(df, group1_key, group2_key):
    """M±SD + U + p + r 통합표"""
    d = df.copy()
    d["변수"] = d["variable"].map(lambda x: var_ko.get(x, x))

    label1 = group_label_map.get(group1_key, str(group1_key))
    label2 = group_label_map.get(group2_key, str(group2_key))

    d[f"M±SD ({label1})"] = (
        d["mean_group_1"].apply(lambda x: f"{x:.2f}") + " ± " +
        d["std_group_1"].apply(lambda x: f"{x:.2f}")
    )
    d[f"M±SD ({label2})"] = (
        d["mean_group_2"].apply(lambda x: f"{x:.2f}") + " ± " +
        d["std_group_2"].apply(lambda x: f"{x:.2f}")
    )

    d["U"] = d["U_statistic"].apply(lambda x: f"{x:,.1f}")

    def format_p(p):
        if p < 0.001: return "< .001*"
        elif p < 0.05: return f"{p:.3f}*".replace("0.", ".")
        else: return f"{p:.3f}".replace("0.", ".")

    d["p"] = d["p_value"].apply(format_p)
    d["r"] = d["rank_biserial_r"].apply(
        lambda x: f"{x:.2f}".replace("0.", ".").replace("-0.", "-.")
    )

    cols = [
        "변수",
        f"M±SD ({label1})",
        f"M±SD ({label2})",
        "U", "p", "r"
    ]
    display(d[cols].style.hide(axis="index"))
    return d[cols]


# ════════════════════════════════════════════════════════════
# 실행
# ════════════════════════════════════════════════════════════
print("=" * 80)
print("[RQ2] 기술통계 + Mann-Whitney 통합표")
print("=" * 80)

# ── Stage 1 비교 ─────────────────────────────────────────────────────
mw_stage1 = run_mann_whitney(
    df_rq2, "cluster_stage1", 0, 1, FINAL_TACTICAL_VARS, "Stage 1"
)
print("\n[Stage 1] 군집 1 vs 군집 2")
tbl_stage1 = display_combined(mw_stage1, 0, 1)
tbl_stage1.to_csv(OUT_TABLE_DIR / "rq2_combined_stage1.csv", index=False, encoding="utf-8-sig")

# ── Cluster 1 세부 비교 (1-1 vs 1-2) ────────────────────────────────
df_stage1_1 = df_rq2[df_rq2["cluster_stage1"] == 0].copy()
mw_stage1_1 = run_mann_whitney(
    df_stage1_1, "cluster_final_hier", "1-1", "1-2", FINAL_TACTICAL_VARS, "C1_Sub"
)
print("\n[세부] 점유 전개형(1-1) vs 고점유 지배형(1-2)")
tbl_11_12 = display_combined(mw_stage1_1, "1-1", "1-2")
tbl_11_12.to_csv(OUT_TABLE_DIR / "rq2_combined_1-1_vs_1-2.csv", index=False, encoding="utf-8-sig")

# ── Cluster 2 세부 비교 (2-1 vs 2-2) ────────────────────────────────
df_stage1_2 = df_rq2[df_rq2["cluster_stage1"] == 1].copy()
mw_stage1_2 = run_mann_whitney(
    df_stage1_2, "cluster_final_hier", "2-1", "2-2", FINAL_TACTICAL_VARS, "C2_Sub"
)
print("\n[세부] 저점유 수비형(2-1) vs 수비적 전개형(2-2)")
tbl_21_22 = display_combined(mw_stage1_2, "2-1", "2-2")
tbl_21_22.to_csv(OUT_TABLE_DIR / "rq2_combined_2-1_vs_2-2.csv", index=False, encoding="utf-8-sig")

# ── 합본 저장 ─────────────────────────────────────────────────────────
mw_results = pd.concat([mw_stage1, mw_stage1_1, mw_stage1_2], ignore_index=True)
mw_results.to_csv(OUT_TABLE_DIR / "rq2_mann_whitney_results.csv", index=False, encoding="utf-8-sig")
print("\n✅ 저장 완료.")

# %% [markdown] Notebook cell 18
# ## RQ2 STEP 5. XGBoost 기반 이진 군집 구분 설명모형 구축 

# %% [code] Notebook cell 19
# ════════════════════════════════════════════════════════════
# [RQ2 STEP 5] Tree-Based Model Comparison
# - train/test 7:3 분할
# - 훈련 성능: 5-fold CV (Mean ± SD)
# - 테스트 성능: held-out test set
# - 4개 모형 비교 후 test F1 기준 최적 모형 선택
# ════════════════════════════════════════════════════════════

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd

print("=" * 80)
print("[RQ2 STEP 5] Tree-Based Model Comparison (7:3 split + 5-fold CV)")
print("=" * 80)

TEST_SIZE    = 0.3
RANDOM_STATE = 42
N_FOLDS      = 5

# ── 4개 모형 정의 ─────────────────────────────────────────────────────────────
def get_models():
    return {
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5, random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=300, learning_rate=0.05,
            max_depth=4, random_state=RANDOM_STATE
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300, learning_rate=0.05,
            max_depth=4, subsample=0.9, colsample_bytree=0.9,
            objective="binary:logistic", eval_metric="logloss",
            random_state=RANDOM_STATE, n_jobs=-1
        ),
    }

# ── Helper ───────────────────────────────────────────────────────────────────
def compare_models_cv(data, features, target_col, target_order,
                      comparison_name):
    df_t   = data[data[target_col].isin(target_order)].copy()
    X      = df_t[features].copy()
    y_orig = df_t[target_col].copy()
    lmap   = {target_order[0]: 0, target_order[1]: 1}
    y_enc  = y_orig.map(lmap).astype(int)

    # train/test 7:3 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=TEST_SIZE,
        random_state=RANDOM_STATE, stratify=y_enc
    )

    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True,
                         random_state=RANDOM_STATE)

    results      = []
    fitted_models = {}

    for model_name, model in get_models().items():

        # ── 5-fold CV (훈련 데이터 기준) ──────────────────────────────────────
        cv_acc = cross_val_score(model, X_train, y_train,
                                 cv=cv, scoring="accuracy", n_jobs=-1)
        cv_f1  = cross_val_score(model, X_train, y_train,
                                 cv=cv, scoring="f1_macro", n_jobs=-1)

        # ── 최종 훈련 & 테스트 평가 ───────────────────────────────────────────
        model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred_test)
        test_f1  = f1_score(y_test, y_pred_test, average="macro")

        results.append({
            "comparison":     comparison_name,
            "model":          model_name,
            "CV_acc (M±SD)":  f"{cv_acc.mean():.4f} ± {cv_acc.std():.4f}",
            "CV_f1 (M±SD)":   f"{cv_f1.mean():.4f} ± {cv_f1.std():.4f}",
            "test_acc":       round(test_acc, 4),
            "test_f1":        round(test_f1, 4),
            # 내부 저장용
            "_cv_f1_mean":    cv_f1.mean(),
            "_test_f1":       test_f1,
        })

        fitted_models[model_name] = {
            "model":           model,
            "X_train":         X_train,
            "X_test":          X_test,
            "y_train":         y_train,
            "y_test":          y_test,
            "X_full":          X,
            "y_full":          y_enc,
            "label_to_num":    lmap,
            "num_to_label":    {0: target_order[0], 1: target_order[1]},
            "comparison_name": comparison_name
        }

    result_df = pd.DataFrame(results)

    # test_f1 기준 최적 모형 선택
    best_model_name = result_df.loc[
        result_df["_test_f1"].idxmax(), "model"
    ]
    result_df["selected"] = result_df["model"].apply(
        lambda x: "★ Best" if x == best_model_name else ""
    )

    # 출력 (내부 계산 컬럼 제외)
    display_cols = ["model", "CV_acc (M±SD)", "CV_f1 (M±SD)",
                    "test_acc", "test_f1", "selected"]

    print(f"\n{'─'*70}")
    print(f"[비교] {comparison_name}")
    print(f"  n_train: {len(X_train):,}  |  n_test: {len(X_test):,}")
    print(f"{'─'*70}")
    display(result_df[display_cols])
    print(f"  → 최적 모형: {best_model_name}")

    return result_df[display_cols + ["_test_f1"]], fitted_models, best_model_name


# ── 서브셋 준비 (변수명 1과 2로 교체) ─────────────────────────────────────────
df_stage1_1 = df_rq2[df_rq2["cluster_stage1"] == 0].copy()
df_stage1_2 = df_rq2[df_rq2["cluster_stage1"] == 1].copy()

# ── 5-1. 1차 전술 유형: Cluster 1 vs Cluster 2 ───────────────────────────────
result_s1, fitted_s1, best_s1 = compare_models_cv(
    df_rq2, FINAL_TACTICAL_VARS, "cluster_stage1", [0, 1],
    "1차 전술 유형: Cluster 1 vs Cluster 2"
)

# ── 5-2. 세부 전술 유형: 1-1 vs 1-2 ─────────────────────────────────────────
result_11_12, fitted_11_12, best_11_12 = compare_models_cv(
    df_stage1_1, FINAL_TACTICAL_VARS, "cluster_final_hier", ["1-1", "1-2"],
    "세부 전술 유형: 1-1 (능동 압박형) vs 1-2 (지배형)"
)

# ── 5-3. 세부 전술 유형: 2-1 vs 2-2 ─────────────────────────────────────────
result_21_22, fitted_21_22, best_21_22 = compare_models_cv(
    df_stage1_2, FINAL_TACTICAL_VARS, "cluster_final_hier", ["2-1", "2-2"],
    "세부 전술 유형: 2-1 (수비 블록형) vs 2-2 (직접 전개형)"
)

# ── 종합 저장 ─────────────────────────────────────────────────────────────────
model_summary = pd.concat(
    [result_s1, result_11_12, result_21_22],
    ignore_index=True
).drop(columns=["_test_f1"])

model_summary.to_csv(
    OUT_TABLE_DIR / "rq2_model_comparison_cv_summary.csv",
    index=False, encoding="utf-8-sig"
)

print("\n" + "=" * 80)
print("[STEP 5 최종 선택 모형 요약]")
print("=" * 80)
print(f"  1차 전술 유형 (Cluster 1 vs 2) : {best_s1}")
print(f"  세부 전술 유형 (1-1 vs 1-2)    : {best_11_12}")
print(f"  세부 전술 유형 (2-1 vs 2-2)    : {best_21_22}")
print("\nSaved: rq2_model_comparison_cv_summary.csv") 

# %% [markdown] Notebook cell 20
# # STEP 6 — XGBoost-SHAP 기반 전술 유형 구분 핵심 지표 해석

# %% [code] Notebook cell 21
 # ─────────────────────────────────────────────────────────────────
# [STEP 6 사전 준비] 커널 재시작 후 변수 복구
# ─────────────────────────────────────────────────────────────────
from pathlib import Path
import pandas as pd
import numpy as np

RANDOM_STATE = 42

# ── 경로 (노트북과 동일한 로직) ────────────────────────────────────
CURRENT_DIR   = Path.cwd()
PROJECT_ROOT  = CURRENT_DIR.parent if CURRENT_DIR.name == "notebooks" else CURRENT_DIR
OUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
OUT_FIG_DIR   = PROJECT_ROOT / "outputs" / "figures"

# ── 상수 ────────────────────────────────────────────────────────────
FINAL_TACTICAL_VARS = [
    "possession", "passes", "long_balls", "final_third_entries",
    "goalkeeping_goal_kicks", "ppda_val", "DEEP",
    "crosses", "dribbles", "box_shots", "shots",
    "tackles", "interceptions", "clearances",
]

# [수정] 1-1, 1-2, 2-1, 2-2 체계 반영
FINAL_CLUSTER_ORDER = ["1-1", "1-2", "2-1", "2-2"]

FINAL_CLUSTER_NAME_MAP = {
    "1-1": "1-1 능동 압박형",
    "1-2": "1-2 지배형",
    "2-1": "2-1 수비 블록형",
    "2-2": "2-2 직접 전개형",
}

# ── 데이터 로드 ── 파일명: 14vars, 컬럼: cluster_final_hier ─────────
DATA_PATH = OUT_TABLE_DIR / "rq1_final_data_14vars_hierarchical_4clusters.csv"
df_model  = pd.read_csv(DATA_PATH)

# cluster_label_str 컬럼 통일 (STEP 6 코드가 이 이름을 사용)
df_model["cluster_label_str"] = df_model["cluster_final_hier"]

# ── 검증 ────────────────────────────────────────────────────────────
missing = [v for v in FINAL_TACTICAL_VARS if v not in df_model.columns]
print(f"✅ df_model 로드 완료  |  shape: {df_model.shape}")
print(f"   FINAL_TACTICAL_VARS 누락: {missing if missing else '없음'}")
print(f"   cluster 분포:")
print(df_model["cluster_label_str"].value_counts()[FINAL_CLUSTER_ORDER])

# %% [code] Notebook cell 22
 # ─────────────────────────────────────────────────────────────────
# STEP 6-A | Stage 1 SHAP — 큰 군집 1 / 2 핵심 지표
#   STEP 5 선정 모델(XGBoost) 재사용
# ─────────────────────────────────────────────────────────────────

import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FIG_DIR_S6A = OUT_FIG_DIR  / "step6a_stage1_shap"
TBL_DIR_S6A = OUT_TABLE_DIR / "step6a_stage1_shap"
FIG_DIR_S6A.mkdir(parents=True, exist_ok=True)
TBL_DIR_S6A.mkdir(parents=True, exist_ok=True)

# ── 0. 논문용 한글 변수명 매핑 (PPDA, DEEP 학술 명칭 반영) ───────────
var_ko = {
    "possession": "점유율 (Possession)", 
    "passes": "패스 (Passes)", 
    "long_balls": "롱볼 (Long balls)", 
    "final_third_entries": "상대 진영 1/3 투입 (Final third entries)", 
    "goalkeeping_goal_kicks": "골킥 (Goal kicks)", 
    "ppda_val": "전방 압박 강도 (PPDA)", 
    "DEEP": "위험 지역 진입 패스 (DEEP)", 
    "crosses": "크로스 (Crosses)", 
    "dribbles": "드리블 (Dribbles)", 
    "box_shots": "박스 내 슈팅 (Box shots)", 
    "shots": "슈팅 (Shots)",
    "tackles": "태클 (Tackles)", 
    "interceptions": "인터셉트 (Interceptions)", 
    "clearances": "클리어링 (Clearances)"
}
translated_features = [var_ko.get(f, f) for f in FINAL_TACTICAL_VARS]

# ── 1. STEP 5 저장 객체에서 꺼내기 ───────────────────────────────
s1_bundle = fitted_s1[best_s1]
model_s1  = s1_bundle["model"]
X_s1_full = s1_bundle["X_full"]
y_s1_full = s1_bundle["y_full"]

n1_count = (y_s1_full == 0).sum()
n2_count = (y_s1_full == 1).sum()
print(f"Stage 1 분포 — Cluster 1: {n1_count:,}  |  Cluster 2: {n2_count:,}")

# ── 2. SHAP 계산 ──────────────────────────────────────────────────
print("\nSHAP 계산 중...")
explainer_s1 = shap.TreeExplainer(model_s1)
shap_s1      = explainer_s1.shap_values(X_s1_full)

mask_c1 = (y_s1_full == 0).values
mask_c2 = (y_s1_full == 1).values

sv_c1 = -shap_s1[mask_c1]  # 기존 Cluster 0
sv_c2 =  shap_s1[mask_c2]  # 기존 Cluster 1

X_c1 = X_s1_full[mask_c1].reset_index(drop=True)
X_c2 = X_s1_full[mask_c2].reset_index(drop=True)

# ── 3. 군집별 Bar + Beeswarm ──────────────────────────────────────
for sv_g, X_g, grp_name, n_g, fname_key in [
    (sv_c1, X_c1, "Stage 1 Cluster 1 (능동·지배 계열)", n1_count, "s1_c1"),
    (sv_c2, X_c2, "Stage 1 Cluster 2 (수비·직접 계열)", n2_count, "s1_c2"),
]:
    mean_abs = np.abs(sv_g).mean(axis=0)
    imp_df = (
        pd.DataFrame({"Feature": translated_features, "Mean_AbsSHAP": mean_abs})
        .sort_values("Mean_AbsSHAP", ascending=False)
        .reset_index(drop=True)
    )
    imp_df["Rank"] = imp_df.index + 1
    imp_df.to_csv(TBL_DIR_S6A / f"shap_importance_{fname_key}.csv", index=False, encoding="utf-8-sig")

    print(f"\n{'─'*58}\n  {grp_name}  (n={n_g:,})\n{'─'*58}")
    print(imp_df[["Rank","Feature","Mean_AbsSHAP"]].head(8).to_string(index=False))

    # Bar chart
    fig, ax = plt.subplots(figsize=(7, 4.5))
    top10 = imp_df.head(10)
    ax.barh(top10["Feature"][::-1], top10["Mean_AbsSHAP"][::-1], color="#2ca02c", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Mean |SHAP value|", fontsize=11)
    ax.set_title(f"{grp_name} (n={n_g:,})\n군집 분류 기여 지표 — Mean |SHAP|", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIG_DIR_S6A / f"shap_bar_{fname_key}.png", dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)

    # Beeswarm
    shap.summary_plot(sv_g, X_g, feature_names=translated_features, plot_type="dot", show=False, plot_size=(8, 5))
    plt.title(f"{grp_name} — SHAP Beeswarm\n빨강=지표값↑  파랑=지표값↓  |  SHAP>0=해당 군집으로 기여", fontsize=9)
    plt.tight_layout()
    plt.savefig(FIG_DIR_S6A / f"shap_beeswarm_{fname_key}.png", dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()

# ── Stage 1: 단일 통합 beeswarm ─────────────────────────
explainer_s1 = shap.TreeExplainer(model_s1)
shap_s1      = explainer_s1.shap_values(X_s1_full)

fig, ax = plt.subplots(figsize=(9, 6))
shap.summary_plot(
    shap_s1, X_s1_full, feature_names=translated_features, show=False, plot_size=None,
)
ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xlabel("SHAP value\n(← 군집 1 방향     군집 2 방향 →)", fontsize=10)
ax.set_title("Stage 1: 군집 1 vs 군집 2\nSHAP Feature Importance", fontsize=12)
plt.tight_layout()
plt.savefig(OUT_FIG_DIR / "shap_s1_unified_beeswarm.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [code] Notebook cell 23
 # ─────────────────────────────────────────────────────────────────
# STEP 6-B | 세부 군집 SHAP  ─ 통합 beeswarm (비교쌍당 1장)
#   Stage 1 방식과 동일: 마스킹/부호반전 없이 raw SHAP 그대로 사용
#   양수 → 오른쪽 군집 방향 / 음수 → 왼쪽 군집 방향
# ─────────────────────────────────────────────────────────────────
import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FIG_DIR_S6B = OUT_FIG_DIR  / "step6b_subcluster_shap"
TBL_DIR_S6B = OUT_TABLE_DIR / "step6b_subcluster_shap"
FIG_DIR_S6B.mkdir(parents=True, exist_ok=True)
TBL_DIR_S6B.mkdir(parents=True, exist_ok=True)

# ── 0. 논문용 한글 변수명 매핑 (PPDA, DEEP 학술 명칭 반영) ───────────
var_ko = {
    "possession": "점유율 (Possession)", 
    "passes": "패스 (Passes)", 
    "long_balls": "롱볼 (Long balls)", 
    "final_third_entries": "상대 진영 1/3 투입 (Final third entries)", 
    "goalkeeping_goal_kicks": "골킥 (Goal kicks)", 
    "ppda_val": "전방 압박 강도 (PPDA)", 
    "DEEP": "위험 지역 진입 패스 (DEEP)", 
    "crosses": "크로스 (Crosses)", 
    "dribbles": "드리블 (Dribbles)", 
    "box_shots": "박스 내 슈팅 (Box shots)", 
    "shots": "슈팅 (Shots)",
    "tackles": "태클 (Tackles)", 
    "interceptions": "인터셉트 (Interceptions)", 
    "clearances": "클리어링 (Clearances)"
}
translated_features = [var_ko.get(f, f) for f in FINAL_TACTICAL_VARS]

# ══════════════════════════════════════════════════════════════════
# SHAP 계산 (마스킹 없이 전체 샘플) - 변수명 11_12, 21_22로 수정
# ══════════════════════════════════════════════════════════════════
bundle_11_12 = fitted_11_12[best_11_12]
model_11_12  = bundle_11_12["model"]
X_11_12      = bundle_11_12["X_full"]   # 전체 샘플

bundle_21_22 = fitted_21_22[best_21_22]
model_21_22  = bundle_21_22["model"]
X_21_22      = bundle_21_22["X_full"]   # 전체 샘플

print("SHAP 계산 중 (1-1 vs 1-2)...")
shap_11_12 = shap.TreeExplainer(model_11_12).shap_values(X_11_12)

print("SHAP 계산 중 (2-1 vs 2-2)...")
shap_21_22 = shap.TreeExplainer(model_21_22).shap_values(X_21_22)

# ══════════════════════════════════════════════════════════════════
# 공통 시각화 함수
# ══════════════════════════════════════════════════════════════════
def plot_unified_shap(shap_vals, X_full, label_a, label_b, fname_key):
    """
    label_a = 0 클래스 군집명 (← 방향)
    label_b = 1 클래스 군집명 (→ 방향)
    """
    n_total = len(X_full)

    # ── ① Mean |SHAP| Bar chart ───────────────────────────
    mean_abs = np.abs(shap_vals).mean(axis=0)
    imp_df = (
        pd.DataFrame({"Feature": translated_features,  # 한글 변수명 적용
                      "Mean_AbsSHAP": mean_abs})
        .sort_values("Mean_AbsSHAP", ascending=False)
        .reset_index(drop=True)
    )
    imp_df["Rank"] = imp_df.index + 1
    imp_df.to_csv(TBL_DIR_S6B / f"shap_importance_{fname_key}.csv",
                  index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    top10 = imp_df.head(10)
    ax.barh(top10["Feature"][::-1], top10["Mean_AbsSHAP"][::-1],
            color="#4C72B0", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Mean |SHAP value|", fontsize=11)
    ax.set_title(f"{label_a} vs {label_b}  (n={n_total:,})\n"
                 f"군집 판별 기여 지표 — Mean |SHAP|", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIG_DIR_S6B / f"shap_bar_{fname_key}.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)

    # ── ② 통합 Beeswarm ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 6))
    shap.summary_plot(
        shap_vals, X_full,
        feature_names=translated_features,  # 한글 변수명 적용
        show=False, plot_size=None
    )
    ax = plt.gca()
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel(
        f"SHAP value\n(← {label_a} 방향     {label_b} 방향 →)",
        fontsize=10
    )
    ax.set_title(
        f"{label_a} vs {label_b}  (n={n_total:,})\nSHAP Feature Importance",
        fontsize=12
    )
    plt.tight_layout()
    plt.savefig(FIG_DIR_S6B / f"shap_beeswarm_{fname_key}.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()

    # ── 콘솔 출력 ─────────────────────────────────────────
    print(f"\n{'─'*55}")
    print(f"  {label_a} vs {label_b}  (n={n_total:,})")
    print(f"{'─'*55}")
    print(imp_df[["Rank", "Feature", "Mean_AbsSHAP"]].head(8).to_string(index=False))

    return imp_df

# ══════════════════════════════════════════════════════════════════
# 실행 (비교쌍당 beeswarm 1장 + bar 1장)
# ══════════════════════════════════════════════════════════════════
imp_11_12 = plot_unified_shap(
    shap_11_12, X_11_12,
    label_a="군집 1-1 (점유 전개형)", label_b="군집 1-2 (고점유 지배형)",
    fname_key="11_12"
)

imp_21_22 = plot_unified_shap(
    shap_21_22, X_21_22,
    label_a="군집 2-1 (저점유 수비형)", label_b="군집 2-2 (수비적 전개형)",
    fname_key="21_22"
)

# ══════════════════════════════════════════════════════════════════
# Top-5 요약표 저장
# ══════════════════════════════════════════════════════════════════
def top5_row(imp_df, label):
    top = imp_df.head(5)["Feature"].tolist()
    return {"비교쌍": label,
            "Top-1": top[0], "Top-2": top[1], "Top-3": top[2],
            "Top-4": top[3], "Top-5": top[4]}

summary_df = pd.DataFrame([
    top5_row(imp_11_12, "1-1 vs 1-2"),
    top5_row(imp_21_22, "2-1 vs 2-2"),
])
summary_df.to_csv(TBL_DIR_S6B / "shap_top5_summary.csv",
                  index=False, encoding="utf-8-sig")

print("\n" + "═"*60)
print("  비교쌍별 SHAP 핵심 지표 Top-5 요약")
print("═"*60)
print(summary_df.to_string(index=False))
print(f"\n✅ STEP 6-B 완료")
print(f"   1-1/1-2 모델: {best_11_12}  |  2-1/2-2 모델: {best_21_22}")
print(f"   그림: {FIG_DIR_S6B}")
print(f"   표  : {TBL_DIR_S6B}")

# %% [code] Notebook cell 24
# Stage 1 SHAP 중요도 저장 (셀 하나로 실행)
import numpy as np
import pandas as pd

# ── 1. 논문용 한글 변수명 매핑 (PPDA, DEEP 학술 명칭 반영) ───────────
var_ko = {
    "possession": "점유율 (Possession)", 
    "passes": "패스 (Passes)", 
    "long_balls": "롱볼 (Long balls)", 
    "final_third_entries": "상대 진영 1/3 투입 (Final third entries)", 
    "goalkeeping_goal_kicks": "골킥 (Goal kicks)", 
    "ppda_val": "전방 압박 강도 (PPDA)", 
    "DEEP": "위험 지역 진입 패스 (DEEP)", 
    "crosses": "크로스 (Crosses)", 
    "dribbles": "드리블 (Dribbles)", 
    "box_shots": "박스 내 슈팅 (Box shots)", 
    "shots": "슈팅 (Shots)",
    "tackles": "태클 (Tackles)", 
    "interceptions": "인터셉트 (Interceptions)", 
    "clearances": "클리어링 (Clearances)"
}
translated_features = [var_ko.get(f, f) for f in FINAL_TACTICAL_VARS]

# ── 2. SHAP 중요도 계산 및 정렬 ──────────────────────────────────────
mean_abs_s1 = np.abs(shap_s1).mean(axis=0)
imp_s1 = (
    pd.DataFrame({"Feature": translated_features, "Mean_AbsSHAP": mean_abs_s1})
    .sort_values("Mean_AbsSHAP", ascending=False)
    .reset_index(drop=True)
)
imp_s1["Rank"] = imp_s1.index + 1

# 가독성을 위해 컬럼 순서 재배치 (Rank를 맨 앞으로)
imp_s1 = imp_s1[["Rank", "Feature", "Mean_AbsSHAP"]]

# ── 3. 파일 저장 (c0_c1 -> c1_c2 이름 변경) ───────────────────────────
save_name = "shap_importance_s1_c1_c2.csv"
imp_s1.to_csv(OUT_TABLE_DIR / save_name, index=False, encoding="utf-8-sig")

# ── 4. 결과 출력 ───────────────────────────────────────────────────────
print("═" * 60)
print(f"✅ Stage 1 (Cluster 1 vs Cluster 2) SHAP 중요도 저장 완료")
print(f"   파일명: {save_name}")
print("═" * 60)
print(imp_s1.to_string(index=False))

# %% [code] Notebook cell 25


