"""
Pokemon League Champion - UI Helpers (Rich-powered)
Centralized display utilities: type colors, HP bars, tables, panels.
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.progress_bar import ProgressBar
from rich import box
from data import MOVES_DB

console = Console()

# ─── Type Color Mapping ────────────────────────────────────────────
TYPE_COLORS = {
    "Normal": "white",
    "Fire": "red1",
    "Water": "dodger_blue1",
    "Grass": "green3",
    "Electric": "yellow1",
    "Ice": "cyan1",
    "Fighting": "dark_orange3",
    "Poison": "medium_purple",
    "Ground": "sandy_brown",
    "Flying": "sky_blue1",
    "Psychic": "hot_pink",
    "Bug": "yellow_green",
    "Rock": "dark_goldenrod",
    "Ghost": "medium_purple1",
    "Dragon": "blue_violet",
    "Dark": "grey37",
    "Steel": "grey70",
    "Fairy": "pink1",
}

TYPE_EMOJIS = {
    "Normal": "⚪", "Fire": "🔥", "Water": "💧", "Grass": "🌿",
    "Electric": "⚡", "Ice": "❄️", "Fighting": "🥊", "Poison": "☠️",
    "Ground": "🌍", "Flying": "🌪️", "Psychic": "🔮", "Bug": "🐛",
    "Rock": "🪨", "Ghost": "👻", "Dragon": "🐉", "Dark": "🌑",
    "Steel": "⚙️", "Fairy": "✨",
}


def type_color(type_name):
    return TYPE_COLORS.get(type_name, "white")


def styled_type(type_name):
    """Return a Rich-styled type tag like [Fire]."""
    color = type_color(type_name)
    emoji = TYPE_EMOJIS.get(type_name, "")
    return f"[bold {color}]{emoji} {type_name}[/]"


def styled_type_compact(type_name):
    """Shorter type tag without emoji."""
    color = type_color(type_name)
    return f"[{color}]{type_name}[/]"


def hp_bar_text(current_hp, max_hp, bar_len=20):
    """Return a Rich-formatted HP bar string."""
    ratio = max(0, current_hp / max_hp) if max_hp > 0 else 0
    filled = int(bar_len * ratio)
    empty = bar_len - filled

    if ratio > 0.5:
        color = "green"
    elif ratio > 0.2:
        color = "yellow"
    else:
        color = "red"

    bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
    return f"{bar} [bold]{current_hp}[/]/{max_hp}"


def pokemon_status_line(pokemon, label=None):
    """Render a full Pokemon status line with type colors and HP bar."""
    types_str = " / ".join(styled_type_compact(t) for t in pokemon.types)
    prefix = f"[bold]{label}:[/] " if label else ""
    name = f"[bold]{pokemon.species}[/] Lv.{pokemon.level}"
    hp = hp_bar_text(pokemon.current_hp, pokemon.max_hp)
    return f"{prefix}{name}  [{types_str}]  {hp}"


def battle_field_panel(player_poke, enemy_poke):
    """Render the battle field as a Rich panel showing both Pokemon."""
    player_line = pokemon_status_line(player_poke, "YOU")
    enemy_line = pokemon_status_line(enemy_poke, "FOE")

    content = f"{player_line}\n\n{enemy_line}"
    return Panel(content, title="[bold]⚔️  BATTLE FIELD[/]", border_style="bright_cyan", padding=(1, 2))


def move_table(pokemon):
    """Render a pokemon's moves as a Rich table for selection."""
    table = Table(
        title=f"[bold]{pokemon.species}'s Moves[/]",
        box=box.ROUNDED,
        border_style="bright_yellow",
        show_header=True,
        header_style="bold bright_yellow",
        padding=(0, 1),
    )
    table.add_column("#", style="bold", width=3, justify="center")
    table.add_column("Move", min_width=14)
    table.add_column("Type", min_width=10)
    table.add_column("Cat.", width=5, justify="center")
    table.add_column("Pow", width=5, justify="right")
    table.add_column("Acc", width=5, justify="right")

    for i, move_name in enumerate(pokemon.moves):
        md = pokemon.get_move_data(move_name)
        if md:
            cat = "PHY" if md["category"] == "physical" else "SPE"
            cat_color = "red" if md["category"] == "physical" else "cyan"
            table.add_row(
                str(i + 1),
                f"[bold]{move_name}[/]",
                styled_type_compact(md["type"]),
                f"[{cat_color}]{cat}[/]",
                str(md["power"]),
                f"{md['accuracy']}%",
            )

    return table


def battle_message(text, style=""):
    """Print a styled battle message."""
    if style:
        console.print(f"  [{style}]{text}[/]")
    else:
        console.print(f"  {text}")


