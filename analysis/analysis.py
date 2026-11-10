"""Re-analysis of the QuASoQ 2026 replication data (popolin47/Library_recommendation)."""
import sys, json
import numpy as np, pandas as pd
from scipy import stats
import scikit_posthocs as sp

D = sys.argv[1]  # data dir
TIERS = ['top', 'middle', 'bottom']
TEMPS = {'0': 0.0, '0.2': 0.2, '0.4': 0.4}
out = {}

def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((x > b).sum() for x in a); lt = sum((x < b).sum() for x in a)
    return (gt - lt) / (len(a) * len(b))

def mag(d):
    d = abs(d)
    return 'negligible' if d < .147 else 'small' if d < .33 else 'medium' if d < .474 else 'large'

def kw(df, val, group='tier'):
    g = [df.loc[df[group] == t, val].dropna().values for t in TIERS]
    H, p = stats.kruskal(*g)
    n = sum(len(x) for x in g)
    eps2 = H / ((n**2 - 1) / (n + 1))
    dunn = sp.posthoc_dunn(df.dropna(subset=[val]), val_col=val, group_col=group, p_adjust='holm')
    pairs = {}
    for a, b in [('top', 'middle'), ('middle', 'bottom'), ('top', 'bottom')]:
        d = cliffs_delta(df.loc[df[group] == a, val].dropna(), df.loc[df[group] == b, val].dropna())
        pairs[f'{a}-{b}'] = dict(p_holm=float(dunn.loc[a, b]), delta=round(float(d), 3), mag=mag(d))
    return dict(H=round(float(H), 2), p=float(p), eps2=round(float(eps2), 3), n=n,
                medians={t: round(float(np.median(x)), 3) for t, x in zip(TIERS, g)},
                means={t: round(float(np.mean(x)), 3) for t, x in zip(TIERS, g)}, pairs=pairs)

human = pd.read_csv(f'{D}/lib_list.csv').rename(columns={'source': 'tier', 'fog_index': 'gfi_h'})
human['wc_h'] = human.description.fillna('').str.split().str.len()

runs = []
for k, t in TEMPS.items():
    r = pd.read_csv(f'{D}/RQ2_readability/{k}_description_RQ2.csv')
    r['T'] = t
    runs.append(r)
runs = pd.concat(runs).rename(columns={'Library': 'library', 'Popularity': 'tier'})
runs['wc_ai'] = runs.Description.fillna('').str.split().str.len()

# per library per T: average of 5 runs
lib = runs.groupby(['T', 'library', 'tier'], as_index=False).agg(
    cos=('Cosine_sim', 'mean'), gfi_ai=('Gunning_Fog_Index', 'mean'), wc_ai=('wc_ai', 'mean'))
lib = lib.merge(human[['library', 'gfi_h', 'wc_h', 'description']], on='library', how='left')
lib['gfi_diff'] = lib.gfi_ai - lib.gfi_h
lib['wc_diff'] = lib.wc_ai - lib.wc_h
assert lib.gfi_h.notna().all(), 'unmatched human rows'

# ---- dataset statistics
dep = []
ori = pd.read_csv(f'{D}/dataset/Ori_lib_list.csv')
for t in TIERS:
    x = pd.read_csv(f'{D}/dataset/{t}_lib.csv')
    x['tier'] = t
    dep.append(x)
dep = pd.concat(dep)
ds = {}
for t in TIERS:
    h = human[human.tier == t]
    a = lib[(lib.tier == t) & (lib['T'] == 0.0)]
    d = dep[dep.tier == t].Num_Dependents
    ds[t] = dict(n_orig=int((dep.tier == t).sum()), n=len(h),
                 dep_min=int(d.min()), dep_med=float(d.median()), dep_max=int(d.max()),
                 wc_h_med=float(h.wc_h.median()), wc_h_q1=float(h.wc_h.quantile(.25)), wc_h_q3=float(h.wc_h.quantile(.75)),
                 wc_ai_med=float(a.wc_ai.median()), wc_ai_q1=float(a.wc_ai.quantile(.25)), wc_ai_q3=float(a.wc_ai.quantile(.75)),
                 gfi_h_med=float(h.gfi_h.median()), gfi_ai_med=float(a.gfi_ai.median()),
                 short_h=int((h.wc_h < 5).sum()))
