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
# # [STEP1] 라이브러리 & 경로 설정

# %% [code] Notebook cell 2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import joblib
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    adjusted_rand_score,
)
from sklearn.utils import resample   # ← 추가

sns.set_style("whitegrid")
plt.rcParams.update({
    "axes.titlesize": 14, "axes.labelsize": 12,
    "legend.fontsize": 11, "xtick.labelsize": 10,
    "ytick.labelsize": 10, "axes.unicode_minus": False,
})
if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"

SEED = 42
RANDOM_STATE = 42
N_INIT = 10

CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "notebooks" else CURRENT_DIR

DATA_DIR      = PROJECT_ROOT / "data" / "processed"
OUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
OUT_FIG_DIR   = PROJECT_ROOT / "outputs" / "figures"

DATA_PATH = DATA_DIR / "tactical_analysis_cleaned.csv"

OUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)

print(f"Data path   : {DATA_PATH}")
print(f"Data exists : {DATA_PATH.exists()}")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Input file not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
print(f"Loaded: {df.shape}")
display(df.head())

# %% [markdown] Notebook cell 3
# # [STEP 2] 14개 핵심 지표 정의 및 정제

# %% [code] Notebook cell 4
# ════════════════════════════════════════════════════════════
# [STEP 2] 데이터 로드, 시즌 필터링 및 14개 핵심 지표 정제
# ════════════════════════════════════════════════════════════
print("="*60); print("[STEP 2] 데이터 로드, 필터링 및 지표 정제"); print("="*60)

df = pd.read_csv(DATA_PATH)
initial_count = len(df)

target_seasons = [
    '2019_2020', '2020_2021', '2021_2022',
    '2022_2023', '2023_2024', '2024_2025'
]
df = df[df['season'].isin(target_seasons)].reset_index(drop=True)
print(f"시즌 필터링: {initial_count:,}행 → {len(df):,}행")

# ── 14개 핵심 전술 변수 ──────────────────────────────────────
TACTICAL_PATTERN_VARS = [
    "possession", "passes", "long_balls", "final_third_entries",
    "goalkeeping_goal_kicks", "ppda_val", "DEEP",
    "crosses", "dribbles", "box_shots", "shots",
    "tackles", "interceptions", "clearances",
]

TACTICAL_VAR_LABELS = {
    "possession":             "Possession",
    "passes":                 "Passes",
    "long_balls":             "Long Balls",
    "final_third_entries":    "Final Third Entries",
    "goalkeeping_goal_kicks": "Goal Kicks",
    "ppda_val":               "PPDA",
    "DEEP":                   "DEEP",
    "crosses":                "Crosses",
    "dribbles":               "Dribbles",
    "box_shots":              "Box Shots",
    "shots":                  "Shots",
    "tackles":                "Tackles",
    "interceptions":          "Interceptions",
    "clearances":             "Clearances",
}

df_model = df.dropna(subset=TACTICAL_PATTERN_VARS).reset_index(drop=True)
X_final  = df_model[TACTICAL_PATTERN_VARS].astype(float).copy()

print(f"✅ 분석 지표 ({len(TACTICAL_PATTERN_VARS)}개): {TACTICAL_PATTERN_VARS}")
print(f"📊 최종 분석 경기 수: {len(df_model):,}건")

# %% [markdown] Notebook cell 5
# # [STEP 3] 표준화

# %% [code] Notebook cell 6
# ════════════════════════════════════════════════════════════
# [STEP 3] 데이터 표준화 (Standard Scaling)
# ════════════════════════════════════════════════════════════
from sklearn.preprocessing import StandardScaler
from IPython.display import display

print("="*60); print("[STEP 3] 14개 전술 지표 표준화"); print("="*60)

scaler = StandardScaler()
X_scaled_array = scaler.fit_transform(X_final)
X_scaled = pd.DataFrame(X_scaled_array, columns=X_final.columns)

print(f"✅ 표준화 완료: {X_scaled.shape[0]:,}행 × {X_scaled.shape[1]}열")

