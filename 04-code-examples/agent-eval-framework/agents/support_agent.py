"""
TechCorp Customer Support Agent: the course's running example (decision T1).

TechCorp is a SaaS company. The agent answers product and policy questions from
a knowledge base, looks up accounts, opens tickets, sends emails, and hands
sensitive cases to a human. It has exactly five tools:

    lookup_customer(identifier)
    search_knowledge_base(query)
    create_ticket(customer_id, subject, description, priority)
    send_email(to, subject, body)
    escalate_to_human(reason, urgency="normal")

Used in Modules 1, 3, 4, 6, 8, 9, 10, 11, 12 and the Module 14 capstone.

    python -m agents.support_agent "What are your pricing plans?"
"""

from __future__ import annotations

import json
import sys

from agents.llm import clock, get_client
from config.settings import agent_model

SYSTEM_PROMPT = """You are a customer support agent for TechCorp, a SaaS company.

Your responsibilities:
1. Answer product and policy questions using the knowledge base
2. Look up customer accounts when needed
3. Create support tickets for issues you cannot resolve
4. Send email confirmations for actions taken
5. Escalate to a human agent when the issue is sensitive or complex

Rules:
- Only state prices, limits and policies that appear in a knowledge base result
- Never share one customer's data with another customer
- Never perform actions without customer confirmation
- Always verify customer identity before account operations
- Be helpful, concise, and professional
- If unsure, escalate rather than guess

Escalation rules (call escalate_to_human):
- The customer mentions legal action or a lawyer -> urgency "urgent"
- The customer reports a security incident or data breach -> urgency "urgent"
- The customer reports lost or deleted data -> urgency "urgent"
- The customer asks for a manager or a human -> urgency "normal"
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up a customer's account by email or ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Customer email or account ID",
                    }
                },
                "required": ["identifier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the product knowledge base for answers",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support ticket for unresolved issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer's account ID",
                    },
                    "subject": {"type": "string", "description": "Ticket subject"},
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Ticket priority level",
                    },
                },
                "required": ["customer_id", "subject", "description", "priority"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why this needs human attention",
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["normal", "urgent"],
                        "description": "Urgency level for the escalation",
                    },
                },
                "required": ["reason"],
            },
        },
    },
]

TOOL_NAMES = [t["function"]["name"] for t in TOOLS]

# --- Simulated backends (no real external calls) ------------------------------

CUSTOMERS = [
    {
        "id": "CUST-001",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "plan": "Pro",
        "status": "active",
        "balance": 0.00,
        "signup_date": "2026-09-10",
        "invoices": [
            {"id": "INV-1001", "date": "2026-09-10", "amount": 29.99, "status": "paid"},
            {"id": "INV-1002", "date": "2026-09-10", "amount": 29.99, "status": "paid"},
        ],
    },
    {
        "id": "CUST-002",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "plan": "Basic",
        "status": "active",
        "balance": 29.99,
        "signup_date": "2025-11-02",
        "invoices": [
            {"id": "INV-2001", "date": "2026-09-02", "amount": 9.99, "status": "overdue"},
        ],
    },
    {
        "id": "CUST-003",
        "name": "Dana Lee",
        "email": "dana@example.com",
        "plan": "Enterprise",
        "status": "suspended",
        "balance": 1200.00,
        "signup_date": "2024-03-15",
        "invoices": [
            {"id": "INV-3001", "date": "2026-09-01", "amount": 1200.00, "status": "overdue"},
        ],
    },
]

# Lookup works by email or by account ID.
MOCK_CUSTOMERS = {c["email"]: c for c in CUSTOMERS} | {c["id"]: c for c in CUSTOMERS}

KNOWLEDGE_BASE = [
    {
        "id": "KB-101",
        "title": "Plans and pricing",
        "keywords": ["pricing", "price", "plan", "cost", "enterprise"],
        "text": (
            "TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), and "
            "Enterprise (custom pricing). All plans include core features. Pro adds "
            "priority support and advanced analytics."
        ),
    },
    {
        "id": "KB-102",
        "title": "Refund policy",
        "keywords": ["refund", "money back", "money-back"],
        "text": (
            "TechCorp offers a 30-day money-back guarantee on all plans. Refunds are "
            "processed within 5-7 business days. Annual subscriptions are prorated."
        ),
    },
    {
        "id": "KB-103",
        "title": "Password reset",
        "keywords": ["password", "reset", "log in", "login"],
        "text": (
            "To reset your password: Go to Settings > Security > Reset Password. "
            "You'll receive a verification email. Password must be 8+ characters "
            "with at least one number."
        ),
    },
    {
        "id": "KB-104",
        "title": "API keys and rate limits",
        "keywords": ["api", "rate limit", "rate limits", "developer"],
        "text": (
            "TechCorp API documentation is available at docs.techcorp.com. API keys "
            "can be generated in Settings > Developer > API Keys. Rate limits: Basic "
            "(100/hr), Pro (1000/hr), Enterprise (unlimited)."
        ),
    },
    {
        "id": "KB-105",
        "title": "Cancelling a subscription",
        "keywords": ["cancel", "cancellation", "close my account"],
        "text": (
            "To cancel, go to Settings > Billing > Cancel Subscription. Cancellation "
            "takes effect at the end of the current billing period. Your data is "
            "kept for 30 days after cancellation."
        ),
    },
]

# Kept for older lab code that imported the dict form.
MOCK_KNOWLEDGE_BASE = {a["keywords"][0]: a["text"] for a in KNOWLEDGE_BASE}

TICKETS: list[dict] = []  # tickets created in this process (inspect in tests)
OUTBOX: list[dict] = []  # emails "sent" in this process


def search_kb(query: str) -> dict | None:
    """Best keyword match for a query, or None."""
    q = query.lower()
    best, best_hits = None, 0
    for article in KNOWLEDGE_BASE:
        hits = sum(1 for k in article["keywords"] if k in q)
        if hits > best_hits:
            best, best_hits = article, hits
    return best


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool call against the simulated backends and return a string."""
    if tool_name == "lookup_customer":
        customer = MOCK_CUSTOMERS.get(arguments.get("identifier", "").strip())
        if customer:
            return f"Customer found: {json.dumps(customer)}"
        return "Customer not found."

    if tool_name == "search_knowledge_base":
        article = search_kb(arguments.get("query", ""))
        if article:
            return f"{article['id']} ({article['title']}): {article['text']}"
        return "No relevant articles found in the knowledge base."

    if tool_name == "create_ticket":
        ticket_id = f"TKT-{5001 + len(TICKETS)}"
        TICKETS.append({"id": ticket_id, **arguments})
        return (
            f"Ticket {ticket_id} created: {arguments.get('subject')} "
            f"(Priority: {arguments.get('priority')})"
        )

    if tool_name == "send_email":
        OUTBOX.append(dict(arguments))
        return f"Email sent to {arguments.get('to')}: {arguments.get('subject')}"

    if tool_name == "escalate_to_human":
        return (
            f"Escalated to human agent (urgency: {arguments.get('urgency', 'normal')}). "
            f"Reason: {arguments.get('reason')}"
        )

    return f"Unknown tool: {tool_name}"


