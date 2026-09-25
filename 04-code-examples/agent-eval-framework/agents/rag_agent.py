"""
RAG Agent — Enterprise Policy Q&A Agent.

A RAG-based agent that answers questions about company policies
by retrieving relevant sections from a knowledge base and generating
responses grounded in the retrieved context.

Used in: Module 05 (Project 2), Module 14 (Capstone)

Enterprise scenario: HR department's policy Q&A bot that answers
employee questions about vacation, expenses, remote work, etc.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# Enterprise policy knowledge base (simulated vector store)
POLICY_DOCUMENTS = [
    {
        "id": "vacation-001",
        "title": "Vacation Policy",
        "section": "4.1",
        "content": (
            "All full-time employees are entitled to 15 days of paid vacation "
            "per calendar year. Unused vacation days may be carried over to the "
            "following year, up to a maximum of 5 days. Vacation requests must "
            "be submitted to the employee's direct manager at least 14 calendar "
            "days before the requested start date. Requests for more than 5 "
            "consecutive days require VP-level approval. Part-time employees "
            "receive prorated vacation based on their scheduled hours."
        ),
    },
    {
        "id": "remote-001",
        "title": "Remote Work Policy",
        "section": "5.2",
        "content": (
            "Eligible employees may work remotely for up to three (3) days per "
            "week, subject to manager approval. A Remote Work Agreement form "
            "must be completed and signed before commencing remote work. All "
            "remote employees must be available during core business hours of "
            "10:00 AM to 3:00 PM in their local timezone. Equipment allowance "
            "of $500 is provided for home office setup. Remote work privileges "
            "may be revoked if performance standards are not maintained."
        ),
    },
    {
        "id": "expense-001",
        "title": "Expense Reimbursement Policy",
        "section": "7.1",
        "content": (
            "Business expenses must be submitted through the company expense "
            "portal within 30 days of the expense date. Original receipts are "
            "required for all expenses exceeding $25. Expenses over $500 require "
            "prior manager approval. Travel expenses follow the GSA per diem "
            "rates for meals and incidentals. Approved reimbursements are "
            "processed within 10 business days. Personal expenses are not "
            "eligible for reimbursement under any circumstances."
        ),
    },
    {
        "id": "pto-001",
        "title": "Paid Time Off — Sick Leave",
        "section": "4.3",
        "content": (
            "Employees receive 10 days of paid sick leave per year. Sick leave "
            "may be used for personal illness, medical appointments, or care "
            "of an immediate family member. A doctor's note is required for "
            "absences exceeding 3 consecutive days. Unused sick leave does not "
            "carry over and is not paid out upon termination. Sick leave abuse "
            "may result in disciplinary action."
        ),
    },
    {
        "id": "conduct-001",
        "title": "Code of Conduct",
        "section": "2.1",
        "content": (
            "All employees are expected to act with integrity, respect, and "
            "professionalism. Harassment, discrimination, and retaliation of "
            "any kind are strictly prohibited. Violations should be reported "
            "to HR or through the anonymous ethics hotline. The company "
            "maintains a zero-tolerance policy for workplace violence. "
            "Confidential company information must not be shared externally "
            "without authorization."
        ),
    },
    {
        "id": "perf-001",
        "title": "Performance Review Process",
        "section": "6.1",
        "content": (
            "Performance reviews are conducted semi-annually in June and "
            "December. Each review includes self-assessment, manager "
            "assessment, and a calibration meeting. Ratings use a 5-point "
            "scale: Exceeds Expectations, Meets Expectations, Developing, "
            "Needs Improvement, Unsatisfactory. Compensation adjustments "
            "and promotions are determined during the December review cycle. "
            "Employees rated Needs Improvement receive a 60-day performance "
            "improvement plan (PIP)."
        ),
    },
    {
        "id": "benefits-001",
        "title": "Health Benefits",
        "section": "8.1",
        "content": (
            "The company offers three health insurance plans: Basic HMO, "
            "Standard PPO, and Premium PPO. Enrollment occurs during the "
            "annual open enrollment period in November or within 30 days "
            "of a qualifying life event. The company covers 80% of employee "
            "premiums and 50% of dependent premiums. Dental and vision "
            "insurance are included in all plans. A Health Savings Account "
            "(HSA) is available with the Standard and Premium plans."
        ),
    },
]

# Irrelevant documents (noise — for testing noise robustness)
NOISE_DOCUMENTS = [
    {
        "id": "noise-001",
        "title": "Office Cafeteria Menu",
        "section": "N/A",
        "content": (
            "Monday: Grilled chicken with rice. Tuesday: Pasta primavera. "
            "Wednesday: Fish tacos. Thursday: Beef stir-fry. Friday: Pizza day. "
            "Vegetarian options available daily. Cafeteria hours: 11:30 AM to 1:30 PM."
        ),
    },
    {
        "id": "noise-002",
        "title": "Parking Lot Assignments",
        "section": "N/A",
        "content": (
            "Parking spots A1-A20 are reserved for senior leadership. "
            "Spots B1-B50 are first-come-first-served. Electric vehicle "
            "charging stations are available in Row C. Motorcycle parking "
            "is in the covered area near entrance D."
        ),
    },
]


def retrieve_context(query: str, top_k: int = 3, include_noise: bool = False) -> list[dict]:
    """
    Simulate vector search retrieval.

    In a real system, this would use a vector database (ChromaDB, Pinecone, etc.)
    with embedding-based similarity search. For course purposes, we use
    keyword matching to simulate retrieval with controllable quality.

    Args:
        query: The user's question
        top_k: Number of documents to retrieve
        include_noise: If True, mix in irrelevant documents (for testing noise robustness)
    """
    query_lower = query.lower()
    scored = []

    all_docs = POLICY_DOCUMENTS.copy()
    if include_noise:
        all_docs.extend(NOISE_DOCUMENTS)

    for doc in all_docs:
        score = 0
        content_lower = doc["content"].lower()
        title_lower = doc["title"].lower()

        # Simple keyword scoring (simulates embedding similarity)
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        title_words = set(title_lower.split())

        # Title match (weighted higher)
        title_overlap = len(query_words & title_words)
        score += title_overlap * 3

        # Content match
        content_overlap = len(query_words & content_words)
        score += content_overlap

        scored.append((score, doc))

    # Sort by score descending, take top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


SYSTEM_PROMPT = """You are an HR Policy Assistant for TechCorp.

