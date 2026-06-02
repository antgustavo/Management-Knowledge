#!/usr/bin/env python3
"""
Closes the two database-dependent reviewer points, run LOCALLY against the Neo4j
instance loaded from the provided dump:

  (6B-3) DIRECT query-level correctness: does each generated Cypher return the same
         result set as the gold Cypher?  (judged on normalised returned values, so
         it is robust to RETURN-projection differences such as `RETURN p` vs
         `RETURN p.nomePessoa`).
  (6B-4) GRAPH STATISTICS: node counts per label and relationship counts per type.

Setup:
  1. Load the dump into a fresh database, e.g.:
        neo4j-admin database load neo4j --from-path=/path/to/dumpdir --overwrite-destination=true
     (or restore via Neo4j Desktop), then start Neo4j.
  2. pip install neo4j numpy
  3. NEO4J_URI=bolt://localhost:7687 NEO4J_USER=neo4j NEO4J_PASS=yourpass \
        python query_level_eval.py
Inputs (same dir): evaluation_GPT4_claudejudge.csv, evaluation_HF27B_claudejudge.csv,
                   evaluation_HF27B+GPT4_claudejudge.csv
Output: prints the metrics and writes query_level_results.csv
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

driver = GraphDatabase.driver(URI, auth=(USER, PASS))

def scalars(value):
    """Flatten any Cypher return value into a set of normalised scalar tokens."""
    out = set()
    def walk(v):
        if v is None: return
        if isinstance(v, dict):              # node/relationship properties
            for x in v.values(): walk(x)
        elif isinstance(v, (list, tuple, set)):
            for x in v: walk(x)
        elif hasattr(v, "items"):            # neo4j Node/Relationship
            for x in dict(v).values(): walk(x)
        else:
            out.add(str(v).strip().lower())
    walk(value)
    return out

def run(tx_cypher):
    """Return a normalised frozenset describing the result set, or None on error."""
    try:
        with driver.session() as s:
            rows = s.run(tx_cypher).data()
        # row -> frozenset of scalar tokens; result -> frozenset of those rows
        return frozenset(frozenset(scalars(r)) for r in rows)
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

# ---- (6B-4) graph statistics ----
print("="*60, "\nGRAPH STATISTICS\n", "="*60)
with driver.session() as s:
    labels = s.run("MATCH (n) UNWIND labels(n) AS l RETURN l, count(*) AS c ORDER BY c DESC").data()
    rels   = s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS c ORDER BY c DESC").data()
    nN = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    nR = s.run("MATCH ()-->() RETURN count(*) AS c").single()["c"]
print(f"Total nodes={nN}, relationships={nR}")
print("Nodes per label:", {d['l']: d['c'] for d in labels})
print("Relationships per type:", {d['t']: d['c'] for d in rels})

# ---- (6B-3) direct query-level correctness ----
print("\n", "="*60, "\nDIRECT QUERY-LEVEL CORRECTNESS (result-set match vs gold)\n", "="*60)
out_rows = []
for cfg, fn in FILES.items():
    rows = list(csv.DictReader(open(fn, encoding='utf-8-sig')))
    correct = 0; by = {}
    for r in rows:
        gid = int(r['id'])
        gold = run(r['gold_cypher']); gen = run(r['generated_cypher'])
        ok = (gold is not None and gen is not None and gold == gen)
        correct += ok
        c = qclass(r['gold_cypher']); by.setdefault(c, [0,0]); by[c][0]+=ok; by[c][1]+=1
        out_rows.append({'config':cfg,'id':gid,'query_class':c,'query_correct':int(ok),
                         'generated_executed':int(gen is not None)})
    n=len(rows); est,lo,hi = wilson(correct, n)
    print(f"\n{cfg}: query-level accuracy {correct}/{n} = {est:.1f}% (95% CI [{lo:.0f},{hi:.0f}])")
    for c,(k,m) in by.items():
        print(f"    {c:15} {k}/{m} ({100*k/m:.0f}%)")

with open('query_level_results.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f, fieldnames=['config','id','query_class','query_correct','generated_executed'])
    w.writeheader(); w.writerows(out_rows)
print("\nPer-item results written to query_level_results.csv")
driver.close()
