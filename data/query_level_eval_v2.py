#!/usr/bin/env python3
"""
Projection-robust query-level correctness (run LOCALLY against the loaded Neo4j).

The v1 script required *exact* result-set identity, which is dominated by RETURN
projection differences (e.g. `RETURN p` vs `RETURN p.nomePessoa`) and therefore
understates correctness. This v2 compares the set of ENTITY NAMES each query
returns, which is invariant to projection:

  * from a returned node (whole node), keep properties whose key starts with
    nome/titulo/tema (the human-readable name);
  * from a projected scalar column (e.g. 'p.nomePessoa'), keep it if the column
    name ends in nome/titulo/tema;
  * numeric results (counts/aggregations) are compared as numbers.

Two metrics per item:
  exact_name_match : generated name-set == gold name-set (no missing, no extra)
  gold_recall_1    : generated name-set CONTAINS every gold name (recall = 1.0)

Setup: load the dump, start Neo4j, `pip install neo4j numpy`, then
  NEO4J_PASS=yourpass python query_level_eval_v2.py
Inputs: the three evaluation_*_claudejudge.csv files. Output: prints metrics and
writes query_level_results_v2.csv.
"""
import os, csv, re
import numpy as np
from neo4j import GraphDatabase

URI  = os.environ.get("NEO4J_URI",  "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER", "neo4j")
PASS = os.environ.get("NEO4J_PASS", "password")
FILES = {'GPT-4':'evaluation_GPT4_claudejudge.csv',
         'HF27B':'evaluation_HF27B_claudejudge.csv',
         'Hybrid':'evaluation_HF27B+GPT4_claudejudge.csv'}
NAME_KEY = re.compile(r'(nome|titulo|tema)', re.I)
driver = GraphDatabase.driver(URI, auth=(USER, PASS))

def names_and_numbers(rows):
    names, nums = set(), []
    for row in rows:
        for key, val in row.items():
            if isinstance(val, dict):                      # whole node returned
                for pk, pv in val.items():
                    if NAME_KEY.search(pk) and pv is not None:
                        names.add(str(pv).strip().lower())
            elif isinstance(val, bool):
                pass
            elif isinstance(val, (int, float)):
                nums.append(float(val))
            elif val is not None:                          # projected scalar
                col = key.split('.')[-1]
                if NAME_KEY.search(col):
                    names.add(str(val).strip().lower())
    return names, sorted(nums)

def run(cy):
    try:
        with driver.session() as s:
            return names_and_numbers(s.run(cy).data())
    except Exception:
        return None

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0, 0)
    p = k/n; den = 1+z*z/n
    c = (p+z*z/(2*n))/den; h = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return 100*c, 100*(c-h), 100*(c+h)

def qclass(cy):
    if re.search(r'count\s*\(|sum\s*\(|avg\s*\(', cy, re.I): return 'Aggregation'
    r = cy.count('-[')
    return 'Property lookup' if r==0 else 'Single-hop' if r==1 else 'Multi-pattern'

out = []
print("="*64, "\nPROJECTION-ROBUST QUERY-LEVEL CORRECTNESS (entity names)\n", "="*64)
for cfg, fn in FILES.items():
    rows = list(csv.DictReader(open(fn, encoding='utf-8-sig')))
    exact = recall1 = 0; by = {}
    for r in rows:
        g = run(r['gold_cypher']); h = run(r['generated_cypher'])
        if g is None or h is None:
            em = rc = False
        else:
            gn, gnum = g; hn, hnum = h
            em = (gn == hn) and (gnum == hnum)
            rc = (gn <= hn) and (set(gnum) <= set(hnum)) if (gn or gnum) else (not hn and not hnum)
        exact += em; recall1 += rc
        c = qclass(r['gold_cypher']); d = by.setdefault(c, [0,0,0]); d[0]+=em; d[1]+=rc; d[2]+=1
        out.append({'config':cfg,'id':int(r['id']),'query_class':c,
                    'exact_name_match':int(em),'gold_recall_1':int(rc)})
    n=len(rows)
    e,el,eh = wilson(exact,n); rr,rl,rh = wilson(recall1,n)
    print(f"\n{cfg}: exact name-set match {exact}/{n} = {e:.0f}% CI[{el:.0f},{eh:.0f}] | "
          f"gold entities fully recovered {recall1}/{n} = {rr:.0f}% CI[{rl:.0f},{rh:.0f}]")
    for c,(em,rc,m) in by.items():
        print(f"    {c:15} exact {em}/{m} ({100*em/m:.0f}%), recall=1 {rc}/{m} ({100*rc/m:.0f}%)")

with open('query_level_results_v2.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f, fieldnames=['config','id','query_class','exact_name_match','gold_recall_1'])
    w.writeheader(); w.writerows(out)
print("\nPer-item results -> query_level_results_v2.csv")
driver.close()
