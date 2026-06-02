#!/usr/bin/env python3
"""
Reproduces all quantitative results in the paper from the labelled evaluation CSVs.

Inputs (same directory):
  evaluation_GPT4_claudejudge.csv
  evaluation_HF27B_claudejudge.csv
  evaluation_HF27B+GPT4_claudejudge.csv
Each row has: id, question, gold_cypher, generated_cypher, cypher_executable,
gold_answer, generated_answer, bert_score_f1, factual_consistency
(GPT-4/Hybrid files also keep the older GPT-4-judge label in
 factual_consistency_gpt4judge, used only for the judge-agreement check).

Outputs: prints every number used in the paper and writes bertscore_boxplot.png.
Requires: numpy, scipy, statsmodels, matplotlib  (pip install ...)
"""
import csv, re
import numpy as np
from collections import Counter
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar

C, P, I = 'CONSISTENTE', 'PARCIALMENTE CONSISTENTE', 'INCONSISTENTE'
FILES = {'GPT-4':'evaluation_GPT4_claudejudge.csv',
         'HF27B':'evaluation_HF27B_claudejudge.csv',
         'Hybrid':'evaluation_HF27B+GPT4_claudejudge.csv'}

def load(fn):
    return {int(r['id']): r for r in csv.DictReader(open(fn, encoding='utf-8-sig'))}
data = {k: load(v) for k, v in FILES.items()}
ids = sorted(data['GPT-4'])
def lab(cfg, i):  # Claude judge label (primary)
    return data[cfg][i]['factual_consistency'].strip().upper()
def is_consistent(cfg, i):
    return lab(cfg, i) == C

# ---------- Wilson score 95% confidence interval for a proportion ----------
def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z*z/n
    centre = (p + z*z/(2*n)) / den
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return 100*centre, 100*(centre-half), 100*(centre+half)

print("="*70, "\n1) FACTUAL CONSISTENCY (Claude judge) + Wilson 95% CI\n", "="*70)
for cfg in FILES:
    cnt = Counter(lab(cfg, i) for i in ids)
    k = cnt[C]; est, lo, hi = wilson(k, len(ids))
    print(f"{cfg:7} Consistent={k}/{len(ids)} = {est:.1f}%  CI[{lo:.1f},{hi:.1f}]  "
          f"(Partial={cnt[P]}, Inconsistent={cnt[I]})")

# ---------- McNemar exact test (paired, binary 'Consistent') ----------
def mcnemar_pair(a, b):
    t = Counter()
    for i in ids:
        t[(is_consistent(a, i), is_consistent(b, i))] += 1
    b01 = t[(False, True)]; b10 = t[(True, False)]      # discordant cells
    table = [[t[(True, True)], b10], [b01, t[(False, False)]]]
    res = mcnemar(table, exact=True)                    # binomial exact test
    return b10, b01, res.pvalue
print("\n", "="*70, "\n2) McNemar exact test (Consistent vs not), paired by id\n", "="*70)
for a, b in [('GPT-4','HF27B'), ('GPT-4','Hybrid'), ('HF27B','Hybrid')]:
    only_a, only_b, p = mcnemar_pair(a, b)
    print(f"{a} vs {b}: discordant {a}-only={only_a}, {b}-only={only_b}  ->  exact p={p:.4f}")

# ---------- Cohen's kappa: Claude judge vs original GPT-4 judge ----------
def norm(x):
    x = x.upper()
    return P if 'PARCIAL' in x else C if x.startswith('CONSIST') else I if 'INCON' in x else 'ERR'
def kappa_binary(cfg):
    items = [i for i in ids
             if norm(data[cfg][i].get('factual_consistency_gpt4judge','')) != 'ERR']
    n = len(items)
    mine  = [1 if is_consistent(cfg, i) else 0 for i in items]                      # Claude
    other = [1 if norm(data[cfg][i]['factual_consistency_gpt4judge']) == C else 0   # GPT-4 judge
             for i in items]
    po = sum(x == y for x, y in zip(mine, other)) / n            # observed agreement
    pm, po_ = np.mean(mine), np.mean(other)
    pe = pm*po_ + (1-pm)*(1-po_)                                 # chance agreement
    kappa = (po - pe) / (1 - pe)
    exact3 = sum(1 for i in items
                 if lab(cfg, i) == norm(data[cfg][i]['factual_consistency_gpt4judge']))
    return n, 100*exact3/n, 100*po, kappa