def effectiveness_message(type_mult):
    """Return styled effectiveness text."""
    if type_mult == 0:
        return "[dim italic]It doesn't affect the target...[/]"
    elif type_mult >= 2.0:
        return "[bold green]It's super effective! 💥[/]"
    elif type_mult <= 0.5:
        return "[dim red]It's not very effective...[/]"
    return None


def damage_message(defender, damage):
    """Return styled damage text."""
    return f"  [bold]{defender.species}[/] took [bold red]{damage}[/] damage! {hp_bar_text(defender.current_hp, defender.max_hp, 12)}"


def faint_message(pokemon):
    """Return styled faint text."""
    return f"  [bold red]💀 {pokemon.species} fainted![/]"


def switch_table(available_pokemon):
    """Render the pokemon selection table for switching."""
    table = Table(
        title="[bold]Choose your next Pokemon[/]",
        box=box.ROUNDED,
        border_style="bright_green",
        show_header=True,
        header_style="bold bright_green",
    )
    table.add_column("#", style="bold", width=3, justify="center")
    table.add_column("Pokemon", min_width=12)
    table.add_column("Type", min_width=12)
    table.add_column("HP", min_width=20)

    for j, (idx, p) in enumerate(available_pokemon):
        types = " / ".join(styled_type_compact(t) for t in p.types)
        hp = hp_bar_text(p.current_hp, p.max_hp, 12)
        table.add_row(str(j + 1), f"[bold]{p.species}[/] Lv.{p.level}", types, hp)

    return table


def league_overview_table(league, challenger_position=None):
    """Render the full league as a Rich table."""
    table = Table(
        title="[bold]🏟️  YOUR LEAGUE[/]",
        box=box.HEAVY,
        border_style="bright_cyan",
        show_header=True,
        header_style="bold bright_cyan",
        padding=(0, 1),
    )
    table.add_column("Stage", width=6, justify="center")
    table.add_column("Member", min_width=20)
    table.add_column("Team", min_width=40)
    table.add_column("", width=20)

    for i, member in enumerate(league):
        stage = str(i + 1)
        name = f"[bold]{member.display_name()}[/]"
        team_parts = []
        for p in member.team:
            types = "/".join(styled_type_compact(t) for t in p.types)
            team_parts.append(f"{p.species} Lv.{p.level} [{types}]")
        team_str = "\n".join(team_parts)

        marker = ""
        if challenger_position is not None and i == challenger_position:
            marker = "[bold red]⬅ CHALLENGER[/]"

        table.add_row(stage, name, team_str, marker)

    return table


def team_detail_table(trainer):
    """Render a trainer's team as a detailed table."""
    table = Table(
        title=f"[bold]{trainer.display_name()}'s Team[/]",
        box=box.ROUNDED,
        border_style="bright_magenta",
        show_header=True,
        header_style="bold bright_magenta",
    )
    table.add_column("#", width=3, justify="center")
    table.add_column("Pokemon", min_width=12)
    table.add_column("Lv", width=4, justify="center")
    table.add_column("Type", min_width=12)
    table.add_column("HP", min_width=16)
    table.add_column("Moves", min_width=24)

    for i, p in enumerate(trainer.team):
        types = "/".join(styled_type_compact(t) for t in p.types)
        hp = hp_bar_text(p.current_hp, p.max_hp, 10) if not p.is_fainted() else "[bold red]FAINTED[/]"
        moves = ", ".join(p.moves)
        table.add_row(
            str(i + 1),
            f"[bold]{p.species}[/]",
            str(p.level),
            types,
            hp,
            moves,
        )

    return table


def day_header(day, money, challengers_beaten):
    """Render the day header panel."""
    content = (
        f"[bold bright_cyan]📅 DAY {day}[/]    "
        f"[bold bright_yellow]💰 ${money}[/]    "
        f"[bold bright_green]🏆 Challengers Defeated: {challengers_beaten}[/]"
    )
    return Panel(content, border_style="bright_blue", padding=(0, 2))


def matchup_panel(challenger, league_member, stage, total_stages):
    """Render the day's matchup info."""
    chall_team = "\n".join(
        f"  {p.species} Lv.{p.level}  [{'/'.join(styled_type_compact(t) for t in p.types)}]"
        for p in challenger.team
    )
    member_team = "\n".join(
        f"  {p.species} Lv.{p.level}  [{'/'.join(styled_type_compact(t) for t in p.types)}]"
        for p in league_member.team
    )

    content = (
        f"[bold red]{challenger.display_name()}[/] [dim](Stage {stage}/{total_stages})[/]\n"
        f"{chall_team}\n\n"
        f"[bold bright_cyan]  ⚔️  VS  ⚔️[/]\n\n"
        f"[bold green]{league_member.display_name()}[/]\n"
        f"{member_team}"
    )
    return Panel(content, title="[bold]Today's Matchup[/]", border_style="bright_yellow", padding=(1, 2))