summary_df = pd.DataFrame({
    "평균 (Mean ≈ 0)": X_scaled.mean(),
    "표준편차 (Std ≈ 1)": X_scaled.std()
}).round(4).T

print("\n📊 [스케일링 검증]")
display(summary_df)

# %% [markdown] Notebook cell 7
# # [STEP 4] PCA 2D 변환

# %% [code] Notebook cell 8
# ════════════════════════════════════════════════════════════
# [STEP 5] PCA 변환 (14D → 2D)
# ════════════════════════════════════════════════════════════
print("="*60); print("[STEP 5] PCA 변환 (14D → 2D)"); print("="*60)

pca   = PCA(n_components=2, random_state=SEED)
X_pca = pca.fit_transform(X_scaled)

ev1, ev2 = pca.explained_variance_ratio_ * 100
print(f"✅ PC1 설명력: {ev1:.2f}%")
print(f"✅ PC2 설명력: {ev2:.2f}%")
print(f"✅ 누적 설명력: {ev1+ev2:.2f}%")

df_model["pc1"] = X_pca[:, 0]
df_model["pc2"] = X_pca[:, 1]
print(f"\n🚀 14개 지표 → 2D 좌표 변환 완료: {X_pca.shape}")

# %% [markdown] Notebook cell 9
# # [STEP 5] Stage 1 K 선택

# %% [code] Notebook cell 10
# ════════════════════════════════════════════════════════════
# [STEP 5] Stage 1 k Selection by Silhouette Index
# ════════════════════════════════════════════════════════════

print("=" * 60)
print("[STEP 5] Stage 1 k Selection by Silhouette Index")
print("=" * 60)

K_RANGE = range(2, 10)
stage1_k_results = []

for k in K_RANGE:
    km = KMeans(
        n_clusters=k,
        init="k-means++",
        n_init=N_INIT,
        random_state=RANDOM_STATE
    )
    
    labels = km.fit_predict(X_pca)
    score = silhouette_score(X_pca, labels)
    
    stage1_k_results.append({
        "k": k,
        "silhouette_score": score
    })

stage1_k_results_df = pd.DataFrame(stage1_k_results)
display(stage1_k_results_df.round(4))

best_k = int(
    stage1_k_results_df
    .sort_values("silhouette_score", ascending=False)
    .iloc[0]["k"]
)

print(f"\nBest k by silhouette score: {best_k}")

km_stage1 = KMeans(
    n_clusters=best_k,
    init="k-means++",
    n_init=N_INIT,
    random_state=RANDOM_STATE
)

labels_stage1 = km_stage1.fit_predict(X_pca)
df_model["cluster_stage1"] = labels_stage1

stage1_k_results_df.to_csv(
    OUT_TABLE_DIR / "rq1_stage1_k_selection_silhouette.csv",
    index=False,
    encoding="utf-8-sig"
)

plt.figure(figsize=(7, 5))
sns.lineplot(
    data=stage1_k_results_df,
    x="k",
    y="silhouette_score",
    marker="o"
)
plt.axvline(best_k, linestyle="--", color="gray", alpha=0.7)
plt.title("Stage 1 k Selection by Silhouette Index", fontsize=13, fontweight="bold")
plt.xlabel("Number of clusters (k)")
plt.ylabel("Silhouette Score")
plt.tight_layout()
plt.savefig(
    OUT_FIG_DIR / "rq1_stage1_k_selection_silhouette.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# %% [markdown] Notebook cell 11
# # [STEP 6] Stage 1 시각화

# %% [code] Notebook cell 12
# ════════════════════════════════════════════════════════════
# [STEP 6.5] Stage 1 Visualization — Global k=2 Split
# ════════════════════════════════════════════════════════════
if "PC1" not in df_model.columns:
    df_model["PC1"] = X_pca[:, 0]
if "PC2" not in df_model.columns:
    df_model["PC2"] = X_pca[:, 1]

df_model["cluster_stage1_label"] = df_model["cluster_stage1"].map({
    0: "Stage 1 - Cluster 1", 1: "Stage 1 - Cluster 2"
})

plt.figure(figsize=(9, 7))
sns.scatterplot(data=df_model, x="PC1", y="PC2",
                hue="cluster_stage1_label", s=18, alpha=0.45, edgecolor=None)
plt.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.5)
plt.axvline(0, color="gray", lw=0.8, ls="--", alpha=0.5)
plt.title("Stage 1 K-Means (k=2) in PCA 2D Space", fontsize=15)
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.tight_layout()
plt.savefig(OUT_FIG_DIR / "rq1_stage1_k2_pca2d_visualization.png", dpi=300, bbox_inches="tight")
plt.show()

