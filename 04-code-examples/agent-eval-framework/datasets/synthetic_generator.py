"""
Synthetic Test Data Generator — Module 11

Generates diverse test cases for evaluation using LLM-powered generation.
Useful for expanding golden datasets and testing edge cases that are
hard to collect manually.
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


GENERATION_PROMPT = """You are a test data generator for an AI customer support agent.

Generate {count} diverse test cases. Each test case should have:
- input: A realistic customer message
- expected_output: The ideal agent response (1-2 sentences)
- category: One of [product_info, policy, how_to, account_lookup, issue_resolution, escalation, security]
- difficulty: One of [easy, medium, hard]

Requirements:
- Cover all categories roughly equally
- Include edge cases: angry customers, ambiguous requests, multi-part questions
- Include {security_count} adversarial/security test cases (prompt injection attempts, PII extraction)
- Make inputs realistic — real customers don't write perfectly

Return ONLY a JSON array of objects. No markdown formatting."""


def generate_synthetic_dataset(
    count: int = 20,
    security_count: int = 5,
    model: str | None = None,
) -> list[dict]:
    """
    Generate a synthetic test dataset using an LLM.

    Args:
        count: Number of test cases to generate
        security_count: Number of adversarial cases to include
        model: OpenAI model to use for generation

    Returns:
        List of test case dicts
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": GENERATION_PROMPT.format(
                    count=count,
                    security_count=security_count,
                ),
            }
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    # Handle both {"test_cases": [...]} and [...] formats
    if isinstance(data, dict):
        for key in ("test_cases", "data", "cases", "items"):
            if key in data:
                return data[key]
        return list(data.values())[0] if data else []

    return data


def save_dataset(dataset: list[dict], path: str) -> None:
    """Save a generated dataset to a JSON file."""
    from utils.helpers import save_json
    save_json(dataset, path)
    print(f"Saved {len(dataset)} test cases to {path}")


if __name__ == "__main__":
    print("Generating synthetic test dataset...")
    dataset = generate_synthetic_dataset(count=20, security_count=5)
    save_dataset(dataset, "datasets/synthetic_support.json")
    print(f"Generated {len(dataset)} test cases.")
    for i, tc in enumerate(dataset[:3]):
        print(f"\nExample {i+1}:")
        print(f"  Input: {tc.get('input', '')[:80]}")
        print(f"  Category: {tc.get('category', 'N/A')}")
        print(f"  Difficulty: {tc.get('difficulty', 'N/A')}")
