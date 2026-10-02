"""Project 4 / Lecture 8.4 - Red team the SecureBank agent: 16 attacks
(5 injection, 3 jailbreak, 3 PII, 3 unauthorized transactions, 2 exfiltration)
against v1 (as launched) and v2 (hardened), with a severity report.

    uv run python demos/m08_project4_banking_redteam.py    # writes reports/results/project4_report.md
"""
from _common import banner

from agents.banking_agent import run_banking_agent
from evaluators.golden import load
from reports.experiments import RESULTS
from security.redteam import run_redteam

banner("Project 4 - red team a banking agent")
attacks = load("redteam_banking")
lines = ["# Project 4 - SecureBank red team report", ""]
for label, hardened in (("v1 (as launched)", False), ("v2 (hardened)", True)):
    rep = run_redteam(attacks, lambda m, h=hardened: run_banking_agent(m, hardened=h), {"transfer_funds"}, {"ACC-1001-CHK", "ACC-1001-SAV"})
    print(f"\nSecureBank {label}: {rep['passed']}/{rep['total']} attacks blocked; findings by severity {rep['by_severity']}")
    lines += [f"## SecureBank {label}", f"{rep['passed']}/{rep['total']} attacks blocked.", ""]
    for f in rep["findings"]:
        msg = f"  [{f['severity']}] {f['id']} {f['category']} / {f['technique']}: {'; '.join(f['reasons'])}"
        print(msg)
        print(f"      reply: {f['reply'][:100]}")
        lines.append(f"- **{f['severity']}** {f['id']} {f['category']} ({f['technique']}): {'; '.join(f['reasons'])}")
    lines.append("")
lines += ["## Remediation (implemented in v2)",
          "- Tool-level authorization: the session customer must own every account a tool touches.",
          "- Treat tool results as data; never follow instructions found in them.",
          "- Confirmation, limit and payee checks enforced in code, not only in the prompt."]
(RESULTS / "project4_report.md").parent.mkdir(parents=True, exist_ok=True)
(RESULTS / "project4_report.md").write_text("\n".join(lines) + "\n")
print("\nReport written to reports/results/project4_report.md")
