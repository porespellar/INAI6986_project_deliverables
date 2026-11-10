"""
title: ALPHIN Human Review
author: J.O.
version: 1.1.0
description: Approve, request correction on, or escalate an ALPHIN Policy Workflow answer. Each decision is written to the review log. Clicking the same decision twice does not create a duplicate record.
"""

import os
import re
import sqlite3
import time

from pydantic import BaseModel

DB_PATH = os.environ.get("ALPHIN_WORKFLOW_DB", "/app/backend/data/alphin_workflow.db")
WORKFLOW_MODEL_PREFIXES = ("alphin_policy_workflow", "alphin-policy-workflow")

# Distinct colour icons so the three buttons are recognisable in the message toolbar (stock Open WebUI
# otherwise shows the same generic icon for every action). PNG, not SVG: v0.12.5 inverts SVG action icons
# in dark mode, which would change the colours. Green check = Approve, amber pencil = Needs correction,
# red flag = Escalate.
ICON_APPROVE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAOWklEQVR42tVbfZCV5XX/nfM892s/QWAXGAo10ajQfIg1ogJLYihx6lqNXnQi6jQzmjExOtZKTC25ewUr1VHU8aPRpi0WR2fXxLEY01GrXFi/SlGrwozFakniB7DL7rIf9973fZ9z+sd772V3YZe7X7A+DANcFvb9/c45v3Oe855jMNFHQViQNJiasPjpYgIWMHbt0iN+bTJp0LSAMTVhccFXGMv2ABnoRD4eTRjopgYDLBOk03LY36dSPG/KlprOzsKfpwDVks//4eY3skd8xlSDATKCNGRyE5BMGiQBrGxxxY9qUotOiLA9nUBnA3QSMc1F4GaCaTZUQ+sSEUQPwtCH6tBJFu9C6d2AdHvHmm2/H0BsS5KxskWA8fGM8SEglWI0pRUUPtQJ6xvmGB/LAbkIgnPJ8jSyJsSrCohC3cDnJyLAEkAEYoI6gXiuj4neUaJnDJvnP7/t5V2lf9CcNP2JPj4EHLKIA4C6O5Yuh+JKVfwFRUwNFFDfASIClNw3RIkiXaVPQ3a08HsFgclQxIAMQbwgAPgVqG7a7+qfQrrFQwoMpHDEMJtwAvpZoD697CwxupYIy2EYmneASME6xKBRfx8FtODuZClqQEyQwL2vAf1dW1PmybF6w+geLNVgkc4E01LnzCZj1xFhFVkT0bwvoe2IJ0BgQzIUoKgxIIKKvsjOrdmban1zcBhODAEKQlOKkE7LjPSSFWD6J46a2ZINAFUHIoNjclQgACUsw0kgjm5pS2XuKwlxS/neUD4BKXAxDc1IL2kiyymIQn0JwGQmLKUOy4M6EDEnLIknzfkD+esObnjjwEhCgspW+XRapt1yTjXXRO7jhPmB9HiuIGaM43sUoo6ro1Zybrvm9Yq2dVt3l0sClWv52lsXT41W8r9zzH5Ten0fhAgm0xENKG6tih6QvPfd9rWvby+HBDpqzAOY1XRGIjAVWyhmz9S+YPKB7xcSFDEGQAdy2rBv3db3jkbC8O7b1GBAUJ8rH+Z45Ezt8ycv+LCaMuo5B0NTNaZPVN963jTsnK9FQ46MgEKqm5Fa0mQqI1eHbk+TF3wJERnNBgFF7Vfjce8ppNOCluSQOM2QRc71z7sT1py73MTsLzXvB8AXAPwhT2D44nNl5OSKRXOo7ye/fQWpBovMHjm6BhTKyxnYUgcj74CoDk51Eqj9aETBUcRy4AV/diDd+tKR9OBwUAuShHRaVNx6jkfq4Yv7YoIHICBAyRA9hFSDPZIeDASmKcbKFjd9zeIzOGYul6zvCkXOF/MwsXrOUdx+ZQbJD4+kBwMJaCpeX+geWI5BFMelwhs2vAlMI3FIYvWcgmhtVaphOla2SH8v4AHCl07LtFTDMoqZBs35x7C2L9ug8J2PXi8Ly6bcYp8g4jhhp1ao/hiAht2qwQS0FD+Qa2EI49VxGa9jiNHj9WJObT3OmvtV7O05UD4JIBbPqbJeNeeeRQmkM67oBXyosdHiZqQaZiqjUXOBQieP9ZkYeedjaqIWT37/bjz3g4dw4fxlONDXBcumnBhlBE4pZr+U64l8G4AWtYBLFR8AkKwwcVsFURlDE2OcwRNUFb1eFv/wvZ9jwcyTEDURPHP1/bjunMvx2cE2UHk9FyGGsmjyCCK4TEKx05XFPuVkETxRxcF8L36ZvB1/ftpSBOIAEEQFGxpX42/OuwYHcz0QSNhXHLIkICOeIyGsmPrT79RiZYuDggwUhG9ltCa16ARL5m4IElDQ8fYAKhR0PV4fHr00hVULGxGIC12eCEQEJw7fOflsnDR9Lp557z8QNXZo4SIQVIWjthrqvZTd+ruPsSBpuBgLFrGFFDFTIDIp3N8ai73d7djQuBqrFjbCd8EA0VMAogpRwfuf7y60Jo5eGpFhsKGlAICXPmLGSx9xeCmQP6UIU7/u7fEDzwafH2zDTUuvwrWLkqHljR3wNYELEDEWTS88jHUvPoKKSBxytPBVkKpACd8EAHR8SRgfVIXVDuE0FcVwV8djBX5vzwHcsGQV7m28BaICwzzgoQJxiBiLTW9txj1bN6K+pg6qUpaoaKAgxYlzblqUQEuzMOrqtOBSc3GcBTBiLNp6O3HDud/HhsbVcIVo7B+RRR3Y9NZzuObpNCqjCSi0vKJFQRAFVGf31UgEIGXMn6/zUg1xqNZDFMNL6fAFF1P4c7Tg9/UcwLdPOgsbLlwNUQEXxG4w+Cfefg7XPJ1CdayilCZH0DVSWIoQzOwwDabT0hl3CQXmqhtdCBARBIo+P4c+Pz9iEiwbtPV2YsmJZ+CpK+4uXUGOBP6tT3bhR7++A1XRELyMBHyYCZSsjSvMnEN1QM4oEfyxFCrd+V48ekkTblx8BfZ2t5ddplo26Mr14Nw/Ph3PXH0/piSqS/9v8bgC+P/+9ANcvPFGGGYYNiMDP9ALwBzitWOt0kQV3fk+PHZJEy7/xvkAgB4viwdaN6G+alqhcBkq1Rl0ZXtw8vR5eObq+1Ebryq4PvcDLzAF8I3/fD26ct2oiMbhZHySVUhA3pFGYUdyyyQi+M6hz8/isUvTWLXwAvguABNjQ+NqABiWBMMGvfksplVMwcbL70BtvKoAdjB4xu87P8OF/xKCr4wmhiW13CpLgxA7A6BozPhE6AARynm3RkUtMQaPXtqEVQsvKKUmJoKTsEy9YfEq7O05PBwMM/q8LGrj1dj8lw/i67NOOQx8Mf115Xpw1VO3oa23c3zAg0idBGDpCglIJnl/OtMDpv8lSyhHUpkZvV4WZ8/7Bq5c2IhAApiC+1AhEwxFAhMjH/iHwM8+BYG4QeAVTCH4izfeiNf2vIPaeNXYwSsUTARfspKr2D2wH6DoKFf/nQiqY5V44YNXceO/rYdlC1EdMPBxGAnd7YiaSOlm98j31uDrs085rMQNhU3RlevGxRtvxKv/9zamV04ZB8sX5g5CL++ycd8BIIPFCYsdn0llw7zTOGaXaeAEOLoaKBTxaAxbPvxPdOa6cf6piyGqhUtMmMKoAOj8UxejK9eNF3e/DoXisUvTuPRry0th0z9Fq4aid92v1+LZna9gZvU0+C4YrzdHQlHDcLpjf3rrY0gmjcWssBSG6s7C2ErZSVxEUF89DQ+0bgKAUvXG/UjgQjzf27ganvPxtVmnlDRj4OUm/GHY4KbNd+GJt36DWTXT4TkfGL8rphITAN0JAJj6EVs0ZRzSgAuC14xPfSCqgBQuxGWcQBzqq4YnoTjz8uBFt5UEbvDNzkn42V9tvgsPbNuE+vG0fD8KVIHA8csAgFlVyiAoUik+EFnxGZy8RxGDwlhK2ac/CTdtvguGeaAmFHuTqiWBG3yzs2zw8xcexIatj2NmzfTxifnBMUtk1AsOEgdvhp2wjCs8yRZGOi0g/hUZxkjHTMohoVg4DS6TB9zsMhtRXz0dwfhbHoAKRY3C6bb29GufIpViELTQE8xIQYSeFc8PgNE1RMshYfDXj/pmNxr/ZybAPF0yeikNEgSpFLeh9UMEuo1iJhw/mUASxuVmNxL3N8yS89uynvtN0f0HvRnawkhDBPyPNNo77VFICMTBqZRy/46x3OxGJn2OY4Yg+mzPna370Zw0xTA/5Opb9iiQ4iz2/E9FEFxGUTMdgcho+wOiippYJV7+8M1SncDEYCIYZrz5u/eQ/Neb4YuPiLETB75Y/Yk6Eb4ym9nTjuZdQHowAWkAP65jXP+8X7n0xM8pSsmwJUM8+rEdRXWsEts+egs7PtmJ2ngVPu9uw71bN+LW396HrJ9DzEYhKhM6UkfxiBHPPdKe3vY4mpMGf7JLhp4PKMzZzUgt2UJx06C5YMzvCIuXGmiYCQJxqI5XwhBPnOWL1rekEHR5Wfly152tnYfGcoeaD2ierwBIRW+GEwcmjFWYnQhqY1WojVehKlaJqRW1YNDEgi/FvmU4XdO1vrUDLUkenOIPJ4DSguYkt61t3SF5/WtORAygY07MTgVOBaICJ27i37yKBpyIWNfr/Wr/7dseGmpajI42JFWXWvw0VUUvkW4vAJPFF+GICsUtayAfe31yRted2zrDIfXDeR86tgtZweY/foFJz6OomYNA3FhEEcdqjtgyCOiUILiw445XPwLA+FbmiE7Hw96dm4Cu9a0dXl5XqtMOihgDUTepwRMJRwxrzl3bnn7tv0JPHnqfYHhrhnpguu7Y9rF43goAHZSwBqLBZJwSBTNTzFrX51+7f13r08UwHn5w4GhnZYtDc9K0r319u+S88yD6NldGLBT+pJoTjlkDog7Jepe13d76WDjykwkwbuPyBRWtvXXx1FglP0kxs0L6AoEoRji1NM5XXHWciFgNZLfL6RXta7duL8fyo1uY6JdKSjsDANRzboyrMaOAHvbOOG4hedec6+37Uff67e0jAT98FjjSadlVGDRMcV/T469UNMx9A8DpFLP1UCWoBgVOaSItDpChRISh2KeB/mz/mswtXuunWSSTBg8/747N0lSR6dT86Aw744cg/C1HuE59gXpOwCg2V3lcrF14m8IxA/Gdp4JfGOev25t+fd9o94XGbql++zl1PzurXiui1wF0GVk+FUThypwrrMwpDjUIh/reoX8VlguLq3NsKMrhtlje7QVhMwd0/9505v3x2B8cD1clNB/aHcRPvhurm5VfIYG7iKDLyZo5ZAgqCjgNfw0XKGXwGxswUXGBkpigAqjvDoLwCgw9S2qe33fby3tL5De3yGisPjGrs4OWKAFg2t+fU209c6YIlqriHAL+CIyZENRQzHJpIIMA9QVQ7YJqN5h2g/AuEWUCS9sP3Jr5wwAh3tmi47VHPBFiFXoEBu4QFx9+3if7qns6MdPGMTPIFcQ6boGc3xNMiXxY0dnjfZbe0XfY0ha2MJoybqwWPzbb44O9Yuc+wq46LXufL5k0mL+v8GwTszVePP8PCfCcwFx1I20AAAAASUVORK5CYII="
ICON_CORRECT = "data:image/png;base64,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"
ICON_ESCALATE = "data:image/png;base64,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"

