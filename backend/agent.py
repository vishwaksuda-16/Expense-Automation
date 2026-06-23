import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an enterprise expense auditing AI. You analyze employee expense submissions and return a structured JSON decision.

Your job is to:
1. Determine the correct expense category
2. Assess the risk level and flag anomalies
3. Recommend an approval routing level

CATEGORIES (pick exactly one):
travel, meals, accommodation, supplies, equipment, entertainment, training, software, medical, other

RISK FLAGS:
- "low"    → Normal expense, matches description, reasonable amount
- "medium" → Slightly unusual amount or category mismatch, worth a human glance  
- "high"   → Suspicious pattern, duplicate risk, very high amount, category mismatch, vague description

APPROVAL LEVELS:
- "auto"           → Low risk, amount under 2000
- "manager"        → Medium risk OR amount 2000–10000
- "director"       → High risk OR amount 10000–50000
- "finance_review" → Amount over 50000 OR critical anomaly detected

ANOMALY SIGNALS TO WATCH FOR:
- Description does not match the submitted category
- Vague descriptions like "miscellaneous", "other stuff", "expenses"
- Round numbers with no context (e.g. amount: 10000, description: "work stuff")
- Entertainment or meals above 5000
- Equipment purchases above 30000 without justification

You must ALWAYS respond with valid JSON only. No explanation, no markdown, no extra text.

JSON format:
{
  "ai_category": "<category>",
  "risk_flag": "<low|medium|high>",
  "risk_reason": "<one concise sentence explaining the risk assessment>",
  "approval_level": "<auto|manager|director|finance_review>",
  "ai_notes": "<one sentence summary of your overall decision>"
}"""


def analyze_expense(employee: str, amount: float, submitted_category: str, description: str) -> dict:
    """
    Sends expense details to Groq LLaMA and returns a structured AI decision.
    Returns a dict with: ai_category, risk_flag, risk_reason, approval_level, ai_notes
    """

    user_message = f"""Analyze this expense submission:

Employee: {employee}
Amount: ₹{amount}
Submitted Category: {submitted_category}
Description: {description}

Return your JSON decision."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,       # low temp = consistent, deterministic decisions
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        # Validate all expected keys are present
        required_keys = {"ai_category", "risk_flag", "risk_reason", "approval_level", "ai_notes"}
        if not required_keys.issubset(result.keys()):
            raise ValueError(f"Missing keys in AI response: {result}")

        return result

    except json.JSONDecodeError:
        # If model returns malformed JSON, fall back to a safe default
        return {
            "ai_category": submitted_category.lower(),
            "risk_flag": "medium",
            "risk_reason": "AI parsing failed — flagged for manual review.",
            "approval_level": "manager",
            "ai_notes": "Automatic fallback due to AI response parse error."
        }

    except Exception as e:
        return {
            "ai_category": submitted_category.lower(),
            "risk_flag": "high",
            "risk_reason": f"AI service error: {str(e)}",
            "approval_level": "finance_review",
            "ai_notes": "Escalated due to AI service failure."
        }