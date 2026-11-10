"""
title: ALPHIN Policy Workflow
author: J.O.
version: 1.1.0
description: Visible, auditable policy-question workflow for the AUtoMLy capstone. Fixed steps (intake and PHI screen, retrieval from both knowledge bases, evidence gate, grounded draft, confidence score from a verifier model plus citation and number checks, confidence threshold, human review of low-confidence answers only, review log) run in code, show live status, and end with a diagram of the path taken with a legend. Type /log to see the review log.
requirements: httpx
"""

import json
import os
import re
import sqlite3
import time
import uuid
from typing import Optional

import httpx
from pydantic import BaseModel, Field

DB_PATH = os.environ.get("ALPHIN_WORKFLOW_DB", "/app/backend/data/alphin_workflow.db")

SYSTEM_PROMPT = (
    "You are ALPHIN, an Alabama Medicaid administrative and provider-billing decision-support "
    "assistant. Answer only from the supplied Alabama Medicaid source material. If the sources are "
    "insufficient, say so clearly. Cite the source URL and page. Do not invent policy, billing "
    "guidance, eligibility rules, or dates."
)

GATE_SYSTEM = (
    "You are an evidence auditor for an Alabama Medicaid policy assistant. You receive numbered "
    "passages and a staff question. Decide whether the passages themselves state the specific fact "
    "the question asks for (for example the exact number of days, dollar amount, form name, rate, "
    "or requirement). Answer SUFFICIENT only if at least one passage states that specific fact. "
    "Answer INSUFFICIENT if the passages only discuss the general topic or give related but "
    "different facts. Do not use outside knowledge. Reply with JSON only, no other text: "
    '{"verdict":"SUFFICIENT" or "INSUFFICIENT","passages":[numbers of passages that state the '
    'fact],"reason":"at most 25 words"}'
)

VERIFY_SYSTEM = (
    "You are a strict verifier for an Alabama Medicaid policy assistant. You receive numbered source "
    "passages, a staff question and a drafted answer. Decide whether the answer is correct: every "
    "statement in it must be directly stated in the passages, and it must answer the specific question "
    "that was asked. Ignore the Sources list formatting. Do not use outside knowledge. "
    "Reply with exactly one word: YES or NO."
)

# Where the review buttons are: stock Open WebUI shows Action buttons as small icons in the toolbar
# under each answer (next to copy, regenerate and the thumbs), with the name only on hover.
BUTTON_HELP = ("Review buttons are the three coloured icons in the small toolbar under this answer: "
               "green check = Approve, amber pencil = Needs correction, red flag = Escalate to policy staff "
               "(hover to see each name).")

# A coded check failure (a citation that matches no retrieved document, or a number that is not in the
# passages) caps confidence here, so the answer always goes to human review whatever the verifier says.
CHECK_FAIL_CAP = 0.40

SCHEMA = """
CREATE TABLE IF NOT EXISTS workflow_runs (
  run_key TEXT PRIMARY KEY, chat_id TEXT, message_id TEXT, created_at TEXT, user_id TEXT,
  user_name TEXT, question TEXT, route TEXT, gate_verdict TEXT, gate_reason TEXT,
  passages INTEGER, sources_json TEXT, citations_ok INTEGER, ungrounded_numbers TEXT,
  answer TEXT, review_status TEXT, reviewer TEXT, review_note TEXT, reviewed_at TEXT,
  latency_s REAL, draft_model TEXT, regenerated INTEGER DEFAULT 0, quote_overlap REAL,
  confidence REAL, verifier_p_yes REAL
);
CREATE TABLE IF NOT EXISTS review_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_key TEXT, at TEXT, reviewer TEXT,
  decision TEXT, note TEXT
);
"""


def db():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    cols = {r[1] for r in con.execute("pragma table_info(workflow_runs)")}
    for col in ("quote_overlap", "confidence", "verifier_p_yes"):  # logs created by older versions
        if col not in cols:
            con.execute(f"alter table workflow_runs add column {col} REAL")
    return con


def now_iso():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def last_user_text(body) -> str:
    for m in reversed(body.get("messages", [])):
        if m.get("role") == "user":
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
            return (c or "").strip()
    return ""


def doc_name(meta: dict) -> str:
    return (meta or {}).get("name") or (meta or {}).get("source") or "unknown"


