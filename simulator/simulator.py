import yaml
import random
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
import asyncio

from simulator.event_sender import send_event

console = Console()

# -------------------------------------------------
# Load tasks
# -------------------------------------------------
TASKS_FILE = Path(__file__).parent / "tasks.yaml"

with open(TASKS_FILE, encoding="utf-8") as f:
    TASKS = yaml.safe_load(f)["tasks"]


def simulate_task(task, user_skill_level=50):
    """
    Simulate task attempt and convert to backend skill event.
    """

    skill_factor = max(0.2, user_skill_level / 100.0)

    errors = max(
        0,
        round(random.gauss(task["base_errors"] * (1 - skill_factor), 0.5))
    )

    success = errors == 0

    # 🔑 GAP LOGIC (THIS IS IMPORTANT)
    skill_gaps = []
    if not success:
        skill_gaps.append(task["skill"].lower())

    return {
        "user_id": None,  # filled later
        "language": task["skill"].lower(),
        "event_type": "simulated_task",
        "skill_gaps": skill_gaps,
        "message": f"Simulated task: {task['name']}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    console.print("[bold blue]Skill Coach Simulator[/bold blue]\n")

    user_id = Prompt.ask("Enter user ID", default="test_user")
    skill_level = int(Prompt.ask("User skill level (0–100)", default="50"))

    table = Table(title="Available Tasks")
    table.add_column("No")
    table.add_column("Task")
    table.add_column("Skill")
    table.add_column("Difficulty")

    for i, t in enumerate(TASKS, 1):
        table.add_row(
            str(i),
            t["name"],
            t["skill"],
            "★" * t["difficulty"]
        )

    console.print(table)

    choice = int(Prompt.ask("Select task number", default="1")) - 1
    task = TASKS[choice]

    console.print(f"\nSimulating: [bold]{task['name']}[/bold]\n")
    time.sleep(1)

    event = simulate_task(task, skill_level)
    event["user_id"] = str(user_id)

    console.print("[bold]Generated Event[/bold]")
    console.print_json(json.dumps(event, indent=2))

    if Confirm.ask("Send to backend?", default=True):
        try:
            response = asyncio.run(send_event(event))
            console.print("[green]Event sent successfully[/green]")
            console.print(response)
        except Exception as e:
            console.print(f"[red]Failed to send event: {e}[/red]")

    console.print("\nSimulation complete.")


if __name__ == "__main__":
    main()
