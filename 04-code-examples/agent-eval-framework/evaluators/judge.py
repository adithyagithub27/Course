"""
The judge model for every DeepEval metric in the course.

    from evaluators.judge import get_judge
    AnswerRelevancyMetric(threshold=0.7, model=get_judge())

Live: returns the judge model name from config (gpt-4.1 by default, decision A8),
which DeepEval turns into its OpenAI judge.

Offline (OFFLINE=1 or no key): returns ``MockJudge``, a DeepEval custom model
(``DeepEvalBaseLLM``). DeepEval sends it the same prompts it would send
gpt-4.1, with a Pydantic schema for the answer; MockJudge reads the parts of
the prompt it needs (statements, context, criteria) and fills the schema using
the deterministic rules in ``evaluators/heuristics.py``. Every DeepEval metric
class therefore runs its real code path offline, with a stand-in brain.
"""

from __future__ import annotations

import json
import re
from typing import Any

from deepeval.models import DeepEvalBaseLLM

from config.settings import is_offline, judge_model
from evaluators import heuristics as h


def _between(prompt: str, start: str, ends: tuple[str, ...] = ("\n\nJSON", "\nJSON:")) -> str:
    i = prompt.rfind(start)
    if i < 0:
        return ""
    rest = prompt[i + len(start) :]
    cut = min((rest.find(e) for e in ends if rest.find(e) >= 0), default=len(rest))
    return rest[:cut].strip()


def _json_list(text: str) -> list[str]:
    try:
        val = json.loads(text)
        if isinstance(val, list):
            return [str(v) for v in val]
    except (json.JSONDecodeError, TypeError):
        pass
    return [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]


def _test_case_fields(block: str) -> dict[str, str]:
    """Parse GEval's 'Test Case:' block ("Input:\n...\n\nActual Output:\n...")."""
    labels = {
        "input": "input", "actual output": "actual_output", "expected output": "expected_output",
        "context": "context", "retrieval context": "retrieval_context", "tools called": "tools_called",
        "expected tools": "expected_tools",
    }
    fields: dict[str, str] = {}
    pattern = re.compile(r"^(Input|Actual Output|Expected Output|Context|Retrieval Context|Tools Called|Expected Tools):\s*$", re.M)
    marks = list(pattern.finditer(block))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(block)
        fields[labels[m.group(1).lower()]] = block[m.end() : end].strip()
    return fields


