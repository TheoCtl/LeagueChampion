"""
Pokemon League Champion - Shop System (Rich UI)
Buy upgrades for your League members using money earned from battles.
"""
from rich.panel import Panel
from rich.table import Table
from rich import box
from data import POKEMON_DB, MOVES_DB
from ui import (
    console, styled_type_compact, hp_bar_text, team_detail_table,
    prompt, info, error, success, warning, menu_panel,
)


def show_shop(league_members, money):
    """Display the shop menu and handle purchases. Returns remaining money."""
    while True:
        console.print()
        console.print(menu_panel([
            ("1", f"Level up a Pokemon [dim](${50}/level)[/]"),
            ("2", f"Teach a new move [dim](${100})[/]"),
            ("3", f"Add a new Pokemon [dim](${200})[/]"),
            ("4", "View League teams"),
            ("5", "Exit shop"),
        ], title=f"🛒 SHOP  |  💰 ${money}"))

        choice = prompt("Choice:").strip()

        if choice == "1":
            money = _shop_level_up(league_members, money)
        elif choice == "2":
            money = _shop_teach_move(league_members, money)
        elif choice == "3":
            money = _shop_add_pokemon(league_members, money)
        elif choice == "4":
            _show_all_teams(league_members)
        elif choice == "5":
            break
        else:
            error("Invalid choice.")

    return money


def _pick_member(league_members):
    """Let the player pick a league member."""
    table = Table(box=box.SIMPLE, border_style="dim", show_header=False, padding=(0, 1))
    table.add_column("#", width=3, justify="center", style="bold")
    table.add_column("Member", min_width=20)
    table.add_column("Team Size", width=10, justify="center")

    for i, member in enumerate(league_members):
        table.add_row(str(i + 1), f"[bold]{member.display_name()}[/]", f"{len(member.team)} Pokemon")

    console.print(table)

    try:
        idx = int(prompt("Choice (0 to cancel):").strip()) - 1
        if idx == -1:
            return None
        if 0 <= idx < len(league_members):
            return league_members[idx]
    except (ValueError, IndexError):
        pass
    error("Invalid choice.")
    return None


def _pick_pokemon(trainer):
    """Let the player pick a Pokemon from a trainer's team."""
    console.print(team_detail_table(trainer))
    try:
        idx = int(prompt("Choice (0 to cancel):").strip()) - 1
        if idx == -1:
            return None
        if 0 <= idx < len(trainer.team):
            return trainer.team[idx]
    except (ValueError, IndexError):
        pass
    error("Invalid choice.")
    return None


def _shop_level_up(league_members, money):
    """Level up a Pokemon. Cost: $50 per level."""
    cost_per_level = 50
    member = _pick_member(league_members)
    if not member:
        return money
    poke = _pick_pokemon(member)
    if not poke:
        return money

    max_affordable = money // cost_per_level
    if max_affordable == 0:
        error(f"Not enough money! Need ${cost_per_level} per level, you have ${money}.")
        return money

    info(f"[bold]{poke.species}[/] is Lv.{poke.level}. Cost: ${cost_per_level}/level. You can afford up to {max_affordable} levels.")

    try:
        levels = int(prompt("How many levels?").strip())
        if levels <= 0:
            return money
        if levels > max_affordable:
            error("Not enough money!")
            return money
    except ValueError:
        error("Invalid input.")
        return money

    cost = levels * cost_per_level
    poke.level_up(levels)
    money -= cost
    success(f"{poke.species} leveled up to Lv.{poke.level}! (-${cost})")
    return money


