import pandas as pd
from pathlib import Path
from ortools.sat.python import cp_model


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# =========================================================
# SETTINGS
# =========================================================

DAYS = ["Day 1", "Day 2", "Day 3", "Day 4"]

DAY_MINUTES = 24 * 60

MAX_ROOMS = 20


# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    companies = pd.read_csv(
        DATA_DIR / "companies.csv"
    )

    students = pd.read_csv(
        DATA_DIR / "students.csv"
    )

    rooms = pd.read_csv(
        DATA_DIR / "rooms.csv"
    )

    availability = pd.read_csv(
        DATA_DIR / "company_availability.csv"
    )

    return (
        companies,
        students,
        rooms,
        availability
    )


# =========================================================
# PARSE SHORTLISTED COMPANIES
# =========================================================

def parse_companies(value):

    if pd.isna(value):
        return []

    value = str(value).strip()

    # Remove brackets
    value = value.strip("[]")

    if not value:
        return []

    companies = []

    for item in value.split(","):

        item = (
            item
            .strip()
            .strip("'")
            .strip('"')
            .strip()
        )

        if item:
            companies.append(item)

    return companies


# =========================================================
# CREATE POSSIBLE INTERVIEWS
# =========================================================

def create_candidates(students):

    candidates = []

    for _, student in students.iterrows():

        student_id = student["student_id"]

        shortlisted = parse_companies(
            student["shortlisted_companies"]
        )

        for company_id in shortlisted:

            candidates.append({
                "student_id": student_id,
                "company_id": company_id
            })

    return candidates


# =========================================================
# TIME HELPERS
# =========================================================

def time_to_minutes(time_string):

    hour, minute = map(
        int,
        str(time_string).split(":")
    )

    return hour * 60 + minute


def minutes_to_time(minutes):

    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


# =========================================================
# BUILD CP-SAT MODEL
# =========================================================

