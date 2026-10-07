"""Audit local research snapshots without changing inputs or fitting models.
Usage: python scripts/verify_snapshot.py --source-root /path/to/research --output-dir /new/audit
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

FEATURES = ['possession','passes','long_balls','final_third_entries',
            'goalkeeping_goal_kicks','ppda_val','DEEP','crosses','dribbles',
            'box_shots','shots','tackles','interceptions','clearances']
KEY = ['league', 'match_id', 'team']
PAPER_COUNTS = {'1-1':6487,'1-2':2855,'2-1':4017,'2-2':8035}
PAPER_MEANS = np.array([
 [56.48,65.50,35.60,46.60],[421.11,541.20,248.46,319.49],
 [54.35,45.77,55.09,59.18],[58.58,68.89,39.71,50.90],
 [6.30,4.73,10.34,8.12],[9.85,8.22,20.59,12.33],
 [7.45,12.56,3.17,4.75],[21.09,25.60,10.78,16.00],
 [17.12,18.99,13.75,15.31],[9.35,13.39,4.90,6.67],
 [14.42,19.98,7.82,10.70],[15.72,14.70,16.47,16.77],
 [9.00,7.72,10.38,10.24],[14.82,10.94,26.57,20.00]])

def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def audit(root, out):
    paths = {'input':'data/processed/tactical_analysis_cleaned.csv',
             'labeled':'outputs/tables/rq1_final_data_14vars_hierarchical_4clusters.csv'}
    source = pd.read_csv(root / paths['input'])
    labeled = pd.read_csv(root / paths['labeled'])
    checks = {}
    for name, frame in [('input', source), ('labeled', labeled)]:
        checks[name] = {
            'shape': list(frame.shape), 'sha256': sha256(root / paths[name]),
            'path': paths[name], 'dtypes':frame.dtypes.astype(str).to_dict(),
            'duplicate_rows': int(frame.duplicated().sum()),
            'duplicate_team_match_keys': int(frame.duplicated(KEY).sum()),
            'nulls_by_column':frame.isna().sum().astype(int).to_dict(),
            'feature_missing_cells':int(frame[FEATURES].isna().sum().sum()),
            'nonfinite_feature_cells':int((~np.isfinite(frame[FEATURES].to_numpy(float))).sum()),
            'date_min':str(frame.date.min()), 'date_max':str(frame.date.max()),
            'leagues':frame.league.value_counts().sort_index().to_dict(),
            'seasons':frame.season.value_counts().sort_index().to_dict()}
    joined = source[KEY + FEATURES].merge(labeled[KEY + FEATURES], on=KEY,
                how='outer', validate='one_to_one', suffixes=('_input','_labeled'), indicator=True)
    differences = {f:int((~np.isclose(joined[f+'_input'],joined[f+'_labeled'],equal_nan=True)).sum()) for f in FEATURES}
    sizes = labeled.groupby(['league','match_id']).size()
    pair_issues = 0
    for _, group in source.groupby(['league','match_id'], sort=False):
        if len(group) != 2:
            pair_issues += 1
            continue
        a,b = group.iloc[0],group.iloc[1]
        if not (a.team == b.opponent and b.team == a.opponent and
                a.team_score == b.opponent_score and b.team_score == a.opponent_score and
                a.is_home + b.is_home == 1 and a.date == b.date):
            pair_issues += 1
    checks['join'] = {'rows':len(joined),'membership':joined['_merge'].value_counts().to_dict(),
                      'feature_mismatches':differences}
    checks['match_pairs'] = {'unique_league_match_ids':len(sizes),
                            'rows_per_match':sizes.value_counts().to_dict(),
                            'reciprocal_team_score_home_date_failures':pair_issues}
    checks['range_flags'] = {'possession_outside_0_100':int((~source.possession.between(0,100)).sum()),
                            'negative_feature_cells':int((source[FEATURES]<0).sum().sum()),
                            'box_shots_above_shots':int((source.box_shots>source.shots).sum())}
    counts = labeled.groupby('cluster_final_hier').size().reindex(PAPER_COUNTS)
    summary = pd.DataFrame({'cluster':counts.index,'current_csv_n':counts.values,
             'current_csv_pct':counts.values/len(labeled)*100,
             'thesis_table8_n':list(PAPER_COUNTS.values())})
    summary['current_minus_thesis'] = summary.current_csv_n-summary.thesis_table8_n
    profile = labeled.groupby('cluster_final_hier')[FEATURES].mean().reindex(PAPER_COUNTS)
    checks['thesis_table7'] = {'all_56_means_match_at_2dp':bool(np.array_equal(profile.to_numpy().T.round(2),PAPER_MEANS)),
                              'source':'Submitted thesis, printed p.23 / PDF p.32, Table 7'}
    checks['thesis_table8'] = {'all_cluster_counts_match':bool((summary.current_minus_thesis==0).all()),
                              'source':'Submitted thesis, printed p.24 / PDF p.33, Table 8'}
    ct = pd.crosstab(labeled.season,labeled.cluster_final_hier)
    chi,p,dof,expected = chi2_contingency(ct)
    checks['season_association'] = {'chi2':float(chi),'p':float(p),'dof':int(dof),
        'cramers_v':float(np.sqrt(chi/(ct.to_numpy().sum()*(min(ct.shape)-1)))),
        'interpretation':'Descriptive association; repeated teams and paired matches are not independent.'}
    checks['verification_scope'] = 'Saved CSV audit only; no clustering/classifier retraining, provider-source or merge-provenance validation.'
    checks['runtime'] = {'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__}
    # Refuse to replace existing review evidence, or write inside the original research folder.
    out = out.resolve()
    if out == root.resolve() or root.resolve() in out.parents:
        raise ValueError('Choose a separate output directory outside the original research folder.')
    out.mkdir(parents=True,exist_ok=True)
    targets = ['snapshot_audit.json','cluster_counts.csv','cluster_profile.csv','coverage.csv','feature_ranges.csv','league_cluster_share.csv','season_cluster_share.csv']
    if any((out/f).exists() for f in targets):
        raise FileExistsError('Output already exists; choose a new directory to preserve prior evidence.')
    (out/'snapshot_audit.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    summary.to_csv(out/'cluster_counts.csv',index=False)
    profile.to_csv(out/'cluster_profile.csv')
    labeled.groupby(['league','season']).size().rename('team_match_rows').to_csv(out/'coverage.csv')
    source[FEATURES].agg(['min','max']).T.to_csv(out/'feature_ranges.csv')
    for col in ['league','season']:
        pd.crosstab(labeled[col],labeled.cluster_final_hier,normalize='index').mul(100).to_csv(out/f'{col}_cluster_share.csv')
    print(json.dumps({'rows':len(labeled),'unique_matches':len(sizes),
        'table7_means_match':checks['thesis_table7']['all_56_means_match_at_2dp'],
        'table8_counts_match':checks['thesis_table8']['all_cluster_counts_match'],
        'feature_mismatches':sum(differences.values()),'pair_issues':pair_issues,
        'range_flags':checks['range_flags']},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    audit(args.source_root,args.output_dir)
