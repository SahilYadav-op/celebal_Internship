"""Helper functions that call the FastAPI backend using requests."""

import requests
import streamlit as st


def _base():
    return st.session_state.get("api_base_url", "http://127.0.0.1:8000").rstrip("/")


def _handle_response(r):
    try:
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.exceptions.HTTPError:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        st.error(f"API error {r.status_code}: {detail}")
        return None


def _get(path, params=None):
    try:
        r = requests.get(_base() + path, params=params, timeout=10)
        return _handle_response(r)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at **{_base()}**. Is the FastAPI server running?")
    except requests.exceptions.Timeout:
        st.warning("API is slow to respond, try again in a moment.")
    return None


def _post(path, body):
    try:
        r = requests.post(_base() + path, json=body, timeout=10)
        return _handle_response(r)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at **{_base()}**.")
    return None


def _put(path, body):
    try:
        r = requests.put(_base() + path, json=body, timeout=10)
        return _handle_response(r)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at **{_base()}**.")
    return None


def _delete(path):
    try:
        r = requests.delete(_base() + path, timeout=10)
        r.raise_for_status()
        return True
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at **{_base()}**.")
    except requests.exceptions.HTTPError:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        st.error(f"API error {r.status_code}: {detail}")
    return False


def _bust_cache():
    # clear cached reads after any write so the UI shows fresh data
    get_questions.clear()
    get_choices.clear()


def health_check():
    try:
        return requests.get(_base() + "/health", timeout=5).status_code == 200
    except Exception:
        return False


# read calls, cached for 30s so we don't hit the api on every rerun

@st.cache_data(ttl=30)
def get_questions(category=None):
    params = {"limit": 200}
    if category:
        params["category"] = category
    return _get("/questions", params) or []


@st.cache_data(ttl=30)
def get_choices(question_id=None):
    params = {"limit": 500}
    if question_id:
        params["question_id"] = question_id
    return _get("/choices", params) or []


# question writes

def create_question(question_text, category=None):
    body = {"question_text": question_text}
    if category:
        body["category"] = category
    result = _post("/questions", body)
    if result:
        _bust_cache()
    return result


def update_question(qid, question_text=None, category=None):
    body = {}
    if question_text is not None:
        body["question_text"] = question_text
    if category is not None:
        body["category"] = category
    result = _put(f"/questions/{qid}", body)
    if result:
        _bust_cache()
    return result


def delete_question(qid):
    ok = _delete(f"/questions/{qid}")
    if ok:
        _bust_cache()
    return ok


# choice writes

def create_choice(question_id, choice_text, is_correct=False):
    body = {"question_id": question_id, "choice_text": choice_text, "is_correct": is_correct}
    result = _post("/choices", body)
    if result:
        _bust_cache()
    return result


def update_choice(cid, choice_text=None, is_correct=None):
    body = {}
    if choice_text is not None:
        body["choice_text"] = choice_text
    if is_correct is not None:
        body["is_correct"] = is_correct
    result = _put(f"/choices/{cid}", body)
    if result:
        _bust_cache()
    return result


def delete_choice(cid):
    ok = _delete(f"/choices/{cid}")
    if ok:
        _bust_cache()
    return ok
