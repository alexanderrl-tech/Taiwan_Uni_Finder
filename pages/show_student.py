import os
import sqlite3

import streamlit as st
from PIL import Image, ImageOps

DB_FILE = "sql/TwUni_Finder.db"
PAGE_SIZE = 8          # 2 rows of 4
COLS = 4

st.set_page_config(page_title="Students", page_icon="🎓", layout="wide")


def load_thumbnail(path, size=(300, 450)):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return ImageOps.fit(img, size, Image.Resampling.LANCZOS)


if "stu_page" not in st.session_state:
    st.session_state["stu_page"] = 1


def go(delta, last):
    st.session_state["stu_page"] = min(max(1, st.session_state["stu_page"] + delta), last)


def pager(key, pages):
    left, mid, right = st.columns([1, 2, 1], vertical_alignment="center")
    page = st.session_state["stu_page"]
    left.button("← Previous", key=f"stu_prev_{key}", on_click=go, args=(-1, pages),
                disabled=page == 1, width="stretch")
    mid.markdown(f"<div style='text-align:center'>Page {page} of {pages}</div>",
                 unsafe_allow_html=True)
    right.button("Next →", key=f"stu_next_{key}", on_click=go, args=(1, pages),
                 disabled=page == pages, width="stretch")


# --- header ---
col_title, col_back = st.columns([6, 1.2], vertical_alignment="center")
col_title.title("🎓 Students")
if col_back.button("← Home", width="stretch"):
    st.switch_page("home.py")

st.divider()

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

total = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
if total == 0:
    st.info("No students yet.")
    st.stop()

pages = max(1, -(-total // PAGE_SIZE))
page = min(st.session_state["stu_page"], pages)
st.session_state["stu_page"] = page

st.caption(f"{total:,} students")
pager("top", pages)

students = cursor.execute("""
    SELECT rowid, name, degree, preferred_degree, photo_path
    FROM students
    ORDER BY rowid DESC
    LIMIT ? OFFSET ?
""", (PAGE_SIZE, (page - 1) * PAGE_SIZE)).fetchall()

# one st.columns row per 4 students, so the cards line up in rows
for start in range(0, len(students), COLS):
    cols = st.columns(COLS)
    for col, (student_id, name, degree, preferred_degree, photo_path) in zip(
        cols, students[start:start + COLS]
    ):
        with col:
            with st.container(border=True):
                if photo_path and os.path.exists(photo_path):
                    st.image(load_thumbnail(photo_path), width=100)
                else:
                    st.markdown("## 🎓")
                    st.caption("No photo")

                st.subheader(name)
                st.caption(degree)
                st.caption(preferred_degree)

                if st.button("Show detail", key=f"detail_{student_id}", width="stretch"):
                    st.session_state["selected_student"] = student_id
                    st.switch_page("pages/student_detail.py")

pager("bottom", pages)