out['dataset'] = ds

# ---- RQ1 + RQ2 per temperature
for t in TEMPS.values():
    x = lib[lib['T'] == t]
    out[f'T={t}'] = dict(cos=kw(x, 'cos'), wc_diff=kw(x, 'wc_diff'), gfi_diff=kw(x, 'gfi_diff'))
    w = stats.wilcoxon(x.gfi_ai, x.gfi_h)
    ww = stats.wilcoxon(x.wc_ai, x.wc_h)
    out[f'T={t}']['ai_vs_human'] = dict(
        gfi_wilcoxon_p=float(w.pvalue), gfi_delta=round(float(cliffs_delta(x.gfi_ai, x.gfi_h)), 3),
        gfi_med_ai=float(x.gfi_ai.median()), gfi_med_h=float(x.gfi_h.median()),
        gfi_diff_med=float(x.gfi_diff.median()), frac_ai_harder=float((x.gfi_diff > 0).mean()),
        wc_wilcoxon_p=float(ww.pvalue), wc_diff_med=float(x.wc_diff.median()))
    # sensitivity: exclude fragment-like human descriptions (<5 words)
    xs = x[x.wc_h >= 5]
    out[f'T={t}']['gfi_sensitivity_wc5'] = dict(
        n=len(xs), diff_med=float(xs.gfi_diff.median()), frac_ai_harder=float((xs.gfi_diff > 0).mean()),
        wilcoxon_p=float(stats.wilcoxon(xs.gfi_ai, xs.gfi_h).pvalue),
        delta=round(float(cliffs_delta(xs.gfi_ai, xs.gfi_h)), 3), kw=kw(xs, 'gfi_diff'))

# ---- temperature effect within tier (Friedman: same libraries across T)
tempfx = {}
for tier in TIERS:
    piv = lib[lib.tier == tier].pivot(index='library', columns='T', values='cos').dropna()
    f = stats.friedmanchisquare(*[piv[c] for c in piv.columns])
    W = f.statistic / (len(piv) * (piv.shape[1] - 1))
    pg = lib[lib.tier == tier].pivot(index='library', columns='T', values='gfi_ai').dropna()
    fg = stats.friedmanchisquare(*[pg[c] for c in pg.columns])
    tempfx[tier] = dict(cos_chi2=round(float(f.statistic), 2), cos_p=float(f.pvalue), cos_W=round(float(W), 4),
                        cos_means={str(c): round(float(piv[c].mean()), 4) for c in piv.columns},
                        gfi_chi2=round(float(fg.statistic), 2), gfi_p=float(fg.pvalue),
                        gfi_W=round(float(fg.statistic / (len(pg) * 2)), 4))
out['temperature_effect'] = tempfx

# run-to-run variability of cosine (per library std over 5 runs)
sd = runs.groupby(['T', 'library']).Cosine_sim.std()
out['run_sd_cos'] = {str(t): round(float(sd.loc[t].median()), 4) for t in TEMPS.values()}

# also try to reproduce the paper's H for GFI on run-level raw AI GFI by tier
for t in TEMPS.values():
    r = runs[runs['T'] == t]
    g = [r.loc[r.tier == k, 'Gunning_Fog_Index'] for k in TIERS]
    out[f'T={t}']['repro_run_level_gfi_ai_H'] = round(float(stats.kruskal(*g).statistic), 2)
    rr = r.merge(human[['library', 'gfi_h']], on='library')
    g = [(rr.Gunning_Fog_Index - rr.gfi_h)[rr.tier == k] for k in TIERS]
    out[f'T={t}']['repro_run_level_gfi_diff_H'] = round(float(stats.kruskal(*g).statistic), 2)

lib.to_csv(sys.argv[2] + '/per_library.csv', index=False)
print(json.dumps(out, indent=1, default=str))