# %% [markdown] Notebook cell 13
# # [STEP7] Stage 1 저장

# %% [code] Notebook cell 14
df_model.to_csv(OUT_TABLE_DIR / "rq1_stage1_labeled_dataset.csv", index=False, encoding="utf-8-sig")
print(f"Saved: {len(df_model):,}행 × {len(df_model.columns)}열")
display(df_model["cluster_stage1"].value_counts().sort_index().to_frame("count"))

# %% [markdown] Notebook cell 15
# # [STEP8] Sub-cluster k 탐색

# %% [code] Notebook cell 16
# ════════════════════════════════════════════════════════════
# [추가 분석] 각 Stage 1 군집 내부 최적 k 탐색 (수정본)
# ════════════════════════════════════════════════════════════
def find_optimal_sub_k(X_sub, cluster_name):
    print(f"\n🔍 {cluster_name} 내부 최적 k 탐색:")
    
    # 안전장치: 데이터가 비어있을 경우 에러를 뱉기 전에 차단
    if len(X_sub) == 0:
        print("  ⚠️ 에러: 데이터가 없습니다. 필터링 라벨 번호를 확인하세요.")
        return []
        
    results = []
    for k in range(2, 6):
        km    = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
        score = silhouette_score(X_sub, km.fit_predict(X_sub))
        results.append((k, score))
        print(f"  k={k} → Silhouette: {score:.4f}")
    return results

# [핵심 수정 사항] 1과 2가 아니라 0과 1로 필터링해야 합니다.
X_c0 = X_pca[labels_stage1 == 0] 
X_c1 = X_pca[labels_stage1 == 1]

res_c0 = find_optimal_sub_k(X_c0, "Stage 1 Cluster 1")
res_c1 = find_optimal_sub_k(X_c1, "Stage 1 Cluster 2")

sub_k_results_df = pd.concat([
    pd.DataFrame(res_c0, columns=["k", "silhouette_score"]).assign(stage1_cluster=0),
    pd.DataFrame(res_c1, columns=["k", "silhouette_score"]).assign(stage1_cluster=1),
], axis=0).reset_index(drop=True)

display(sub_k_results_df)

sub_k_results_df.to_csv(
    OUT_TABLE_DIR / "rq1_subcluster_k_selection_silhouette.csv",
    index=False,
    encoding="utf-8-sig"
)

# %% [code] Notebook cell 17
# ════════════════════════════════════════════════════════════
# [STEP 8-2] Stage 2 — 각 군집 내부 재군집화 → final_labels_4k 생성
# ════════════════════════════════════════════════════════════
km_sub0 = KMeans(n_clusters=2, init="k-means++", n_init=N_INIT, random_state=RANDOM_STATE)
km_sub1 = KMeans(n_clusters=2, init="k-means++", n_init=N_INIT, random_state=RANDOM_STATE)

sub_labels_c0 = km_sub0.fit_predict(X_c0)
sub_labels_c1 = km_sub1.fit_predict(X_c1)

final_labels_4k = np.zeros(len(X_pca), dtype=int)
final_labels_4k[labels_stage1 == 0] = sub_labels_c0      # 0 또는 1
final_labels_4k[labels_stage1 == 1] = sub_labels_c1 + 2  # 2 또는 3

print("final_labels_4k 생성 완료")
print(pd.Series(final_labels_4k).value_counts().sort_index())

# %% [markdown] Notebook cell 18
# # [STEP 9] 계층적 최종 분할

