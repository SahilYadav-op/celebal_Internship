"""
Week 8 - Agentic AI: CGPA/SGPA Agent — Streamlit Interface
A Streamlit app for the Cohere-powered CGPA/SGPA agent.
SGPA is entered as a number (0-10) per semester. CGPA = average of all SGPAs.

Name: Sahil Yadav
"""

import json
import streamlit as st
import cohere

# ─── Page Config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="🎓 CGPA Agent — Week 8",
    page_icon="🎓",
    layout="centered",
)

# ─── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .main-header p { color: #888; font-size: 1rem; }

    .tool-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .tool-card h4 { color: #667eea; margin: 0 0 0.3rem 0; font-size: 0.95rem; }
    .tool-card p { color: #aaa; margin: 0; font-size: 0.85rem; }

    .status-connected { color: #4ade80; font-weight: 600; }
    .status-disconnected { color: #f87171; font-weight: 600; }

    .trajectory-step {
        background: #1e1e2e;
        border-left: 3px solid #667eea;
        padding: 0.6rem 1rem;
        margin-bottom: 0.4rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
    }

    .result-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .cgpa-big {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Tool Functions ─────────────────────────────────────────────

def calculate_cgpa(semester_sgpas: list[float]) -> dict:
    """Calculate CGPA from a list of semester SGPAs (0-10 scale)."""
    if not semester_sgpas:
        return {"error": "No SGPAs provided"}
    cgpa = round(sum(semester_sgpas) / len(semester_sgpas), 2)
    return {"cgpa": cgpa, "semesters_counted": len(semester_sgpas)}


def check_remarks(cgpa: float) -> dict:
    """Check remarks based on CGPA: year back (<4), scholarship (>9), or nothing."""
    if cgpa < 4.0:
        return {
            "cgpa": cgpa,
            "status": "⚠️ YEAR BACK",
            "remark": f"CGPA {cgpa} is below 4.0 — student has a year back.",
        }
    elif cgpa >= 9.0:
        return {
            "cgpa": cgpa,
            "status": "🏆 SCHOLARSHIP ELIGIBLE",
            "remark": f"CGPA {cgpa} is 9.0 or above — eligible for scholarship!",
        }
    else:
        return {
            "cgpa": cgpa,
            "status": "✅ REGULAR",
            "remark": f"CGPA {cgpa} — no year back, no scholarship. Keep going!",
        }


# ─── Tool Definitions for Cohere ────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_cgpa",
            "description": "Calculate CGPA (Cumulative Grade Point Average) from semester SGPAs. Each SGPA is a number between 0 and 10. CGPA is the average of all semester SGPAs. If only 1 semester, CGPA equals that SGPA.",
            "parameters": {
                "type": "object",
                "properties": {
                    "semester_sgpas": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of SGPA values (0-10) for each semester, e.g. [7.5, 8.2, 6.9]",
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
            "description": "Check academic remarks based on CGPA. Below 4.0 = year back. 9.0 and above = scholarship eligible. Between 4-9 = regular, no remarks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cgpa": {
                        "type": "number",
                        "description": "The student's CGPA (0-10 scale)",
                    },
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


# ─── Agent Function ──────────────────────────────────────────────

def run_agent(user_query: str, api_key: str):
    """Run the Cohere agent and return response + trajectory."""
    co = cohere.ClientV2(api_key=api_key)
    trajectory = []

    system_msg = (
        "You are an academic CGPA assistant. Students give you their SGPA (0-10 scale) "
        "for each semester. SGPA is the score of one semester. CGPA is the average of all "
        "semester SGPAs. If only 1 semester, CGPA = that SGPA. "
        "Use the calculate_cgpa tool to compute CGPA, then use check_remarks to determine "
        "if the student has a year back (CGPA < 4), scholarship (CGPA >= 9), or nothing special. "
        "Always be encouraging."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_query},
    ]

    trajectory.append({"step": "🚀 Sent query to Cohere", "detail": user_query})
    response = co.chat(model="command-a-03-2025", messages=messages, tools=TOOLS)

    if response.message.tool_calls:
        trajectory.append({
            "step": f"🔧 Agent called {len(response.message.tool_calls)} tool(s)",
            "detail": ", ".join(tc.function.name for tc in response.message.tool_calls),
        })

        messages.append({"role": "assistant", "tool_calls": response.message.tool_calls})

        tool_results = []
        for tc in response.message.tool_calls:
            tool_name = tc.function.name
            tool_args = json.loads(tc.function.arguments)

            if tool_name in TOOL_MAP:
                result = TOOL_MAP[tool_name](**tool_args)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            trajectory.append({"step": f"✅ {tool_name}", "detail": json.dumps(result)})
            tool_results.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

        messages.extend(tool_results)

        trajectory.append({"step": "💬 Getting final response", "detail": ""})
        final_response = co.chat(model="command-a-03-2025", messages=messages, tools=TOOLS)
        answer = final_response.message.content[0].text if final_response.message.content else "Done."
    else:
        answer = response.message.content[0].text if response.message.content else "Done."

    trajectory.append({"step": "🏁 Done", "detail": ""})
    return answer, trajectory


# ─── Sidebar ─────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    st.markdown(
        "🔑 **Get your free API key:**\n\n"
        "[👉 dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)"
    )

    api_key = st.text_input(
        "Cohere API Key",
        type="password",
        placeholder="Paste your Cohere API key...",
        help="Sign up free at dashboard.cohere.com → API Keys → Create key",
    )

    if api_key:
        st.markdown('<span class="status-connected">● Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-disconnected">● Not connected — paste key above</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📋 How it works")
    st.markdown("""
    1. Enter **SGPA** (0-10) for each semester
    2. **CGPA** = average of all SGPAs
    3. Agent checks **remarks**:
       - CGPA **< 4** → ⚠️ Year Back
       - CGPA **≥ 9** → 🏆 Scholarship
       - Between → ✅ Regular
    """)

    st.markdown("---")
    st.markdown("## 🛠️ Agent Tools")
    tools_info = [
        ("📊 calculate_cgpa", "Averages all SGPAs"),
        ("📝 check_remarks", "Year back / Scholarship / Regular"),
    ]
    for name, desc in tools_info:
        st.markdown(f"""
        <div class="tool-card">
            <h4>{name}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Week 8 — Agentic AI | Sahil Yadav")


# ─── Main Content ────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🎓 CGPA/SGPA Agent</h1>
    <p>Week 8 — Agentic AI with Cohere Tool Calling</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

tab1, tab2 = st.tabs(["📊 Enter SGPAs", "💬 Chat with Agent"])

# ─── Tab 1: Enter SGPAs ─────────────────────────────────────────
with tab1:
    st.markdown("### Enter your SGPA for each semester")
    st.caption("SGPA is your semester score (0 to 10). Leave as 0 for semesters not yet completed.")

    num_semesters = st.slider("How many semesters completed?", 1, 8, 4, key="num_sem")

    sgpa_values = []
    # Show 4 per row
    for row_start in range(0, num_semesters, 4):
        cols = st.columns(4)
        for j in range(4):
            idx = row_start + j
            if idx < num_semesters:
                with cols[j]:
                    val = st.number_input(
                        f"Sem {idx + 1} SGPA",
                        min_value=0.0,
                        max_value=10.0,
                        value=0.0,
                        step=0.1,
                        format="%.1f",
                        key=f"sem_sgpa_{idx}",
                    )
                    sgpa_values.append(val)

    st.markdown("---")

    if st.button("🚀 Calculate CGPA & Check Remarks", use_container_width=True, type="primary", key="btn_calc"):
        valid_sgpas = sgpa_values

        if not api_key:
            st.error("⚠️ Paste your Cohere API key in the sidebar first!")
        else:
            sgpa_str = ", ".join(str(s) for s in valid_sgpas)
            query = (
                f"My semester SGPAs are: {sgpa_str}. "
                f"I have completed {len(valid_sgpas)} semester(s). "
                f"Calculate my CGPA and check if I have any remarks (year back, scholarship, or regular)."
            )

            with st.spinner("🤖 Agent is thinking..."):
                try:
                    answer, trajectory = run_agent(query, api_key)

                    # Quick local calculation for the big display
                    cgpa_local = round(sum(valid_sgpas) / len(valid_sgpas), 2)

                    # Determine color
                    if cgpa_local < 4:
                        color = "#f87171"
                        emoji = "⚠️"
                        status = "YEAR BACK"
                    elif cgpa_local >= 9:
                        color = "#4ade80"
                        emoji = "🏆"
                        status = "SCHOLARSHIP ELIGIBLE"
                    else:
                        color = "#667eea"
                        emoji = "✅"
                        status = "REGULAR"

                    st.markdown(f"""
                    <div class="result-box">
                        <p style="text-align:center; color:#888; margin:0;">Your CGPA</p>
                        <p class="cgpa-big" style="color:{color};">{cgpa_local}</p>
                        <p style="text-align:center; font-size:1.3rem; margin:0;">{emoji} {status}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("#### 🤖 Agent's Response:")
                    st.markdown(answer)

                    with st.expander("🔍 Agent Trajectory (Tool Calls)"):
                        for step in trajectory:
                            st.markdown(
                                f'<div class="trajectory-step">'
                                f'<strong>{step["step"]}</strong><br>'
                                f'<span style="color:#888">{step["detail"]}</span>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ─── Tab 2: Free Chat ───────────────────────────────────────────
with tab2:
    st.markdown("### Chat with the Agent")
    st.caption("Type anything — the agent will pick the right tool automatically")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "trajectory" in msg:
                with st.expander("🔍 Agent Trajectory"):
                    for step in msg["trajectory"]:
                        st.markdown(
                            f'<div class="trajectory-step">'
                            f'<strong>{step["step"]}</strong><br>'
                            f'<span style="color:#888">{step["detail"]}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

    user_input = st.chat_input("e.g. My SGPAs are 7.5, 8.2, 6.9. What is my CGPA?")

    if user_input:
        if not api_key:
            st.error("⚠️ Please enter your Cohere API key in the sidebar first!")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("🤖 Agent is thinking..."):
                    try:
                        answer, trajectory = run_agent(user_input, api_key)
                        st.markdown(answer)
                        with st.expander("🔍 Agent Trajectory"):
                            for step in trajectory:
                                st.markdown(
                                    f'<div class="trajectory-step">'
                                    f'<strong>{step["step"]}</strong><br>'
                                    f'<span style="color:#888">{step["detail"]}</span>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "trajectory": trajectory,
                        })
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