def _tokens(text: str) -> list:
    return re.findall(r"[a-z0-9$%.]+", (text or "").lower().replace(",", ""))


def quote_overlap(body: str, passage_text: str, n: int = 4) -> float:
    """Share of the answer's word n-grams that appear verbatim in the retrieved passages (0..1).

    A high value means the answer is close to a quotation of the source, which leaves little room for an
    unsupported claim. Answers shorter than n words must appear in the passages as one contiguous phrase.
    """
    b, p = _tokens(body), _tokens(passage_text)
    if not b:
        return 0.0
    if len(b) < n:
        joined = " " + " ".join(p) + " "
        return 1.0 if " " + " ".join(b) + " " in joined else 0.0
    grams = {tuple(p[i:i + n]) for i in range(len(p) - n + 1)}
    mine = [tuple(b[i:i + n]) for i in range(len(b) - n + 1)]
    return sum(g in grams for g in mine) / len(mine)


CITE_RE = re.compile(r"[\w.\-]+\.pdf(?:,?\s*(?:p\.|page)\s*\d+)?", re.I)


def split_citations(answer: str):
    """Separate an answer's body from its citations, whatever format the model used.

    Handles a "Sources:" list, a dash list of documents without a header, and inline
    "Source: <file>.pdf p. N" text. Returns (body_without_citations, citation_lines). Citation text is
    removed from the body so page numbers and file names are not mistaken for policy numbers.
    """
    head, sep, tail = answer.partition("Sources:")
    cited, body_lines = [], []
    for line in tail.splitlines() if sep else []:
        if line.strip().startswith(("-", "*")) and line.strip(" -*"):
            cited.append("- " + line.strip(" -*").strip())
    for line in head.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")) and CITE_RE.search(stripped) and len(CITE_RE.sub("", stripped).strip(" -*:;,.")) < 3:
            cited.append("- " + stripped.strip(" -*").strip())  # dash list of documents with no header
            continue
        for m in re.finditer(r"\(?\bSources?:\s*([^\n)]*\.pdf[^\n)]*)\)?", line, re.I):
            cited += ["- " + c.group(0) for c in CITE_RE.finditer(m.group(1))]
        line = re.sub(r"\(?\bSources?:\s*[^\n)]*\.pdf[^\n)]*\)?", "", line, flags=re.I)
        body_lines.append(CITE_RE.sub("", line))
    return "\n".join(body_lines).strip(), cited


def yes_probability(top_logprobs: list) -> Optional[float]:
    """P(YES) from the verifier's first-token alternatives, renormalised over YES and NO.

    This is the "P(True)" self-evaluation measure: the model's own probability that the answer is
    supported, read from its token probabilities rather than from a number it writes. Returns None when
    neither YES nor NO is among the alternatives (the confidence is then unknown and the answer goes to
    human review).
    """
    import math

    yes = no = 0.0
    for t in top_logprobs or []:
        word = str(t.get("token", "")).strip().strip(".").upper()
        p = math.exp(float(t.get("logprob", -100.0)))
        if word == "YES":
            yes += p
        elif word == "NO":
            no += p
    if yes + no <= 0:
        return None
    return yes / (yes + no)


def combine_confidence(p_yes: Optional[float], checks_passed: bool) -> float:
    """Final confidence: the verifier probability, capped when a coded check failed."""
    conf = 0.0 if p_yes is None else max(0.0, min(1.0, p_yes))
    return conf if checks_passed else min(conf, CHECK_FAIL_CAP)


YES_COLOR = "#15803d"  # green "yes" labels
NO_COLOR = "#dc2626"   # red "no" labels
# Nodes that mean "stopped" or "a person must look at this" are amber when taken, not green.
REVIEW_NODES = ("C", "F", "J")


