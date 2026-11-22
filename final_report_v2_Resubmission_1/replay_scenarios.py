#!/usr/bin/env python3
"""Offline financial arithmetic only. No network, models, judges or benchmark data."""
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parent
p = json.loads((ROOT/'cost_inputs.json').read_text())
expected = json.loads((ROOT/'scenario_results.json').read_text())
assert p['original_displayed_savings']-p['original_displayed_cost'] == p['original_displayed_net'] == 88440
unit = p['volume']*p['manual_sec']/3600*p['rate_staff']
rows=[]
for x,ref in zip(p['scenarios'],expected['scenarios'],strict=True):
    extra=p['volume']*x['escalation_share']*x['incremental_minutes']/60*p['rate_staff']
    cost=p['original_unrounded_cost']+extra
    benefit=unit*x['usable_proxy']
    row={**x,'escalation':extra,'cost':cost,'savings':benefit,'net':benefit-cost,'roi':(benefit-cost)/cost}
    for k,v in row.items():
        if isinstance(v,(float,int)): assert math.isclose(v,ref[k],rel_tol=1e-12,abs_tol=1e-8),(x['name'],k,v,ref[k])
        else: assert v==ref[k]
    rows.append(row)
assert math.isclose(rows[0]['net']/p['volume']/p['rate_staff']*3600,expected['max_extra_seconds_per_question'])
assert math.isclose(p['original_unrounded_cost']/unit,expected['breakeven_usable_no_escalation'])
assert math.isclose(rows[4]['cost']/unit,expected['breakeven_usable_5pct_5min'])
assert round(rows[2]['net']) == -10482
assert round(rows[4]['net']) == -21965
print(json.dumps({'verified':True,'scenarios':len(rows),'historical_displayed_net':p['original_displayed_net'],
                  'net_values_rounded':[round(x['net']) for x in rows],
                  'scope':'Economic arithmetic only; no measurement or semantic audit'},indent=2))