LABELS = {
    "approve": ("APPROVED", "✅ Approved"),
    "correct": ("NEEDS_CORRECTION", "✏️ Needs correction"),
    "escalate": ("ESCALATED", "🚩 Escalated to policy staff"),
}


class Action:
    class Valves(BaseModel):
        pass

    actions = [
        {"id": "approve", "name": "Approve", "icon_url": ICON_APPROVE},
        {"id": "correct", "name": "Needs correction", "icon_url": ICON_CORRECT},
        {"id": "escalate", "name": "Escalate to policy staff", "icon_url": ICON_ESCALATE},
    ]

    def __init__(self):
        self.valves = self.Valves()

    async def action(self, body: dict, __user__=None, __event_emitter__=None, __event_call__=None,
                     __model__=None, __id__=None):
        emit = __event_emitter__

        async def notify(kind, text):
            if emit:
                await emit({"type": "notification", "data": {"type": kind, "content": text}})

        model_id = str((__model__ or {}).get("id", body.get("model", "")))
        if not model_id.startswith(WORKFLOW_MODEL_PREFIXES):
            await notify("warning", "Review buttons only apply to ALPHIN Policy Workflow answers.")
            return
        sub = (__id__ or "").split(".")[-1]
        if sub not in LABELS:
            await notify("error", f"Unknown review action: {sub}")
            return
        decision, label = LABELS[sub]
        reviewer = (__user__ or {}).get("name") or "unknown"
        run_key = f"{body.get('chat_id')}:{body.get('id')}"

        con = sqlite3.connect(DB_PATH, timeout=10)
        con.row_factory = sqlite3.Row
        row = con.execute("select review_status, review_note from workflow_runs where run_key=?", (run_key,)).fetchone()
        if row is None:
            con.close()
            await notify("error", "No workflow record found for this answer, so nothing was logged.")
            return

        note = ""
        if sub in ("correct", "escalate") and __event_call__:
            res = await __event_call__({"type": "input", "data": {
                "title": "Reviewer note",
                "message": "What should the policy team know? (optional for escalation, required for correction)",
                "placeholder": "e.g. The timely-filing period is quoted from the wrong chapter.",
            }})
            note = (res if isinstance(res, str) else (res or {}).get("value", "") if isinstance(res, dict) else "") or ""
            note = note.strip()
            if sub == "correct" and not note:
                con.close()
                await notify("warning", "A note is required when requesting a correction. Nothing was logged.")
                return

        # Idempotency: the same decision with the same note is not recorded twice.
        if row["review_status"] == decision and (row["review_note"] or "") == note:
            con.close()
            await notify("info", f"Already recorded as {decision.lower().replace('_', ' ')}. No duplicate created.")
            return

        at = time.strftime("%Y-%m-%d %H:%M:%S")
        con.execute(
            "update workflow_runs set review_status=?, reviewer=?, review_note=?, reviewed_at=? where run_key=?",
            (decision, reviewer, note, at, run_key),
        )
        con.execute(
            "insert into review_events (run_key,at,reviewer,decision,note) values (?,?,?,?,?)",
            (run_key, at, reviewer, decision, note),
        )
        con.commit()
        con.close()

        # Update the visible status line in the message.
        msgs = body.get("messages") or []
        content = ""
        for m in reversed(msgs):
            if m.get("role") == "assistant":
                content = m.get("content", "")
                break
        line = f"**Review status:** {label} by {reviewer} at {at}" + (f" ({note})" if note else "")
        if re.search(r"\*\*Review status:\*\*[^\n]*", content):
            content = re.sub(r"\*\*Review status:\*\*[^\n]*", lambda _: line, content)
        else:
            content = content + "\n\n" + line
        if emit:
            await emit({"type": "chat:message", "data": {"content": content}})
        await notify("success", f"{label}. Recorded in the review log (type /log in this chat to view it).")
        # v0.12.5 renders structured output ahead of content. Returning the
        # changed message lets its stock Action handler synchronize both and
        # persist the visible decision; a content-only event leaves output stale.
        return {"messages": [{"id": body.get("id"), "role": "assistant", "content": content}]}