def mermaid(path_nodes: set, route: str, threshold: float = 0.80) -> str:
    """Workflow diagram with the path taken highlighted and a legend.

    Decisions are diamonds; "yes" labels are green and "no" labels red. Laid out top to bottom with
    short labels so it stays readable in the chat column. The legend sits under the diagram.
    """
    pct = f"{threshold:.0%}"
    n = {
        "A": 'A(["Staff question"])',
        "B": 'B{"1 Valid question,<br/>no PHI?"}',
        "C": 'C["Ask to<br/>rephrase"]',
        "D": 'D["2 Search both<br/>knowledge bases"]',
        "E": 'E{"3 Fact stated<br/>in the passages?"}',
        "F": 'F["Not in documents:<br/>route to<br/>policy staff"]',
        "G": 'G["4 Draft a<br/>cited answer"]',
        "H": 'H["5 Score confidence:<br/>verifier model +<br/>citation and number checks"]',
        "L": f'L{{"6 Confidence<br/>{pct} or higher?"}}',
        "M": 'M["Released:<br/>high confidence,<br/>no review needed"]',
        "J": 'J["7 Human review:<br/>approve, correct,<br/>or escalate"]',
        "K": 'K[("8 Review log")]',
    }
    # (from, label, to); label None = plain arrow
    edges = [
        ("A", None, "B"), ("B", "no", "C"), ("B", "yes", "D"), ("D", None, "E"), ("E", "no", "F"),
        ("E", "yes", "G"), ("G", None, "H"), ("H", None, "L"), ("L", "yes", "M"), ("L", "no", "J"),
        ("F", None, "J"), ("C", None, "K"), ("J", None, "K"), ("M", None, "K"),
    ]
    legend = {
        "LG1": 'LG1["Step on this<br/>answer\'s path"]',
        "LG2": 'LG2["Stopped or sent<br/>to a person"]',
        "LG3": 'LG3["Step not used<br/>this time"]',
        "LG4": 'LG4{"Decision"}',
        "LG5": 'LG5["yes = condition met"]',
        "LG6": 'LG6["no = condition not met"]',
    }
    # White label boxes keep the green/red yes/no text readable in both light and dark chat themes.
    css = (".edgeLabel rect{fill:#ffffff !important;opacity:1 !important} "
           ".edgeLabel text{font-weight:700} .cluster-label text{fill:#1f2937 !important;font-weight:700}")
    init = ('%%{init: {"flowchart": {"nodeSpacing": 40, "rankSpacing": 34, "padding": 12, '
            '"curve": "basis", "subGraphTitleMargin": {"top": 10, "bottom": 6}}, '
            '"themeVariables": {"fontSize": "18px", "edgeLabelBackground": "#ffffff", "titleColor": "#1f2937"}, '
            '"themeCSS": "' + css + '"}}%%')
    lines = [init, "flowchart TD"] + ["  " + v for v in n.values()]
    link_styles = []
    for i, (a, label, b) in enumerate(edges):
        lines.append(f"  {a} -- {label} --> {b}" if label else f"  {a} --> {b}")
        if label:
            color = YES_COLOR if label == "yes" else NO_COLOR
            link_styles.append(f"  linkStyle {i} color:{color},font-weight:bold")
    lines.append('  subgraph LEGEND["Legend"]')
    lines += ["    " + v for v in legend.values()]
    lines.append("  end")
    # Invisible links lay the legend out as a 3 x 2 grid under the review log.
    lines += ["  K ~~~ LG1", "  K ~~~ LG2", "  K ~~~ LG3", "  LG1 ~~~ LG4", "  LG2 ~~~ LG5", "  LG3 ~~~ LG6"]
    lines += link_styles
    lines.append("  classDef hit fill:#1d6b3a,stroke:#0f3d20,color:#ffffff,stroke-width:2px")
    lines.append("  classDef warn fill:#a35a00,stroke:#5c3300,color:#ffffff,stroke-width:2px")
    lines.append("  classDef idle fill:#e8ebf0,stroke:#9aa3b2,color:#4b5563")
    lines.append("  classDef key fill:#ffffff,stroke:#9aa3b2,color:#1f2937")
    lines.append(f"  classDef yeskey fill:#ffffff,stroke:{YES_COLOR},color:{YES_COLOR},font-weight:bold")
    lines.append(f"  classDef nokey fill:#ffffff,stroke:{NO_COLOR},color:{NO_COLOR},font-weight:bold")
    lines.append("  style LEGEND fill:#f8fafc,stroke:#9aa3b2,color:#1f2937")
    hit = sorted(x for x in path_nodes if x in n and x not in REVIEW_NODES)
    warn = sorted(x for x in path_nodes if x in REVIEW_NODES)
    idle = sorted(set(n) - path_nodes)
    if hit:
        lines.append("  class " + ",".join(hit) + " hit")
    if warn:
        lines.append("  class " + ",".join(warn) + " warn")
    if idle:
        lines.append("  class " + ",".join(idle) + " idle")
    lines += ["  class LG1 hit", "  class LG2 warn", "  class LG3 idle", "  class LG4 key",
              "  class LG5 yeskey", "  class LG6 nokey"]
    return "```mermaid\n" + "\n".join(lines) + "\n```"


