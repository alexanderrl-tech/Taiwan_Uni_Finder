import streamlit as st
import os
# from header import app_header
import sqlite3

connection = sqlite3.connect("sql/TwUni_Finder.db")
cursor = connection.cursor()

st.set_page_config(
    page_title="Add Alumni",
    page_icon="🎓",
    layout="wide"
)

# STYLE
st.markdown("""
<style>
.st-key-add_alumni_btn button {
    background-color: #28A745 !important;
    color: white !important;
    border: none !important;
}
.st-key-add_alumni_btn button:hover {
    background-color: #1E7E34 !important;
}
</style>
""", unsafe_allow_html=True)

from PIL import Image, ImageOps
def load_thumbnail(path, size=(300, 450)):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # fixes sideways phone photos
    return ImageOps.fit(img, size, Image.Resampling.LANCZOS)

# app_header()
col_title, col_back = st.columns([6, 1.2], vertical_alignment="center")
col_title.title("Add Alumni")
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

job_title = st.text_input(
    "Job Title",
    placeholder="e.g. Software Engineer"
)

company = st.text_input(
    "Company",
    placeholder="e.g. Google"
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

# st.subheader("Academic Interests")

# interests = st.multiselect(
#     "Select your interests",
#     [
#     "Agriculture & Forestry",
#     "Architecture",
#     "Business & Management",
#     "Communication & Journalism",
#     "Computer Science & IT",
#     "Culinary Arts",
#     "Economics & Finance",
#     "Education",
#     "Engineering",
#     "Environmental Science",
#     "Fashion Design",
#     "Film & Media Studies",
#     "Fine Arts & Design",
#     "History",
#     "Hospitality & Tourism",
#     "International Relations / International Studies",
#     "Law",
#     "Linguistics",
#     "Literature & Languages",
#     "Marine Science / Oceanography",
#     "Mathematics & Statistics",
#     "Medicine & Health Sciences",
#     "Music & Performing Arts",
#     "Natural Sciences (Physics, Chemistry, Biology)",
#     "Nursing & Allied Health",
#     "Philosophy",
#     "Psychology",
#     "Public Administration / Public Policy",
#     "Public Health",
#     "Religious Studies / Theology",
#     "Social Sciences (Sociology, Political Science, Anthropology)",
#     "Sports Science / Kinesiology",
#     "Urban Planning",
#     "Veterinary Science",
#     "Other"
#     ]
# )

# # -------------------------
# # Study Goal
# # -------------------------

# st.subheader("Study Goal")

# preferred_degree = st.selectbox(
#     "Degree you are interested in",
#     [
#         "Bachelor's",
#         "Master's",
#         "Doctorate"
#     ]
# )

# preferred_field = st.text_input(
#     "Preferred field / major",
#     placeholder="e.g. Artificial Intelligence"
# )

# -------------------------
# Submit
# -------------------------

st.divider()

if st.button("Add Alumni", type="primary", use_container_width=True, key="add_alumni_btn"):    
    if not name:
        st.error("Please enter your name.")

    elif not affiliation:
        st.error("Please enter your affiliation.")

    else:
        try:
            cursor.execute("""
                INSERT INTO students (
                    name, affiliation, major, degree, job_title, company, about, photo_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, affiliation, major, degree, job_title, company, about, "assets/no_image_placeholder.png"
            ))

            student_id = cursor.lastrowid

            photo_path = "assets/no_image_placeholder.png"

            if photo:
                os.makedirs("uploads/students", exist_ok=True)
                photo_path = f"uploads/students/{student_id}.jpg"
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

                cursor.execute("""
                    UPDATE students SET photo_path = ? WHERE id = ?
                """, (photo_path, student_id))

            connection.commit()

            st.session_state["flash"] = "Student information submitted!"
            st.switch_page("home.py")

        except Exception as e:
            st.error(f"Failed to save student information: {e}")