def _shop_teach_move(league_members, money):
    """Teach a new move. Cost: $100."""
    cost = 100
    if money < cost:
        error(f"Not enough money! Need ${cost}, you have ${money}.")
        return money

    member = _pick_member(league_members)
    if not member:
        return money
    poke = _pick_pokemon(member)
    if not poke:
        return money

    available = [m for m in poke.learnable_moves if m not in poke.moves]
    if not available:
        warning(f"{poke.species} already knows all available moves!")
        return money

    table = Table(
        title=f"[bold]Learnable Moves[/] [dim](cost: ${cost})[/]",
        box=box.ROUNDED,
        border_style="bright_yellow",
    )
    table.add_column("#", width=3, justify="center", style="bold")
    table.add_column("Move", min_width=14)
    table.add_column("Type", min_width=10)
    table.add_column("Cat.", width=5, justify="center")
    table.add_column("Pow", width=5, justify="right")
    table.add_column("Acc", width=5, justify="right")

    for i, move_name in enumerate(available):
        md = MOVES_DB[move_name]
        cat = "PHY" if md["category"] == "physical" else "SPE"
        cat_color = "red" if md["category"] == "physical" else "cyan"
        table.add_row(
            str(i + 1), f"[bold]{move_name}[/]",
            styled_type_compact(md["type"]),
            f"[{cat_color}]{cat}[/]",
            str(md["power"]), f"{md['accuracy']}%",
        )

    console.print(table)

    try:
        idx = int(prompt("Choose move (0 to cancel):").strip()) - 1
        if idx == -1:
            return money
        if 0 <= idx < len(available):
            new_move = available[idx]
        else:
            error("Invalid choice.")
            return money
    except ValueError:
        return money

    if len(poke.moves) >= 4:
        warning(f"{poke.species} already knows 4 moves. Replace one?")
        for i, m in enumerate(poke.moves):
            md = MOVES_DB[m]
            info(f"  {i+1}. [bold]{m}[/] ({styled_type_compact(md['type'])}, Pow:{md['power']})")
        console.print("  [dim]0. Cancel[/]")
        try:
            rep = int(prompt("Replace which?").strip()) - 1
            if rep == -1:
                return money
            if 0 <= rep < len(poke.moves):
                old_move = poke.moves[rep]
                poke.moves[rep] = new_move
                money -= cost
                success(f"{poke.species} forgot {old_move} and learned {new_move}! (-${cost})")
            else:
                error("Invalid choice.")
        except ValueError:
            return money
    else:
        poke.moves.append(new_move)
        money -= cost
        success(f"{poke.species} learned {new_move}! (-${cost})")

    return money


def _shop_add_pokemon(league_members, money):
    """Add a new Pokemon to a member's team. Cost: $200."""
    cost = 200
    if money < cost:
        error(f"Not enough money! Need ${cost}, you have ${money}.")
        return money

    member = _pick_member(league_members)
    if not member:
        return money

    current_species = {p.species for p in member.team}
    available_pokemon = sorted([s for s in POKEMON_DB if s not in current_species])

    page = 0
    page_size = 10
    while True:
        start = page * page_size
        end = min(start + page_size, len(available_pokemon))
        total_pages = (len(available_pokemon) - 1) // page_size + 1

        table = Table(
            title=f"[bold]Available Pokemon[/] [dim](page {page+1}/{total_pages}, cost: ${cost})[/]",
            box=box.ROUNDED,
            border_style="bright_green",
        )
        table.add_column("#", width=4, justify="center", style="bold")
        table.add_column("Pokemon", min_width=12)
        table.add_column("Type", min_width=16)

        for i in range(start, end):
            species = available_pokemon[i]
            pdata = POKEMON_DB[species]
            types = " / ".join(styled_type_compact(t) for t in pdata["types"])
            table.add_row(str(i + 1), f"[bold]{species}[/]", types)

        console.print(table)
        console.print("  [dim]n = next page, p = prev page, 0 = cancel[/]")
        inp = prompt("Choose Pokemon (number/n/p/0):").strip().lower()

        if inp == "n":
            if end < len(available_pokemon):
                page += 1
            continue
        elif inp == "p":
            if page > 0:
                page -= 1
            continue
        elif inp == "0":
            return money

        try:
            idx = int(inp) - 1
            if 0 <= idx < len(available_pokemon):
                species = available_pokemon[idx]
                break
            else:
                error("Invalid choice.")
        except ValueError:
            error("Invalid input.")

    avg_level = sum(p.level for p in member.team) // len(member.team) if member.team else 10
    new_level = max(5, avg_level - 2)

    pdata = POKEMON_DB[species]
    default_moves = pdata["learnable_moves"][:2]

    from pokemon import Pokemon
    new_poke = Pokemon(species, new_level, default_moves)

    if len(member.team) >= 6:
        warning(f"{member.display_name()} already has 6 Pokemon. Replace one?")
        for i, p in enumerate(member.team):
            info(f"  {i+1}. [bold]{p.species}[/] Lv.{p.level}")
        console.print("  [dim]0. Cancel[/]")
        try:
            rep = int(prompt("Replace which?").strip()) - 1
            if rep == -1:
                return money
            if 0 <= rep < len(member.team):
                old = member.team[rep]
                member.team[rep] = new_poke
                money -= cost
                success(f"{old.species} was replaced by {species} Lv.{new_level}! (-${cost})")
            else:
                error("Invalid choice.")
        except ValueError:
            return money
    else:
        member.team.append(new_poke)
        money -= cost
        success(f"{species} Lv.{new_level} joined {member.display_name()}'s team! (-${cost})")

    return money


def _show_all_teams(league_members):
    """Display all league member teams."""
    for member in league_members:
        console.print(team_detail_table(member))
        console.print()