# %% [code] Notebook cell 19
# ════════════════════════════════════════════════════════════
# [STEP 9] Hierarchical Optimal Partitioning (최종 반영)
# ════════════════════════════════════════════════════════════
print("="*60); print("[STEP 9] Hierarchical Optimal Partitioning"); print("="*60)

# 1. 군집 데이터 할당
df_model["cluster_final_num"] = final_labels_4k
final_hier_label_map = {0: "1-1", 1: "1-2", 2: "2-1", 3: "2-2"}
df_model["cluster_final_hier"] = df_model["cluster_final_num"].map(final_hier_label_map)

# 2. 최종 명칭 매핑
final_cluster_name_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}
df_model["cluster_final_name"] = df_model["cluster_final_hier"].map(final_cluster_name_map)

# 3. 한글 변수명 매핑
var_ko = {
    "possession":             "점유율 (Possession)",
    "passes":                 "패스 (Passes)",
    "long_balls":             "롱볼 (Long balls)",
    "final_third_entries":    "상대 진영 1/3 투입 (Final third entries)",
    "goalkeeping_goal_kicks": "골킥 (Goal kicks)",
    "ppda_val":               "전방 압박 강도 (PPDA)",
    "DEEP":                   "위험 지역 진입 패스 (DEEP)",
    "crosses":                "크로스 (Crosses)",
    "dribbles":               "드리블 (Dribbles)",
    "box_shots":              "박스 내 슈팅 (Box shots)",
    "shots":                  "슈팅 (Shots)",
    "tackles":                "태클 (Tackles)",
    "interceptions":          "인터셉트 (Interceptions)",
    "clearances":             "클리어링 (Clearances)",
}

# 4. 데이터 프로파일 생성
hier_order = ["1-1", "1-2", "2-1", "2-2"]
final_profile = df_model.groupby("cluster_final_hier", observed=True)[TACTICAL_PATTERN_VARS].mean().reindex(hier_order)

final_profile_final = final_profile.T  # 먼저 정의
final_profile_final.index = final_profile_final.index.map(lambda x: var_ko.get(x, x))
final_profile_final.columns = [final_cluster_name_map[c] for c in final_profile_final.columns]

# 5. 분포 정보 정리
final_distribution = (df_model["cluster_final_hier"].value_counts().reindex(hier_order)
                      .reset_index(name="count"))
final_distribution["percentage"] = (final_distribution["count"] / len(df_model) * 100).round(2)
final_distribution["cluster_final_name"] = final_distribution["cluster_final_hier"].map(final_cluster_name_map)

# 6. 출력 및 저장
print("\n[최종 군집 분포]")
display(final_distribution.round(2))

print("\n[Table. 최종 전술적 특성 프로파일]")
display(final_profile_final.round(3))

final_distribution.to_csv(OUT_TABLE_DIR / "rq1_final_hierarchical_cluster_distribution.csv", index=False, encoding="utf-8-sig")
final_profile_final.to_csv(OUT_TABLE_DIR / "rq1_final_hierarchical_cluster_profile.csv", encoding="utf-8-sig")
df_model.to_csv(OUT_TABLE_DIR / "rq1_final_labeled_dataset.csv", index=False, encoding="utf-8-sig")
print(f"\nSaved all files to {OUT_TABLE_DIR}")

# %% [markdown] Notebook cell 20
# # [STEP 10] 최종 4개 군집 시각화

# %% [code] Notebook cell 21
 # ════════════════════════════════════════════════════════════
# [STEP 10] Final 4-Cluster Visualization (논문용 명칭 적용)
# ════════════════════════════════════════════════════════════
import matplotlib.pyplot as plt

print("="*60); print("[STEP 8] Final 4-Cluster Tactical Map"); print("="*60)

# PCA 좌표 확인
if "PC1" in df_model.columns:
    x_col, y_col = "PC1", "PC2"
elif "pc1" in df_model.columns:
    x_col, y_col = "pc1", "pc2"
