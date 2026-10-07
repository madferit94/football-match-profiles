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
# # 연구내용 3. 전술 유형의 시즌 구간 및 리그별 분포 분석
# 
# - RQ3-1: 시즌별(2019/20~2024/25) 전술 유형 분포 변화
# - RQ3-2: 유럽 5대 리그별 전술 유형 분포 비교

# %% [code] Notebook cell 2
 # ════════════════════════════════════════════════════════════
# [RQ3 STEP 0] 라이브러리 로드 및 데이터 준비 (최종 명칭 반영)
# ════════════════════════════════════════════════════════════
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import seaborn as sns
from scipy.stats import chi2_contingency
from pathlib import Path
import platform
import warnings
warnings.filterwarnings("ignore")

# ── 폰트 설정 ──────────────────────────────────────────────
if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# ── 경로 설정 ──────────────────────────────────────────────
CURRENT_DIR   = Path.cwd()
PROJECT_ROOT  = CURRENT_DIR.parent if CURRENT_DIR.name == "notebooks" else CURRENT_DIR
OUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
OUT_FIG_DIR   = PROJECT_ROOT / "outputs" / "figures"
OUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── 데이터 로드 ─────────────────────────────────────────────
DATA_PATH = OUT_TABLE_DIR / "rq1_final_data_14vars_hierarchical_4clusters.csv"
df_rq3 = pd.read_csv(DATA_PATH)
df_rq3["cluster_final_hier"] = df_rq3["cluster_final_hier"].astype(str)

# ── 공통 상수 (확정된 최종 명칭 및 순서 반영) ───────────────────
HIER_ORDER = ["1-1", "1-2", "2-1", "2-2"]

LABEL_KR = {
    "1-1": "1-1\n점유 전개형",
    "1-2": "1-2\n고점유 지배형",
    "2-1": "2-1\n저점유 수비형",
    "2-2": "2-2\n수비적 전개형",
}

LABEL_KR_FLAT = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

# 능동형(1-1, 1-2)은 푸른색 계열, 수비적 직접형(2-1, 2-2)은 붉은/주황 계열
PALETTE = {
    "1-1": "#2E86AB",
    "1-2": "#003F5C",
    "2-1": "#F39C12",
    "2-2": "#E63946",
}

SEASON_ORDER = [
    "2019_2020", "2020_2021", "2021_2022",
    "2022_2023", "2023_2024", "2024_2025"
]
SEASON_LABEL = {
    "2019_2020": "19/20", "2020_2021": "20/21", "2021_2022": "21/22",
    "2022_2023": "22/23", "2023_2024": "23/24", "2024_2025": "24/25"
}

# ── 검증 ────────────────────────────────────────────────────
print(f"✅ 로드 완료: {df_rq3.shape[0]:,}행 × {df_rq3.shape[1]}열")
# 데이터셋 내에 cluster_final_hier가 우리가 정의한 1-1, 1-2, 2-1, 2-2 값을 가지고 있는지 확인
print(f"군집 분포 확인:\n{df_rq3['cluster_final_hier'].value_counts().reindex(HIER_ORDER)}")

# %% [code] Notebook cell 3
# ════════════════════════════════════════════════════════════
# [RQ3 STEP 0-CHECK] 리그명·시즌명 실제 값 확인
# ════════════════════════════════════════════════════════════
print("▶ season 고유값:", sorted(df_rq3["season"].unique()))
print()
print("▶ league 고유값 및 경기 수:")
print(df_rq3["league"].value_counts().sort_index())
print()
print("▶ cluster_final_hier 분포:")
print(df_rq3["cluster_final_hier"].value_counts().reindex(HIER_ORDER))

# %% [code] Notebook cell 4
 # ════════════════════════════════════════════════════════════
# [RQ3-1] 시즌별 전술 유형 분포 — 카이제곱 독립성 검정 (최종 명칭 반영)
# ════════════════════════════════════════════════════════════
from scipy.stats import chi2_contingency
import numpy as np

print("="*60); print("[RQ3-1] 시즌별 전술 유형 분포 분석"); print("="*60)

