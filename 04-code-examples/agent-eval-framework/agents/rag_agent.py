"""
TechCorp Policy Assistant: a RAG agent over TechCorp's internal policies.

Three policy domains (Project 2 needs five golden cases per domain):
    hr              vacation, remote work, sick leave, reviews, benefits, conduct
    it_security     passwords/MFA, devices, phishing, data classification, VPN
    travel_expense  expenses, travel booking, meals/per diem, mileage, approvals

Retrieval is a simple keyword scorer standing in for a vector database, so the
retrieval step is visible and testable. ``remove_stopwords=False`` is the
shipped (slightly naive) behaviour; Module 5 shows how a retrieval fix moves
context precision.

The two steps are separate functions so Module 5.3 can test them in isolation:
    retrieve_context(question)            -> list[dict]
    generate_answer(question, contexts)   -> dict
    run_rag_agent(question)               -> both, end to end

    python -m agents.rag_agent "How many vacation days do I get?"
"""

from __future__ import annotations

import re
import sys

from agents.llm import clock, get_client
from config.settings import agent_model

POLICY_DOCUMENTS = [
    # ---- HR ---------------------------------------------------------------
    {
        "id": "vacation-001", "domain": "hr", "title": "Vacation Policy", "section": "4.1",
        "content": (
            "All full-time employees are entitled to 15 days of paid vacation per calendar year. "
            "Unused vacation days may be carried over to the following year, up to a maximum of 5 days. "
            "Vacation requests must be submitted to the employee's direct manager at least 14 calendar days "
            "before the requested start date. Requests for more than 5 consecutive days require VP-level approval. "
            "Part-time employees receive prorated vacation based on their scheduled hours."
        ),
    },
    {
        "id": "remote-001", "domain": "hr", "title": "Remote Work Policy", "section": "5.2",
        "content": (
            "Eligible employees may work remotely for up to three (3) days per week, subject to manager approval. "
            "A Remote Work Agreement form must be completed and signed before commencing remote work. "
            "All remote employees must be available during core business hours of 10:00 AM to 3:00 PM in their local timezone. "
            "An equipment allowance of $500 is provided for home office setup. "
            "Remote work privileges may be revoked if performance standards are not maintained."
        ),
    },
    {
        "id": "pto-001", "domain": "hr", "title": "Sick Leave", "section": "4.3",
        "content": (
            "Employees receive 10 days of paid sick leave per year. "
            "Sick leave may be used for personal illness, medical appointments, or care of an immediate family member. "
            "A doctor's note is required for absences exceeding 3 consecutive days. "
            "Unused sick leave does not carry over and is not paid out upon termination."
        ),
    },
    {
        "id": "perf-001", "domain": "hr", "title": "Performance Review Process", "section": "6.1",
        "content": (
            "Performance reviews are conducted semi-annually in June and December. "
            "Each review includes a self-assessment, a manager assessment, and a calibration meeting. "
            "Compensation adjustments and promotions are determined during the December review cycle. "
            "Employees rated Needs Improvement receive a 60-day performance improvement plan (PIP)."
        ),
    },
    {
        "id": "benefits-001", "domain": "hr", "title": "Health Benefits", "section": "8.1",
        "content": (
            "The company offers three health insurance plans: Basic HMO, Standard PPO, and Premium PPO. "
            "Enrollment occurs during the annual open enrollment period in November or within 30 days of a qualifying life event. "
            "The company covers 80% of employee premiums and 50% of dependent premiums. "
            "Dental and vision insurance are included in all plans."
        ),
    },
    # ---- IT security ------------------------------------------------------
    {
        "id": "itsec-001", "domain": "it_security", "title": "Password and MFA Standard", "section": "IT-1",
        "content": (
            "Passwords must be at least 14 characters long and must be changed every 180 days. "
            "Multi-factor authentication (MFA) is mandatory for email, VPN and all production systems. "
            "Approved MFA methods are the Okta Verify app or a hardware security key; SMS codes are not allowed. "
            "Passwords must never be shared, including with IT staff."
        ),
    },
    {
        "id": "itsec-002", "domain": "it_security", "title": "Device and Laptop Policy", "section": "IT-2",
        "content": (
            "Company laptops must use full-disk encryption and lock automatically after 5 minutes of inactivity. "
            "Personal devices may access email only through the managed Outlook app. "
            "A lost or stolen device must be reported to the IT Service Desk within 1 hour. "
            "Software may only be installed from the Self Service portal."
        ),
    },
    {
        "id": "itsec-003", "domain": "it_security", "title": "Phishing and Incident Reporting", "section": "IT-3",
        "content": (
            "Suspected phishing emails must be reported with the Report Phishing button in Outlook. "
            "Do not click links or open attachments in a suspected phishing email. "
            "Security incidents must be reported to security@techcorp.com or the 24/7 hotline at extension 4357. "
            "The security team acknowledges incident reports within 15 minutes."
        ),
    },
    {
        "id": "itsec-004", "domain": "it_security", "title": "Data Classification", "section": "IT-4",
        "content": (
            "TechCorp data is classified as Public, Internal, Confidential or Restricted. "
            "Customer personal data is Restricted and may not be stored on personal devices or shared outside approved systems. "
            "Confidential data may be emailed externally only when encrypted. "
            "Restricted data may not be pasted into external AI tools."
        ),
    },
    {
        "id": "itsec-005", "domain": "it_security", "title": "VPN and Remote Access", "section": "IT-5",
        "content": (
            "The company VPN must be used on any network outside the office, including home networks. "
            "VPN sessions disconnect after 12 hours and require MFA to reconnect. "
            "Public Wi-Fi may only be used with the VPN connected."
        ),
    },
    # ---- Travel & expense -------------------------------------------------
    {
        "id": "expense-001", "domain": "travel_expense", "title": "Expense Reimbursement Policy", "section": "7.1",
        "content": (
            "Business expenses must be submitted through the company expense portal within 30 days of the expense date. "
            "Original receipts are required for all expenses exceeding $25. "
            "Expenses over $500 require prior manager approval. "
            "Approved reimbursements are processed within 10 business days. "
            "Personal expenses are not eligible for reimbursement."
        ),
    },
    {
        "id": "travel-001", "domain": "travel_expense", "title": "Travel Booking", "section": "7.2",
        "content": (
            "All business travel must be booked through the Navan travel portal. "
            "Economy class is required for flights under 6 hours; premium economy is allowed for flights of 6 hours or more. "
            "International travel requires VP approval at least 21 days before departure. "
            "Hotel stays are capped at $250 per night in standard cities and $350 per night in high-cost cities."
        ),
    },
    {
        "id": "travel-002", "domain": "travel_expense", "title": "Meals and Per Diem", "section": "7.3",
        "content": (
            "Meals during business travel are reimbursed up to a daily per diem of $75. "
            "Alcohol is not reimbursable. "
            "Client entertainment meals require the names of all attendees on the expense report."
        ),
    },
    {
        "id": "travel-003", "domain": "travel_expense", "title": "Mileage and Ground Transport", "section": "7.4",
        "content": (
            "Personal car use for business is reimbursed at $0.70 per mile. "
            "Rideshare and taxis are reimbursable for business travel; parking at the home office is not. "
            "Rental cars must be mid-size or smaller unless four or more employees travel together."
        ),
    },
]

