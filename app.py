from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "literature.db"


st.set_page_config(page_title="Literature Shelf", layout="wide")


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


@st.cache_data(show_spinner=False)
def load_papers() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    with connect() as conn:
        return pd.read_sql_query("SELECT * FROM papers ORDER BY filename", conn)


def save_row(row: pd.Series) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE papers
            SET category = ?, tags = ?, abstract = ?, notes = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                row.get("category", ""),
                row.get("tags", ""),
                row.get("abstract", ""),
                row.get("notes", ""),
                int(row["id"]),
            ),
        )
        conn.commit()
    st.cache_data.clear()


def open_pdf(path: str) -> None:
    if sys.platform.startswith("win"):
        subprocess.Popen(["cmd", "/c", "start", "", path], shell=False)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


st.title("Literature Shelf")

if not DB_PATH.exists():
    st.warning("No database found. Run `python scan_papers.py` first.")
    st.stop()

df = load_papers()
if df.empty:
    st.info("No papers found yet.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    query = st.text_input("Search", placeholder="title, filename, tag, author")
    categories = ["All"] + sorted(x for x in df["category"].dropna().unique().tolist() if x)
    category = st.selectbox("Category", categories)

filtered = df.copy()
if query:
    q = query.lower()
    search_cols = ["filename", "title", "authors", "abstract", "tags", "notes"]
    mask = filtered[search_cols].fillna("").apply(
        lambda row: row.astype(str).str.lower().str.contains(q, regex=False).any(),
        axis=1,
    )
    filtered = filtered[mask]

if category != "All":
    filtered = filtered[filtered["category"] == category]

left, right = st.columns([0.72, 0.28], gap="large")

with left:
    st.subheader(f"Papers ({len(filtered)} / {len(df)})")
    show_cols = ["id", "filename", "year", "category", "tags", "abstract"]
    st.dataframe(
        filtered[show_cols],
        hide_index=True,
        use_container_width=True,
        height=560,
    )

with right:
    st.subheader("Edit")
    if filtered.empty:
        st.caption("No matching paper.")
    else:
        options = filtered["id"].tolist()
        selected_id = st.selectbox(
            "Select paper",
            options,
            format_func=lambda paper_id: filtered.loc[filtered["id"] == paper_id, "title"].iloc[0][:80],
        )
        row = df.loc[df["id"] == selected_id].iloc[0].copy()

        st.caption(row["filename"])
        category_value = st.text_input("Category", value=row.get("category") or "Unsorted")
        tags_value = st.text_input("English tags", value=row.get("tags") or "")
        if len(tags_value.split()) > 20:
            st.warning("Tags are longer than 20 words. Shorter tags are easier to search.")
        abstract_value = st.text_area("Abstract", value=row.get("abstract") or "", height=220)
        notes_value = st.text_area("Notes", value=row.get("notes") or "", height=120)

        if st.button("Save changes", type="primary", use_container_width=True):
            row["category"] = category_value
            row["tags"] = tags_value
            row["abstract"] = abstract_value
            row["notes"] = notes_value
            save_row(row)
            st.success("Saved.")
            st.rerun()

        if st.button("Open PDF", use_container_width=True):
            open_pdf(row["path"])

st.download_button(
    "Export current list to CSV",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="literature_shelf_export.csv",
    mime="text/csv",
)