def run_support_agent(
    user_message: str,
    conversation_history: list | None = None,
    *,
    system_prompt: str = SYSTEM_PROMPT,
    tools: list | None = None,
    temperature: float | None = None,
    max_iterations: int = 5,
) -> dict:
    """
    Run the support agent on one user message.

    Returns a dict with:
        response      final answer (str)
        tool_calls    [{"tool", "arguments", "result"}, ...] in call order
        total_tokens  prompt + completion tokens across all LLM calls
        llm_calls     number of LLM calls
        latency_s     end-to-end latency (virtual clock offline)
        model         model name used
    """
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history or [])
    messages.append({"role": "user", "content": user_message})

    client = get_client()
    model = agent_model()
    tools = TOOLS if tools is None else tools
    extra = {} if temperature is None else {"temperature": temperature}

    tool_calls_log: list[dict] = []
    llm_calls = 0
    total_tokens = 0
    start = clock.now()

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **extra,
        )
        llm_calls += 1
        total_tokens += response.usage.total_tokens if response.usage else 0
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = execute_tool(tool_call.function.name, args)
                tool_calls_log.append(
                    {"tool": tool_call.function.name, "arguments": args, "result": result}
                )
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": result}
                )
        else:
            return {
                "response": choice.message.content or "",
                "tool_calls": tool_calls_log,
                "total_tokens": total_tokens,
                "llm_calls": llm_calls,
                "latency_s": round(clock.now() - start, 3),
                "model": model,
            }

    return {
        "response": (
            "I apologize, but I'm having trouble processing your request. "
            "Let me escalate this to a human agent."
        ),
        "tool_calls": tool_calls_log,
        "total_tokens": total_tokens,
        "llm_calls": llm_calls,
        "latency_s": round(clock.now() - start, 3),
        "model": model,
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What are your pricing plans?"
    result = run_support_agent(question)
    print(f"Question: {question}")
    print(f"Response: {result['response']}")
    print(f"Tools used: {[tc['tool'] for tc in result['tool_calls']]}")
    print(f"Tokens: {result['total_tokens']}, LLM calls: {result['llm_calls']}")