else:
    df_model["PC1"] = X_pca[:, 0]; df_model["PC2"] = X_pca[:, 1]
    x_col, y_col = "PC1", "PC2"

# 확정된 군집 순서 및 색상 팔레트
hier_order = ["1-1", "1-2", "2-1", "2-2"]

# Cluster 1(능동적)은 푸른 계열, Cluster 2(수비적)는 붉은/주황 계열로 구분
palette_final = {
    "1-1": "#2E86AB",  # 1-1 점유 전개형
    "1-2": "#003F5C",  # 1-2 고점유 지배형
    "2-1": "#F39C12",  # 2-1 저점유 수비형
    "2-2": "#E63946",  # 2-2 수비적 전개형
}

# 범례 명칭 (확정된 명칭 적용)
label_name_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

plt.figure(figsize=(11, 8))
for label in hier_order:
    mask = df_model["cluster_final_hier"] == label
    plt.scatter(df_model.loc[mask, x_col], df_model.loc[mask, y_col],
                s=25, alpha=0.6, c=palette_final[label],
                edgecolors="white", linewidths=0.2, label=label_name_map[label])

plt.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.45)
plt.axvline(0, color="gray", lw=0.8, ls="--", alpha=0.45)

# 논문용 제목 (한글)
plt.title("전술적 특성에 따른 4개 군집의 PCA 분포도\n"
          "(14개 전술 지표 기반 계층적 군집 분석)",
          fontsize=16, fontweight="bold", pad=20)

plt.xlabel("제 1 주성분 (PC1)", fontsize=12)
plt.ylabel("제 2 주성분 (PC2)", fontsize=12)
plt.legend(title="최종 전술 군집", loc="upper right", fontsize=11, frameon=True)
plt.grid(alpha=0.3, ls="--"); plt.tight_layout()

# 저장 파일명 수정
save_path = OUT_FIG_DIR / "rq1_final_4cluster_tactical_map_hierarchical.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Saved: {save_path.name}")

# %% [code] Notebook cell 22
# ════════════════════════════════════════════════════════════
# [STEP 10] Final 4-Cluster Visualization (계열별 분리 출력)
# ════════════════════════════════════════════════════════════
import matplotlib.pyplot as plt

print("="*60); print("[STEP 10] Final 4-Cluster Tactical Map (Split Plot)"); print("="*60)

# PCA 좌표 확인 (기존 로직 유지)
x_col, y_col = ("PC1", "PC2") if "PC1" in df_model.columns else ("pc1", "pc2")

# 군집 정의
palette_final = {"1-1": "#2E86AB", "1-2": "#003F5C", "2-1": "#F39C12", "2-2": "#E63946"}
label_name_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

# 그림 두 개를 나란히 출력하기 위해 서브플롯 설정
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# ── 1. 능동적 점유형 계열 (1-1, 1-2) ─────────────────────────
ax = axes[0]
for label in ["1-1", "1-2"]:
    mask = df_model["cluster_final_hier"] == label
    ax.scatter(df_model.loc[mask, x_col], df_model.loc[mask, y_col],
               s=30, alpha=0.6, c=palette_final[label], edgecolors="white", linewidths=0.2, label=label_name_map[label])
ax.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.45)
ax.axvline(0, color="gray", lw=0.8, ls="--", alpha=0.45)
ax.set_title("능동적 점유형 계열 (C1) 세부 군집 분포", fontsize=15, fontweight="bold")
ax.set_xlabel("PC1", fontsize=12); ax.set_ylabel("PC2", fontsize=12)
ax.legend(loc="upper right"); ax.grid(alpha=0.3, ls="--")

# ── 2. 수비적 직접형 계열 (2-1, 2-2) ─────────────────────────
ax = axes[1]
for label in ["2-1", "2-2"]:
    mask = df_model["cluster_final_hier"] == label
    ax.scatter(df_model.loc[mask, x_col], df_model.loc[mask, y_col],
               s=30, alpha=0.6, c=palette_final[label], edgecolors="white", linewidths=0.2, label=label_name_map[label])
