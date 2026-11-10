"""Regenerate Fig 4: GFI difference (AI - human) per library, styled like Fig 2."""
import sys
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

lib = pd.read_csv(sys.argv[1])
out = sys.argv[2]
TIERS = ['bottom', 'middle', 'top']
COLORS = {'bottom': '#c6dceb', 'middle': '#74acd2', 'top': '#cfe9b3'}
TEMPS = [0.0, 0.2, 0.4]

fig, ax = plt.subplots(figsize=(12, 7.6), dpi=200)
pos, data, cols, top_ticks = [], [], [], []
for i, t in enumerate(TEMPS):
    base = i * 4
    for j, tier in enumerate(TIERS):
        p = base + j
        pos.append(p); top_ticks.append((p, tier.capitalize()))
        data.append(lib[(lib['T'] == t) & (lib.tier == tier)].gfi_diff.values)
        cols.append(COLORS[tier])
bp = ax.boxplot(data, positions=pos, widths=0.65, patch_artist=True,
                medianprops=dict(color='black', linewidth=1.5),
                flierprops=dict(marker='o', markerfacecolor='none', markeredgecolor='black', markersize=6))
for patch, c in zip(bp['boxes'], cols):
    patch.set_facecolor(c); patch.set_edgecolor('#555555'); patch.set_linewidth(1.5)
ax.axhline(0, color='#888888', linewidth=1, linestyle='--')
ax.set_xticks([1, 5, 9]); ax.set_xticklabels(['T=0', 'T=0.2', 'T=0.4'], fontsize=20)
ax.yaxis.grid(True, linestyle=':', color='#cccccc'); ax.set_axisbelow(True)
ax.tick_params(axis='y', labelsize=14)
ax.set_ylabel('GFI difference (AI − human)', fontsize=15)
sec = ax.secondary_xaxis('top')
sec.set_xticks([p for p, _ in top_ticks]); sec.set_xticklabels([l for _, l in top_ticks], fontsize=14)
ax.set_xlim(-0.8, 10.8)
fig.tight_layout()
fig.savefig(out)