print("\n", "="*70, "\n3) Judge agreement: Claude vs original GPT-4 judge (Cohen's kappa)\n", "="*70)
for cfg in ['GPT-4','Hybrid']:   # only these keep the GPT-4-judge column
    n, ex3, agr, k = kappa_binary(cfg)
    print(f"{cfg:6} (n={n} scored by GPT-4 judge): 3-way exact={ex3:.0f}%, "
          f"binary agreement={agr:.0f}%, Cohen kappa={k:.2f}")

# ---------- BERTScore: box plot + Kruskal-Wallis + Wilcoxon ----------
bs = {cfg: np.array([float(data[cfg][i]['bert_score_f1']) for i in ids]) for cfg in FILES}
print("\n", "="*70, "\n4) BERTScore F1 distribution tests\n", "="*70)
H, p = stats.kruskal(*bs.values())
print(f"Kruskal-Wallis: H={H:.2f}, p={p:.4f}")
for a, b in [('GPT-4','HF27B'), ('GPT-4','Hybrid'), ('HF27B','Hybrid')]:
    w, pp = stats.wilcoxon(bs[a], bs[b])   # paired, two-sided
    print(f"Wilcoxon signed-rank {a} vs {b}: p={pp:.4f}")

# ---------- Query-class breakdown (from gold Cypher structure) ----------
def qclass(cy):
    if re.search(r'count\s*\(|sum\s*\(|avg\s*\(', cy, re.I): return 'Aggregation'
    r = cy.count('-[')
    return 'Property lookup' if r==0 else 'Single-hop' if r==1 else 'Multi-pattern'
cls = {i: qclass(data['GPT-4'][i]['gold_cypher']) for i in ids}
print("\n", "="*70, "\n5) Consistent rate by query class (Claude judge)\n", "="*70)
for c in ['Property lookup','Single-hop','Multi-pattern','Aggregation']:
    sub = [i for i in ids if cls[i]==c]; n=len(sub)
    rates = {cfg: sum(is_consistent(cfg,i) for i in sub) for cfg in FILES}
    print(f"{c:15} n={n:2}  " + "  ".join(f"{cfg} {rates[cfg]}/{n}({100*rates[cfg]/n:.0f}%)" for cfg in FILES))

# ---------- Box plot ----------
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7,4.2))
    order=['GPT-4','HF27B','Hybrid']; vals=[bs[c] for c in order]
    bp=ax.boxplot(vals, tick_labels=['GPT-4','HF 27B','Hybrid\n(HF 27B+GPT-4)'],
                  showmeans=True, patch_artist=True, widths=0.55,
                  medianprops=dict(color='black',linewidth=1.5),
                  meanprops=dict(marker='D',markerfacecolor='white',markeredgecolor='black',markersize=6))
    for patch,c in zip(bp['boxes'], ['#4C72B0','#DD8452','#55A868']):
        patch.set_facecolor(c); patch.set_alpha(0.65)
    for k,v in enumerate(vals,1):
        x=np.random.default_rng(0).normal(k,0.05,len(v)); ax.scatter(x,v,s=10,color='black',alpha=0.25,zorder=3)
    ax.set_ylabel('BERTScore F1'); ax.set_ylim(0,1.02); ax.yaxis.grid(True,linestyle='--',alpha=0.4)
    ax.set_title('BERTScore F1 distribution by configuration (n=95)'); plt.tight_layout()
    plt.savefig('bertscore_boxplot.png', dpi=200)
    print("\n[box plot written to bertscore_boxplot.png]")
except Exception as e:
    print("box plot skipped:", e)
