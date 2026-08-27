# Placement Week Scheduler

An optimization-based interview scheduling system built with Python, Pandas, Google OR-Tools CP-SAT, and Streamlit.

The system generates an interview schedule for a placement week while considering student availability, company availability, interview durations, room capacity, and scheduling conflicts.

---

## 📌 Project Overview

Placement week can involve hundreds of students, multiple companies, limited rooms, and different interview durations.

Creating such a schedule manually can lead to:

- Student scheduling conflicts
- Company/panel conflicts
- Room conflicts
- Poor room utilization
- Unscheduled interviews
- Difficulty managing hundreds of interview combinations

This project uses **constraint programming and optimization** to automatically generate a valid interview schedule.

---

## 🎯 Problem Statement

Given:

- 800 students
- 35 companies
- 20 interview rooms
- 4 placement days
- Company availability slots
- Student-company shortlists
- Different interview durations

the system determines which interviews can be scheduled and assigns valid time slots and rooms while avoiding conflicts.

---

## 🚀 Features

- Automatic interview scheduling
- Constraint-based optimization using OR-Tools CP-SAT
- Student conflict prevention
- Company conflict prevention
- Room capacity constraints
- Company availability handling
- Different interview durations
- Automatic room assignment
- Schedule validation
- Schedule analysis
- CSV schedule generation
- Interactive Streamlit dashboard
- Filtering by day, company, room, and student
- Room utilization analysis
- Interview duration analysis
- Student interview statistics

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming |
| Pandas | Data processing |
| NumPy | Data generation |
| Google OR-Tools | CP-SAT optimization |
| Streamlit | Interactive dashboard |
| Pytest | Testing |
| CSV | Input/output data storage |

---

## 🧠 Scheduling Approach

The scheduler uses **Google OR-Tools CP-SAT** to model the placement scheduling problem as a constraint optimization problem.

The system first identifies possible student-company interviews.

For the current dataset:

```text
Companies:           35
Students:            800
Rooms:               20
Availability slots:  70
Possible interviews: 3023