ax.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.45)
ax.axvline(0, color="gray", lw=0.8, ls="--", alpha=0.45)
ax.set_title("수비적 직접형 계열 (C2) 세부 군집 분포", fontsize=15, fontweight="bold")
ax.set_xlabel("PC1", fontsize=12); ax.set_ylabel("PC2", fontsize=12)
ax.legend(loc="upper right"); ax.grid(alpha=0.3, ls="--")

plt.tight_layout()
save_path = OUT_FIG_DIR / "rq1_split_tactical_map_hierarchical.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Saved: {save_path.name}")

# %% [markdown] Notebook cell 23
# # 군집 프로파일 표

# %% [code] Notebook cell 24
import pandas as pd

# ── 1. 핵심 상수 재정의 (오류 방지) ──────────────────────────────────
FINAL_TACTICAL_VARS = [
    "possession", "passes", "long_balls", "final_third_entries",
    "goalkeeping_goal_kicks", "ppda_val", "DEEP",
    "crosses", "dribbles", "box_shots", "shots",
    "tackles", "interceptions", "clearances",
]

# ── 2. 한글 변수명 매핑 ────────────────────────────────────────────
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

# ── 3. 확정된 군집 명칭 및 순서 ────────────────────────────────────
hier_order = ["1-1", "1-2", "2-1", "2-2"]
final_cluster_name_map = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

# ── 4. 데이터 생성 및 프로파일링 ──────────────────────────────────
# df_model이 로드되어 있어야 합니다.
final_profile = df_model.groupby("cluster_final_hier", observed=True)[FINAL_TACTICAL_VARS].mean().reindex(hier_order)

# 명칭 결합
final_profile_named = final_profile.copy()
final_profile_named.index = [f"{c} {final_cluster_name_map[c]}" for c in final_profile_named.index]

# 전치 및 한글 변수명 매핑
final_profile_named = final_profile_named.T
final_profile_named.index = final_profile_named.index.map(lambda x: var_ko.get(x, x))

# ── 5. 결과 출력 ──────────────────────────────────────────────────
display(final_profile_named.round(3))

# 저장
save_path = OUT_TABLE_DIR / "rq1_final_hierarchical_cluster_profile_named.csv"
final_profile_named.to_csv(save_path, encoding="utf-8-sig")
print(f"\nSaved: {save_path.name}")

# %% [markdown] Notebook cell 25
# # 최종 저장

# %% [code] Notebook cell 26
 # ════════════════════════════════════════════════════════════
# [STEP 11] Save Final RQ1 Results (최종 명칭 적용)
# ════════════════════════════════════════════════════════════
print("="*60); print("[STEP 11] Save Final RQ1 Results"); print("="*60)

hier_order = ["1-1", "1-2", "2-1", "2-2"]

# 선생님께서 확정하신 4개 군집 명칭 반영
cluster_map_kr = {
    "1-1": "점유 전개형",
    "1-2": "고점유 지배형",
    "2-1": "저점유 수비형",
    "2-2": "수비적 전개형",
}

# 영문 명칭은 논문 투고/학술지 성격에 맞춰 표준화
cluster_map_en = {
    "1-1": "Progressive Possession",
    "1-2": "High-Possession Control",
    "2-1": "Low-Possession Defensive",
    "2-2": "Defensive Direct",
}

df_model["cluster_label"]    = df_model["cluster_final_hier"].map(cluster_map_en)
df_model["cluster_label_kr"] = df_model["cluster_final_hier"].map(cluster_map_kr)

# 데이터 보존을 위한 열 선택
base_cols    = ["match_id","date","season","league","team","opponent","result","team_score","opponent_score"]
pca_cols     = ["PC1","PC2"] if "PC1" in df_model.columns else (["pc1","pc2"] if "pc1" in df_model.columns else [])
cluster_cols = ["cluster_stage1","cluster_final_num","cluster_final_hier","cluster_label","cluster_label_kr"]
keep_cols    = [c for c in base_cols + FINAL_TACTICAL_VARS + pca_cols + cluster_cols if c in df_model.columns]

