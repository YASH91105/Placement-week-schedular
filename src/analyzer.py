import pandas as pd
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# =========================================================
# LOAD SCHEDULE
# =========================================================

schedule_path = DATA_DIR / "schedule.csv"

schedule = pd.read_csv(schedule_path)


print("=" * 70)
print("PLACEMENT SCHEDULE ANALYSIS")
print("=" * 70)


# =========================================================
# BASIC STATISTICS
# =========================================================

total_interviews = len(schedule)

total_students = schedule["student_id"].nunique()

total_companies = schedule["company_id"].nunique()

total_rooms = schedule["room_id"].nunique()


print()
print("BASIC STATISTICS")
print("-" * 70)

print("Total interviews:", total_interviews)
print("Students scheduled:", total_students)
print("Companies involved:", total_companies)
print("Rooms used:", total_rooms)


# =========================================================
# INTERVIEWS PER DAY
# =========================================================

print()
print("INTERVIEWS PER DAY")
print("-" * 70)

interviews_per_day = (
    schedule
    .groupby("day")
    .size()
)

print(
    interviews_per_day.to_string()
)


# =========================================================
# INTERVIEWS PER COMPANY
# =========================================================

print()
print("INTERVIEWS PER COMPANY")
print("-" * 70)

interviews_per_company = (
    schedule
    .groupby("company_id")
    .size()
    .sort_values(ascending=False)
)

print(
    interviews_per_company.to_string()
)


# =========================================================
# INTERVIEWS PER ROOM
# =========================================================

print()
print("INTERVIEWS PER ROOM")
print("-" * 70)

interviews_per_room = (
    schedule
    .groupby("room_id")
    .size()
    .sort_values(ascending=False)
)

print(
    interviews_per_room.to_string()
)


# =========================================================
# INTERVIEWS PER TIME SLOT
# =========================================================

print()
print("INTERVIEWS PER START TIME")
print("-" * 70)

interviews_per_time = (
    schedule
    .groupby(
        ["day", "start_time"]
    )
    .size()
)

print(
    interviews_per_time.to_string()
)


# =========================================================
# INTERVIEW DURATION
# =========================================================

print()
print("INTERVIEW DURATION")
print("-" * 70)

duration_stats = schedule[
    "duration"
].describe()

print(
    duration_stats.to_string()
)


# =========================================================
# STUDENTS WITH MULTIPLE INTERVIEWS
# =========================================================

student_interview_counts = (
    schedule
    .groupby("student_id")
    .size()
)

print()
print("STUDENT INTERVIEW STATISTICS")
print("-" * 70)

print(
    "Students with interviews:",
    len(student_interview_counts)
)

print(
    "Maximum interviews for one student:",
    student_interview_counts.max()
)

print(
    "Average interviews per scheduled student:",
    round(
        student_interview_counts.mean(),
        2
    )
)


# =========================================================
# ROOM UTILIZATION
# =========================================================

print()
print("ROOM UTILIZATION")
print("-" * 70)

rooms = pd.read_csv(
    DATA_DIR / "rooms.csv"
)

total_available_rooms = len(rooms)

print(
    "Total rooms available:",
    total_available_rooms
)

print(
    "Rooms actually used:",
    total_rooms
)

print(
    "Unused rooms:",
    total_available_rooms - total_rooms
)

room_utilization = (
    total_rooms
    / total_available_rooms
    * 100
)

print(
    "Room utilization:",
    round(room_utilization, 2),
    "%"
)


# =========================================================
# SAVE ANALYSIS
# =========================================================

analysis_path = (
    DATA_DIR
    / "schedule_analysis.txt"
)

with open(
    analysis_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "PLACEMENT SCHEDULE ANALYSIS\n"
    )

    file.write(
        "=" * 70 + "\n\n"
    )

    file.write(
        f"Total interviews: {total_interviews}\n"
    )

    file.write(
        f"Students scheduled: {total_students}\n"
    )

    file.write(
        f"Companies involved: {total_companies}\n"
    )

    file.write(
        f"Rooms used: {total_rooms}\n"
    )

    file.write(
        "\nINTERVIEWS PER DAY\n"
    )

    file.write(
        interviews_per_day.to_string()
    )

    file.write(
        "\n\nINTERVIEWS PER COMPANY\n"
    )

    file.write(
        interviews_per_company.to_string()
    )

    file.write(
        "\n\nINTERVIEWS PER ROOM\n"
    )

    file.write(
        interviews_per_room.to_string()
    )

    file.write(
        "\n\nINTERVIEW DURATION\n"
    )

    file.write(
        duration_stats.to_string()
    )


print()
print("=" * 70)
print("Analysis complete!")
print("=" * 70)

print()
print("Analysis saved to:")
print(analysis_path)