def build_model(
    students,
    companies,
    availability
):

    model = cp_model.CpModel()

    candidates = create_candidates(
        students
    )

    print(
        "Possible interviews:",
        len(candidates)
    )

    # -----------------------------------------------------
    # INTERVALS BY STUDENT
    # -----------------------------------------------------

    student_intervals = {}

    # -----------------------------------------------------
    # INTERVALS BY COMPANY
    # -----------------------------------------------------

    company_intervals = {}

    # -----------------------------------------------------
    # INTERVALS BY STUDENT-COMPANY
    # -----------------------------------------------------

    pair_intervals = {}

    # -----------------------------------------------------
    # CREATE INTERVIEW OPTIONS
    # -----------------------------------------------------

    for index, candidate in enumerate(candidates):

        student_id = candidate["student_id"]
        company_id = candidate["company_id"]

        # -------------------------------------------------
        # Find company
        # -------------------------------------------------

        company_rows = companies[
            companies["company_id"].astype(str)
            == str(company_id)
        ]

        if company_rows.empty:
            continue

        company = company_rows.iloc[0]

        # -------------------------------------------------
        # Interview duration
        # -------------------------------------------------

        duration = int(
            company["interview_duration"]
        )

        # -------------------------------------------------
        # Company availability
        # -------------------------------------------------

        company_windows = availability[
            availability["company_id"].astype(str)
            == str(company_id)
        ]

        pair_key = (
            student_id,
            company_id
        )

        pair_intervals.setdefault(
            pair_key,
            []
        )

        # -------------------------------------------------
        # Create possible interval in each availability
        # window.
        # -------------------------------------------------

        for window_index, window in company_windows.iterrows():

            day = str(window["day"])

            if day not in DAYS:
                continue

            start_time = str(
                window["start_time"]
            )

            end_time = str(
                window["end_time"]
            )

            window_start = time_to_minutes(
                start_time
            )

            window_end = time_to_minutes(
                end_time
            )

            # Window too short
            if (
                window_end
                - window_start
                < duration
            ):
                continue

            day_number = DAYS.index(day)

            # -------------------------------------------------
            # Put each day on its own timeline.
            # -------------------------------------------------

            absolute_window_start = (
                day_number * DAY_MINUTES
                + window_start
            )

            absolute_window_end = (
                day_number * DAY_MINUTES
                + window_end
            )

            variable_name = (
                f"interview_"
                f"{index}_"
                f"window_"
                f"{window_index}"
            )

            # -------------------------------------------------
            # Presence
            # -------------------------------------------------

            present = model.NewBoolVar(
                f"{variable_name}_present"
            )

            # -------------------------------------------------
            # Start
            # -------------------------------------------------

            start = model.NewIntVar(
                absolute_window_start,
                absolute_window_end - duration,
                f"{variable_name}_start"
            )

            # -------------------------------------------------
            # End
            # -------------------------------------------------

            end = model.NewIntVar(
                absolute_window_start + duration,
                absolute_window_end,
                f"{variable_name}_end"
            )

            model.Add(
                end == start + duration
            )

            # -------------------------------------------------
            # Optional interval
            # -------------------------------------------------

            interval = model.NewOptionalIntervalVar(
                start,
                duration,
                end,
                present,
                variable_name
            )

            interview = {

                "student_id": student_id,

                "company_id": company_id,

                "day": day,

                "start": start,

                "end": end,

                "duration": duration,

                "present": present,

                "interval": interval
            }

            # -------------------------------------------------
            # Student intervals
            # -------------------------------------------------

            student_intervals.setdefault(
                student_id,
                []
            ).append(interview)

            # -------------------------------------------------
            # Company intervals
            # -------------------------------------------------

            company_intervals.setdefault(
                company_id,
                []
            ).append(interview)

            # -------------------------------------------------
            # Student-company pair
            # -------------------------------------------------

            pair_intervals[
                pair_key
            ].append(interview)

    # =====================================================
    # CONSTRAINT 1
    #
    # STUDENT CANNOT HAVE TWO INTERVIEWS AT ONCE
    # =====================================================

    for student_id, intervals in student_intervals.items():

        model.AddNoOverlap([
            item["interval"]
            for item in intervals
        ])

    print(
        "Student conflict constraints created:",
        len(student_intervals)
    )

    # =====================================================
    # CONSTRAINT 2
    #
    # COMPANY CANNOT INTERVIEW TWO STUDENTS AT ONCE
    # =====================================================

    for company_id, intervals in company_intervals.items():

        model.AddNoOverlap([
            item["interval"]
            for item in intervals
        ])

    print(
        "Company conflict constraints created:",
        len(company_intervals)
    )

    # =====================================================
    # CONSTRAINT 3
    #
    # EACH STUDENT-COMPANY PAIR AT MOST ONCE
    # =====================================================

    for pair_key, intervals in pair_intervals.items():

        model.Add(
            sum(
                item["present"]
                for item in intervals
            )
            <= 1
        )

    print(
        "Student-company constraints created:",
        len(pair_intervals)
    )

    # =====================================================
    # CONSTRAINT 4
    #
    # MAXIMUM 20 ROOMS AT ANY TIME
    #
    # Each interview consumes one room.
    #
    # CP-SAT cumulative constraint:
    #
    #   interval = interview
    #   demand   = 1 room
    #   capacity = 20 rooms
    #
    # =====================================================

    all_intervals = []
    all_demands = []

    for intervals in pair_intervals.values():

        for item in intervals:

            all_intervals.append(
                item["interval"]
            )

            all_demands.append(1)

    model.AddCumulative(
        all_intervals,
        all_demands,
        MAX_ROOMS
    )

    print(
        "Room capacity constraint created:",
        MAX_ROOMS,
        "rooms"
    )

    # =====================================================
    # OBJECTIVE
    #
    # MAXIMIZE NUMBER OF INTERVIEWS
    # =====================================================

    all_presence_variables = []

    for intervals in pair_intervals.values():

        for item in intervals:

            all_presence_variables.append(
                item["present"]
            )

    model.Maximize(
        sum(all_presence_variables)
    )

    return (
        model,
        student_intervals,
        company_intervals,
        pair_intervals
    )


# =========================================================
# SOLVE MODEL
# =========================================================

def solve_model(model):

    solver = cp_model.CpSolver()

    # Give CP-SAT some time to optimize.
    solver.parameters.max_time_in_seconds = 60

    # Use multiple CPU cores.
    solver.parameters.num_workers = 8

    print()
    print("Solving model...")

    status = solver.Solve(
        model
    )

    print(
        "Solver status:",
        solver.StatusName(status)
    )

    if status in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        print(
            "Interviews scheduled:",
            int(
                solver.ObjectiveValue()
            )
        )

    else:

        print(
            "No feasible schedule found."
        )

    return solver, status


