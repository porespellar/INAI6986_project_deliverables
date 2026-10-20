"""Build and execute the identity-safe public replay for final-test arithmetic only."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'notebook/final_test_replay_20261019.ipynb'

nb = nbformat.v4.new_notebook(metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}})
nb.cells = [
    nbformat.v4.new_markdown_cell(
        '# AUtoMLy final-test public replay (October 19, 2026)\n\n'
        'Recomputes the reported aggregate metrics from 600 **de-identified final-rating records**. It makes no model '
        'calls. It does not contain benchmark questions or keys, source passages or page locators, model answer text, '
        'raw judge requests/responses, or the signed review spreadsheet. The private repository retains the complete '
        'audit record. This replay checks the arithmetic of the final ratings; it cannot independently reassess factual '
        'correctness or source support without the withheld content.'),
    nbformat.v4.new_markdown_cell('## 1. Load and validate the scrubbed data bundle'),
    nbformat.v4.new_code_cell(
        "import json, sys\nfrom pathlib import Path\nROOT = Path.cwd().resolve()\n"
        "while not (ROOT / 'README.md').exists() or not (ROOT / 'notebook').exists(): ROOT = ROOT.parent\n"
        "B = ROOT / 'notebook/evidence_final_test_20261019'\nsys.path.insert(0, str(B))\n"
        "from replay_final_test_public import load_rows, replay\n"
        "rows = load_rows()\nmanifest = json.loads((B / 'manifest.json').read_text())\n"
        "assert len(rows) == manifest['records'] == 600\n"
        "assert len({r['pair_id'] for r in rows}) == manifest['paired_items'] == 150\n"
        "forbidden = {'question', 'reference_answer', 'evidence_quotes', 'passage_text', 'output_text', 'source_id', 'pdf_page'}\n"
        "assert not (forbidden & set(rows[0]))\n"
        "print('Loaded 600 de-identified rating rows; 150 paired question IDs; excluded raw text and source locators.')"),
    nbformat.v4.new_markdown_cell('## 2. Recompute the saved final-test aggregates'),
    nbformat.v4.new_code_cell(
        "stored = json.loads((B / 'final_results_public.json').read_text())\n"
        "fresh = replay()\nassert fresh == stored, 'Recomputed public metrics differ from the saved aggregate.'\n"
        "print('All aggregate fields reproduced exactly from the scrubbed per-output ratings.')"),
    nbformat.v4.new_markdown_cell('## 3. Headline results'),
    nbformat.v4.new_code_cell(
        "P = fresh['primary_answerable_main']\n"
        "print('Answerable strict pass: base {}/{} ({:.1f}%), adapter {}/{} ({:.1f}%), difference {:+.1f} points.'.format(P['base']['k'],P['base']['n'],P['base']['pct'],P['adapter']['k'],P['adapter']['n'],P['adapter']['pct'],P['diff_points']))\n"
        "for label, key in [('Unsupported claims','unsupported_claim_main'), ('Correct abstention','correct_abstention_main'), ('Correct citations','citation_correctness_main')]:\n"
        "    vals = fresh[key]\n    print(label + ':', ', '.join('{} {}/{} ({:.1f}%)'.format(c,vals[c]['k'],vals[c]['n'],vals[c]['pct']) for c in ('base','adapter')))\n"
        "print('PM thresholds met:', fresh['pm_thresholds'])\n"
        "print('Judge agreement counts:', json.dumps(fresh['judge_agreement'], sort_keys=True))\n"
        "print('Human review: main outputs reviewed =', fresh['user_review']['main_outputs_reviewed'], '; cut disagreements reviewed =', fresh['user_review']['cut_disagreements_reviewed'], '; flags =', fresh['user_review']['flags'])\n"
        "assert (P['base']['k'], P['adapter']['k']) == (114,111)\n"
        "assert all(v is False for v in fresh['pm_thresholds'].values())"),
]
NotebookClient(nb, timeout=120, kernel_name='python3', resources={'metadata': {'path': str(ROOT)}}).execute()
errors = [o for c in nb.cells if c.cell_type == 'code' for o in c.get('outputs', []) if o.get('output_type') == 'error']
assert not errors, errors
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(f'Executed {sum(c.cell_type == "code" for c in nb.cells)} code cells; errors={len(errors)}; wrote {OUT.name}.')
