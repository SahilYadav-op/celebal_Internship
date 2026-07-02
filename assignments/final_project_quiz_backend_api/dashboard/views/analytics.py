# Analytics tab - charts and stats built from the API data

import pandas as pd
import plotly.express as px
import streamlit as st

import api_client as api


def show():
    st.header("📊 Analytics Dashboard")

    questions = api.get_questions()
    if not questions:
        st.info("No questions yet. Go to **🛠️ Manage** and add some!")
        return

    # build a dataframe with one row per question
    q_rows = []
    for q in questions:
        choices = q.get("choices", [])
        q_rows.append({
            "id": q["id"],
            "question_text": q["question_text"],
            "category": q.get("category") or "Uncategorized",
            "num_choices": len(choices),
            "has_correct": any(c["is_correct"] for c in choices),
        })
    df_q = pd.DataFrame(q_rows)

    # and one row per choice
    c_rows = []
    for q in questions:
        for c in q.get("choices", []):
            c_rows.append({
                "question_id": q["id"],
                "category": q.get("category") or "Uncategorized",
                "is_correct": c["is_correct"],
                "choice_text": c["choice_text"],
            })
    c_cols = ["question_id", "category", "is_correct", "choice_text"]
    df_c = pd.DataFrame(c_rows) if c_rows else pd.DataFrame(columns=c_cols)

    # top row of stats
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📝 Total Questions", len(df_q))
    k2.metric("🔘 Total Choices", len(df_c))
    k3.metric("🏷️ Categories", df_q["category"].nunique())
    avg = f"{df_q['num_choices'].mean():.1f}" if not df_q.empty else "-"
    k4.metric("Avg Choices / Question", avg)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Questions per Category")
        cat_df = (
            df_q.groupby("category", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=False)
        )
        fig = px.bar(
            cat_df, x="category", y="count",
            color="category",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"category": "Category", "count": "# Questions"},
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-30, margin=dict(t=10, b=60))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Correct vs Incorrect Choices")
        if not df_c.empty:
            pie_df = (
                df_c["is_correct"]
                .map({True: "Correct ✅", False: "Incorrect ❌"})
                .value_counts()
                .reset_index()
            )
            pie_df.columns = ["label", "count"]
            fig2 = px.pie(
                pie_df, values="count", names="label",
                hole=0.55,
                color="label",
                color_discrete_map={"Correct ✅": "#2ecc71", "Incorrect ❌": "#e74c3c"},
            )
            fig2.update_traces(textinfo="percent+label")
            fig2.update_layout(showlegend=False, margin=dict(t=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Add choices to see this chart.")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Distribution of Choices per Question")
        fig3 = px.histogram(
            df_q, x="num_choices",
            nbins=max(1, int(df_q["num_choices"].max())),
            color_discrete_sequence=["#3498db"],
            labels={"num_choices": "# Choices", "count": "# Questions"},
        )
        fig3.update_layout(margin=dict(t=10), bargap=0.1)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Questions vs Choices per Category")
        if not df_c.empty:
            cat_q = df_q.groupby("category")["id"].count().reset_index(name="questions")
            cat_c = df_c.groupby("category").size().reset_index(name="choices")
            bubble = pd.merge(cat_q, cat_c, on="category", how="left").fillna(0)
            fig4 = px.scatter(
                bubble, x="questions", y="choices",
                size="choices", color="category",
                size_max=50,
                labels={"questions": "# Questions", "choices": "# Choices"},
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig4.update_layout(showlegend=False, margin=dict(t=10))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Add choices to see this chart.")

    # full table of questions at the bottom
    st.divider()
    st.subheader("📋 All Questions")

    df_display = df_q[["id", "category", "question_text", "num_choices", "has_correct"]].copy()
    df_display["status"] = df_display.apply(
        lambda r: "✅ Ready" if r["num_choices"] >= 2 and r["has_correct"] else "⚠️ Incomplete",
        axis=1,
    )
    df_display = df_display.rename(columns={
        "id": "ID", "category": "Category",
        "question_text": "Question", "num_choices": "# Choices",
        "has_correct": "Has Correct", "status": "Status",
    })
    st.dataframe(df_display.drop(columns=["Has Correct"]), use_container_width=True, hide_index=True)

    incomplete = (df_q["num_choices"] < 2) | (~df_q["has_correct"])
    if incomplete.any():
        st.warning(f"⚠️ {incomplete.sum()} question(s) have fewer than 2 choices or no correct answer marked. Fix them in the Manage tab.")