# =========================================================
# EXTRACT SCHEDULE
# =========================================================

def extract_schedule(
    solver,
    status,
    pair_intervals
):

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        return []

    schedule = []

    for pair_key, intervals in pair_intervals.items():

        for item in intervals:

            if solver.Value(
                item["present"]
            ) != 1:

                continue

            absolute_start = solver.Value(
                item["start"]
            )

            absolute_end = solver.Value(
                item["end"]
            )

            day_number = (
                absolute_start
                // DAY_MINUTES
            )

            start_minutes = (
                absolute_start
                % DAY_MINUTES
            )

            end_minutes = (
                absolute_end
                % DAY_MINUTES
            )

            schedule.append({

                "student_id":
                    item["student_id"],

                "company_id":
                    item["company_id"],

                "day":
                    DAYS[day_number],

                "start_time":
                    minutes_to_time(
                        start_minutes
                    ),

                "end_time":
                    minutes_to_time(
                        end_minutes
                    ),

                "duration":
                    item["duration"]
            })

    # -----------------------------------------------------
    # Sort schedule
    # -----------------------------------------------------

    schedule.sort(
        key=lambda x: (
            DAYS.index(x["day"]),
            x["start_time"],
            x["company_id"],
            x["student_id"]
        )
    )

    return schedule


# =========================================================
# ASSIGN ROOMS
# =========================================================

def assign_rooms(
    schedule,
    rooms
):

    room_ids = [
        str(room_id)
        for room_id in rooms["room_id"]
    ]

    # Make sure we never use more than MAX_ROOMS.
    room_ids = room_ids[:MAX_ROOMS]

    room_usage = {
        room_id: []
        for room_id in room_ids
    }

    def overlaps(
        start1,
        end1,
        start2,
        end2
    ):

        return (
            start1 < end2
            and
            start2 < end1
        )

    unassigned = 0

    # -----------------------------------------------------
    # Assign rooms
    # -----------------------------------------------------

    for interview in schedule:

        day = interview["day"]

        start = time_to_minutes(
            interview["start_time"]
        )

        end = time_to_minutes(
            interview["end_time"]
        )

        assigned_room = None

        for room_id in room_ids:

            room_free = True

            for existing in room_usage[
                room_id
            ]:

                if existing["day"] != day:
                    continue

                if overlaps(
                    start,
                    end,
                    existing["start"],
                    existing["end"]
                ):

                    room_free = False
                    break

            if room_free:

                assigned_room = room_id

                room_usage[
                    room_id
                ].append({

                    "day": day,

                    "start": start,

                    "end": end
                })

                break

        interview[
            "room_id"
        ] = assigned_room

        if assigned_room is None:

            unassigned += 1

    print()
    print(
        "Room assignment complete!"
    )

    print(
        "Interviews without a room:",
        unassigned
    )

    return schedule


# =========================================================
# VALIDATE SCHEDULE
# =========================================================

def validate_schedule(
    schedule
):

    print()
    print("=" * 70)
    print("VALIDATING SCHEDULE")
    print("=" * 70)

    student_events = {}
    company_events = {}
    room_events = {}

    student_conflicts = 0
    company_conflicts = 0
    room_conflicts = 0

    # -----------------------------------------------------
    # Build event lists
    # -----------------------------------------------------

    for interview in schedule:

        day = interview["day"]

        start = time_to_minutes(
            interview["start_time"]
        )

        end = time_to_minutes(
            interview["end_time"]
        )

        student_id = interview[
            "student_id"
        ]

        company_id = interview[
            "company_id"
        ]

        room_id = interview[
            "room_id"
        ]

        student_events.setdefault(
            (day, student_id),
            []
        ).append(
            (start, end)
        )

        company_events.setdefault(
            (day, company_id),
            []
        ).append(
            (start, end)
        )

        if room_id is not None:

            room_events.setdefault(
                (day, room_id),
                []
            ).append(
                (start, end)
            )

    # -----------------------------------------------------
    # Check overlaps
    # -----------------------------------------------------

    def has_overlap(events):

        events = sorted(events)

        for i in range(
            1,
            len(events)
        ):

            previous_end = events[
                i - 1
            ][1]

            current_start = events[
                i
            ][0]

            if current_start < previous_end:

                return True

        return False

    # -----------------------------------------------------
    # Student conflicts
    # -----------------------------------------------------

    for events in student_events.values():

        if has_overlap(events):

            student_conflicts += 1

    # -----------------------------------------------------
    # Company conflicts
    # -----------------------------------------------------

    for events in company_events.values():

        if has_overlap(events):

            company_conflicts += 1

    # -----------------------------------------------------
    # Room conflicts
    # -----------------------------------------------------

    for events in room_events.values():

        if has_overlap(events):

            room_conflicts += 1

    # -----------------------------------------------------
    # Print validation
    # -----------------------------------------------------

    print(
        "Student conflicts:",
        student_conflicts
    )

    print(
        "Company conflicts:",
        company_conflicts
    )

    print(
        "Room conflicts:",
        room_conflicts
    )

    unassigned = sum(
        1
        for interview in schedule
        if interview["room_id"] is None
    )

    print(
        "Unassigned rooms:",
        unassigned
    )

    # -----------------------------------------------------
    # Overall result
    # -----------------------------------------------------

    if (
        student_conflicts == 0
        and company_conflicts == 0
        and room_conflicts == 0
        and unassigned == 0
    ):

        print()
        print(
            "VALIDATION PASSED!"
        )

        return True

    print()
    print(
        "VALIDATION FAILED!"
    )

    return False


