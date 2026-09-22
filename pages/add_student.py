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
col_title.title("Add Student")
if col_back.button("← Home", width="stretch"):
    st.switch_page("home.py")
# st.title("Add Student")
st.write("Share your information to be featured on the student page.")

# -------------------------
# Personal Information
# -------------------------

st.subheader("Personal Information")

preview = st.container()
photo = st.file_uploader(
    "Profile Photo",
    type=["jpg", "jpeg", "png"]
)
if photo:
    preview.image(load_thumbnail(photo), width=100)

name = st.text_input(
    "Name",
    placeholder="Enter your name"
)

affiliation = st.text_input(
    "Affiliation / University",
    placeholder="e.g. iSTTS"
)

major = st.text_input(
    "Major",
    placeholder="e.g. Informatics"
)

degree = st.selectbox(
    "Current Degree",
    [
        "High School",
        "Diploma",
        "Bachelor's",
        "Master's",
        "Doctorate",
        "Other"
    ]
)

# -------------------------
# About
# -------------------------

st.subheader("About")

about = st.text_area(
    "About Me",
    placeholder="Tell us a little about yourself...",
    height=150
)

# -------------------------
# Academic Interests
# -------------------------

st.subheader("Academic Interests")

interests = st.multiselect(
    "Select your interests",
    [
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
)

# -------------------------
# Study Goal
# -------------------------

st.subheader("Study Goal")

preferred_degree = st.selectbox(
    "Degree you are interested in",
    [
        "Bachelor's",
        "Master's",
        "Doctorate"
    ]
)

preferred_field = st.text_input(
    "Preferred field / major",
    placeholder="e.g. Artificial Intelligence"
)

# -------------------------
# Submit
# -------------------------

st.divider()

if st.button("Add Student", type="primary", use_container_width=True):

    if not name:
        st.error("Please enter your name.")

    elif not affiliation:
        st.error("Please enter your affiliation.")

    else:
        try:
            photo_path = "bg waterfall.jpg"

            if photo:
                os.makedirs("uploads/students", exist_ok=True)
                cursor.execute("SELECT COUNT(*) FROM students")
                student_count = cursor.fetchone()[0]

                photo_path = f"uploads/students/{student_count}.jpg"

                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

            # Save student to database
            cursor.execute("""
                INSERT INTO students (
                    name,
                    affiliation,
                    major,
                    degree,
                    about,
                    interests,
                    preferred_degree,
                    preferred_field,
                    photo_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                affiliation,
                major,
                degree,
                about,
                ", ".join(interests),
                preferred_degree,
                preferred_field,
                photo_path
            ))
            
            connection.commit()

            st.session_state["flash"] = "Student information submitted!"
            st.switch_page("home.py")

        except Exception as e:
            st.error(f"Failed to save student information: {e}")