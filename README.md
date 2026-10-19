# Task Tracker CLI

A lightweight command-line application for tracking tasks. It uses only the Python standard library and stores tasks in a local JSON file.

## Requirements

- Python 3

## Usage

Run commands from the task tracker directory:

```bash
cd projects/task_tracker
python3 main.py <command> [arguments]
```

On systems where Python 3 is invoked as `python`, replace `python3` with `python`.

### Add a task

```bash
python3 main.py add "Buy groceries"
```

### List tasks

```bash
python3 main.py list
python3 main.py list todo
python3 main.py list in-progress
python3 main.py list done
```

### Update or delete a task

```bash
python3 main.py update 1 "Buy groceries and cook dinner"
python3 main.py delete 1
```

### Change a task's status

```bash
python3 main.py mark-in-progress 1
python3 main.py mark-done 1
python3 main.py mark-todo 1
```

Task data is stored in `projects/task_tracker/task_file.json`, alongside the script. If that file contains invalid JSON, the application reports the parse location and leaves the file unchanged.

This project is part of the [Task Tracker challenge on roadmap.sh](https://roadmap.sh/projects/task-tracker).
