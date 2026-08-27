import streamlit as st
import pandas as pd
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Placement Week Scheduler",
    page_icon="🎓",
    layout="wide"
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    schedule = pd.read_csv(
        DATA_DIR / "schedule.csv"
    )

    students = pd.read_csv(
        DATA_DIR / "students.csv"
    )

    companies = pd.read_csv(
        DATA_DIR / "companies.csv"
    )

    rooms = pd.read_csv(
        DATA_DIR / "rooms.csv"
    )

    return (
        schedule,
        students,
        companies,
        rooms
    )


schedule, students, companies, rooms = load_data()


# =========================================================
# TITLE
# =========================================================

st.title("🎓 Placement Week Scheduler")

st.markdown(
    """
    **Optimization-based interview scheduling system**

    Built using **Python, Pandas, Streamlit and Google OR-Tools CP-SAT**.
    """
)


# =========================================================
# KEY METRICS
# =========================================================

total_interviews = len(schedule)

total_students = len(students)

scheduled_students = schedule[
    "student_id"
].nunique()

unscheduled_students = (
    total_students
    - scheduled_students
)

total_companies = len(companies)

total_rooms = len(rooms)

rooms_used = schedule[
    "room_id"
].nunique()

average_interviews = round(
    total_interviews
    / scheduled_students,
    2
) if scheduled_students else 0


col1, col2, col3, col4, col5, col6 = st.columns(6)


with col1:

    st.metric(
        "Interviews",
        total_interviews
    )


with col2:

    st.metric(
        "Students",
        total_students
    )


with col3:

    st.metric(
        "Scheduled",
        scheduled_students
    )


with col4:

    st.metric(
        "Unscheduled",
        unscheduled_students
    )


with col5:

    st.metric(
        "Companies",
        total_companies
    )


with col6:

    st.metric(
        "Rooms",
        f"{rooms_used}/{total_rooms}"
    )


st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔎 Schedule Filters")


# ---------------------------------------------------------
# Day
# ---------------------------------------------------------

days = [
    "All"
] + sorted(
    schedule["day"].unique()
)


selected_day = st.sidebar.selectbox(
    "Day",
    days
)


# ---------------------------------------------------------
# Company
# ---------------------------------------------------------

company_options = [
    "All"
] + sorted(
    schedule["company_id"].unique()
)


selected_company = st.sidebar.selectbox(
    "Company",
    company_options
)


# ---------------------------------------------------------
# Room
# ---------------------------------------------------------

room_options = [
    "All"
] + sorted(
    schedule["room_id"].unique()
)


selected_room = st.sidebar.selectbox(
    "Room",
    room_options
)


# ---------------------------------------------------------
# Student
# ---------------------------------------------------------

student_options = [
    "All"
] + sorted(
    schedule["student_id"].unique()
)


selected_student = st.sidebar.selectbox(
    "Student",
    student_options
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_schedule = schedule.copy()


if selected_day != "All":

    filtered_schedule = filtered_schedule[
        filtered_schedule["day"]
        == selected_day
    ]


if selected_company != "All":

    filtered_schedule = filtered_schedule[
        filtered_schedule["company_id"]
        == selected_company
    ]


if selected_room != "All":

    filtered_schedule = filtered_schedule[
        filtered_schedule["room_id"]
        == selected_room
    ]


if selected_student != "All":

    filtered_schedule = filtered_schedule[
        filtered_schedule["student_id"]
        == selected_student
    ]


# =========================================================
# FILTERED RESULTS
# =========================================================

st.header("📅 Interview Schedule")

st.caption(
    f"Showing {len(filtered_schedule)} interviews"
)


display_columns = [
    "day",
    "start_time",
    "end_time",
    "room_id",
    "student_id",
    "company_id",
    "duration"
]


st.dataframe(
    filtered_schedule[
        display_columns
    ],
    use_container_width=True,
    hide_index=True,
    height=450
)


# =========================================================
# DOWNLOAD
# =========================================================

csv_data = filtered_schedule.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="📥 Download Filtered Schedule",
    data=csv_data,
    file_name="filtered_schedule.csv",
    mime="text/csv"
)


st.divider()


# =========================================================
# ANALYTICS
# =========================================================

st.header("📊 Schedule Analytics")


col1, col2 = st.columns(2)


# =========================================================
# INTERVIEWS PER DAY
# =========================================================

with col1:

    st.subheader(
        "Interviews by Day"
    )

    day_counts = (
        schedule
        .groupby("day")
        .size()
        .reset_index(
            name="Interviews"
        )
    )

    st.bar_chart(
        day_counts.set_index("day")
    )


# =========================================================
# INTERVIEWS PER COMPANY
# =========================================================

with col2:

    st.subheader(
        "Interviews by Company"
    )

    company_counts = (
        schedule
        .groupby("company_id")
        .size()
        .sort_values(
            ascending=False
        )
    )

    st.bar_chart(
        company_counts
    )


# =========================================================
# ROOM UTILIZATION
# =========================================================

st.divider()

st.subheader(
    "🚪 Room Utilization"
)


room_counts = (
    schedule
    .groupby("room_id")
    .size()
    .sort_values(
        ascending=False
    )
)


st.bar_chart(
    room_counts
)


# =========================================================
# STUDENT ANALYTICS
# =========================================================

st.divider()

st.header("👨‍🎓 Student Analytics")


student_counts = (
    schedule
    .groupby("student_id")
    .size()
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Scheduled Students",
        scheduled_students
    )


with col2:

    st.metric(
        "Students Without Interviews",
        unscheduled_students
    )


with col3:

    st.metric(
        "Average Interviews / Student",
        average_interviews
    )


# =========================================================
# STUDENT INTERVIEW DISTRIBUTION
# =========================================================

st.subheader(
    "Interviews per Student"
)


student_distribution = (
    student_counts
    .value_counts()
    .sort_index()
)


student_distribution.index = (
    student_distribution.index
    .astype(str)
)


st.bar_chart(
    student_distribution
)


# =========================================================
# COMPANY ANALYTICS
# =========================================================

st.divider()

st.header("🏢 Company Analytics")


company_stats = (
    schedule
    .groupby("company_id")
    .agg(
        Interviews=(
            "student_id",
            "count"
        ),
        Students=(
            "student_id",
            "nunique"
        ),
        Average_Duration=(
            "duration",
            "mean"
        )
    )
    .sort_values(
        "Interviews",
        ascending=False
    )
)


company_stats[
    "Average_Duration"
] = company_stats[
    "Average_Duration"
].round(1)


st.dataframe(
    company_stats,
    use_container_width=True,
    height=400
)


# =========================================================
# DURATION ANALYSIS
# =========================================================

st.divider()

st.header("⏱️ Interview Duration")


duration_counts = (
    schedule
    .groupby("duration")
    .size()
    .reset_index(
        name="Interviews"
    )
)


duration_counts[
    "duration"
] = duration_counts[
    "duration"
].astype(str) + " min"


st.bar_chart(
    duration_counts.set_index(
        "duration"
    )
)


# =========================================================
# STUDENT SEARCH RESULT
# =========================================================

if selected_student != "All":

    st.divider()

    st.header(
        f"👤 Schedule for {selected_student}"
    )

    student_schedule = schedule[
        schedule["student_id"]
        == selected_student
    ]

    st.dataframe(
        student_schedule[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Placement Week Scheduler | "
    "Python • Pandas • OR-Tools • Streamlit"
)