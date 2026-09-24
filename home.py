import streamlit as st
from database import init_database
import sqlite3

import os
init_database()

# pg = st.navigation([...], position="hidden")
# pg.run()

from PIL import Image, ImageOps
def load_thumbnail(path, size=(300, 450)):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # fixes sideways phone photos
    return ImageOps.fit(img, size, Image.Resampling.LANCZOS)

# Notification student success
if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅", duration=5)

# Notification student fail
if "badflash" in st.session_state:
    st.toast(st.session_state.pop("badflash"), icon="✅", duration=5)

st.set_page_config(
    page_title="UniMatch",
    page_icon="🎓",
    layout="wide"
)

# --- Top navigation ---
col1, col2, col3 = st.columns([6, 1.5, 1.2])

with col1:
    st.title("🎓 UniMatch")

# with col2:
#     if st.button("Universities", use_container_width=True):
#         st.switch_page("pages/universities.py")

with col3:
    if st.button("Add Alumni", use_container_width=True):
        st.switch_page("pages/add_student.py")


# --- Home page ---
st.divider()

# Get Started button
col1, col2, col3 = st.columns([1, 2, 1])

connection = sqlite3.connect("sql/TwUni_Finder.db")
cursor = connection.cursor()

# rowid works as an ID even if your table has no explicit id column
HOME_LIMIT = 4
cursor.execute("""
    SELECT rowid, name, degree, preferred_degree, photo_path
    FROM students
    ORDER BY rowid DESC
    LIMIT ?
""", (HOME_LIMIT,))
students = cursor.fetchall()

head_left, head_right = st.columns([6, 1], vertical_alignment="center")
head_left.subheader("Latest Alumni")

if students:
    if head_right.button("See More", key="see_more_students", width="stretch"):
        st.switch_page("pages/show_student.py")
else:
    st.info("No students yet.")

COLS = 4
cols = st.columns(COLS)

for i, (student_id, name, degree, preferred_degree, photo_path) in enumerate(students):
    with cols[i % COLS]:
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

st.markdown(
    """
    <div style="text-align: center; padding: 80px 20px;">
        <h1>Find the Right University for You</h1>
        <p style="font-size: 20px;">
            Explore universities and discover programs that match
            your academic profile and interests.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
if st.button("Get Started", use_container_width=True):
        st.switch_page("pages/show_uni.py")
# with col3:
#     if st.button("Get Started", use_container_width=True):
#         st.switch_page("pages/show_uni.py")