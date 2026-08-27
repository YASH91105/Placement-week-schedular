import random
import pandas as pd
import numpy as np

# Make data generation reproducible
random.seed(42)
np.random.seed(42)


DAYS = ["Day 1", "Day 2", "Day 3", "Day 4"]


def generate_companies():
    companies = []

    branches = ["CSE", "ISE", "ECE", "EEE", "ME", "CIVIL"]

    for i in range(35):

        if i < 10:
            priority = 1
            panel_count = random.randint(2, 4)

        elif i < 25:
            priority = 2
            panel_count = random.randint(1, 3)

        else:
            priority = 3
            panel_count = random.randint(1, 2)

        company = {
            "company_id": f"C{i+1:03d}",
            "name": f"Company {i+1}",
            "priority": priority,
            "cgpa_cutoff": round(random.uniform(6.5, 9.0), 2),
            "branches": random.sample(
                branches,
                random.randint(2, 4)
            ),
            "interview_duration": random.choice([30, 45, 60]),
            "panel_count": panel_count
        }

        companies.append(company)

    return pd.DataFrame(companies)


def generate_students(companies):
    students = []

    branches = ["CSE", "ISE", "ECE", "EEE", "ME", "CIVIL"]

    for i in range(800):

        branch = random.choice(branches)

        cgpa = round(
            np.clip(
                np.random.normal(7.8, 0.8),
                6.0,
                10.0
            ),
            2
        )

        eligible_companies = []

        for _, company in companies.iterrows():

            if (
                cgpa >= company["cgpa_cutoff"]
                and branch in company["branches"]
            ):
                eligible_companies.append(
                    company["company_id"]
                )

        if eligible_companies:

            max_shortlist = min(
                len(eligible_companies),
                8
            )

            shortlist_count = random.randint(
                1,
                max_shortlist
            )

            shortlisted = random.sample(
                eligible_companies,
                shortlist_count
            )

        else:
            shortlisted = []

        student = {
            "student_id": f"S{i+1:03d}",
            "name": f"Student {i+1}",
            "branch": branch,
            "cgpa": cgpa,
            "shortlisted_companies": shortlisted
        }

        students.append(student)

    return pd.DataFrame(students)


def generate_rooms():
    rooms = []

    for i in range(20):

        room = {
            "room_id": f"R{i+1:02d}",
            "name": f"Room {i+1}",
            "capacity": random.choice([4, 6, 8])
        }

        rooms.append(room)

    return pd.DataFrame(rooms)


def generate_company_availability(companies):
    availability = []

    for _, company in companies.iterrows():

        # Each company is available on 1-3 days
        available_days = random.sample(
            DAYS,
            random.randint(1, 3)
        )

        for day in available_days:

            start_hour = random.choice(
                [9, 10, 11]
            )

            duration_hours = random.choice(
                [4, 6, 8]
            )

            end_hour = min(
                start_hour + duration_hours,
                18
            )

            availability.append({
                "company_id": company["company_id"],
                "day": day,
                "start_time": f"{start_hour:02d}:00",
                "end_time": f"{end_hour:02d}:00"
            })

    return pd.DataFrame(availability)


if __name__ == "__main__":

    # Generate data
    companies = generate_companies()
    students = generate_students(companies)
    rooms = generate_rooms()
    availability = generate_company_availability(companies)

    # Save data to CSV files
    companies.to_csv("data/companies.csv", index=False)
    students.to_csv("data/students.csv", index=False)
    rooms.to_csv("data/rooms.csv", index=False)
    availability.to_csv(
        "data/company_availability.csv",
        index=False
    )

    # Display summary
    print("Got", len(companies), "companies")
    print("Got", len(students), "students")
    print("Got", len(rooms), "rooms")
    print("Got", len(availability), "availability slots")

    print("\nData saved successfully!")