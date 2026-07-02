# Manage tab - forms to add/edit/delete questions and choices

import streamlit as st

import api_client as api


def show():
    st.header("🛠️ Manage Questions & Choices")

    # form to create a new question
    with st.expander("➕  Add a new question", expanded=False):
        with st.form("form_create_question", clear_on_submit=True):
            q_text = st.text_area(
                "Question text *",
                placeholder="e.g. What is the capital of France?",
                height=80,
            )
            q_cat = st.text_input(
                "Category  (optional)",
                placeholder="e.g. General Knowledge, Programming, Mathematics ...",
            )
            submitted = st.form_submit_button("✅ Create Question", type="primary")
            if submitted:
                if not q_text.strip():
                    st.error("Question text cannot be empty.")
                else:
                    result = api.create_question(q_text.strip(), q_cat.strip() or None)
                    if result:
                        st.success(f"Question #{result['id']} created!")
                        st.rerun()

    st.divider()

    questions = api.get_questions()
    if not questions:
        st.info("No questions yet, add one above!")
        return

    def _label(q):
        cat = f"[{q.get('category') or '-'}]"
        text = q["question_text"]
        short = text[:65] + "..." if len(text) > 65 else text
        return f"#{q['id']} {cat}  {short}"

    q_map = {_label(q): q for q in questions}
    picked_label = st.selectbox("Select a question to manage", list(q_map.keys()))
    q = q_map[picked_label]

    choices = q.get("choices", [])
    n_correct = sum(1 for c in choices if c["is_correct"])
    info_cols = st.columns(3)
    info_cols[0].metric("Choices", len(choices))
    info_cols[1].metric("Correct marked", n_correct)
    info_cols[2].metric("Status", "✅ Ready" if len(choices) >= 2 and n_correct >= 1 else "⚠️ Incomplete")

    # edit or delete the selected question
    edit_col, del_col = st.columns([4, 1])
    with edit_col:
        with st.expander("✏️  Edit question text / category"):
            with st.form(f"form_edit_q_{q['id']}"):
                new_text = st.text_area("Question text", value=q["question_text"], height=80)
                new_cat = st.text_input("Category", value=q.get("category") or "")
                if st.form_submit_button("Save changes", type="primary"):
                    if not new_text.strip():
                        st.error("Question text cannot be empty.")
                    else:
                        res = api.update_question(
                            q["id"],
                            question_text=new_text.strip(),
                            category=new_cat.strip() or None,
                        )
                        if res:
                            st.success("Question updated!")
                            st.rerun()

    with del_col:
        st.write("")
        st.write("")
        if st.button("🗑️ Delete", key=f"del_q_btn_{q['id']}", type="secondary", use_container_width=True):
            st.session_state["_confirm_del_q"] = q["id"]

    # ask for confirmation before deleting
    if st.session_state.get("_confirm_del_q") == q["id"]:
        st.warning(f"Delete question #{q['id']} and **all {len(choices)} choices**?  This cannot be undone.")
        yes, no = st.columns(2)
        if yes.button("Yes, delete everything", type="primary", key="confirm_del_yes"):
            if api.delete_question(q["id"]):
                st.success("Deleted.")
                st.session_state.pop("_confirm_del_q", None)
                st.rerun()
        if no.button("Cancel", key="confirm_del_no"):
            st.session_state.pop("_confirm_del_q", None)
            st.rerun()

    # choices of the selected question
    st.subheader(f"Choices for question #{q['id']}")

    if choices:
        for c in choices:
            icon = "✅" if c["is_correct"] else "☐"
            label = f"{icon}  [{c['id']}]  {c['choice_text'][:60]}"
            with st.expander(label):
                with st.form(f"form_edit_c_{c['id']}"):
                    new_ct = st.text_input("Choice text", value=c["choice_text"])
                    new_correct = st.checkbox("Mark as the correct answer", value=c["is_correct"])
                    save_col, del_col2 = st.columns(2)
                    if save_col.form_submit_button("💾 Save", type="primary"):
                        if not new_ct.strip():
                            st.error("Choice text cannot be empty.")
                        else:
                            res = api.update_choice(c["id"], choice_text=new_ct.strip(), is_correct=new_correct)
                            if res:
                                st.success("Updated!")
                                st.rerun()
                    if del_col2.form_submit_button("🗑️ Delete this choice"):
                        if api.delete_choice(c["id"]):
                            st.success("Choice deleted.")
                            st.rerun()
    else:
        st.info("No choices yet, add at least 2 below.")

    with st.expander("➕  Add a choice to this question"):
        with st.form(f"form_add_choice_{q['id']}", clear_on_submit=True):
            new_ct = st.text_input("Choice text *", placeholder="e.g. Paris")
            is_correct = st.checkbox("This is the correct answer", value=False)
            if st.form_submit_button("Add choice", type="primary"):
                if not new_ct.strip():
                    st.error("Choice text cannot be empty.")
                else:
                    res = api.create_choice(q["id"], new_ct.strip(), is_correct=is_correct)
                    if res:
                        st.success(f"Choice '{new_ct.strip()}' added!")
                        st.rerun()
