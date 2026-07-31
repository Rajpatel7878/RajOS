# RajOS Database Design

> Version: 1.0
> Database: PostgreSQL
> Status: Planning

---

# Overview

RajOS uses PostgreSQL as its primary database.

Every module has its own table.

Relationships are connected using Primary Keys and Foreign Keys.

---

# Database Structure

Users
│
├── Tasks
├── Goals
├── Projects
├── Habits
├── Coding Logs
├── Study Sessions
├── Subjects
├── Assignments
├── Finance
├── Health
├── Notes
├── Journal
├── Calendar Events
├── Notifications
└── Settings

---

# Table 1 — Users

Columns

- id (UUID) PRIMARY KEY
- full_name
- email
- password_hash
- profile_image
- role
- created_at
- updated_at

---

# Table 2 — Tasks

Columns

- id (UUID)
- user_id
- title
- description
- priority
- status
- due_date
- category
- completed_at
- created_at
- updated_at

Relationship

Many Tasks → One User

---

# Table 3 — Goals

Columns

- id
- user_id
- title
- description
- category
- target_date
- progress
- status
- created_at

Relationship

Many Goals → One User

---

# Table 4 — Milestones

Columns

- id
- goal_id
- title
- completed
- due_date

Relationship

Many Milestones → One Goal

---

# Table 5 — Habits

Columns

- id
- user_id
- habit_name
- frequency
- streak
- completed_today
- created_at

---

# Table 6 — Habit Logs

Columns

- id
- habit_id
- completed_date
- status

Relationship

Many Logs → One Habit

---

# Table 7 — Projects

Columns

- id
- user_id
- title
- description
- tech_stack
- github_url
- live_url
- status
- progress
- start_date
- end_date

---

# Table 8 — Project Tasks

Columns

- id
- project_id
- task_name
- completed

Relationship

Many Tasks → One Project

---

# Table 9 — Coding Sessions

Columns

- id
- user_id
- language
- platform
- hours
- problems_solved
- notes
- date

---

# Table 10 — Subjects

Columns

- id
- user_id
- subject_name
- semester
- credits

---

# Table 11 — Assignments

Columns

- id
- subject_id
- assignment_name
- due_date
- submitted

---

# Table 12 — Exams

Columns

- id
- subject_id
- exam_name
- exam_date
- marks
- total_marks

---

# Table 13 — Notes

Columns

- id
- user_id
- title
- content
- category
- pinned
- created_at

---

# Table 14 — Journal

Columns

- id
- user_id
- title
- content
- mood
- date

---

# Table 15 — Finance

Columns

- id
- user_id
- type
- category
- amount
- description
- date

---

# Table 16 — Health

Columns

- id
- user_id
- sleep_hours
- water
- workout
- weight
- mood
- steps
- date

---

# Table 17 — Calendar Events

Columns

- id
- user_id
- title
- description
- start_time
- end_time
- reminder
- location

---

# Table 18 — Learning

Columns

- id
- user_id
- course_name
- platform
- progress
- completion_date

---

# Table 19 — Certifications

Columns

- id
- user_id
- certificate_name
- issuer
- issue_date
- certificate_url

---

# Table 20 — Internship Applications

Columns

- id
- user_id
- company
- role
- status
- applied_date
- interview_date

---

# Table 21 — Achievements

Columns

- id
- user_id
- title
- description
- earned_date

---

# Table 22 — Notifications

Columns

- id
- user_id
- title
- message
- read
- created_at

---

# Table 23 — Settings

Columns

- id
- user_id
- theme
- language
- notifications
- timezone

---

# Relationships

User
│
├── Tasks
├── Goals
│      └── Milestones
├── Habits
│      └── Habit Logs
├── Projects
│      └── Project Tasks
├── Coding Sessions
├── Subjects
│      ├── Assignments
│      └── Exams
├── Notes
├── Journal
├── Finance
├── Health
├── Calendar Events
├── Learning
├── Certifications
├── Internship Applications
├── Achievements
├── Notifications
└── Settings

---

# Estimated Database Statistics

Tables : 23

Columns : 180+

Relationships : 25+

Indexes : 40+

Views : 10+

Triggers : Future Version

---

# Future Database

Future versions may include

- AI Logs
- Chat History
- Voice Notes
- Cloud Sync
- Team Workspace
- Activity Feed
- File Storage
- Media Library

---

# Database Status

Planning Complete

Next Document

Architecture.md