class MockJudge(DeepEvalBaseLLM):
    """Deterministic offline judge that answers DeepEval's prompts."""

    def __init__(self) -> None:
        super().__init__("mock-judge")
        self.calls: list[str] = []  # schema names, for debugging

    def load_model(self, *args: Any, **kwargs: Any) -> MockJudge:
        return self

    def get_model_name(self, *args: Any, **kwargs: Any) -> str:
        return "mock-judge (offline)"

    def generate(self, prompt: str, schema: Any = None, **kwargs: Any) -> Any:
        data = self._answer(prompt, schema)
        if schema is None:
            return json.dumps(data)
        return schema.model_validate(data)

    async def a_generate(self, prompt: str, schema: Any = None, **kwargs: Any) -> Any:
        return self.generate(prompt, schema, **kwargs)

    # ------------------------------------------------------------------
    def _answer(self, prompt: str, schema: Any) -> dict:
        name = getattr(schema, "__name__", "")
        module = getattr(schema, "__module__", "")
        self.calls.append(f"{module.split('.')[-2] if '.' in module else module}.{name}")

        if name.endswith("ScoreReason") or name == "Reason":
            return {"reason": "Scored offline by the deterministic mock judge (word overlap and number matching)."}

        if "answer_relevancy" in module:
            if name == "Statements":
                return {"statements": h.sentences(_between(prompt, "Text:"))}
            if name == "Verdicts":
                question = _between(prompt, "Input:", ("\n\nStatements:",))
                stmts = _json_list(_between(prompt, "Statements:"))
                return {"verdicts": [self._v(h.relevant(s, question), "off-topic") for s in stmts]}

        if "faithfulness" in module:
            if name == "Truths":
                return {"truths": h.sentences(_between(prompt, "Text:"))}
            if name == "Claims":
                return {"claims": h.sentences(_between(prompt, "AI Output:"))}
            if name == "Verdicts":
                ctx = _between(prompt, "Retrieval Contexts:", ("\n\nClaims:",))
                claims = _json_list(_between(prompt, "Claims:"))
                out = []
                for c in claims:
                    if h.supported(c, ctx) or h.is_refusal(c):
                        out.append({"verdict": "yes"})
                    elif h.contradicts(c, ctx):
                        out.append({"verdict": "no", "reason": "The numbers in this claim contradict the context."})
                    else:
                        out.append({"verdict": "borderline" if h.overlap(c, ctx) >= 0.2 else "yes", "reason": "Not stated in the context."})
                return {"verdicts": out}

        if "hallucination" in module and name == "Verdicts":
            contexts = _json_list(_between(prompt, "Contexts:", ("\n\nActual Output:",)))
            output = _between(prompt, "Actual Output:")
            out = []
            for c in contexts:
                bad = h.contradicts(output, c)
                out.append({"verdict": "no" if bad else "yes", "reason": "Output contradicts this context." if bad else "Output agrees with this context."})
            return {"verdicts": out}

        if "contextual_precision" in module and name == "Verdicts":
            expected = _between(prompt, "Expected output:", ("\n\nRetrieval Context",)) or _between(prompt, "Expected Output:", ("\n\nRetrieval Context",))
            nodes = _json_list(_between(prompt, "Retrieval Context", ("\n\nJSON",)).split(":", 1)[-1])
            return {"verdicts": [{"verdict": "yes" if h.overlap(expected, n) >= 0.3 else "no", "reason": "Node overlaps the expected answer." if h.overlap(expected, n) >= 0.3 else "Node is not about the expected answer."} for n in nodes]}

        if "contextual_recall" in module and name == "Verdicts":
            expected = _between(prompt, "Expected Output:", ("\n\nRetrieval Context",))
            ctx = _between(prompt, "Retrieval Context:")
            return {"verdicts": [{"verdict": "yes" if h.supported(s, ctx) else "no", "reason": "Attributable to the retrieval context." if h.supported(s, ctx) else "Not found in the retrieval context."} for s in h.sentences(expected)]}

        if "g_eval" in module:
            if name == "Steps":
                criteria = _between(prompt, "Evaluation Criteria:", ("\n\n**", "\n**"))
                return {"steps": [f"Criteria: {criteria}", "Read the input and the actual output.", "Check the output against the criteria and any expected output or context.", "Lower the score for each violation."]}
            if name == "ReasonScore":
                steps = _between(prompt, "Evaluation Steps:", ("\n\nRubric:", "\n\nTest Case:"))
                criteria = steps.split("Criteria:", 1)[-1].split("\n")[0] if "Criteria:" in steps else steps
                fields = _test_case_fields(_between(prompt, "Test Case:", ("\n\nParameters:",)))
                lo, hi = (0, 10)
                m = re.search(r"between (\d+) and (\d+)", prompt)
                if m:
                    lo, hi = int(m.group(1)), int(m.group(2))
                s, reason = h.geval_score(criteria, fields)
                return {"reason": reason, "score": round(lo + s * (hi - lo))}

        if "task_completion" in module:
            if name == "TaskAndOutcome":
                task = _between(prompt, "input:", ("\ntools called:", "\nresponse:"))
                resp = _between(prompt, "response:")
                return {"task": task, "outcome": resp}
            if name == "TaskCompletionVerdict":
                task = _between(prompt, "Task:", ("\n\nActual outcome",))
                outcome = _between(prompt, "Actual outcome:")
                ok = h.overlap(task, outcome) > 0 or h.is_refusal(outcome)
                return {"verdict": 1.0 if ok else 0.2, "reason": "The outcome addresses the task." if ok else "The outcome does not address the task."}

        if "pii_leakage" in module:
            if name == "ExtractedPII":
                return {"extracted_pii": h.find_pii(_between(prompt, "Text:"))}
            if name == "Verdicts":
                items = _json_list(_between(prompt, "statements:", ("\n",)))
                return {"verdicts": [{"verdict": "yes", "reason": "Contains personal data."} for _ in items]}

        if "argument_correctness" in module and name == "Verdicts":
            calls = _between(prompt, "Tools Called:") or _between(prompt, "Tool Calls:")
            n = max(1, calls.count('"name"') or calls.count("name="))
            return {"verdicts": [{"verdict": "yes"} for _ in range(n)]}

        if name == "ToolSelectionScore":
            return {"score": 1.0, "reason": "Tool selection judged offline: names compared deterministically."}

        return self._generic(schema)

    @staticmethod
    def _v(verdict: str, why: str) -> dict:
        return {"verdict": verdict} if verdict == "yes" else {"verdict": verdict, "reason": why}

    @staticmethod
    def _generic(schema: Any) -> dict:
        if schema is None:
            return {}
        out: dict[str, Any] = {}
        for fname, field in schema.model_fields.items():
            ann = str(field.annotation)
            if "List" in ann or "list" in ann:
                out[fname] = []
            elif "float" in ann or "int" in ann:
                out[fname] = 1
            elif "bool" in ann:
                out[fname] = True
            else:
                out[fname] = "offline"
        return out


_MOCK: MockJudge | None = None


def get_judge() -> Any:
    """The judge for DeepEval metrics: MockJudge offline, the judge model name live."""
    global _MOCK
    if is_offline():
        _MOCK = _MOCK or MockJudge()
        return _MOCK
    return judge_model()
