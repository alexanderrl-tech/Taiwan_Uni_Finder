import sqlite3

import streamlit as st
import folium
from streamlit_folium import st_folium

DB_FILE = "sql/TwUni_Finder.db"
PAGE_SIZE = 10
LEVELS = ["Junior College", "Bachelor", "Master", "Ph.D."]

st.set_page_config(page_title="Programs", page_icon="🎓", layout="wide")
col_title, col_back = st.columns([6, 1.2], vertical_alignment="center")
col_title.title("Programs in Taiwan")
if col_back.button("← Home", width="stretch"):
    st.switch_page("home.py")
# st.title("Programs in Taiwan")

conn = sqlite3.connect(DB_FILE)

if "prog_page" not in st.session_state:
    st.session_state["prog_page"] = 1

if "selected_uni_id" not in st.session_state:
    st.session_state["selected_uni_id"] = None


def select_uni(uni_id):
    st.session_state["selected_uni_id"] = uni_id


def reset_page():
    st.session_state["prog_page"] = 1


def clear_filters():
    st.session_state["q"] = ""
    for k in ("f_region", "f_level", "f_type", "f_field", "f_uni"):
        st.session_state[k] = []
    st.session_state["f_schol"] = False
    st.session_state["prog_page"] = 1


def go(delta, last):
    st.session_state["prog_page"] = min(max(1, st.session_state["prog_page"] + delta), last)


def pager(key, pages):
    left, mid, right = st.columns([1, 2, 1], vertical_alignment="center")
    page = st.session_state["prog_page"]
    left.button("← Previous", key=f"prev_{key}", on_click=go, args=(-1, pages),
                disabled=page == 1, width="stretch")
    mid.markdown(f"<div style='text-align:center'>Page {page} of {pages}</div>",
                 unsafe_allow_html=True)
    right.button("Next →", key=f"next_{key}", on_click=go, args=(1, pages),
                 disabled=page == pages, width="stretch")


# ---------- filter options, read from the database ----------
regions = [r[0] for r in conn.execute(
    "SELECT DISTINCT region FROM universities WHERE region != '' ORDER BY region")]
types = [r[0] for r in conn.execute(
    "SELECT DISTINCT type FROM universities WHERE type != '' ORDER BY type")]
fields = [r[0] for r in conn.execute(
    "SELECT DISTINCT field FROM programs WHERE field != '' ORDER BY field")]
unis = [r[0] for r in conn.execute("SELECT name FROM universities ORDER BY name")]

# ---------- search + filters ----------
st.text_input("🔍 Search", key="q", on_change=reset_page,
              placeholder="e.g. robotics, artificial intelligence, Tsing Hua ...")

with st.expander("Filters"):
    c1, c2, c3 = st.columns(3)
    c1.multiselect("Region", regions, key="f_region", on_change=reset_page)
    c2.multiselect("Level of study", LEVELS, key="f_level", on_change=reset_page)
    c3.multiselect("Institution type", types, key="f_type", on_change=reset_page)

    c4, c5 = st.columns(2)
    c4.multiselect("Field of study", fields, key="f_field", on_change=reset_page)
    c5.multiselect("University", unis, key="f_uni", on_change=reset_page)

    st.checkbox("Only programs with scholarships", key="f_schol", on_change=reset_page)
    st.button("Clear filters", on_click=clear_filters)

# ---------- build the WHERE clause ----------
where, params = [], []


def add_in(column, values):
    if values:
        where.append(f"{column} IN ({','.join('?' * len(values))})")
        params.extend(values)


for word in st.session_state["q"].split():          # every word must match somewhere
    like = f"%{word}%"
    where.append("(p.program_name LIKE ? OR u.name LIKE ? OR p.field LIKE ?)")
    params += [like, like, like]

add_in("u.region", st.session_state["f_region"])
add_in("u.type", st.session_state["f_type"])
add_in("p.field", st.session_state["f_field"])
add_in("u.name", st.session_state["f_uni"])

if st.session_state["f_level"]:                     # levels is text like 'Master, Ph.D.'
    where.append("(" + " OR ".join(["p.levels LIKE ?"] * len(st.session_state["f_level"])) + ")")
    params += [f"%{lv}%" for lv in st.session_state["f_level"]]

if st.session_state["f_schol"]:
    where.append("CAST(p.scholarship AS INTEGER) > 0")

where_sql = ("WHERE " + " AND ".join(where)) if where else ""

# ---------- count, page, fetch ----------
FROM_SQL = "FROM programs p JOIN universities u ON u.id = p.university_id"

total = conn.execute(f"SELECT COUNT(*) {FROM_SQL} {where_sql}", params).fetchone()[0]
pages = max(1, -(-total // PAGE_SIZE))
page = min(st.session_state["prog_page"], pages)     # in case the filters shrank the list
st.session_state["prog_page"] = page

st.caption(f"{total:,} programs found")

if total == 0:
    st.info("No programs match your search. Try fewer words or clear some filters.")
    st.stop()

pager("top", pages)

rows = conn.execute(f"""
    SELECT p.program_name, u.name, u.type, u.region,
           p.field, p.levels, p.scholarship, p.website_url,
           u.id, u.lat, u.lng
    {FROM_SQL} {where_sql}
    ORDER BY u.name, p.program_name
    LIMIT ? OFFSET ?
""", params + [PAGE_SIZE, (page - 1) * PAGE_SIZE]).fetchall()

PANEL_HEIGHT = 650  # shared height so list + map line up and each scrolls independently

col_list, col_map = st.columns([2, 3])

# ---------- left: narrower, vertically-stacked list of cards ----------
with col_list:
    list_panel = st.container(height=PANEL_HEIGHT, border=False)
    with list_panel:
        for program, uni, utype, region, field, levels, scholarship, url, uni_id, lat, lng in rows:
            with st.container(border=True):
                st.markdown(f"**{program}**")
                st.caption(uni)
                st.write(field or "—")
                st.caption(levels)
                st.write(f"📍 {region}" + (f" · {utype}" if utype else ""))
                if scholarship:
                    st.caption(f"🏅 {scholarship} scholarship(s) listed")

                b1, b2 = st.columns(2)
                with b1:
                    if url:
                        link = url if url.startswith("http") else "https://" + url
                        st.link_button("Website", link, width="stretch")
                    else:
                        st.caption("No website")
                with b2:
                    if lat is not None and lng is not None:
                        st.button("📍 Map", key=f"map_{uni_id}_{program}",
                                   on_click=select_uni, args=(uni_id,), width="stretch")

# ---------- right: map of the currently selected university ----------
with col_map:
    st.subheader("📍 Location")

    selected_id = st.session_state["selected_uni_id"]
    selected = next((r for r in rows if r[8] == selected_id), None) if selected_id else None

    if selected and selected[9] is not None and selected[10] is not None:
        _, uni, *_rest, lat, lng = selected
        m = folium.Map(location=[lat, lng], zoom_start=14)
        folium.Marker([lat, lng], popup=uni, tooltip=uni).add_to(m)
    else:
        # default view: whole of Taiwan, with pins for every uni on this page that has coordinates
        m = folium.Map(location=[23.7, 121.0], zoom_start=7)
        for r in rows:
            uni, r_lat, r_lng = r[1], r[9], r[10]
            if r_lat is not None and r_lng is not None:
                folium.Marker([r_lat, r_lng], tooltip=uni).add_to(m)
        st.caption("Click \"📍 Map\" on a program to zoom to its university.")

    st_folium(m, width=None, height=PANEL_HEIGHT - 60, key="uni_map")

pager("bottom", pages)