Your role is to answer employee questions about company policies accurately
and helpfully, using ONLY the policy documents provided in the context.

Rules:
1. Base your answers strictly on the provided context
2. If the context doesn't contain the answer, say so clearly
3. Quote specific policy sections when relevant
4. Be concise but thorough
5. Never make up policies or numbers not in the context
6. If a question involves sensitive HR matters, recommend contacting HR directly
"""


def run_rag_agent(
    question: str,
    top_k: int = 3,
    include_noise: bool = False,
) -> dict:
    """
    Run the RAG agent on an employee question.

    Returns:
        dict with keys:
        - answer: str (the generated response)
        - retrieved_contexts: list[str] (retrieved document contents)
        - retrieved_titles: list[str] (retrieved document titles)
        - total_tokens: int
        - model: str
    """
    # Step 1: Retrieve relevant context
    retrieved_docs = retrieve_context(question, top_k=top_k, include_noise=include_noise)
    context_texts = [doc["content"] for doc in retrieved_docs]
    context_titles = [f"{doc['title']} (Section {doc['section']})" for doc in retrieved_docs]

    # Step 2: Build the prompt with retrieved context
    context_block = "\n\n---\n\n".join(
        f"**{title}**\n{content}"
        for title, content in zip(context_titles, context_texts)
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Context from company policy documents:\n\n"
                f"{context_block}\n\n"
                f"---\n\n"
                f"Employee question: {question}"
            ),
        },
    ]

    # Step 3: Generate answer
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
    )

    return {
        "answer": response.choices[0].message.content or "",
        "retrieved_contexts": context_texts,
        "retrieved_titles": context_titles,
        "total_tokens": response.usage.total_tokens if response.usage else 0,
        "model": model,
    }


# Pre-built evaluation dataset for RAG testing
RAG_EVAL_DATASET = [
    {
        "question": "How many vacation days do employees get per year?",
        "ground_truth": "All full-time employees are entitled to 15 days of paid vacation per calendar year.",
        "expected_section": "vacation-001",
    },
    {
        "question": "How many days can I carry over unused vacation?",
        "ground_truth": "Unused vacation days may be carried over up to a maximum of 5 days.",
        "expected_section": "vacation-001",
    },
    {
        "question": "How many days per week can I work remotely?",
        "ground_truth": "Eligible employees may work remotely for up to three (3) days per week, subject to manager approval.",
        "expected_section": "remote-001",
    },
    {
        "question": "What are the core business hours for remote workers?",
        "ground_truth": "All remote employees must be available during core business hours of 10:00 AM to 3:00 PM in their local timezone.",
        "expected_section": "remote-001",
    },
    {
        "question": "What is the deadline for submitting expense reports?",
        "ground_truth": "Business expenses must be submitted within 30 days of the expense date.",
        "expected_section": "expense-001",
    },
    {
        "question": "Do I need receipts for a $20 expense?",
        "ground_truth": "Original receipts are required for all expenses exceeding $25. A $20 expense does not require a receipt.",
        "expected_section": "expense-001",
    },
    {
        "question": "How many sick days do I get?",
        "ground_truth": "Employees receive 10 days of paid sick leave per year.",
        "expected_section": "pto-001",
    },
    {
        "question": "When do I need a doctor's note for sick leave?",
        "ground_truth": "A doctor's note is required for absences exceeding 3 consecutive days.",
        "expected_section": "pto-001",
    },
    {
        "question": "When are performance reviews conducted?",
        "ground_truth": "Performance reviews are conducted semi-annually in June and December.",
        "expected_section": "perf-001",
    },
    {
        "question": "What percentage of health insurance premiums does the company cover?",
        "ground_truth": "The company covers 80% of employee premiums and 50% of dependent premiums.",
        "expected_section": "benefits-001",
    },
]


if __name__ == "__main__":
    print("RAG Agent — Enterprise Policy Q&A")
    print("=" * 50)

    test_questions = [
        "How many vacation days do I get?",
        "Can I work from home?",
        "How do I submit expense reports?",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        result = run_rag_agent(q)
        print(f"A: {result['answer'][:200]}...")
        print(f"Sources: {result['retrieved_titles']}")
        print(f"Tokens: {result['total_tokens']}")