class Pipe:
    class Valves(BaseModel):
        LLM_BASE_URL: str = Field(default="http://vllm-nemo:8000/v1", description="OpenAI-compatible endpoint")
        DRAFT_MODEL: str = Field(default="nemotron-3.5-lightning:30b-a3b-bf16", description="Model that drafts the cited answer (untouched base by default)")
        GATE_MODEL: str = Field(default="nemotron-3.5-lightning:30b-a3b-bf16", description="Model that audits evidence")
        KNOWLEDGE_BASES: str = Field(
            default="Alabama Medicaid Provider Manual,Alabama Medicaid Administrative Code",
            description="Comma-separated knowledge base names to search",
        )
        TOP_K: int = Field(default=8, ge=1, le=15, description="Passages retrieved")
        MAX_QUESTION_CHARS: int = Field(default=1500, ge=100, le=6000)
        MAX_ANSWER_TOKENS: int = Field(default=900, ge=200, le=3000)
        VERIFY_MODEL: str = Field(default="nemotron-3.5-lightning:30b-a3b-bf16", description="Model that scores confidence (its probability of answering YES to 'is this answer supported and responsive?')")
        CONFIDENCE_THRESHOLD: float = Field(default=0.80, ge=0.0, le=1.0, description="Answers at or above this confidence are released without review; below it they go to human review. Set to 1.0 to send every answer to review")
        ENFORCE_GATE: bool = Field(default=True, description="If off, the draft step always runs (for comparison runs)")

    def __init__(self):
        self.valves = self.Valves()
        self.name = "ALPHIN Policy Workflow"

    # ------------------------------------------------------------------ helpers
    async def _status(self, emit, text, done=False):
        if emit:
            await emit({"type": "status", "data": {"description": text, "done": done}})

    async def _chat(self, model, messages, max_tokens, stream=False, temperature=0.0):
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        url = self.valves.LLM_BASE_URL.rstrip("/") + "/chat/completions"
        return url, payload

    async def _complete(self, model, messages, max_tokens):
        url, payload = await self._chat(model, messages, max_tokens)
        async with httpx.AsyncClient(timeout=180) as c:
            r = await c.post(url, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"] or ""

    async def _stream(self, url, payload):
        """Stream the draft's text deltas from the OpenAI-compatible endpoint."""
        async with httpx.AsyncClient(timeout=300) as c:
            async with c.stream("POST", url, json=payload) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.startswith("data: ") or line.strip() == "data: [DONE]":
                        continue
                    try:
                        delta = json.loads(line[6:])["choices"][0]["delta"].get("content") or ""
                    except Exception:
                        continue
                    if delta:
                        yield delta

    async def _verifier_yes_probability(self, question, answer, numbered) -> Optional[float]:
        """Ask the verifier one YES/NO question and read P(YES) from its token probabilities."""
        url, payload = await self._chat(
            self.valves.VERIFY_MODEL,
            [{"role": "system", "content": VERIFY_SYSTEM},
             {"role": "user", "content": f"Passages:\n{numbered}\n\nQuestion: {question}\n\nAnswer:\n{answer}\n\n"
                                         "Is the answer fully supported by the passages and responsive to the question? YES or NO."}],
            1,
        )
        payload.update({"logprobs": True, "top_logprobs": 10})
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(url, json=payload)
            r.raise_for_status()
            choice = r.json()["choices"][0]
        content = (choice.get("logprobs") or {}).get("content") or []
        return yes_probability(content[0].get("top_logprobs") if content else [])

    async def _resolve_kb_ids(self, user):
        from open_webui.models.knowledge import Knowledges

        wanted = [n.strip() for n in self.valves.KNOWLEDGE_BASES.split(",") if n.strip()]
        found = {}
        res = Knowledges.get_knowledge_bases() if hasattr(Knowledges, "get_knowledge_bases") else None
        if hasattr(res, "__await__"):
            res = await res
        for kb in res or []:
            if kb.name in wanted:
                found[kb.name] = kb.id
        return [found[n] for n in wanted if n in found], [n for n in wanted if n not in found]

    async def _retrieve(self, request, user_id, query, kb_ids):
        from open_webui.models.users import Users
        from open_webui.routers.retrieval import QueryCollectionsForm, query_collection_handler

        user = Users.get_user_by_id(user_id)
        if hasattr(user, "__await__"):
            user = await user
        form = QueryCollectionsForm(collection_names=kb_ids, query=query, k=self.valves.TOP_K)
        res = await query_collection_handler(request, form, user)
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dist = res["distances"][0]
        out = []
        for d, m, s in zip(docs, metas, dist):
            out.append({"text": d, "meta": m, "score": float(s), "name": doc_name(m), "page": int((m or {}).get("page", 0)) + 1})
        return out

    # ------------------------------------------------------------- log display
    def _render_log(self):
        con = db()
        rows = con.execute(
            "select created_at,user_name,question,route,confidence,review_status,reviewer,review_note from workflow_runs "
            "order by created_at desc limit 15"
        ).fetchall()
        tot = con.execute("select count(*) c from workflow_runs").fetchone()["c"]
        by = con.execute("select review_status s,count(*) c from workflow_runs group by 1").fetchall()
        routes = con.execute("select route r,count(*) c from workflow_runs group by 1").fetchall()
        con.close()
        out = [f"### ALPHIN Review Log\n\n**{tot}** workflow runs. "
               + "Routes: " + ", ".join(f"{r['r']} {r['c']}" for r in routes) + ". "
               + "Review status: " + ", ".join(f"{r['s']} {r['c']}" for r in by) + ".\n"]
        out.append("| Time | Staff | Question | Route | Confidence | Review | Reviewer | Note |\n|---|---|---|---|---|---|---|---|")
        for r in rows:
            q = (r["question"] or "").replace("|", "/").replace("\n", " ")
            q = q[:70] + ("…" if len(q) > 70 else "")
            out.append(
                f"| {r['created_at']} | {r['user_name']} | {q} | {r['route']} | "
                f"{'' if r['confidence'] is None else format(r['confidence'], '.0%')} | {r['review_status']} | "
                f"{r['reviewer'] or ''} | {(r['review_note'] or '').replace('|', '/')[:50]} |"
            )
        return "\n".join(out)

    # ---------------------------------------------------------------- the flow
    async def pipe(self, body: dict, __user__: Optional[dict] = None, __request__=None,
                   __event_emitter__=None, __metadata__: Optional[dict] = None,
                   __task__: Optional[str] = None):
        # Stock WebUI also calls the selected Pipe for title/tag/follow-up tasks.
        # These are UI metadata, not staff questions: do not retrieve or log them.
        if __task__:
            yield json.dumps({"title": "ALPHIN Policy Workflow", "tags": ["Alabama Medicaid"], "follow_ups": []})
            return
        t0 = time.time()
        emit = __event_emitter__
        meta = __metadata__ or {}
        user = __user__ or {}
        chat_id = str(meta.get("chat_id") or "")
        message_id = str(meta.get("message_id") or "")
        run_key = f"{chat_id}:{message_id}" if chat_id and message_id else f"adhoc:{uuid.uuid4().hex[:12]}"
        question = last_user_text(body)
        path = {"A"}
        trace = []  # (step, result, seconds)

        # Utility command: show the log
        if question.lower().startswith("/log"):
            yield self._render_log()
            return

        def log_run(**f):
            con = db()
            prev = con.execute("select 1 from workflow_runs where run_key=?", (run_key,)).fetchone()
            f.setdefault("review_status", "pending")
            cols = ["run_key", "chat_id", "message_id", "created_at", "user_id", "user_name", "question",
                    "latency_s", "draft_model", "regenerated"] + list(f)
            vals = [run_key, chat_id, message_id, now_iso(), user.get("id"), user.get("name"), question,
                    round(time.time() - t0, 1), self.valves.DRAFT_MODEL, 1 if prev else 0] + list(f.values())
            con.execute(
                f"insert or replace into workflow_runs ({','.join(cols)}) values ({','.join('?' * len(cols))})", vals
            )
            if prev:
                con.execute("insert into review_events (run_key,at,reviewer,decision,note) values (?,?,?,?,?)",
                            (run_key, now_iso(), user.get("name"), "regenerated", "answer regenerated; review reset"))
            con.commit()
            con.close()

        def footer(route_label, extra=""):
            rows = ["| Step | Result | Time |", "|---|---|---|"] + [f"| {a} | {b} | {c:.1f}s |" for a, b, c in trace]
            return (
                "\n\n---\n**Workflow trace**\n\n" + "\n".join(rows) + "\n\n"
                + mermaid(path, route_label, self.valves.CONFIDENCE_THRESHOLD)
                + extra
            )

        # ---- Step 1: intake, scope and PHI screen
        s = time.time()
        await self._status(emit, "Step 1 of 8: checking the question…")
        problem = None
        if len(question) < 8:
            problem = "The question is too short to search on. Please ask a full question about Alabama Medicaid policy."
        elif len(question) > self.valves.MAX_QUESTION_CHARS:
            problem = f"The question is longer than {self.valves.MAX_QUESTION_CHARS} characters. Please shorten it."
        elif re.search(r"\b\d{3}-\d{2}-\d{4}\b", question) or re.search(r"\b\d{9}\b", question) and re.search(r"(?i)\b(ssn|social security|medicaid id|recipient id)\b", question):
            problem = ("This looks like it contains a Social Security or recipient identifier. "
                       "This tool answers policy questions only. Please remove personal identifiers and ask again.")
        trace.append(("1 Intake and PHI screen", "needs rephrasing" if problem else "passed", time.time() - s))
        if problem:
            path |= {"B", "C", "K"}
            log_run(route="REPHRASE", gate_verdict="n/a", gate_reason=problem, passages=0, sources_json="[]",
                    citations_ok=0, ungrounded_numbers="[]", answer=problem, review_status="n/a")
            await self._status(emit, "Stopped at step 1: question needs rephrasing", done=True)
            yield problem + footer("REPHRASE", "\n\n**Review status:** not needed (nothing was answered)")
            return
        path |= {"B", "D"}

        # ---- Step 2: retrieval
        s = time.time()
        await self._status(emit, "Step 2 of 8: searching both knowledge bases…")
        try:
            kb_ids, missing = await self._resolve_kb_ids(user)
            if not kb_ids:
                raise RuntimeError("knowledge bases not found: " + ", ".join(missing))
            passages = await self._retrieve(__request__, user.get("id"), question, kb_ids)
        except Exception as e:  # surface, never hide, a retrieval failure
            path |= {"K"}
            msg = f"Retrieval failed ({type(e).__name__}: {e}). Nothing was answered."
            log_run(route="ERROR", gate_verdict="n/a", gate_reason=msg, passages=0, sources_json="[]",
                    citations_ok=0, ungrounded_numbers="[]", answer=msg, review_status="n/a")
            await self._status(emit, "Retrieval failed", done=True)
            yield msg
            return
        docs_hit = sorted({p["name"] for p in passages})
        trace.append(("2 Retrieve", f"{len(passages)} passages from {len(docs_hit)} documents", time.time() - s))
        if emit:
            for i, p in enumerate(passages, 1):
                await emit({"type": "source", "data": {
                    "source": {"name": p["name"]},
                    "document": [p["text"]],
                    "metadata": [{"source": p["name"], "name": p["name"], "page": p["page"] - 1}],
                    "distances": [p["score"]],
                }})
        await self._status(emit, f"Step 2 of 8: found {len(passages)} passages in {len(docs_hit)} documents")

        # ---- Step 3: evidence gate
        s = time.time()
        await self._status(emit, "Step 3 of 8: checking the passages contain the answer…")
        numbered = "\n\n".join(f"[{i}] ({p['name']}, page {p['page']})\n{p['text'][:1800]}" for i, p in enumerate(passages, 1))
        gate_raw = ""
        try:
            gate_raw = await self._complete(
                self.valves.GATE_MODEL,
                [{"role": "system", "content": GATE_SYSTEM},
                 {"role": "user", "content": f"Question: {question}\n\nPassages:\n{numbered}"}],
                200,
            )
        except Exception as e:
            path |= {"E", "K"}
            msg = (f"The evidence check could not run ({type(e).__name__}), so nothing was answered. "
                   "This is a service problem, not a finding about the documents. Please try again shortly.")
            trace.append(("3 Evidence gate", f"service unavailable ({type(e).__name__})", time.time() - s))
            log_run(route="ERROR", gate_verdict="n/a", gate_reason=msg, passages=len(passages),
                    sources_json=json.dumps(docs_hit), citations_ok=0, ungrounded_numbers="[]", answer=msg, review_status="n/a")
            await self._status(emit, "Evidence check unavailable: stopped safely", done=True)
            yield msg
            return
        m = re.search(r"\b(INSUFFICIENT|SUFFICIENT)\b", gate_raw.upper())
        verdict = m.group(1) if m else "INSUFFICIENT"
        pm = re.search(r'"passages"\s*:\s*\[([^\]]*)\]', gate_raw)
        gate_passages = sorted({int(x) for x in re.findall(r"\d+", pm.group(1)) if 1 <= int(x) <= len(passages)}) if pm else []
        rm = re.search(r'"reason"\s*:\s*"([^"]*)"', gate_raw)
        reason = rm.group(1) if rm else gate_raw.strip()[:160]
        trace.append(("3 Evidence gate", f"{verdict.lower()}: {reason}", time.time() - s))
        path |= {"E"}

        if verdict == "INSUFFICIENT" and self.valves.ENFORCE_GATE:
            path |= {"F", "J", "K"}
            closest = "\n".join(f"- {n}" for n in docs_hit[:4])
            answer = (
                "**I could not find this in the Alabama Medicaid documents I searched.**\n\n"
                f"Why: {reason}\n\nClosest documents (they discuss the topic but do not state the specific answer):\n{closest}\n\n"
                "This question has been routed to policy staff. Please do not rely on a guess."
            )
            log_run(route="NO_ANSWER", gate_verdict=verdict, gate_reason=reason, passages=len(passages),
                    sources_json=json.dumps(docs_hit), citations_ok=0, ungrounded_numbers="[]", answer=answer)
            await self._status(emit, "Evidence gate: not in the documents, routed to policy staff", done=True)
            yield answer + footer("NO_ANSWER", "\n\n**Review status:** ⏳ Pending human review (routed to policy staff)"
                                  "\n\n**Reviewer:** " + BUTTON_HELP)
            return
        path |= {"G"}

        # ---- Step 4: grounded draft (streamed)
        s = time.time()
        await self._status(emit, f"Step 4 of 8: drafting a cited answer with {self.valves.DRAFT_MODEL}…")
        ctx = "\n\n".join(f"[SOURCE: {p['name']}, page {p['page']}]\n{p['text']}" for p in passages)
        user_msg = (
            "Use only the sources below to answer.\n\n" + ctx + f"\n\nQuestion: {question}\n\n"
            "Answer concisely, then end with a Sources: list with one line per citation in the form "
            "'- <document file name> p. <page>'."
        )
        url, payload = await self._chat(
            self.valves.DRAFT_MODEL,
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
            self.valves.MAX_ANSWER_TOKENS, stream=True,
        )
        answer = ""
        try:
            async for delta in self._stream(url, payload):
                answer += delta
                yield delta
        except Exception as e:
            msg = f"\n\nThe drafting step failed ({type(e).__name__}). No answer was produced; please try again."
            log_run(route="ERROR", gate_verdict=verdict, gate_reason=reason, passages=len(passages),
                    sources_json=json.dumps(docs_hit), citations_ok=0, ungrounded_numbers="[]", answer=answer + msg,
                    review_status="n/a")
            await self._status(emit, "Drafting failed: stopped safely", done=True)
            yield msg
            return
        trace.append(("4 Draft", f"{len(answer.split())} words ({self.valves.DRAFT_MODEL})", time.time() - s))

        # ---- Step 5: confidence score = verifier model probability, capped by coded checks
        s = time.time()
        await self._status(emit, "Step 5 of 8: scoring confidence (verifier model, citation and number checks)…")
        body_text, cited_lines = split_citations(answer)
        retrieved_names = {p["name"] for p in passages}
        added_sources = ""
        if not cited_lines and gate_passages:
            # The draft left out its Sources list (common for one-line answers). Cite the passages the
            # evidence gate said state the fact, and say plainly that the workflow added them.
            seen = []
            for i in gate_passages:
                line = f"- {passages[i - 1]['name']} p. {passages[i - 1]['page']}"
                if line not in seen:
                    seen.append(line)
            cited_lines = seen
            added_sources = "\n\nSources (added by the workflow from the evidence gate):\n" + "\n".join(seen)
            yield added_sources
        bad_cites, good_cites = [], 0
        for l in cited_lines:
            if any(n.rsplit(".", 1)[0] in l or n in l for n in retrieved_names):
                good_cites += 1
            else:
                bad_cites.append(l.strip()[:90])
        all_text = " ".join(p["text"] for p in passages).replace(",", "")
        nums = {t.replace(",", "") for t in re.findall(r"\$?\d[\d,]*\.?\d*%?", body_text) if len(t.strip("$%.")) > 1 or "$" in t or "%" in t}
        ungrounded = sorted(n for n in nums if n.strip("$%.") not in all_text)
        citations_ok = good_cites > 0 and not bad_cites
        checks_passed = citations_ok and not ungrounded
        overlap = quote_overlap(body_text.replace("**", ""), all_text)
        verifier_note = ""
        try:
            p_yes = await self._verifier_yes_probability(question, answer + added_sources, numbered)
            if p_yes is None:
                verifier_note = "verifier gave no YES/NO probability"
        except Exception as e:  # unknown confidence is treated as low confidence, never as high
            p_yes = None
            verifier_note = f"verifier unavailable ({type(e).__name__})"
        confidence = combine_confidence(p_yes, checks_passed)
        threshold = self.valves.CONFIDENCE_THRESHOLD
        high = confidence >= threshold
        trace.append(("5 Confidence score",
                      (f"verifier {p_yes:.0%} supported" if p_yes is not None else verifier_note)
                      + f"; citations {good_cites}/{len(cited_lines)} traced"
                      + (" (added from the evidence gate)" if added_sources else "")
                      + f"; {len(ungrounded)} ungrounded numbers; "
                      f"quote match {overlap:.0%} → **confidence {confidence:.0%}**", time.time() - s))
        trace.append(("6 Threshold", f"{confidence:.0%} {'≥' if high else '<'} {threshold:.0%}: "
                      + ("released without review" if high else "sent to human review"), 0.0))
        path |= {"H", "L", "K"} | ({"M"} if high else {"J"})
        route = "HIGH_CONFIDENCE" if high else "LOW_CONFIDENCE"
        reasons = []
        if not cited_lines:
            reasons.append("the answer has no Sources list")
        if bad_cites:
            reasons.append("citations that match no retrieved document: " + "; ".join(bad_cites))
        if ungrounded:
            reasons.append("numbers not found in the retrieved passages: " + ", ".join(ungrounded))
        if verifier_note:
            reasons.append(verifier_note)
        if not reasons and not high:
            reasons.append("the verifier model was not sure every statement is supported by the passages")
        warn = ""
        if not high:
            warn = (f"\n\n> ⚠️ **Low confidence ({confidence:.0%}), sent to human review:** "
                    + "; ".join(reasons) + ".")
        log_run(route=route, gate_verdict=verdict, gate_reason=reason, passages=len(passages),
                sources_json=json.dumps(docs_hit), citations_ok=1 if citations_ok else 0,
                ungrounded_numbers=json.dumps(ungrounded), answer=answer + added_sources, quote_overlap=round(overlap, 3),
                confidence=round(confidence, 4), verifier_p_yes=None if p_yes is None else round(p_yes, 4),
                review_status="AUTO_RELEASED" if high else "pending")
        if high:
            await self._status(emit, f"Step 6 of 8: confidence {confidence:.0%}, released without review", done=True)
            status_line = (f"✅ Released with high confidence ({confidence:.0%}, threshold {threshold:.0%}). "
                           "No review needed.")
            button_note = "\n\n<sub>If you disagree, you can still review it. " + BUTTON_HELP + "</sub>"
        else:
            await self._status(emit, f"Step 7 of 8: confidence {confidence:.0%}, waiting for human review", done=True)
            status_line = f"⏳ Pending human review (confidence {confidence:.0%}, below the {threshold:.0%} threshold)"
            button_note = "\n\n**Reviewer:** " + BUTTON_HELP
        yield warn + footer(route, f"\n\n**Confidence:** {confidence:.0%}\n\n**Review status:** {status_line}"
                            + button_note)
