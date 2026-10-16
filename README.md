# Task Tracker CLI 🚀

A simple, robust, and lightweight Command Line Interface (CLI) application built with Python to track and manage your daily tasks. This project runs entirely on native libraries with zero external dependencies and utilizes local JSON persistence for state management.

---

## Features

- **Add Tasks**: Create new tasks with an automatically generated unique ID.
- **List Tasks**: View all tasks or filter them dynamically by status (`todo`, `in-progress`, `done`).
- **Update Tasks**: Modify the description of any existing task.
- **Delete Tasks**: Remove tasks by their unique ID[cite: 2].
- **Status Management**: Quickly transition task statuses using dedicated commands (`mark-todo`, `mark-in-progress`, `mark-done`)[cite: 2].
- **Defensive Error Handling**: Gracefully handles missing files, invalid argument lengths, corrupted JSON data, and type mismatches[cite: 2].

---

## Prerequisites

- Ensure you have **Python 3.x** installed on your machine. You can verify your installation by running:
  ```bash
  python --version