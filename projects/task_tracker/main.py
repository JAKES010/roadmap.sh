import sys
import os
import json
from datetime import datetime
from enum import Enum

if len(sys.argv) < 2:
    sys.exit("Usage: python script.py <command> <task_input>") 

command = sys.argv[1] 
t_command = command.lower()

valid_commands = ["add", "list", "update", "delete", "mark-done", "mark-in-progress", "mark-todo"]
if t_command not in valid_commands:
    sys.exit(f"Error: '{t_command}' is not a valid command. Choose from: {', '.join(valid_commands)}")

FILENAME = "task_file.json"

# --- HELPER FUNCTIONS ---
def load_tasks():
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    with open(FILENAME, "w") as file:
        json.dump(tasks, file, indent=4)


# --- COMMAND HANDLING ---
if t_command == "add":
    if len(sys.argv) < 3:
        sys.exit("Error: Please provide a task description. Example: add 'My task'")
        
    task_info = sys.argv[2]
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
        sys.exit("tasks not found")
    
    if len(sys.argv) > 2:
        filter_status = sys.argv[2].lower()

        class TaskStatus(Enum):
            TODO = "todo"
            IN_PROGRESS = "in-progress"
            DONE = "done"
            
        try:
            TaskStatus(filter_status)
        except ValueError:
            print(f"Error: '{filter_status}' is not a valid task status.")
            sys.exit("Please choose from: todo, in-progress, done")

        found_status = False
        for task in tasks:
            if task["status"] == filter_status:
                print(f"[{task['status'].upper()}] \nID: {task['id']} \nTasks: {task['description']} \nCreatedAt: {task['createdAt']} \nUpdatedAt: {task['updatedAt']}")
                found_status = True

        if not found_status:
            sys.exit(f"No tasks found with status '{filter_status}'.")
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
