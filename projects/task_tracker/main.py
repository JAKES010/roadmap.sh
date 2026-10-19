import sys
import json
from datetime import datetime
from pathlib import Path

USAGE = """Usage: python3 main.py <command> [arguments]

Commands:
  add <description>           Add a task
  list [status]               List tasks, optionally filtered by status
  update <id> <description>   Update a task description
  delete <id>                 Delete a task
  mark-todo <id>              Mark a task as todo
  mark-in-progress <id>       Mark a task as in-progress
  mark-done <id>              Mark a task as done

Statuses: todo, in-progress, done
Use quotes around descriptions containing spaces."""

if len(sys.argv) < 2:
    sys.exit(USAGE)

command = sys.argv[1] 
t_command = command.lower()

valid_commands = ["add", "list", "update", "delete", "mark-done", "mark-in-progress", "mark-todo"]
if t_command in ("-h", "--help", "help"):
    if len(sys.argv) > 2:
        sys.exit("Error: Help does not accept additional arguments.")
    print(USAGE)
    sys.exit(0)

if t_command not in valid_commands:
    sys.exit(f"Error: '{t_command}' is not a valid command. Choose from: {', '.join(valid_commands)}")

max_argument_counts = {
    "add": 3,
    "list": 3,
    "update": 4,
    "delete": 3,
    "mark-done": 3,
    "mark-in-progress": 3,
    "mark-todo": 3,
}
if len(sys.argv) > max_argument_counts[t_command]:
    sys.exit(f"Error: Too many arguments for '{t_command}'.")

FILENAME = Path(__file__).resolve().with_name("task_file.json")
VALID_STATUSES = {"todo", "in-progress", "done"}

# --- HELPER FUNCTIONS ---
def load_tasks():
    if not FILENAME.exists():
        return []
    with open(FILENAME, "r") as file:
        try:
            tasks = json.load(file)
        except json.JSONDecodeError as error:
            sys.exit(
                f"Error: Task data file contains invalid JSON at line "
                f"{error.lineno}, column {error.colno}; file was left unchanged."
            )

    if not isinstance(tasks, list):
        sys.exit("Error: Task data file must contain a JSON list; file was left unchanged.")

    task_ids = set()
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            sys.exit(f"Error: Task {index} must be a JSON object; file was left unchanged.")
        if type(task.get("id")) is not int or task["id"] < 1:
            sys.exit(f"Error: Task {index} must have a positive integer ID; file was left unchanged.")
        if task["id"] in task_ids:
            sys.exit(f"Error: Task {index} has a duplicate ID; file was left unchanged.")
        task_ids.add(task["id"])
        if not isinstance(task.get("description"), str):
            sys.exit(f"Error: Task {index} must have a string description; file was left unchanged.")
        if not isinstance(task.get("status"), str) or task["status"] not in VALID_STATUSES:
            sys.exit(f"Error: Task {index} has an invalid status; file was left unchanged.")
        if not isinstance(task.get("createdAt"), str) or not isinstance(task.get("updatedAt"), str):
            sys.exit(f"Error: Task {index} must have string createdAt and updatedAt values; file was left unchanged.")

    return tasks

def save_tasks(tasks):
    with open(FILENAME, "w") as file:
        json.dump(tasks, file, indent=4)


# --- COMMAND HANDLING ---
if t_command == "add":
    if len(sys.argv) < 3:
        sys.exit("Error: Please provide a task description. Example: add 'My task'")
        
    task_info = sys.argv[2]
    if not task_info.strip():
        sys.exit("Error: Task description cannot be empty.")

    tasks = load_tasks()
    next_id = max((task["id"] for task in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "description": task_info,
        "status": "todo",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {new_task['id']})")

elif t_command == "list":
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        sys.exit(0)
    
    if len(sys.argv) > 2:
        filter_status = sys.argv[2].lower()
        if filter_status not in VALID_STATUSES:
            print(f"Error: '{filter_status}' is not a valid task status.")
            sys.exit("Please choose from: todo, in-progress, done")

        found_status = False
        for task in tasks:
            if task["status"] == filter_status:
                print(f"[{task['status'].upper()}] \nID: {task['id']} \nTasks: {task['description']} \nCreatedAt: {task['createdAt']} \nUpdatedAt: {task['updatedAt']}")
                found_status = True

        if not found_status:
            print(f"No tasks found with status '{filter_status}'.")
    else:
        for task in tasks:
            print(f"[{task['status'].upper()}] \nID: {task['id']} \nTasks: {task['description']} \nCreatedAt: {task['createdAt']} \nUpdatedAt: {task['updatedAt']}")

elif t_command == "update":
    if len(sys.argv) < 4:
        sys.exit("Error: Please provide a task ID and new description. Example: update 1 'Updated task description'")

    try:
        task_id = int(sys.argv[2])
    except ValueError:
        sys.exit("Error: Task ID must be an integer.")

    new_description = sys.argv[3]
    if not new_description.strip():
        sys.exit("Error: Task description cannot be empty.")

    tasks = load_tasks()

    found_description = False
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = new_description
            task["updatedAt"] = datetime.now().isoformat()
            found_description = True
            break

    if not found_description:
        sys.exit(f"Error: Task with ID {task_id} not found.")

    save_tasks(tasks)
    print(f"Task with ID {task_id} updated successfully.")

elif t_command == "delete":
    if len(sys.argv) < 3:
        sys.exit("Error: Please provide a task ID to delete. Example: delete 1")

    try:
        task_id = int(sys.argv[2])
    except ValueError:
        sys.exit("Error: Task ID must be an integer.")

    tasks = load_tasks()

    found_delete = False
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            found_delete = True
            break

    if not found_delete:
        sys.exit(f"Error: Task with ID {task_id} not found.")

    save_tasks(tasks)
    print(f"Task with ID {task_id} deleted successfully.")

elif t_command in ("mark-done", "mark-in-progress", "mark-todo"):
    _, status = t_command.split("-", 1)
    if len(sys.argv) < 3:
        sys.exit("Error: Please provide a task ID.")

    try:
        task_id = int(sys.argv[2])
    except ValueError:
        sys.exit("Error: Task ID must be an integer.")

    tasks = load_tasks()
    found_status = False
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updatedAt"] = datetime.now().isoformat()
            found_status = True
            break

    if not found_status:
        sys.exit(f"Error: Task with ID {task_id} not found.")

    save_tasks(tasks)
    print(f"Task {task_id} marked as {status}.")
