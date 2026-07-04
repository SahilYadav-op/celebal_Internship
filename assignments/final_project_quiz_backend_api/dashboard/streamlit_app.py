# Streamlit dashboard for the Quiz Backend API
# run with: streamlit run dashboard/streamlit_app.py

import os
import sys

# so `import api_client` works no matter where streamlit is run from
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="Quiz Backend Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_api_url():
    # priority: env var > streamlit secrets > local default
    url = os.environ.get("API_BASE_URL", "").rstrip("/")
    if url:
        return url
    try:
        return st.secrets["API_BASE_URL"].rstrip("/")
    except Exception:
        pass
    return "http://127.0.0.1:8000"


if "api_base_url" not in st.session_state:
    st.session_state["api_base_url"] = get_api_url()

import api_client as api
from views import analytics, manage, quiz


def _safe_show(view, label):
    # Any unexpected error is shown as a plain message instead of letting
    # Streamlit's default traceback through, which prints internal server
    # file paths that shouldn't be exposed to visitors.
    try:
        view.show()
    except Exception:
        st.error(f"Something went wrong loading {label}. Please refresh and try again.")


# sidebar
with st.sidebar:
    st.title("Quiz Dashboard")
    st.caption("Quiz Backend Management System")
    st.divider()

    st.subheader("API Connection")
    # Not an editable field: letting any visitor to a public deployment
    # redirect the server's own outbound requests to an arbitrary URL
    # would be a server-side request forgery risk. The API base URL is
    # configured once via an env var or secrets.toml (see get_api_url()),
    # never from user input.
    st.caption(st.session_state["api_base_url"])

    if api.health_check():
        st.success("Connected")
    else:
        st.error("Offline")
        is_local = any(h in st.session_state["api_base_url"] for h in ("127.0.0.1", "localhost"))
        if is_local:
            st.caption("Start the FastAPI server, then refresh.")
            st.code("uvicorn app.main:app --reload", language="bash")
        else:
            st.caption(
                "The free-tier API sleeps after inactivity. "
                "Wait about a minute, then reload the page."
            )

    st.divider()
    st.caption("**Tabs**")
    st.caption("Take a Quiz - test yourself")
    st.caption("Manage - add / edit / delete")
    st.caption("Analytics - charts & KPIs")
    st.caption("")
    api_docs = f"{st.session_state['api_base_url']}/docs"
    st.markdown(f"[API docs / Swagger]({api_docs})")

    st.divider()
    st.markdown(
        'Made by <a href="https://www.linkedin.com/in/sahilgod01" target="_blank">Sahil Yadav</a>',
        unsafe_allow_html=True,
    )


# main area with 3 tabs - quiz first, then manage, then analytics
tab_quiz, tab_manage, tab_analytics = st.tabs(["Take a Quiz", "Manage", "Analytics"])

with tab_quiz:
    _safe_show(quiz, "the quiz")

with tab_manage:
    _safe_show(manage, "the manage page")

with tab_analytics:
    _safe_show(analytics, "the analytics page")
