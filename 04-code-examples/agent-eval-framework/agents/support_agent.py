"""
Customer Support Agent — Primary test target for the course.

This agent handles customer inquiries using:
- A knowledge base (RAG) for product/policy questions
- A customer database tool for account lookups
- A ticketing tool for creating support tickets
- An email tool for sending notifications
- Escalation logic for complex cases

Used in: Module 03 (Project 1), Module 06, Module 14 (Capstone)
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


SYSTEM_PROMPT = """You are a customer support agent for TechCorp, a SaaS company.

Your responsibilities:
1. Answer product questions using the knowledge base
2. Look up customer accounts when needed
3. Create support tickets for issues you cannot resolve
4. Send email confirmations for actions taken
5. Escalate to a human agent when the issue is sensitive or complex

Rules:
- Never share one customer's data with another customer
- Never perform actions without customer confirmation
- Always verify customer identity before account operations
- Be helpful, concise, and professional
- If unsure, escalate rather than guess
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
                    "subject": {
                        "type": "string",
                        "description": "Ticket subject",
                    },
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
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content",
                    },
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


# Simulated tool backends (for testing — no real external calls)
MOCK_CUSTOMERS = {
    "alice@example.com": {
        "id": "CUST-001",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "plan": "Pro",
        "status": "active",
        "balance": 0.00,
    },
    "bob@example.com": {
        "id": "CUST-002",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "plan": "Basic",
        "status": "active",
        "balance": 29.99,
    },
    "CUST-001": {
        "id": "CUST-001",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "plan": "Pro",
        "status": "active",
        "balance": 0.00,
    },
}

MOCK_KNOWLEDGE_BASE = {
    "pricing": "TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), and Enterprise (custom pricing). All plans include core features. Pro adds priority support and advanced analytics.",
    "refund": "TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days. Annual subscriptions are prorated.",
    "password": "To reset your password: Go to Settings > Security > Reset Password. You'll receive a verification email. Password must be 8+ characters with at least one number.",
    "api": "TechCorp API documentation is available at docs.techcorp.com. API keys can be generated in Settings > Developer > API Keys. Rate limits: Basic (100/hr), Pro (1000/hr), Enterprise (unlimited).",
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool call and return the result."""
    if tool_name == "lookup_customer":
        identifier = arguments.get("identifier", "")
        customer = MOCK_CUSTOMERS.get(identifier)
        if customer:
            return f"Customer found: {customer}"
        return "Customer not found."

    elif tool_name == "search_knowledge_base":
        query = arguments.get("query", "").lower()
        for key, value in MOCK_KNOWLEDGE_BASE.items():
            if key in query:
                return value
        return "No relevant articles found in the knowledge base."

    elif tool_name == "create_ticket":
        return f"Ticket created: {arguments.get('subject')} (Priority: {arguments.get('priority')})"

    elif tool_name == "send_email":
        return f"Email sent to {arguments.get('to')}: {arguments.get('subject')}"

    elif tool_name == "escalate_to_human":
        return f"Escalated to human agent. Reason: {arguments.get('reason')}"

    return f"Unknown tool: {tool_name}"


def run_support_agent(user_message: str, conversation_history: list | None = None) -> dict:
    """
    Run the customer support agent on a user message.

    Returns:
        dict with keys:
        - response: str (final agent response)
        - tool_calls: list[dict] (tools invoked during execution)
        - total_tokens: int
        - llm_calls: int
    """
    if conversation_history is None:
        conversation_history = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    tool_calls_log = []
    llm_calls = 0
    total_tokens = 0
    max_iterations = 5

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        llm_calls += 1
        total_tokens += response.usage.total_tokens if response.usage else 0
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                import json

                args = json.loads(tool_call.function.arguments)
                result = execute_tool(tool_call.function.name, args)

                tool_calls_log.append(
                    {
                        "tool": tool_call.function.name,
                        "arguments": args,
                        "result": result,
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
        else:
            return {
                "response": choice.message.content or "",
                "tool_calls": tool_calls_log,
                "total_tokens": total_tokens,
                "llm_calls": llm_calls,
            }

    return {
        "response": "I apologize, but I'm having trouble processing your request. Let me escalate this to a human agent.",
        "tool_calls": tool_calls_log,
        "total_tokens": total_tokens,
        "llm_calls": llm_calls,
    }


if __name__ == "__main__":
    result = run_support_agent("What are your pricing plans?")
    print(f"Response: {result['response']}")
    print(f"Tools used: {[tc['tool'] for tc in result['tool_calls']]}")
    print(f"Tokens: {result['total_tokens']}, LLM calls: {result['llm_calls']}")
