# simulator/simulator.py
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
import websockets

console = Console()

# Load tasks
TASKS_FILE = Path(__file__).parent / "tasks.yaml"
try:
    with open(TASKS_FILE, encoding="utf-8") as f:
        TASKS = yaml.safe_load(f)["tasks"]
except FileNotFoundError:
    console.print(f"[red] tasks.yaml not found at {TASKS_FILE}[/red]")
    TASKS = [
        {
            "id": "demo_task",
            "name": "Demo Task (No tasks.yaml)",
            "skill": "Demo Skill",
            "category": "Demo",
            "base_time_sec": 10,
            "base_errors": 1,
            "difficulty": 2
        }
    ]


def simulate_task(task, user_skill_level=50):
    """
    Simulate task attempt.
    user_skill_level: 0–100 (from UserSkillProfile)
    Returns event dict.
    """
    skill_factor = max(0.2, user_skill_level / 100.0)  # min 20% efficiency

    difficulty = task["difficulty"]
    base_errors = task["base_errors"]
    base_time = task["base_time_sec"]

    # Errors: higher skill → fewer errors
    errors = max(0, round(random.gauss(base_errors * (1 - skill_factor), 0.5)))
    
    # Time: higher skill → faster
    time_factor = 1.0 / (0.5 + 0.5 * skill_factor)  # 1.0 (skilled) to 2.0 (novice)
    time_taken = max(2, round(random.gauss(base_time * time_factor, base_time * 0.2)))

    retries = errors
    success = errors == 0

    return {
        "user_id": "U1",
        "task_id": task["id"],
        "skill": task["skill"],
        "category": task["category"],
        "errors": errors,
        "retries": retries,
        "time_taken_sec": time_taken,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "success": success
    }


def main():
    console.print("[bold blue] Skill Agent Task Simulator[/bold blue]")
    console.print("Simulate user task attempts to generate skill gap events.\n")

    # Select user
    user_id = Prompt.ask("Enter user ID", default="U1")
    try:
        skill_level = int(Prompt.ask("User skill level (0–100)", default="50"))
        if not (0 <= skill_level <= 100):
            raise ValueError
    except ValueError:
        console.print("[yellow]  Invalid skill level. Using 50.[/yellow]")
        skill_level = 50

    # Select task
    table = Table(title="Available Tasks", expand=False)
    table.add_column("No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("Task", style="white")
    table.add_column("Skill", style="green")
    table.add_column("Difficulty", style="yellow")

    for i, t in enumerate(TASKS, 1):
        table.add_row(str(i), t["name"], t["skill"], "★" * t["difficulty"])
    console.print(table)

    try:
        choice = int(Prompt.ask("Select task number", default="1")) - 1
        task = TASKS[choice]
    except (ValueError, IndexError):
        console.print("[yellow]  Invalid choice. Using first task.[/yellow]")
        task = TASKS[0]

    console.print(f"\n[bold] Simulating: {task['name']}[/bold]")

    with console.status("[bold green]Working...[/bold green]") as status:
        time.sleep(1.5)
        event = simulate_task(task, skill_level)
        event["user_id"] = user_id  # Override with user input

    # Show result
    color = "green" if event["success"] else "red"
    console.print(f"\n[bold {color}]{' Success' if event['success'] else ' Failed'}![/bold {color}]")
    console.print(f"Errors: {event['errors']} | Retries: {event['retries']} | Time: {event['time_taken_sec']}s")

    # Output event
    console.print("\n[bold] Generated Event:[/bold]")
    console.print_json(json.dumps(event, indent=2))

    # Save to file
    log_file = Path("simulator/events.log")
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    console.print(f"\n Saved to [cyan]{log_file}[/cyan]")

    # --- Send to Backend (WebSocket) ---
    if Confirm.ask("Send to backend (ws://localhost:8000/api/events)?", default=True):
        try:
            # Ensure user_id is string
            event["user_id"] = str(event["user_id"])

            async def send_ws():
                uri = "ws://localhost:8000/api/events"
                async with websockets.connect(uri) as websocket:
                    await websocket.send(json.dumps(event, ensure_ascii=False))
                    response = await websocket.recv()
                    return json.loads(response)

            console.print("[bold cyan]📡 Sending to backend...[/bold cyan]")
            response = asyncio.run(send_ws())
            
            status = response.get("status", "unknown")
            if status == "received":
                console.print(f"[green] Backend received event for skill: {response.get('skill')}[/green]")
            else:
                console.print(f"[yellow]  Backend response: {response}[/yellow]")

        except Exception as e:
            console.print(f"[red] Failed to send: {e}[/red]")
            console.print("[yellow] Tip: Is your backend running? Check: http://localhost:8000/docs[/yellow]")

    console.print("\n[bold] Simulation complete![/bold]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]  Simulation interrupted.[/bold yellow]")
    except Exception as e:
        console.print(f"[red] Unexpected error: {e}[/red]")
        raise