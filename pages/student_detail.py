import streamlit as st
import os
# from header import app_header
import sqlite3

connection = sqlite3.connect("sql/TwUni_Finder.db")
cursor = connection.cursor()

st.set_page_config(
    page_title="Add Student",
    page_icon="🎓",
    layout="wide"
)

from PIL import Image, ImageOps
def load_thumbnail(path, size=(300, 450)):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # fixes sideways phone photos
    return ImageOps.fit(img, size, Image.Resampling.LANCZOS)

# app_header()
col_title, col_back = st.columns([6, 1.2], vertical_alignment="center")
col_title.title("Edit Student")
if col_back.button("← Home", width="stretch"):
    st.switch_page("home.py")
# st.title("Edit Student")
# st.write("Share your information to be featured on the student page.")

st.divider()

# -------------------------
# Personal Information
# -------------------------

# use get not pop so the value will still be there to be rechecked every field update or action
student_id = st.session_state.get("selected_student")
cursor.execute("""
    SELECT name, affiliation, major, degree, about, interests,
        preferred_degree, preferred_field, photo_path
    FROM students WHERE id = ?
""", (student_id,))
dbname, dbaffiliation, dbmajor, dbdegree, dbabout, dbinterests, dbpreferred_degree, dbpreferred_field, dbphoto_path = cursor.fetchone()

st.subheader("Personal Information")

preview = st.container()
new_photo = st.file_uploader(
    "Profile Photo",
    type=["jpg", "jpeg", "png"]
)
if new_photo:
    preview.image(load_thumbnail(new_photo), width=100)          # the newly chosen photo
elif dbphoto_path and os.path.exists(dbphoto_path):
    preview.image(load_thumbnail(dbphoto_path), width=100)  

name = st.text_input(
    "Name",
    value=dbname,
    placeholder="Enter your name"
)

affiliation = st.text_input(
    "Affiliation / University",
    value=dbaffiliation,
    placeholder="e.g. iSTTS"
)

major = st.text_input(
    "Major",
    value=dbmajor,
    placeholder="e.g. Informatics"
)

DEGREES = ["High School", "Diploma", "Bachelor's", "Master's", "Doctorate", "Other"]
degree = st.selectbox(
    "Current Degree",
    DEGREES,
    index=DEGREES.index(dbdegree) if dbdegree in DEGREES else 0
)

# -------------------------
# About
# -------------------------

st.subheader("About")

about = st.text_area(
    "About Me",
    value=dbabout,
    placeholder="Tell us a little about yourself...",
    height=150
)

# -------------------------
# Academic Interests
# -------------------------

st.subheader("Academic Interests")
INTEREST_OPTIONS = [
        "Artificial Intelligence",
        "Machine Learning",
        "Computer Vision",
        "Natural Language Processing",
        "Robotics",
        "Data Science",
        "Software Engineering",
        "Cybersecurity",
        "Computer Networks",
        "Other"
    ]
interests = st.multiselect(
    "Select your interests",
    INTEREST_OPTIONS,
    default=[i for i in (dbinterests or "").split(", ") if i in INTEREST_OPTIONS]
)

# -------------------------
# Study Goal
# -------------------------

st.subheader("Study Goal")
PREF_DEGREE = [
        "Bachelor's",
        "Master's",
        "Doctorate"
    ]
preferred_degree = st.selectbox(
    "Degree you are interested in",
    PREF_DEGREE,
    index=PREF_DEGREE.index(dbpreferred_degree) if dbpreferred_degree in PREF_DEGREE else 0
)

preferred_field = st.text_input(
    "Preferred field / major",
    value = dbpreferred_field,
    placeholder="e.g. Artificial Intelligence"
)

# -------------------------
# Submit
# -------------------------

st.divider()

if st.button("Submit Student", type="primary", use_container_width=True):

    if not name:
        st.error("Please enter your name.")

    elif not affiliation:
        st.error("Please enter your affiliation.")

    else:
        try:
            if new_photo:
                new_photo_path = f"uploads/students/{student_id}.jpg"

                with open(new_photo_path, "wb") as f:
                    f.write(new_photo.getbuffer())
            else:
                new_photo_path = f"bg waterfall.jpg"

            cursor.execute("""
                UPDATE students
                SET name = ?, affiliation = ?, major = ?, degree = ?,
                    about = ?, interests = ?, preferred_degree = ?,
                    preferred_field = ?, photo_path = ?
                WHERE id = ?
            """, (
                name, affiliation, major, degree, about,
                ", ".join(interests), preferred_degree,
                preferred_field, new_photo_path, student_id
            ))

            connection.commit()

            st.session_state["flash"] = "Student information submitted!"
            st.switch_page("home.py")

        except Exception as e:
            st.error(f"Failed to save student information: {e}")