# =========================================================
# SAVE SCHEDULE
# =========================================================

def save_schedule(
    schedule
):

    if not schedule:

        print(
            "No schedule to save."
        )

        return

    schedule_df = pd.DataFrame(
        schedule
    )

    # Put columns in a clean order.

    columns = [
        "day",
        "start_time",
        "end_time",
        "room_id",
        "student_id",
        "company_id",
        "duration"
    ]

    schedule_df = schedule_df[
        columns
    ]

    output_path = (
        DATA_DIR
        / "schedule.csv"
    )

    schedule_df.to_csv(
        output_path,
        index=False
    )

    print()
    print(
        "Schedule saved to:"
    )

    print(
        output_path
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    (
        companies,
        students,
        rooms,
        availability
    ) = load_data()

    print(
        "Data loaded successfully!"
    )

    print(
        "Companies:",
        len(companies)
    )

    print(
        "Students:",
        len(students)
    )

    print(
        "Rooms:",
        len(rooms)
    )

    print(
        "Availability slots:",
        len(availability)
    )

    # -----------------------------------------------------
    # BUILD MODEL
    # -----------------------------------------------------

    (
        model,
        student_intervals,
        company_intervals,
        pair_intervals
    ) = build_model(
        students,
        companies,
        availability
    )

    print()
    print(
        "CP-SAT model created successfully!"
    )

    print(
        "Students with possible interviews:",
        len(student_intervals)
    )

    print(
        "Companies modeled:",
        len(company_intervals)
    )

    print(
        "Student-company pairs:",
        len(pair_intervals)
    )

    print(
        "Scheduling constraints created successfully!"
    )

    # -----------------------------------------------------
    # SOLVE
    # -----------------------------------------------------

    solver, status = solve_model(
        model
    )

    # -----------------------------------------------------
    # STOP IF NO SOLUTION
    # -----------------------------------------------------

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        print()
        print(
            "Scheduling failed."
        )

        raise SystemExit

    # -----------------------------------------------------
    # EXTRACT
    # -----------------------------------------------------

    schedule = extract_schedule(
        solver,
        status,
        pair_intervals
    )

    # -----------------------------------------------------
    # ASSIGN ROOMS
    # -----------------------------------------------------

    schedule = assign_rooms(
        schedule,
        rooms
    )

    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    validate_schedule(
        schedule
    )

    # -----------------------------------------------------
    # PRINT FIRST 50
    # -----------------------------------------------------

    print()
    print("=" * 95)
    print("GENERATED INTERVIEW SCHEDULE")
    print("=" * 95)

    for interview in schedule[:50]:

        print(
            f"{interview['day']:>6} | "
            f"{interview['start_time']} - "
            f"{interview['end_time']} | "
            f"Room: "
            f"{str(interview['room_id']):>4} | "
            f"Student: "
            f"{interview['student_id']} | "
            f"Company: "
            f"{interview['company_id']}"
        )

    if len(schedule) > 50:

        print()
        print(
            f"... and "
            f"{len(schedule) - 50} more interviews."
        )

    print("=" * 95)

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    save_schedule(
        schedule
    )

    print()
    print(
        "Scheduling complete!"
    )