# Quiz tab - pick a category, answer questions, get a score

import random
import streamlit as st

import api_client as api
from api_client import escape_markdown as esc


def _reset():
    for key in ["_quiz_qs", "_quiz_answers", "_quiz_submitted"]:
        st.session_state.pop(key, None)


def show():
    st.header("Take a Quiz")

    questions = api.get_questions()
    # a question is only playable if it has 2+ choices and a correct answer marked
    playable = [
        q for q in questions
        if len(q.get("choices", [])) >= 2
        and any(c["is_correct"] for c in q.get("choices", []))
    ]

    if not questions:
        st.info("No questions yet. Add some in the Manage tab first.")
        return
    if not playable:
        st.warning(
            "None of the questions are ready for a quiz yet. "
            "Each question needs at least 2 choices and one correct answer marked. "
            "Fix them in the Manage tab."
        )
        return

    # setup screen (shown until the user starts a quiz)
    if "_quiz_qs" not in st.session_state:
        raw_categories = sorted(set(q.get("category") or "Uncategorized" for q in playable))
        # Map escaped (safe-to-display) labels back to the raw category
        # values so filtering below still matches what's stored on each
        # question - only the label shown in the dropdown is escaped.
        cat_label_map = {esc(c): c for c in raw_categories}

        st.subheader("Configure your quiz")
        st.write(f"{len(playable)} ready question(s) available.")

        col1, col2 = st.columns(2)
        with col1:
            selected_label = st.selectbox("Category", ["All categories"] + list(cat_label_map.keys()))
            selected_cat = "All categories" if selected_label == "All categories" else cat_label_map[selected_label]
        with col2:
            pool = [
                q for q in playable
                if selected_cat == "All categories"
                or q.get("category") == selected_cat
            ]
            max_q = len(pool)
            if max_q == 0:
                st.warning(f"No ready questions in '{esc(selected_cat)}'.")
                return
            if max_q == 1:
                # st.slider requires min < max, so a single-question pool
                # can't use a slider - just use the one available question.
                st.write("Only 1 question available in this category.")
                n = 1
            else:
                n = st.slider("Number of questions", 1, min(max_q, 15), min(max_q, 5))

        if st.button("Start Quiz", type="primary"):
            sample = random.sample(pool, n)
            st.session_state["_quiz_qs"] = sample
            st.session_state["_quiz_answers"] = {}
            st.session_state["_quiz_submitted"] = False
            st.rerun()
        return

    qs = st.session_state["_quiz_qs"]
    answers = st.session_state["_quiz_answers"]  # question id -> chosen choice id
    submitted = st.session_state["_quiz_submitted"]

    # quiz in progress
    if not submitted:
        answered = len(answers)
        st.progress(answered / len(qs), text=f"Answered {answered} of {len(qs)}")
        st.divider()

        for i, q in enumerate(qs, 1):
            st.markdown(f"**Q{i}.  {esc(q['question_text'])}**")

            # Use choice ids as the radio options (format_func displays the
            # text) instead of matching a selection back to an id by
            # comparing displayed text - that breaks if two choices in the
            # same question happen to share identical text.
            choice_ids = [c["id"] for c in q["choices"]]
            choice_text_by_id = {c["id"]: esc(c["choice_text"]) for c in q["choices"]}

            current_id = answers.get(q["id"])
            current_index = choice_ids.index(current_id) if current_id in choice_ids else None

            chosen_id = st.radio(
                label=f"q{q['id']}",
                options=choice_ids,
                index=current_index,
                format_func=lambda cid: choice_text_by_id[cid],
                key=f"radio_{q['id']}",
                label_visibility="collapsed",
            )

            if chosen_id is not None:
                st.session_state["_quiz_answers"][q["id"]] = chosen_id

            st.divider()

        all_answered = len(st.session_state["_quiz_answers"]) == len(qs)

        c1, c2 = st.columns([2, 3])
        with c1:
            if st.button(
                "Submit answers",
                type="primary",
                disabled=not all_answered,
                use_container_width=True,
            ):
                st.session_state["_quiz_submitted"] = True
                st.rerun()
        with c2:
            if not all_answered:
                remaining = len(qs) - len(st.session_state["_quiz_answers"])
                st.caption(f"Answer {remaining} more question(s) to submit.")

        if st.button("Restart", type="secondary"):
            _reset()
            st.rerun()

    # results screen
    else:
        qs = st.session_state["_quiz_qs"]
        answers = st.session_state["_quiz_answers"]

        score = sum(
            1 for q in qs
            if answers.get(q["id"]) == next(
                (c["id"] for c in q["choices"] if c["is_correct"]), None
            )
        )
        total = len(qs)
        pct = score / total * 100

        if pct == 100:
            st.balloons()
            st.success(f"Perfect score: {score}/{total} ({pct:.0f}%)")
        elif pct >= 80:
            st.success(f"Great job: {score}/{total} ({pct:.0f}%)")
        elif pct >= 60:
            st.info(f"Good effort: {score}/{total} ({pct:.0f}%)")
        elif pct >= 40:
            st.warning(f"Keep practising: {score}/{total} ({pct:.0f}%)")
        else:
            st.error(f"{score}/{total} ({pct:.0f}%). Try again.")

        m1, m2, m3 = st.columns(3)
        m1.metric("Score", f"{score}/{total}")
        m2.metric("Percentage", f"{pct:.0f}%")
        m3.metric("Grade", "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 70 else "D" if pct >= 60 else "F")

        st.divider()
        st.subheader("Review")

        for i, q in enumerate(qs, 1):
            chosen_id = answers.get(q["id"])
            correct_choice = next((c for c in q["choices"] if c["is_correct"]), None)
            correct_id = correct_choice["id"] if correct_choice else None
            got_it = chosen_id == correct_id

            chosen_text = next((c["choice_text"] for c in q["choices"] if c["id"] == chosen_id), "No answer")
            correct_text = correct_choice["choice_text"] if correct_choice else "-"

            status = "correct" if got_it else "incorrect"
            with st.expander(f"Q{i} ({status}): {esc(q['question_text'][:70])}"):
                st.write(f"Your answer: {esc(chosen_text)}")
                if got_it:
                    st.success("Correct.")
                else:
                    st.error(f"Incorrect. The correct answer was: {esc(correct_text)}")
                if q.get("category"):
                    st.caption(f"Category: {esc(q['category'])}")

        st.divider()
        if st.button("Take another quiz", type="primary"):
            _reset()
            st.rerun()