# Irrelevant documents (noise) for testing noise robustness.
NOISE_DOCUMENTS = [
    {
        "id": "noise-001", "domain": "noise", "title": "Office Cafeteria Menu", "section": "N/A",
        "content": (
            "Monday: Grilled chicken with rice. Tuesday: Pasta primavera. Wednesday: Fish tacos. "
            "Thursday: Beef stir-fry. Friday: Pizza day. Cafeteria hours are 11:30 AM to 1:30 PM."
        ),
    },
    {
        "id": "noise-002", "domain": "noise", "title": "Parking Lot Assignments", "section": "N/A",
        "content": (
            "Parking spots A1-A20 are reserved for senior leadership. Spots B1-B50 are first-come-first-served. "
            "Electric vehicle charging stations are available in Row C."
        ),
    },
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "i", "my", "me", "for", "to", "of", "in", "on",
    "what", "how", "when", "can", "many", "much", "be", "it", "and", "or", "if", "with", "at",
    "per", "get", "need", "there", "any", "by", "from", "this", "that", "should", "will", "we",
}

_WORD = re.compile(r"[a-z0-9$%]+")


def _words(text: str, remove_stopwords: bool) -> set[str]:
    words = set(_WORD.findall(text.lower()))
    return words - STOPWORDS if remove_stopwords else words


