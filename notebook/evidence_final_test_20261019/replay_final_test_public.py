"""Recompute Oct. 19 final-test aggregate metrics from privacy-scrubbed public rating rows.

No benchmark text, source passage, expected answer, model answer, raw judge request/response,
reviewer identity or timestamp is available to this replay. It reproduces the reported arithmetic,
not the underlying model responses or a fresh semantic judgment.
"""
from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def wilson(k, n, z=1.96):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(100 * (c - m) / d, 1), round(100 * (c + m) / d, 1))


def rate(k, n):
    return {'k': k, 'n': n, 'pct': None if n == 0 else round(100 * k / n, 1), 'wilson95': list(wilson(k, n))}


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n), 6)


def load_rows():
    return [json.loads(line) for line in (HERE / 'final_ratings_public.jsonl').read_text().splitlines() if line.strip()]


def replay():
    rows = load_rows()
    assert len(rows) == 600 and len({r['pair_id'] for r in rows}) == 150
    assert Counter(r['passage'] for r in rows) == {'full': 300, 'cut60': 300}
    by = defaultdict(dict)
    for r in rows:
        by[(r['pair_id'], r['passage'])][r['condition']] = r

    result = {'conditions': ['base', 'adapter']}
    answer_pairs = sorted({r['pair_id'] for r in rows if r['answerable']})
    prim = {}
    for cond in ('base', 'adapter'):
        selected = [r for r in rows if r['passage'] == 'full' and r['condition'] == cond and r['answerable']]
        prim[cond] = rate(sum(r['pass'] for r in selected), len(selected))
    base_only = sum(by[(q, 'full')]['base']['pass'] and not by[(q, 'full')]['adapter']['pass'] for q in answer_pairs)
    adapter_only = sum(by[(q, 'full')]['adapter']['pass'] and not by[(q, 'full')]['base']['pass'] for q in answer_pairs)
    result['primary_answerable_main'] = {**prim, 'diff_points': round(prim['adapter']['pct'] - prim['base']['pct'], 1),
        'mcnemar': {'base_only_pass': base_only, 'adapter_only_pass': adapter_only,
                    'exact_two_sided_p': mcnemar_exact(base_only, adapter_only)}}
    result['unsupported_claim_main'] = {c: rate(sum(r['unsupported_claim'] for r in rows if r['passage']=='full' and r['condition']==c),150)
                                       for c in ('base','adapter')}
    result['citation_correctness_main'] = {}
    for c in ('base','adapter'):
        sel=[r for r in rows if r['passage']=='full' and r['condition']==c and r['answerable'] and not r['abstained']]
        result['citation_correctness_main'][c]={**rate(sum(r['citation_code']=='correct' for r in sel),len(sel)),
                                                'breakdown':dict(Counter(r['citation_code'] for r in sel))}
    result['correct_abstention_main']={c:rate(sum(r['pass'] for r in rows if r['passage']=='full' and r['condition']==c and not r['answerable']),30)
                                      for c in ('base','adapter')}
    strata={q:by[(q,'full')]['base']['cut_stratum'] for q in answer_pairs}
    robust={}
    for c in ('base','adapter'):
        surv=[q for q in answer_pairs if strata[q]=='evidence_survives_cut']
        rem=[q for q in answer_pairs if strata[q]=='evidence_removed_by_cut']
        sm=sum(by[(q,'full')][c]['pass'] for q in surv); sc=sum(by[(q,'cut60')][c]['pass'] for q in surv)
        rc=sum(by[(q,'cut60')][c]['pass'] for q in rem)
        unans=sorted({r['pair_id'] for r in rows if not r['answerable']})
        uc=sum(by[(q,'cut60')][c]['pass'] for q in unans)
        robust[c]={'survives_main':rate(sm,len(surv)),'survives_cut':rate(sc,len(surv)),
                   'survives_change_points':round(rate(sc,len(surv))['pct']-rate(sm,len(surv))['pct'],1),
                   'evidence_removed_correct_abstention_cut':rate(rc,len(rem)),'unanswerable_cut':rate(uc,len(unans))}
    result['robustness']=robust

    subgroup={}
    for dim in ('family','question_type'):
        for group in sorted({r[dim] for r in rows if r['answerable']}):
            group_ids={r['pair_id'] for r in rows if r['answerable'] and r[dim]==group}
            subgroup[f'{dim}:{group}']={c:rate(sum(r['pass'] for r in rows if r['passage']=='full' and r['condition']==c and r['answerable'] and r[dim]==group),len(group_ids))
                                      for c in ('base','adapter')}
    result['subgroups_main_answerable']=subgroup
    agreement={}
    for run,passage in (('main','full'),('cut60','cut60')):
        part=[r for r in rows if r['passage']==passage]
        diff=[r for r in part if r['judges_differ']]
        agreement[run]={'rows':len(part),'judges_differ_on_any_field':len(diff),
            'strict_pass_agree':sum(r['A_pass']==r['B_pass'] for r in part),
            'A_strict_pass':sum(r['A_pass'] for r in part),'B_strict_pass':sum(r['B_pass'] for r in part),
            'andy_chose_A':sum(r['author_choice']=='A' for r in diff),'andy_chose_B':sum(r['author_choice']=='B' for r in diff)}
    result['judge_agreement']=agreement
    result['andy_review']={'flags':0,'calls':sum(v['judges_differ_on_any_field'] for v in agreement.values()),
        'ratings_changed_by_flag':0,'review_scope':'All 300 main-run outputs; all 17 cut-run judge disagreements',
        'main_outputs_reviewed':300,'cut_disagreements_reviewed':agreement['cut60']['judges_differ_on_any_field']}
    lat={}
    for passage,run in (('full','main'),('cut60','cut60')):
        for c in ('base','adapter'):
            selected=[r for r in rows if r['passage']==passage and r['condition']==c]
            times=sorted(r['seconds'] for r in selected)
            lat[f'{passage}:{c}']={'median_s':round(statistics.median(times),2),'p90_s':round(times[int(.9*len(times))-1],2),
                'mean_tokens':round(statistics.mean(r['tokens'] for r in selected),1),
                'truncated':sum(r['finish']=='length' for r in selected)}
    result['latency']=lat
    def mode(r):
        if r['pass']: return 'No error'
        if not r['answerable']: return 'Answered an unanswerable question'
        if r['abstained']: return 'Declined although the passage had the answer'
        if not r['correct']: return 'Wrong or incomplete answer'
        return 'Correct answer with an unsupported extra claim'
    result['error_mix_main']={c:dict(Counter(mode(r) for r in rows if r['passage']=='full' and r['condition']==c)) for c in ('base','adapter')}
    result['citation_present_main_answerable']={c:sum(r['citation_code']!='no_citation' for r in rows if r['passage']=='full' and r['condition']==c and r['answerable']) for c in ('base','adapter')}
    result['per_judge_strict_pass_main_answerable']={c:{j:sum(r[f'{j}_pass'] for r in rows if r['passage']=='full' and r['condition']==c and r['answerable']) for j in ('A','B')} for c in ('base','adapter')}
    result['per_judge_strict_pass_main_unanswerable']={c:{j:sum(r[f'{j}_pass'] for r in rows if r['passage']=='full' and r['condition']==c and not r['answerable']) for j in ('A','B')} for c in ('base','adapter')}
    a=result['primary_answerable_main']
    cit=result['citation_correctness_main']
    result['pm_thresholds']={'adapter_at_least_10pts_over_base':a['diff_points']>=10,
        'citation_correct_at_least_95pct_adapter':(cit['adapter']['pct'] or 0)>=95,
        'unsupported_below_2pct_adapter':result['unsupported_claim_main']['adapter']['pct']<2,
        'correct_abstention_at_least_90pct_adapter':result['correct_abstention_main']['adapter']['pct']>=90}
    return result


def main():
    fresh = replay()
    stored=json.loads((HERE/'final_results_public.json').read_text())
    assert fresh==stored, 'scrubbed row-level replay differs from public aggregate results'
    assert fresh['primary_answerable_main']['base']['k']==114 and fresh['primary_answerable_main']['adapter']['k']==111
    print('Replay passed: 600 scrubbed rating records; final aggregate results reproduced exactly.')
    p=fresh['primary_answerable_main']
    print(f"Answerable: base {p['base']['k']}/{p['base']['n']}, adapter {p['adapter']['k']}/{p['adapter']['n']}, difference {p['diff_points']} points.")
    print('Thresholds:',fresh['pm_thresholds'])
    print('Judge agreement (counts):',json.dumps(fresh['judge_agreement'],sort_keys=True))

if __name__=='__main__':
    main()
