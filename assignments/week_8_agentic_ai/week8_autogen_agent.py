"""
Week 8 - Agentic AI: CGPA/SGPA Agent with Cohere
A basic agent that uses Cohere's tool-calling to calculate CGPA from SGPAs
and check remarks (year back / scholarship / regular).

Name: Sahil Yadav
"""

import os
import json
import cohere
from dotenv import load_dotenv

# ─── Load API Key ───────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
if not COHERE_API_KEY or COHERE_API_KEY == "your-key-here":
    raise ValueError("Set your COHERE_API_KEY in the .env file")

co = cohere.ClientV2(api_key=COHERE_API_KEY)


# ─── Tool Functions ─────────────────────────────────────────────

def calculate_cgpa(semester_sgpas: list[float]) -> dict:
    """Calculate CGPA from semester SGPAs (0-10 scale). CGPA = average of all SGPAs."""
    if not semester_sgpas:
        return {"error": "No SGPAs provided"}
    cgpa = round(sum(semester_sgpas) / len(semester_sgpas), 2)
    return {"cgpa": cgpa, "semesters_counted": len(semester_sgpas)}


def check_remarks(cgpa: float) -> dict:
    """Check remarks: CGPA < 4 = year back, CGPA >= 9 = scholarship, else regular."""
    if cgpa < 4.0:
        return {"cgpa": cgpa, "status": "YEAR BACK", "remark": f"CGPA {cgpa} is below 4.0 — year back."}
    elif cgpa >= 9.0:
        return {"cgpa": cgpa, "status": "SCHOLARSHIP", "remark": f"CGPA {cgpa} is 9.0+ — scholarship eligible!"}
    else:
        return {"cgpa": cgpa, "status": "REGULAR", "remark": f"CGPA {cgpa} — no year back, no scholarship."}


# ─── Tool Definitions for Cohere ────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_cgpa",
            "description": "Calculate CGPA from semester SGPAs (0-10). CGPA = average of all SGPAs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "semester_sgpas": {
                        "type": "array", "items": {"type": "number"},
                        "description": "List of SGPA values (0-10) per semester",
                    },
                },
                "required": ["semester_sgpas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_remarks",
            "description": "Check remarks: <4 year back, >=9 scholarship, else regular.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cgpa": {"type": "number", "description": "The CGPA (0-10)"},
                },
                "required": ["cgpa"],
            },
        },
    },
]

TOOL_MAP = {
    "calculate_cgpa": calculate_cgpa,
    "check_remarks": check_remarks,
}


# ─── Agent Class ─────────────────────────────────────────────────

class CGPAAgent:
    """A basic Cohere-powered agent for CGPA calculation."""

    def __init__(self):
        self.model = "command-a-03-2025"
        self.system_msg = (
            "You are an academic CGPA assistant. Students give you their SGPA (0-10) "
            "for each semester. CGPA = average of all SGPAs. "
            "Use calculate_cgpa to compute, then check_remarks for year back/scholarship. "
            "Always be encouraging."
        )

    def run(self, user_query: str) -> str:
        """Run the agent on a query."""
        print(f"\n{'='*60}")
        print(f"  Query: {user_query}")
        print(f"{'='*60}")

        messages = [
            {"role": "system", "content": self.system_msg},
            {"role": "user", "content": user_query},
        ]

        print("  [Step 1] Sending to Cohere...")
        response = co.chat(model=self.model, messages=messages, tools=TOOLS)

        if response.message.tool_calls:
            print(f"  [Step 2] Agent called {len(response.message.tool_calls)} tool(s)")
            messages.append({"role": "assistant", "tool_calls": response.message.tool_calls})

            tool_results = []
            for tc in response.message.tool_calls:
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments)
                print(f"    🔧 {tool_name}({tool_args})")

                result = TOOL_MAP[tool_name](**tool_args) if tool_name in TOOL_MAP else {"error": "Unknown tool"}
                print(f"    ✅ {result}")

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })

            messages.extend(tool_results)
            print("  [Step 3] Getting final response...")
            final = co.chat(model=self.model, messages=messages, tools=TOOLS)
            answer = final.message.content[0].text if final.message.content else "Done."
        else:
            answer = response.message.content[0].text if response.message.content else "Done."

        print(f"\n  💬 Response:\n  {answer}")
        return answer


# ─── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = CGPAAgent()

    print("\n" + "=" * 60)
    print("  🎓 CGPA AGENT — Week 8 Agentic AI Demo")
    print("=" * 60)

    # Demo queries
    queries = [
        "My SGPAs are 7.5, 8.2, 6.9, 8.0. Calculate my CGPA and check remarks.",
        "I have only 1 semester with SGPA 3.5. What is my CGPA? Do I have a year back?",
        "My SGPAs are 9.2, 9.5, 9.0, 9.8. Am I eligible for scholarship?",
    ]

    for q in queries:
        agent.run(q)
        print()

    # Interactive mode
    print("\n" + "=" * 60)
    print("  🎤 INTERACTIVE MODE — Type your own queries!")
    print("  (type 'quit' to exit)")
    print("=" * 60)

    while True:
        user_input = input("\n  You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("  Goodbye! 👋")
            break
        if user_input:
            agent.run(user_input)