# ── 1. 교차표 생성 (시즌 × 군집) ─────────────────────────
df_chi = df_rq3[df_rq3["season"].isin(SEASON_ORDER)].copy()
df_chi["cluster_final_hier"] = df_chi["cluster_final_hier"].astype(str)

ct = pd.crosstab(
    df_chi["season"].map(SEASON_LABEL),   # 행: 시즌 레이블
    df_chi["cluster_final_hier"],         # 열: 군집
)
# 시즌 순서 고정 및 군집 순서 고정 (HIER_ORDER 사용)
ct = ct.reindex([SEASON_LABEL[s] for s in SEASON_ORDER])
ct = ct.reindex(columns=HIER_ORDER)

# ── 2. 행 비율 (%) 및 명칭 매핑 ───────────────────────────
ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

# 출력용 테이블: 컬럼명을 최종 한글 명칭으로 매핑
ct_display = ct.rename(columns=LABEL_KR_FLAT)
ct_pct_display = ct_pct.rename(columns=LABEL_KR_FLAT)

print("[교차표 — 시즌별 군집 경기 수]")
display(ct_display)

print("\n[교차표 — 시즌별 군집 비율 (%)]")
display(ct_pct_display.round(2))

# ── 3. 카이제곱 검정 ──────────────────────────────────────
chi2, p, dof, expected = chi2_contingency(ct)

n = ct.values.sum()
min_dim = min(ct.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))

# 효과 크기 해석
if   cramers_v < 0.10: v_label = "미미 (Negligible)"
elif cramers_v < 0.30: v_label = "소 (Small)"
elif cramers_v < 0.50: v_label = "중 (Medium)"
else:                  v_label = "대 (Large)"

# 기대빈도 5 미만 셀 비율
low_exp_pct = (expected < 5).sum() / expected.size * 100

# ── 4. 결과 요약표 ────────────────────────────────────────
result_df = pd.DataFrame({
    "항목": ["χ²", "자유도 (df)", "p-value", "Cramér's V", "효과 크기 해석", "기대빈도 < 5 셀 비율", "검정 조건 충족 여부"],
    "값": [
        f"{chi2:.3f}",
        f"{dof}",
        f"{p:.4e}" if p < 0.001 else f"{p:.4f}",
        f"{cramers_v:.4f}",
        v_label,
        f"{low_exp_pct:.1f}%",
        "충족" if low_exp_pct <= 20 else "주의 필요 (20% 초과)",
    ]
})

print("\n[카이제곱 독립성 검정 결과 — 시즌 × 전술 유형]")
display(result_df.set_index("항목"))

# ── 5. 저장 ──────────────────────────────────────────────
result_df.to_csv(OUT_TABLE_DIR / "rq3_1_chisq_season_cluster.csv", index=False, encoding="utf-8-sig")
ct_pct.round(2).to_csv(OUT_TABLE_DIR / "rq3_1_crosstab_season_pct.csv", encoding="utf-8-sig")
print("\n✅ 저장 완료: rq3_1_chisq_season_cluster.csv / rq3_1_crosstab_season_pct.csv")

# %% [code] Notebook cell 5
 # ════════════════════════════════════════════════════════════
# [RQ3-1] 리그별 시즌 추세 시각화 (최종 통합본)
# ════════════════════════════════════════════════════════════
import matplotlib.ticker as mticker

# 1. 상수 정의 (누락 방지)
SEASON_ORDER = ["2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024", "2024_2025"]
SEASON_LABEL = {"2019_2020": "19/20", "2020_2021": "20/21", "2021_2022": "21/22",
                "2022_2023": "22/23", "2023_2024": "23/24", "2024_2025": "24/25"}
HIER_ORDER   = ["1-1", "1-2", "2-1", "2-2"]
LEAGUE_ORDER = ["EPL", "LaLiga", "Bundesliga", "SerieA", "Ligue1"]
LEAGUE_LABEL = {"EPL": "EPL", "LaLiga": "LaLiga", "Bundesliga": "Bundesliga",
                "SerieA": "Serie A", "Ligue1": "Ligue 1"}

