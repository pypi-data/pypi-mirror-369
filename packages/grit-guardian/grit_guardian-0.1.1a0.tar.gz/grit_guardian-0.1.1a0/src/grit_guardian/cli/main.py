import click

from ..pet import Pet
from ..core import HabitTracker
from ..persistence import DatabaseManager
from ..analytics import (
    generate_weekly_view,
    identify_struggled_habits,
)

_tracker = None


# Lazy loading the DatabaseManager instance to prevent initializing
# before test fixtures can patch the database path
def get_tracker():
    """Get or create the HabitTracker instance."""
    global _tracker
    if _tracker is None:
        db_manager = DatabaseManager()
        _tracker = HabitTracker(db_manager)
    return _tracker


@click.group()
def main():
    """Grit Guardian - CLI habit tracker."""
    pass


@main.command()
@click.argument("name")
@click.argument("task")
@click.argument("periodicity", type=click.Choice(["daily", "weekly"]))
def add(name, task, periodicity):
    """Adds a new habit to track."""
    try:
        habit = get_tracker().add_habit(name, task, periodicity)
        click.echo(f"✓ Added habit '{habit.name}' ({habit.periodicity.value})")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)


@main.command()
def list():
    """Lists all habits."""
    habits = get_tracker().list_habits()
    if not habits:
        click.echo("No habits found. Add one with 'grit-guardian add'")
        return

    click.echo("\nYour Habits:")
    click.echo("-" * 50)
    for habit in habits:
        click.echo(f"• {habit.name} - {habit.task} ({habit.periodicity.value})")


@main.command()
@click.argument("name")
def delete(name):
    """Deletes a habit."""
    if click.confirm(f"Delete habit '{name}'?"):
        try:
            get_tracker().delete_habit(name)
            click.echo(f"✓ Deleted habit '{name}'")
        except Exception as e:
            click.echo(f"✗ {str(e)}", err=True)


@main.command()
@click.argument("name")
def complete(name):
    """Marks a habit as completed"""
    try:
        get_tracker().complete_habit(name)
        click.echo(f"✓ Completed '{name}'!")
    except Exception as e:
        click.echo(f"✗ {str(e)}", err=True)


@main.command()
def status():
    """Shows today's habit status"""
    status = get_tracker().get_status()

    click.echo("\n📊 Today's Status")
    click.echo("=" * 30)

    if status["pending"]:
        click.echo("\n⏳ Pending:")
        for habit in status["pending"]:
            click.echo(f"  • {habit.name}")

    if status["completed"]:
        click.echo("\n✅ Completed:")
        for habit in status["completed"]:
            click.echo(f"  • {habit.name}")

    if not status["pending"] and not status["completed"]:
        click.echo("\nNo habits found. Add one with 'grit-guardian add'")
    else:
        click.echo(f"\nProgress: {len(status['completed'])}/{status['total']}")
        if len(status["completed"]) == status["total"] and status["total"] > 0:
            click.echo("🎉 All habits completed!")


@main.command()
def streaks():
    """Views current streaks and completion rates for all habits."""
    streaks_data = get_tracker().get_streaks()

    if not streaks_data:
        click.echo("No habits found. Add one with 'grit-guardian add'")
        return

    click.echo("\n🔥 Habit Streaks & Analytics")
    click.echo("=" * 60)

    for streak_info in streaks_data:
        click.echo(f"\n📌 {streak_info['name']}")
        click.echo(f"   Current Streak: {streak_info['current_streak']} days")
        click.echo(f"   Longest Streak: {streak_info['longest_streak']} days")
        click.echo(f"   Completion Rate: {streak_info['completion_rate']:.1f}%")

    # Calculate total stats
    total_current_streak = sum(s["current_streak"] for s in streaks_data)
    avg_completion_rate = sum(s["completion_rate"] for s in streaks_data) / len(
        streaks_data
    )

    click.echo("\n" + "-" * 60)
    click.echo("📊 Overall Stats:")
    click.echo(f"   Total Active Streaks: {total_current_streak}")
    click.echo(f"   Average Completion Rate: {avg_completion_rate:.1f}%")


@main.command()
def weekly():
    """Shows weekly progress view"""
    habits = get_tracker().list_habits()
    if not habits:
        click.echo("No habits to display")
        return

    click.echo("\n📅 Weekly Progress")
    click.echo("=" * 60)
    click.echo(generate_weekly_view(habits))

    # Show summary
    click.echo("\n" + "-" * 60)
    click.echo("✓ = Completed  |  ✗ = Missed  |  - = Future")


@main.command()
@click.option("--since", default=30, help="Days to analyze")
def struggled(since):
    """Shows habits you've struggled with"""
    habits = get_tracker().list_habits()
    struggled_habits = identify_struggled_habits(habits, since)

    if not struggled_habits:
        click.echo(f"\n🌟 Great job! No struggled habits in the last {since} days.")
        click.echo("Keep up the excellent work!")
    else:
        click.echo(f"\n⚠️  Habits needing attention (last {since} days):")
        click.echo("=" * 50)

        for habit in struggled_habits:
            percentage = habit["completion_rate"] * 100
            click.echo(f"\n• {habit['name']}")
            click.echo(f"  Completion rate: {percentage:.0f}%")
            click.echo(f"  Missed: {habit['missed']} times")

        click.echo("\n💡 Tip: Focus on one habit at a time to build momentum!")


@main.command()
def pet():
    """View your Grit Guardian pet's status"""
    pet = get_tracker().get_pet()

    click.echo("\n🐉 Your Grit Guardian")
    click.echo("=" * 40)
    click.echo(pet.get_ascii_art())
    click.echo("\n" + "-" * 40)
    click.echo(f"Name: {pet.name}")
    click.echo(f"Mood: {pet.current_mood.value.capitalize()}")
    click.echo("\n" + pet.get_mood_message())

    # Show tips based on mood
    if pet.current_mood.value in ["sad", "worried"]:
        click.echo("\n💡 Tip: Complete some habits to cheer up your pet!")
    elif pet.current_mood.value == "ecstatic":
        click.echo("\n⭐ Amazing work! Keep up the great consistency!")


@main.command()
def init():
    """Initialize Grit Guardian with sample habits"""
    click.echo("\n🐉 Welcome to Grit Guardian!\n")

    if get_tracker().initialize_sample_data():
        click.echo("✓ Created sample habits to get you started:")
        habits = get_tracker().list_habits()
        for habit in habits:
            click.echo(f"  • {habit.name} - {habit.task}")

        click.echo("\n🎯 Quick Start Guide:")
        click.echo("  - View your habits: grit-guardian list")
        click.echo('  - Complete a habit: grit-guardian complete "Morning Reading"')
        click.echo("  - Check your pet: grit-guardian pet")
        click.echo("  - See weekly progress: grit-guardian weekly")
        click.echo("  - View your streaks: grit-guardian streaks")
        click.echo("\nYour Guardian dragon is waiting to see your progress!")

        # Show initial pet
        pet = Pet()
        click.echo("\n" + pet.get_ascii_art())
        click.echo(f"\n{pet.name} says: Let's build great habits together! 🌟")
    else:
        click.echo("Grit Guardian is already initialized.")
        click.echo("Use 'grit-guardian status' to see today's habits.")

        # Show current stats instead
        habits = get_tracker().list_habits()
        if habits:
            click.echo(f"\nYou have {len(habits)} habits tracked.")
            pet = get_tracker().get_pet()
            click.echo(f"Your pet's mood: {pet.current_mood.value.capitalize()}")


if __name__ == "__main__":
    main()