def menu_panel(options, title="Actions"):
    """Render a menu of numbered options."""
    lines = []
    for num, label in options:
        lines.append(f"  [bold bright_yellow]{num}.[/] {label}")
    content = "\n".join(lines)
    return Panel(content, title=f"[bold]{title}[/]", border_style="dim", padding=(0, 2))


def victory_panel(message, reward):
    """Render victory message."""
    return Panel(
        f"[bold green]🎉 Victory![/]\n{message}\n[bold bright_yellow]💰 +${reward}[/]",
        border_style="bright_green",
        padding=(1, 2),
    )


def defeat_panel(message):
    """Render defeat message."""
    return Panel(
        f"[bold red]😤 Defeat![/]\n{message}",
        border_style="red",
        padding=(1, 2),
    )


def game_over_panel(day, challengers_beaten):
    """Render the game over screen."""
    content = (
        "[bold red]💀  GAME OVER  💀[/]\n\n"
        "The Champion has fallen!\n\n"
        f"[dim]You lasted [bold]{day}[/dim] days\n"
        f"[dim]Challengers defeated: [bold]{challengers_beaten}[/dim]"
    )
    return Panel(content, border_style="bold red", padding=(1, 4))


def banner():
    """Render the game banner."""
    art = """
[bold bright_yellow]⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡[/]

[bold bright_cyan]    ██████╗  ██████╗ ██╗  ██╗███████╗███╗   ███╗ ██████╗ ███╗   ██╗[/]
[bold bright_cyan]    ██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗ ████║██╔═══██╗████╗  ██║[/]
[bold bright_cyan]    ██████╔╝██║   ██║█████╔╝ █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║[/]
[bold bright_cyan]    ██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║[/]
[bold bright_cyan]    ██║     ╚██████╔╝██║  ██╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║[/]
[bold bright_cyan]    ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝[/]

[bold bright_red]             ██╗     ███████╗ █████╗  ██████╗ ██╗   ██╗███████╗[/]
[bold bright_red]             ██║     ██╔════╝██╔══██╗██╔════╝ ██║   ██║██╔════╝[/]
[bold bright_red]             ██║     █████╗  ███████║██║  ███╗██║   ██║█████╗  [/]
[bold bright_red]             ██║     ██╔══╝  ██╔══██║██║   ██║██║   ██║██╔══╝  [/]
[bold bright_red]             ███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝███████╗[/]
[bold bright_red]             ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝[/]

[bold bright_green]       ██████╗██╗  ██╗ █████╗ ███╗   ███╗██████╗ ██╗ ██████╗ ███╗   ██╗[/]
[bold bright_green]      ██╔════╝██║  ██║██╔══██╗████╗ ████║██╔══██╗██║██╔═══██╗████╗  ██║[/]
[bold bright_green]      ██║     ███████║███████║██╔████╔██║██████╔╝██║██║   ██║██╔██╗ ██║[/]
[bold bright_green]      ██║     ██╔══██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║██║   ██║██║╚██╗██║[/]
[bold bright_green]      ╚██████╗██║  ██║██║  ██║██║ ╚═╝ ██║██║     ██║╚██████╔╝██║ ╚████║[/]
[bold bright_green]       ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝[/]

[bold bright_yellow]⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡[/]

[italic]      Defend your title. Manage your League. Stop every challenger.[/]
"""
    console.print(art)


def starter_table(options):
    """Render the starter team selection as a table."""
    table = Table(
        title="[bold]Choose Your Champion Team[/]",
        box=box.DOUBLE,
        border_style="bright_yellow",
        show_header=True,
        header_style="bold bright_yellow",
        padding=(0, 1),
    )
    table.add_column("#", width=3, justify="center", style="bold")
    table.add_column("Style", min_width=12)
    table.add_column("Team", min_width=50)

    for i, option in enumerate(options):
        team_parts = []
        for pdata in option["team"]:
            moves_str = ", ".join(pdata["moves"])
            team_parts.append(f"{pdata['species']} Lv.{pdata['level']} ({moves_str})")
        table.add_row(str(i + 1), f"[bold]{option['label']}[/]", "\n".join(team_parts))

    return table


def prompt(text, style="bold bright_cyan"):
    """Styled input prompt."""
    return console.input(f"  [{style}]{text}[/] ")


def info(text):
    console.print(f"  [bright_cyan]{text}[/]")


def warning(text):
    console.print(f"  [bold yellow]⚠ {text}[/]")


def error(text):
    console.print(f"  [bold red]✗ {text}[/]")


def success(text):
    console.print(f"  [bold green]✓ {text}[/]")
