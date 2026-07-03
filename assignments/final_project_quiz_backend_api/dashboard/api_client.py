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


def clear_cache():
    # clear cached reads - after any write, or when the API base URL changes
    _cached_questions.clear()
    _cached_choices.clear()


def _bust_cache():
    clear_cache()


def health_check():
    try:
        return requests.get(_base() + "/health", timeout=5).status_code == 200
    except Exception:
        return False


# Read calls, cached for 30s so we don't hit the api on every rerun.
#
# The cached functions below raise on failure instead of showing an error
# and returning []. This matters: st.cache_data also caches (and replays)
# any st.error()/st.warning() calls made while the function ran, so a
# function that "handles" its own failure by returning [] would freeze a
# single transient error and keep replaying it for the full 30s ttl even
# after the API has recovered. A function that raises is never cached by
# Streamlit, so a transient failure only affects the current run - the
# next rerun tries the real request again.

def _get_json(path, params=None):
    r = requests.get(_base() + path, params=params, timeout=10)
    r.raise_for_status()
    return r.json() if r.content else {}


@st.cache_data(ttl=30)
def _cached_questions(category=None):
    params = {"limit": 200}
    if category:
        params["category"] = category
    return _get_json("/questions", params)


@st.cache_data(ttl=30)
def _cached_choices(question_id=None):
    params = {"limit": 500}
    if question_id:
        params["question_id"] = question_id
    return _get_json("/choices", params)


def get_questions(category=None):
    try:
        return _cached_questions(category)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at **{_base()}**. Is the FastAPI server running?")
    except requests.exceptions.Timeout:
        st.warning("API is slow to respond, try again in a moment.")
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
    return []


def get_choices(question_id=None):
    try:
        return _cached_choices(question_id)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at **{_base()}**. Is the FastAPI server running?")
    except requests.exceptions.Timeout:
        st.warning("API is slow to respond, try again in a moment.")
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
    return []


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