# 최종 확정된 스타일 (PALETTE 활용)
LINE_STYLE = {
    "1-1": {"color": PALETTE["1-1"], "marker": "o", "ls": "-", "lw": 2.5},
    "1-2": {"color": PALETTE["1-2"], "marker": "s", "ls": "-", "lw": 2.5},
    "2-1": {"color": PALETTE["2-1"], "marker": "^", "ls": "--", "lw": 2.5},
    "2-2": {"color": PALETTE["2-2"], "marker": "D", "ls": "--", "lw": 2.5},
}

# 2. 데이터 준비
season_x = {s: i for i, s in enumerate(SEASON_ORDER)}
df_calc = df_rq3[df_rq3["season"].isin(SEASON_ORDER)].copy()
df_calc["cluster_final_hier"] = df_calc["cluster_final_hier"].astype(str)

league_counts = df_calc.groupby(["league", "season", "cluster_final_hier"], observed=True).size().reset_index(name="n")
league_sum = df_calc.groupby(["league", "season"], observed=True).size().reset_index(name="total")
league_pct = league_counts.merge(league_sum, on=["league", "season"])
league_pct["pct"] = league_pct["n"] / league_pct["total"] * 100

# 3. 리그별 시각화 루프
for league in LEAGUE_ORDER:
    df_lg = league_pct[league_pct["league"] == league].copy()
    df_lg["x"] = df_lg["season"].map(season_x)

    fig, ax = plt.subplots(figsize=(10, 6))

    for cl in HIER_ORDER:
        sub = df_lg[df_lg["cluster_final_hier"] == cl].sort_values("x")
        cfg = LINE_STYLE[cl]

        ax.plot(sub["x"], sub["pct"], color=cfg["color"], marker=cfg["marker"],
                linestyle=cfg["ls"], linewidth=cfg["lw"], markersize=8, 
                label=LABEL_KR_FLAT[cl], zorder=3)

        for _, row in sub.iterrows():
            ax.annotate(f"{row['pct']:.1f}%", xy=(row["x"], row["pct"]),
                        xytext=(0, 10), textcoords="offset points",
                        fontsize=9, color=cfg["color"], ha="center", fontweight="bold")

    ax.set_title(f"{LEAGUE_LABEL[league]} — 시즌별 전술 유형 비율 추세", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(range(len(SEASON_ORDER)))
    ax.set_xticklabels([SEASON_LABEL[s] for s in SEASON_ORDER], fontsize=11)
    ax.set_ylim(0, league_pct["pct"].max() + 15)
    ax.set_ylabel("전술 유형 비율 (%)", fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.grid(axis="y", alpha=0.2, ls="--")
    
    ax.legend(title="최종 전술 군집", fontsize=10, title_fontsize=10, 
              loc="upper left", bbox_to_anchor=(0, 1), frameon=True, facecolor="white")

    plt.tight_layout()
    fname = f"rq3_1_league_trend_{league}.png"
    plt.savefig(OUT_FIG_DIR / fname, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"✅ 저장 완료: {fname}")

# %% [code] Notebook cell 6
 # ════════════════════════════════════════════════════════════
# [RQ3-2] 리그별 군집 비중 — 묶음 막대그래프 (최종 명칭 반영)
# ════════════════════════════════════════════════════════════
import numpy as np
import matplotlib.pyplot as plt

# 1. 확정된 데이터 매핑
# (실제 데이터 분석 시에는 df_rq3에서 직접 계산하는 것을 권장하지만, 
#  선생님이 제공한 데이터를 기반으로 매핑만 수정했습니다)
data = {
    "EPL":        {"1-1": 30.0, "1-2": 17.1, "2-1": 21.2, "2-2": 31.6},
    "LaLiga":     {"1-1": 29.1, "1-2": 10.8, "2-1": 17.8, "2-2": 42.2},
    "Bundesliga": {"1-1": 30.1, "1-2": 13.9, "2-1": 18.5, "2-2": 37.6},
    "Serie A":    {"1-1": 31.8, "1-2": 12.2, "2-1": 19.9, "2-2": 36.1},
    "Ligue 1":    {"1-1": 30.6, "1-2": 12.7, "2-1": 18.7, "2-2": 38.0},
}

leagues  = list(data.keys())
clusters = HIER_ORDER # ["1-1", "1-2", "2-1", "2-2"]

n_leagues  = len(leagues)
n_clusters = len(clusters)
bar_width  = 0.18
x          = np.arange(n_leagues)

fig, ax = plt.subplots(figsize=(12, 6))

for i, cl in enumerate(clusters):
    offset = (i - n_clusters / 2 + 0.5) * bar_width
    vals   = [data[lg][cl] for lg in leagues]
    
    bars   = ax.bar(x + offset, vals,
                    width=bar_width,
                    color=PALETTE[cl], # 최종 팔레트 사용
                    label=LABEL_KR_FLAT[cl], # 최종 한글 명칭 사용
                    edgecolor="white",
                    linewidth=0.5)
    
    # 막대 위 수치 표기
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{v:.1f}%",
                ha="center", va="bottom",
                fontsize=8, color=PALETTE[cl],
                fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(leagues, fontsize=12)
ax.set_ylabel("전술 유형 비율 (%)", fontsize=12)
ax.set_xlabel("리그", fontsize=12)
ax.set_ylim(0, 55) # 비율이 높은 경우를 대비해 상단 여유 확보
ax.set_title("유럽 5대 리그별 전술 유형 분포 비교 (2019/20 ~ 2024/25)",
             fontsize=14, fontweight="bold", pad=15)

# 범례 위치 최적화
ax.legend(title="최종 전술 군집", ncol=2,
          loc="upper right", fontsize=10, title_fontsize=10,
          framealpha=0.9, edgecolor="#ccc")
ax.grid(axis="y", alpha=0.3, ls="--")

plt.tight_layout()
plt.savefig(OUT_FIG_DIR / "rq3_2_league_cluster_grouped_bar_FINAL.png", dpi=300, bbox_inches="tight")
plt.show()
print("✅ 저장 완료: rq3_2_league_cluster_grouped_bar_FINAL.png")

# %% [code] Notebook cell 7
 # ════════════════════════════════════════════════════════════
# [RQ3-2] League-season tactical type trend + table
# ════════════════════════════════════════════════════════════

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# Cluster order
CLUSTERS = ["1-1", "1-2", "2-1", "2-2"]

LABELS = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

COLORS = {
    "1-1": "#2E91B9",
    "1-2": "#004766",
    "2-1": "#F39C12",
    "2-2": "#E83E4D",
}

MARKERS = {
    "1-1": "o",
    "1-2": "s",
    "2-1": "^",
    "2-2": "D",
}

SEASONS = ["2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024", "2024_2025"]
SEASON_LABELS = ["19/20", "20/21", "21/22", "22/23", "23/24", "24/25"]

# Check actual league names first
print("Actual league values in data:")
print(df_rq3["league"].dropna().unique())

# Adjust these keys to match the actual values in df_rq3["league"]
LEAGUE_ORDER = ["EPL", "LaLiga", "Bundesliga", "SerieA", "Ligue1"]

LEAGUE_LABEL = {
    "EPL": "EPL",
    "LaLiga": "LaLiga",
    "Bundesliga": "Bundesliga",
    "SerieA": "Serie A",
    "Ligue1": "Ligue 1",
}


def make_league_season_pct(data, season_col="season", cluster_col="cluster_final_hier"):
    """Calculate season-by-cluster percentage table."""
    
    count_table = (
        data.groupby([season_col, cluster_col])
        .size()
        .unstack(fill_value=0)
    )
    
    count_table = count_table.reindex(index=SEASONS, columns=CLUSTERS, fill_value=0)
    
    row_sum = count_table.sum(axis=1)
    pct_table = count_table.div(row_sum.replace(0, np.nan), axis=0) * 100
    
    return pct_table


def plot_league_final(df, league_key, league_name, ax_line, ax_table):
    """Plot league-season tactical type trend and table."""
    
    league_df = df[df["league"] == league_key].copy()
    
    # Empty league check
    if league_df.empty:
        ax_line.text(
            0.5, 0.5,
            f"No data for league key: {league_key}",
            ha="center", va="center",
            fontsize=14, transform=ax_line.transAxes
        )
        ax_line.set_title(f"{league_name} — 시즌별 전술 유형 비율 추세", fontsize=14, fontweight="bold")
        ax_table.axis("off")
        return
    
    pct = make_league_season_pct(league_df)
    x = np.arange(len(SEASONS))
    
    # Line chart
    for i, cl in enumerate(CLUSTERS):
        vals = pct[cl].values
        
        ax_line.plot(
            x, vals,
            color=COLORS[cl],
            marker=MARKERS[cl],
            markersize=7,
            linewidth=2.4,
            markerfacecolor="white",
            markeredgewidth=2.0,
            linestyle="-" if cl in ["1-1", "1-2"] else "--",
            label=LABELS[cl],
            zorder=3
        )
    
    ax_line.set_title(
        f"{league_name} — 시즌별 전술 유형 비율 추세",
        fontsize=15,
        fontweight="bold",
        pad=18
    )
    
    ax_line.set_xticks(x)
    ax_line.set_xticklabels(SEASON_LABELS, fontsize=11)
    ax_line.set_ylabel("전술 유형 비율 (%)", fontsize=11)
    ax_line.set_ylim(0, 65)
    ax_line.grid(axis="y", alpha=0.25, linestyle="--")
    ax_line.spines["top"].set_visible(False)
    ax_line.spines["right"].set_visible(False)
    
    # Legend below the line chart title
    ax_line.legend(
        ncol=4,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        fontsize=9,
        frameon=True
    )
    
    # Table
    ax_table.axis("off")
    
    col_labels = ["시즌"] + [LABELS[cl] for cl in CLUSTERS]
    
    row_data = []
    for season, season_label in zip(SEASONS, SEASON_LABELS):
        row = [season_label]
        for cl in CLUSTERS:
            value = pct.loc[season, cl]
            row.append("" if pd.isna(value) else f"{value:.1f}%")
        row_data.append(row)
    
    tbl = ax_table.table(
        cellText=row_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center"
    )
    
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.65)
    
    # Header style
    for ci in range(len(col_labels)):
        tbl[0, ci].set_facecolor("#2C3E50")
        tbl[0, ci].set_text_props(color="white", fontweight="bold")
    
    # Cell style and highlight max value by season
    for (ri, ci), cell in tbl.get_celld().items():
        cell.set_edgecolor("#CCCCCC")
        
        if ri > 0 and ci > 0:
            season = SEASONS[ri - 1]
            
            if pct.loc[season].notna().any():
                max_cluster = pct.loc[season].idxmax()
                current_cluster = CLUSTERS[ci - 1]
                
                if current_cluster == max_cluster:
                    cell.set_facecolor(COLORS[current_cluster] + "25")
                else:
                    cell.set_facecolor("white")


# Output directory
OUT_FIG_DIR = Path("rq3_figures")
OUT_FIG_DIR.mkdir(exist_ok=True)

# Main loop
for league_key in LEAGUE_ORDER:
    league_name = LEAGUE_LABEL.get(league_key, league_key)
    
    fig = plt.figure(figsize=(13, 8.5))
    gs = gridspec.GridSpec(
        2, 1,
        height_ratios=[2.2, 1],
        hspace=0.22,
        top=0.90,
        bottom=0.06
    )
    
    ax_line = fig.add_subplot(gs[0])
    ax_table = fig.add_subplot(gs[1])
    
    plot_league_final(df_rq3, league_key, league_name, ax_line, ax_table)
    
    plt.savefig(
        OUT_FIG_DIR / f"rq3_season_trend_{league_key}_FINAL.png",
        dpi=300,
        bbox_inches="tight"
    )
    
    plt.show()
    print(f"Saved: {league_key} tactical type trend chart")

# %% [code] Notebook cell 8


