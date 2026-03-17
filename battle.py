"""
Pokemon League Champion - Battle System (Rich UI)
Turn-based combat between two trainers.
"""
import random
from data import MOVES_DB, get_type_multiplier
from ui import (
    console, battle_field_panel, move_table, battle_message,
    effectiveness_message, damage_message, faint_message,
    switch_table, prompt, info,
)


def calc_damage(attacker, defender, move_data):
    """Calculate damage using a simplified Pokemon damage formula."""
    level = attacker.level
    power = move_data["power"]

    if move_data["category"] == "physical":
        atk_stat = attacker.atk
        def_stat = defender.defense
    else:
        atk_stat = attacker.spa
        def_stat = defender.spd

    base = ((2 * level / 5 + 2) * power * atk_stat / def_stat) / 50 + 2
    type_mult = get_type_multiplier(move_data["type"], defender.types)
    stab = 1.5 if move_data["type"] in attacker.types else 1.0
    rand_factor = random.randint(85, 100) / 100.0
    damage = int(base * type_mult * stab * rand_factor)
    return max(1, damage), type_mult


def ai_choose_move(pokemon, opponent):
    """Simple AI: pick the move that would deal the most expected damage."""
    best_move = None
    best_score = -1

    for move_name in pokemon.moves:
        move_data = pokemon.get_move_data(move_name)
        if not move_data:
            continue
        level = pokemon.level
        power = move_data["power"]
        if move_data["category"] == "physical":
            atk_stat = pokemon.atk
            def_stat = opponent.defense
        else:
            atk_stat = pokemon.spa
            def_stat = opponent.spd

        base = ((2 * level / 5 + 2) * power * atk_stat / def_stat) / 50 + 2
        type_mult = get_type_multiplier(move_data["type"], opponent.types)
        stab = 1.5 if move_data["type"] in pokemon.types else 1.0
        score = base * type_mult * stab * (move_data["accuracy"] / 100.0)

        if score > best_score:
            best_score = score
            best_move = move_name

    return best_move if best_move else pokemon.moves[0]


def execute_move(attacker, defender, move_name):
    """Execute a move and print results with Rich formatting."""
    move_data = attacker.get_move_data(move_name)
    if not move_data:
        battle_message(f"{attacker.species} tried to use {move_name}, but it failed!", "dim")
        return

    battle_message(f"[bold]{attacker.species}[/] used [bold bright_yellow]{move_name}[/]!")

    # Accuracy check
    if random.randint(1, 100) > move_data["accuracy"]:
        battle_message("It missed!", "dim italic")
        return

    damage, type_mult = calc_damage(attacker, defender, move_data)

    if type_mult == 0:
        eff = effectiveness_message(type_mult)
        if eff:
            console.print(f"  {eff}")
        return

    eff = effectiveness_message(type_mult)
    if eff:
        console.print(f"  {eff}")

    defender.current_hp -= damage
    if defender.current_hp < 0:
        defender.current_hp = 0

    console.print(damage_message(defender, damage))

    if defender.is_fainted():
        console.print(faint_message(defender))


def run_battle(player_trainer, enemy_trainer, player_controlled=True):
    """
    Run a full battle between two trainers.
    Returns (winner_is_player: bool, battle_log: list[str])
    """
    from rich.panel import Panel

    log = []

    title = f"⚔️  {player_trainer.display_name()}  vs  {enemy_trainer.display_name()}  ⚔️"
    console.print(Panel(f"[bold]{title}[/]", border_style="bright_red", padding=(0, 2)))

    player_poke = player_trainer.first_available()
    enemy_poke = enemy_trainer.first_available()

    if not player_poke or not enemy_poke:
        battle_message("One side has no Pokemon!", "bold red")
        return player_poke is not None, log

    info(f"{player_trainer.name} sends out [bold]{player_poke.species}[/]!")
    info(f"{enemy_trainer.name} sends out [bold]{enemy_poke.species}[/]!")

    while player_trainer.has_pokemon_left() and enemy_trainer.has_pokemon_left():
        # Display battle field
        console.print()
        console.print(battle_field_panel(player_poke, enemy_poke))

        # Player picks move
        if player_controlled:
            console.print(move_table(player_poke))

            while True:
                try:
                    choice = prompt("Choose move (number):").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(player_poke.moves):
                        player_move = player_poke.moves[idx]
                        break
                except (ValueError, IndexError):
                    pass
                console.print("  [dim]Invalid choice, try again.[/]")
        else:
            player_move = ai_choose_move(player_poke, enemy_poke)

        enemy_move = ai_choose_move(enemy_poke, player_poke)

        # Determine turn order by speed
        if player_poke.spe >= enemy_poke.spe:
            first = (player_poke, enemy_poke, player_move, "player")
            second = (enemy_poke, player_poke, enemy_move, "enemy")
        else:
            first = (enemy_poke, player_poke, enemy_move, "enemy")
            second = (player_poke, enemy_poke, player_move, "player")

        console.print()
        for atk, dfn, move, side in [first, second]:
            if atk.is_fainted():
                continue
            execute_move(atk, dfn, move)

            if dfn.is_fainted():
                if side == "player":
                    # Enemy's pokemon fainted
                    enemy_poke = enemy_trainer.first_available()
                    if enemy_poke:
                        console.print()
                        info(f"{enemy_trainer.name} sends out [bold]{enemy_poke.species}[/]!")
                else:
                    # Player's pokemon fainted
                    player_poke = player_trainer.first_available()
                    if player_poke:
                        if player_controlled:
                            available = [(i, p) for i, p in enumerate(player_trainer.team) if not p.is_fainted()]
                            if len(available) == 1:
                                player_poke = available[0][1]
                            else:
                                console.print()
                                console.print(switch_table(available))
                                while True:
                                    try:
                                        pick = int(prompt("Send out (number):").strip()) - 1
                                        if 0 <= pick < len(available):
                                            player_poke = available[pick][1]
                                            break
                                    except (ValueError, IndexError):
                                        pass
                                    console.print("  [dim]Invalid choice.[/]")
                        else:
                            player_poke = player_trainer.first_available()
                        console.print()
                        info(f"{player_trainer.name} sends out [bold]{player_poke.species}[/]!")

    player_won = player_trainer.has_pokemon_left()

    if player_won:
        console.print(Panel(
            f"[bold green]🎉 {player_trainer.display_name()} wins![/]",
            border_style="bright_green", padding=(0, 2),
        ))
    else:
        console.print(Panel(
            f"[bold red]{enemy_trainer.display_name()} wins![/]",
            border_style="red", padding=(0, 2),
        ))

    return player_won, log