# 파일 저장
save_path = OUT_TABLE_DIR / "rq1_final_data_14vars_hierarchical_4clusters.csv"
df_model[keep_cols].to_csv(save_path, index=False, encoding="utf-8-sig")

# 모델 및 스케일러 저장
joblib.dump(scaler, OUT_TABLE_DIR / "scaler_14vars.pkl")
joblib.dump(pca,    OUT_TABLE_DIR / "pca_2d_14vars.pkl")

# 군집 분포 요약 생성
cluster_distribution = (
    df_model.groupby(["cluster_final_hier","cluster_label_kr"], observed=True).size()
    .reset_index(name="n"))
cluster_distribution["percent"] = (cluster_distribution["n"] / len(df_model) * 100).round(2)
cluster_distribution["cluster_final_hier"] = pd.Categorical(
    cluster_distribution["cluster_final_hier"], categories=hier_order, ordered=True)
cluster_distribution = cluster_distribution.sort_values("cluster_final_hier").reset_index(drop=True)

cluster_distribution.to_csv(
    OUT_TABLE_DIR / "rq1_cluster_distribution_14vars_hierarchical_4clusters.csv",
    index=False, encoding="utf-8-sig")

# 결과 출력
pc1_var = pca.explained_variance_ratio_[0]*100
pc2_var = pca.explained_variance_ratio_[1]*100

print(f"\n{'═'*60}")
print(f"{'RQ1 Tactical Clustering Summary':^60}")
print(f"{'═'*60}")
print(f"  Total observations  : {len(df_model):,}")
print(f"  Tactical indicators : {len(FINAL_TACTICAL_VARS)}")
print(f"  PCA 2D variance     : {pc1_var+pc2_var:.2f}% (PC1 {pc1_var:.2f}% + PC2 {pc2_var:.2f}%)")
print(f"  Final clusters      : 4 (Hierarchical 2×2)")
for _, row in cluster_distribution.iterrows():
    print(f"  {row['cluster_final_hier']} ({row['cluster_label_kr']}): {int(row['n']):,}건 ({row['percent']:.2f}%)")
print(f"\nSaved: {save_path.name}")

# %% [code] Notebook cell 27
check_path = OUT_TABLE_DIR / "rq1_final_data_14vars_hierarchical_4clusters.csv"
df_check   = pd.read_csv(check_path)
print(df_check.shape)
print(df_check["cluster_final_hier"].value_counts().sort_index())
print(df_check[["cluster_final_hier","cluster_label_kr"]].drop_duplicates().sort_values("cluster_final_hier"))

# %% [code] Notebook cell 28
# ════════════════════════════════════════════════════════════
# [STEP 12 전처리] team_summary 생성
# ════════════════════════════════════════════════════════════

hier_order = ["1-1", "1-2", "2-1", "2-2"]

cluster_name_full = {
    "1-1": "1-1 점유 전개형",
    "1-2": "1-2 고점유 지배형",
    "2-1": "2-1 저점유 수비형",
    "2-2": "2-2 수비적 전개형",
}

