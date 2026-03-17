"""
Pokemon League Champion - Main Game Loop (Rich UI)
"""
import os
import sys
from pokemon import Trainer
from battle import run_battle
from generator import generate_challenger
from shop import show_shop
from data import (
    DEFAULT_GYM_LEADERS, DEFAULT_ELITE_FOUR, CHAMPION_STARTER_OPTIONS,
)
from ui import (
    console, banner, starter_table, day_header, matchup_panel,
    menu_panel, league_overview_table, victory_panel, defeat_panel,
    game_over_panel, prompt, info, warning, success,
)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def setup_game():
    """Initialize the game: pick champion team, build league."""
    clear_screen()
    banner()

    player_name = prompt("Enter your name, Champion:").strip()
    if not player_name:
        player_name = "Champion"

    # Pick starter team
    console.print()
    console.print(starter_table(CHAMPION_STARTER_OPTIONS))

    while True:
        try:
            choice = int(prompt("Your choice (1-3):").strip())
            if 1 <= choice <= 3:
                break
        except ValueError:
            pass
        console.print("  [dim]Invalid choice.[/]")

    champion_data = CHAMPION_STARTER_OPTIONS[choice - 1]

    # Build league
    gym_leaders = []
    for gl_data in DEFAULT_GYM_LEADERS:
        trainer = Trainer(gl_data["name"], gl_data["title"], gl_data["team"], gl_data.get("specialty"))
        gym_leaders.append(trainer)

    elite_four = []
    for e4_data in DEFAULT_ELITE_FOUR:
        trainer = Trainer(e4_data["name"], e4_data["title"], e4_data["team"], e4_data.get("specialty"))
        elite_four.append(trainer)

    champion = Trainer(player_name, "Champion", champion_data["team"])

    league = gym_leaders + elite_four + [champion]

    return league, champion, player_name


def main():
    league, champion, player_name = setup_game()

    money = 200
    day = 1
    challengers_beaten = 0
    current_challenger = None
    challenger_position = 0

    from rich.panel import Panel
    console.print()
    console.print(Panel(
        "[bright_cyan]Your League is set up! Challengers will come daily.\n"
        "Win battles to earn money. Spend it in the shop to\n"
        "strengthen your League and stay on top![/]",
        border_style="bright_cyan", padding=(1, 2),
    ))
    prompt("Press Enter to begin...")

    while True:
        clear_screen()

        # Generate new challenger if needed
        if current_challenger is None:
            challenger_data = generate_challenger(challengers_beaten)
            current_challenger = Trainer(
                challenger_data["name"],
                challenger_data["title"],
                challenger_data["team"],
            )
            challenger_position = 0

        # Day header
        console.print()
        console.print(day_header(day, money, challengers_beaten))

        # Matchup
        league_member = league[challenger_position]
        console.print(matchup_panel(
            current_challenger, league_member,
            challenger_position + 1, len(league),
        ))

        # Menu
        console.print(menu_panel([
            ("1", "⚔️  Fight the battle!"),
            ("2", "🛒 Visit the Shop"),
            ("3", "🏟️  View League Overview"),
            ("4", "🚪 Quit Game"),
        ]))

        choice = prompt("Choice:").strip()

        if choice == "2":
            money = show_shop(league, money)
            continue
        elif choice == "3":
            console.print()
            console.print(league_overview_table(league, challenger_position))
            prompt("Press Enter to go back...")
            continue
        elif choice == "4":
            console.print()
            console.print(Panel(
                f"[bold]Thanks for playing, {player_name}![/]\n"
                f"[dim]You lasted {day} days and defeated {challengers_beaten} challengers.[/]",
                border_style="bright_cyan", padding=(1, 2),
            ))
            sys.exit(0)
        elif choice != "1":
            continue

        # ── BATTLE ──
        league_member.heal_all()
        current_challenger.heal_all()

        is_champion_fight = (league_member is champion)

        console.print()
        info(f"You will fight as [bold]{league_member.display_name()}[/]!")
        prompt("Press Enter to start the battle...")
        console.print()

        player_won, battle_log = run_battle(league_member, current_challenger, player_controlled=True)

        if player_won:
            day_reward = 50 + challenger_position * 25
            money += day_reward
            challengers_beaten += 1

            console.print()
            console.print(victory_panel(
                f"{current_challenger.display_name()} has been defeated!",
                day_reward,
            ))
            info(f"Total money: [bold bright_yellow]${money}[/]")

            current_challenger = None
            challenger_position = 0
        else:
            if is_champion_fight:
                # GAME OVER
                console.print()
                console.print(game_over_panel(day, challengers_beaten))
                prompt("Press Enter to exit...")
                sys.exit(0)
            else:
                daily_income = 30
                money += daily_income
                challenger_position += 1

                console.print()
                console.print(defeat_panel(
                    f"{league_member.display_name()} was defeated!\n"
                    f"{current_challenger.display_name()} advances to stage {challenger_position + 1}!\n"
                    f"[bright_yellow]💰 +${daily_income}[/]",
                ))

                remaining = len(league) - challenger_position
                if remaining <= 2:
                    warning(f"The challenger is {remaining} stage(s) from YOU!")

        day += 1
        prompt("Press Enter to continue to the next day...")


if __name__ == "__main__":
    main()