def retrieve_context(
    query: str,
    top_k: int = 3,
    include_noise: bool = False,
    remove_stopwords: bool = False,
) -> list[dict]:
    """
    Keyword retrieval standing in for vector search.

    Score = 3 x (query words in the title) + (query words in the content).
    With remove_stopwords=False (the shipped default) words like "the" and
    "for" also count, which is the retrieval weakness Module 5 diagnoses.
    """
    docs = POLICY_DOCUMENTS + (NOISE_DOCUMENTS if include_noise else [])
    q = _words(query, remove_stopwords)
    scored = []
    for i, doc in enumerate(docs):
        score = 3 * len(q & _words(doc["title"], remove_stopwords)) + len(
            q & _words(doc["content"], remove_stopwords)
        )
        scored.append((score, -i, doc))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [doc for _score, _i, doc in scored[:top_k]]


SYSTEM_PROMPT = """You are the TechCorp Policy Assistant for employees.

Answer questions about HR, IT security, and travel & expense policies using ONLY
the policy documents provided in the context.

Rules:
1. Base your answers strictly on the provided context
2. If the context doesn't contain the answer, say so clearly
3. Cite the policy title and section you used
4. Be concise but complete
5. Never make up policies or numbers that are not in the context
6. For sensitive HR matters (harassment, discipline), recommend contacting HR directly
"""


def generate_answer(question: str, contexts: list[dict], *, temperature: float = 0.1) -> dict:
    """Generation step only: answer from the contexts you pass in."""
    titles = [f"{d['title']} (Section {d['section']})" for d in contexts]
    context_block = "\n\n---\n\n".join(
        f"**{t}**\n{d['content']}" for t, d in zip(titles, contexts, strict=True)
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Context from company policy documents:\n\n{context_block}\n\n---\n\n"
                f"Employee question: {question}"
            ),
        },
    ]
    model = agent_model()
    start = clock.now()
    response = get_client().chat.completions.create(
        model=model, messages=messages, temperature=temperature
    )
    return {
        "answer": response.choices[0].message.content or "",
        "total_tokens": response.usage.total_tokens if response.usage else 0,
        "latency_s": round(clock.now() - start, 3),
        "model": model,
    }


def run_rag_agent(
    question: str,
    top_k: int = 3,
    include_noise: bool = False,
    remove_stopwords: bool = False,
) -> dict:
    """
    Retrieve, then generate.

    Returns: answer, retrieved_contexts (texts), retrieved_ids, retrieved_titles,
    total_tokens, latency_s, model.
    """
    docs = retrieve_context(
        question, top_k=top_k, include_noise=include_noise, remove_stopwords=remove_stopwords
    )
    gen = generate_answer(question, docs)
    return {
        "answer": gen["answer"],
        "retrieved_contexts": [d["content"] for d in docs],
        "retrieved_ids": [d["id"] for d in docs],
        "retrieved_titles": [f"{d['title']} (Section {d['section']})" for d in docs],
        "total_tokens": gen["total_tokens"],
        "latency_s": gen["latency_s"],
        "model": gen["model"],
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "How many vacation days do I get?"
    r = run_rag_agent(q)
    print(f"Q: {q}\nA: {r['answer']}\nSources: {r['retrieved_ids']}")