# 군집별 경기 수 피벗
cluster_counts = (
    df_model.groupby(["team", "cluster_final_hier"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=hier_order, fill_value=0)
)

# 전체 경기 수 및 군집별 비율
cluster_counts["n_matches"] = cluster_counts[hier_order].sum(axis=1)
cluster_pct_cols = {}
for cl in hier_order:
    col_name = f"pct_{cl}"
    cluster_counts[col_name] = (cluster_counts[cl] / cluster_counts["n_matches"] * 100).round(2)
    cluster_pct_cols[cl] = col_name

# dominant cluster
cluster_counts["dominant_cluster"] = cluster_counts[hier_order].idxmax(axis=1)
cluster_counts["dominant_cluster_name"] = cluster_counts["dominant_cluster"].map(cluster_name_full)

team_summary = cluster_counts.reset_index()

print(f"team_summary 생성 완료: {len(team_summary)}개 팀")
display(team_summary.head())

# %% [code] Notebook cell 29
# ════════════════════════════════════════════════════════════
# [STEP 12] Team-Level Distribution (3시즌 이상 참가 & 군집별 상위 10개 팀)
# ════════════════════════════════════════════════════════════

# 1. 3시즌 이상 & 30경기 이상 참가 팀 필터링
team_season_count = df_model.groupby("team")["season"].nunique()
valid_teams = team_season_count[team_season_count >= 3].index

team_summary_filtered = team_summary[
    (team_summary["team"].isin(valid_teams)) & 
    (team_summary["n_matches"] >= 30)
].copy()

print(f"조건 만족 팀 수 (3시즌 이상 & 30경기 이상): {len(team_summary_filtered)}")

# 2. 각 군집별로 해당 군집이 Dominant(주력)인 팀들을 추출하여 상위 10개 출력
for cl in hier_order:
    # 해당 군집을 주력으로 하는 팀만 필터링
    df_cl = team_summary_filtered[team_summary_filtered["dominant_cluster"] == cl].copy()
    
    # 해당 군집의 비율(%)이 높은 순으로 정렬 (head 10)
    col = cluster_pct_cols[cl]
    df_display = df_cl.sort_values(col, ascending=False).head(10)[["team", "n_matches"] + list(cluster_pct_cols.values()) + ["dominant_cluster_name"]]
    
    # 출력용 헤더 한글화
    df_display.columns = ["팀명", "경기수"] + list(cluster_name_full.values()) + ["주력 전술"]
    
    print(f"\n[주력 전술이 '{cluster_name_full[cl]}'인 팀 상위 10개]")
    display(df_display)

# 3. 저장
team_summary_filtered.to_csv(OUT_TABLE_DIR / "rq1_team_final_tactical_type_distribution_top10.csv", index=False, encoding="utf-8-sig")
print(f"\nSaved: rq1_team_final_tactical_type_distribution_top10.csv")

# %% [code] Notebook cell 30
# ════════════════════════════════════════════════════════════
# [STEP 12] Team-Level Distribution (전 시즌 참가 & 군집별 상위 10개 팀)
# ════════════════════════════════════════════════════════════

# 1. 6시즌 모두 참가한 팀 리스트 추출 (전 시즌 기준)
# 6시즌을 전체라고 가정하고, 고유 시즌 수가 6인 팀만 필터링
total_seasons = df_model["season"].nunique()
team_season_count = df_model.groupby("team")["season"].nunique()
all_season_teams = team_season_count[team_season_count == total_seasons].index

# 2. 전 시즌 참가 & 30경기 이상 참가 팀 필터링
team_summary_filtered = team_summary[
    (team_summary["team"].isin(all_season_teams)) & 
    (team_summary["n_matches"] >= 30)
].copy()

print(f"조건 만족 팀 수 (전 시즌({total_seasons}시즌) 참가 & 30경기 이상): {len(team_summary_filtered)}")

# 3. 각 군집별로 해당 군집이 Dominant(주력)인 팀들을 추출하여 상위 10개 출력
for cl in hier_order:
    df_cl = team_summary_filtered[team_summary_filtered["dominant_cluster"] == cl].copy()
    
    # 해당 군집의 비율(%)이 높은 순으로 정렬
    col = cluster_pct_cols[cl]
    df_display = df_cl.sort_values(col, ascending=False).head(10)[["team", "n_matches"] + list(cluster_pct_cols.values()) + ["dominant_cluster_name"]]
    
    # 출력용 헤더 한글화
    df_display.columns = ["팀명", "경기수"] + list(cluster_name_full.values()) + ["주력 전술"]
    
    print(f"\n[주력 전술이 '{cluster_name_full[cl]}'인 팀 상위 10개]")
    display(df_display)

# 4. 저장
team_summary_filtered.to_csv(OUT_TABLE_DIR / "rq1_team_all_seasons_distribution_top10.csv", index=False, encoding="utf-8-sig")
print(f"\nSaved: rq1_team_all_seasons_distribution_top10.csv")

# %% [code] Notebook cell 31


