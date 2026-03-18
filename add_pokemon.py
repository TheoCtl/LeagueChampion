"""
Pokemon League Champion - Bulbapedia Scraper Tool
Automatically adds new Pokemon, moves, and evolutions to data.py
by scraping Bulbapedia pages.

Usage:
    python add_pokemon.py
    Then paste a Bulbapedia URL when prompted.
"""
import random
import re
import sys
import textwrap

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_FILE = "data.py"
VALID_TYPES = [
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic",
    "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy",
]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------

def fetch_page(url: str) -> BeautifulSoup:
    """Fetch and parse a Bulbapedia Pokemon page."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_name(soup: BeautifulSoup) -> str:
    """Extract the Pokemon name from the page title."""
    title = soup.find("h1", id="firstHeading")
    if not title:
        raise ValueError("Could not find page title")
    text = title.get_text(strip=True)
    m = re.match(r"(.+?)\s*\(", text)
    return m.group(1) if m else text


def parse_types(soup: BeautifulSoup) -> list[str]:
    """Extract base-form types from the infobox."""
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        raise ValueError("Could not find infobox")
    for b_tag in infobox.find_all("b"):
        if b_tag.get_text(strip=True) in ("Type", "Types"):
            type_cell = b_tag.find_parent("td")
            if not type_cell:
                continue
            # Each form has its own inner table; take the first one
            for tbl in type_cell.find_all("table"):
                own_links = []
                for a in tbl.find_all("a", href=lambda h: h and "_(type)" in h):
                    if a.find_parent("table") == tbl:
                        t = a.get_text(strip=True)
                        if t in VALID_TYPES:
                            own_links.append(t)
                if own_links:
                    return own_links
    raise ValueError("Could not parse types")


def parse_abilities(soup: BeautifulSoup, known_abilities: set[str]) -> list[str]:
    """Extract abilities from the infobox, filtered to known game abilities."""
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        return []
    for b_tag in infobox.find_all("b"):
        if b_tag.get_text(strip=True) in ("Abilities", "Ability"):
            parent_td = b_tag.find_parent("td")
            if not parent_td:
                continue
            links = parent_td.find_all(
                "a", href=lambda h: h and "_(Ability)" in h
            )
            raw = [a.get_text(strip=True) for a in links]
            # Filter out Cacophony (form separator) and keep only known abilities
            filtered = []
            for ab in raw:
                if ab == "Cacophony" or ab == "Hidden Ability":
                    continue
                if ab in known_abilities and ab not in filtered:
                    filtered.append(ab)
            return filtered
    return []


def parse_base_stats(soup: BeautifulSoup) -> dict:
    """Extract base stats from the Base stats table."""
    heading = soup.find("span", id="Base_stats")
    if not heading:
        raise ValueError("Could not find Base stats section")
    tbl = heading.parent.find_next("table")
    if not tbl:
        raise ValueError("Could not find base stats table")
    stat_map = {
        "HP": "hp", "Attack": "atk", "Defense": "def",
        "Sp. Atk": "spa", "Sp. Def": "spd", "Speed": "spe",
    }
    stats = {}
    for row in tbl.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        label_text = cells[0].get_text(strip=True)
        for full_name, key in stat_map.items():
            if label_text.startswith(full_name + ":"):
                # e.g. "HP:39" or "Attack:52"
                val_str = label_text.split(":")[-1]
                try:
                    stats[key] = int(val_str)
                except ValueError:
                    pass
    if len(stats) != 6:
        raise ValueError(f"Expected 6 stats, got {len(stats)}: {stats}")
    return stats


def _extract_cell_value(cell) -> str:
    """Get the visible text from a cell, stripping hidden sort-key spans."""
    for span in cell.find_all("span", style=lambda s: s and "display:none" in s.replace(" ", "")):
        span.decompose()
    return cell.get_text(strip=True)


def parse_learnset(soup: BeautifulSoup) -> list[dict]:
    """Parse the 'By leveling up' learnset table (Gen IX / latest).
    Handles both old format (Level|Move|Type|Cat|Pwr|Acc|PP)
    and new format (Learn|Plus|Move|Type|Cat|Power|CD).
    """
    heading = soup.find("span", id="By_leveling_up")
    if not heading:
        return []
    # Find the first sortable table after the heading
    tables = heading.parent.find_all_next("table", class_="sortable")
    if not tables:
        return []
    tbl = tables[0]
    rows = tbl.find_all("tr")
    if not rows:
        return []

    # Detect table format from header row
    header_cells = rows[0].find_all(["td", "th"])
    header_texts = [c.get_text(strip=True).lower() for c in header_cells]

    # Determine column indices based on headers
    if "move" in header_texts:
        move_idx = header_texts.index("move")
    elif "move" in [h.split()[0] if h else "" for h in header_texts]:
        move_idx = 1  # fallback
    else:
        move_idx = 1

    type_idx = move_idx + 1
    cat_idx = move_idx + 2
    power_idx = move_idx + 3

    # Check if there's an accuracy column (old format has Acc., new has CD)
    has_accuracy = any("acc" in h for h in header_texts)
    if has_accuracy:
        acc_idx = power_idx + 1
    else:
        acc_idx = None

    moves = []
    for row in rows[1:]:  # skip header
        cells = row.find_all(["td", "th"])
        if len(cells) <= power_idx:
            continue
        move_name = _extract_cell_value(cells[move_idx])
        move_type = _extract_cell_value(cells[type_idx])
        category = _extract_cell_value(cells[cat_idx]).lower()
        power_str = _extract_cell_value(cells[power_idx]).replace("—", "0").replace("%", "")
        if acc_idx is not None and acc_idx < len(cells):
            acc_str = _extract_cell_value(cells[acc_idx]).replace("%", "").replace("—", "0")
        else:
            acc_str = "100"
        try:
            power = int(power_str)
        except ValueError:
            power = 0
        try:
            accuracy = int(acc_str)
        except ValueError:
            accuracy = 100
        if move_type not in VALID_TYPES:
            continue
        moves.append({
            "name": move_name,
            "type": move_type,
            "category": category,
            "power": power,
            "accuracy": accuracy,
            "pp": 20,
        })
    return moves


def parse_evolution_chain(soup: BeautifulSoup, current_name: str = "") -> list[str]:
    """Extract the evolution chain from the Evolution data section.
    Returns a list of (stage, name) tuples, e.g. [(0,'Charmander'), (1,'Charmeleon'), (2,'Charizard')].
    Branching evolutions produce multiple entries at the same stage.
    """
    heading = soup.find("span", id="Evolution_data")
    if not heading:
        return []
    tbl = heading.parent.find_next("table")
    if not tbl:
        return []
    # Inner tables contain the form names (Unevolved, First Evolution, etc.)
    # Labels like "Unevolved", "First Evolution", "Second Evolution" give order.
    stage_order = {"Unevolved": 0, "First Evolution": 1, "Second Evolution": 2,
                   "Third Evolution": 3}
    stages: list[tuple[int, str]] = []
    for inner_tbl in tbl.find_all("table"):
        text = inner_tbl.get_text(strip=True)
        if len(text) > 200:
            continue
        # Determine stage from text labels
        stage_num = -1
        for label, num in stage_order.items():
            if label in text:
                stage_num = num
                break
        if stage_num < 0:
            continue
        # Find the Pokemon name (link or text) in this inner table
        # First try links
        found = False
        for a in inner_tbl.find_all("a", href=lambda h: h and "(Pok" in h):
            name = a.get_text(strip=True)
            if name:
                stages.append((stage_num, name))
                found = True
                break
        # If no link found (current pokemon on its own page), use current_name
        if not found and current_name and current_name.lower() in text.lower():
            stages.append((stage_num, current_name))
    # Sort by stage
    stages.sort(key=lambda x: x[0])
    return stages


# ---------------------------------------------------------------------------
# Data file manipulation
# ---------------------------------------------------------------------------

def read_data_file() -> str:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return f.read()


def write_data_file(content: str):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def get_existing_pokemon(content: str) -> set[str]:
    """Extract existing Pokemon names from POKEMON_DB."""
    return set(re.findall(r'^\s+"([^"]+)":\s*\{', content, re.MULTILINE))


def extract_existing_pokemon_data(content: str, name: str) -> dict | None:
    """Extract an existing Pokemon's data from POKEMON_DB for comparison.
    Returns a dict with types, stats, abilities, move_tiers or None."""
    # Match the Pokemon entry block
    pattern = rf'"\s*{re.escape(name)}"\s*:\s*\{{'
    m = re.search(pattern, content)
    if not m:
        return None
    # Find the matching closing brace for this entry
    start = m.start()
    brace_depth = 0
    end = start
    for i in range(m.end() - 1, len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                end = i + 1
                break
    block = content[m.end():end]
    # Parse types
    types_m = re.search(r'"types":\s*\[([^\]]+)\]', block)
    types = re.findall(r'"([^"]+)"', types_m.group(1)) if types_m else []
    # Parse stats
    stats_m = re.search(r'"stats":\s*\{([^}]+)\}', block)
    stats = {}
    if stats_m:
        for k, v in re.findall(r'"(\w+)":\s*(\d+)', stats_m.group(1)):
            stats[k] = int(v)
    # Parse abilities
    abil_m = re.search(r'"abilities":\s*\[([^\]]+)\]', block)
    abilities = re.findall(r'"([^"]+)"', abil_m.group(1)) if abil_m else []
    # Parse move_tiers
    mt_m = re.search(r'"move_tiers":\s*\{(.+)\}', block, re.DOTALL)
    move_tiers = {}
    if mt_m:
        for type_match in re.finditer(r'"(\w+)":\s*\[([^\]]+)\]', mt_m.group(1)):
            move_tiers[type_match.group(1)] = re.findall(r'"([^"]+)"', type_match.group(2))
    return {"types": types, "stats": stats, "abilities": abilities, "move_tiers": move_tiers}


def replace_pokemon_entry(content: str, name: str, new_entry: str) -> str:
    """Replace an existing Pokemon entry in POKEMON_DB with a new one."""
    pattern = rf'^(\s*)"\s*{re.escape(name)}"\s*:\s*\{{'
    m = re.search(pattern, content, re.MULTILINE)
    if not m:
        raise ValueError(f"Could not find {name} in POKEMON_DB")
    # Find the full entry: from the start of the line to the closing '},'
    line_start = content.rfind("\n", 0, m.start()) + 1
    brace_depth = 0
    end = m.end()
    for i in range(m.end() - 1, len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                end = i + 1
                break
    # Include trailing comma if present
    if end < len(content) and content[end] == ",":
        end += 1
    return content[:line_start] + new_entry + "\n" + content[end:].lstrip("\n")


def get_existing_moves(content: str) -> set[str]:
    """Extract existing move names from MOVES_DB."""
    # Find the MOVES_DB section
    m = re.search(r"^MOVES_DB\s*=\s*\{", content, re.MULTILINE)
    if not m:
        return set()
    start = m.start()
    # Find the closing brace
    brace_depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                end = i + 1
                break
    section = content[start:end]
    return set(re.findall(r'^\s+"([^"]+)":\s*\{', section, re.MULTILINE))


def get_known_abilities(content: str) -> set[str]:
    """Extract ability names from the ABILITIES dict."""
    m = re.search(r"^ABILITIES\s*=\s*\{", content, re.MULTILINE)
    if not m:
        return set()
    start = m.start()
    brace_depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                end = i + 1
                break
    section = content[start:end]
    return set(re.findall(r'^\s+"([^"]+)":', section, re.MULTILINE))


def get_type_tiers(content: str) -> dict[str, list[str]]:
    """Parse existing TYPE_TIERS from data.py."""
    m = re.search(r"^TYPE_TIERS\s*=\s*\{", content, re.MULTILINE)
    if not m:
        return {}
    start = m.start()
    brace_depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                end = i + 1
                break
    section = content[start:end]
    # Use a safe eval approach
    tiers = {}
    for match in re.finditer(r'"(\w+)":\s*\[([^\]]+)\]', section):
        type_name = match.group(1)
        pokemon_list = re.findall(r'"([^"]+)"', match.group(2))
        tiers[type_name] = pokemon_list
    return tiers


def build_move_tiers(learnset: list[dict]) -> dict[str, list[str]]:
    """Group moves by type, sorted by power ascending within each type.
    Only includes damaging moves (power > 0).
    """
    by_type: dict[str, list[dict]] = {}
    for move in learnset:
        if move["power"] > 0:
            by_type.setdefault(move["type"], []).append(move)
    result = {}
    for t, moves in by_type.items():
        # Sort by power ascending, deduplicate by name
        moves.sort(key=lambda m: m["power"])
        seen_names: set[str] = set()
        unique: list[dict] = []
        for m in moves:
            if m["name"] not in seen_names:
                seen_names.add(m["name"])
                unique.append(m)
        # Remove duplicates where multiple moves share the same power,
        # keeping one random move per power value
        by_power: dict[int, list[dict]] = {}
        for m in unique:
            by_power.setdefault(m["power"], []).append(m)
        final: list[dict] = []
        for pwr, group in by_power.items():
            if len(group) > 1:
                final.append(random.choice(group))
            else:
                final.append(group[0])
        final.sort(key=lambda m: m["power"])
        result[t] = [m["name"] for m in final]
    return result


def format_move_tiers(tiers: dict[str, list[str]]) -> str:
    """Format move_tiers dict as a Python literal."""
    parts = []
    for t, names in tiers.items():
        quoted = ", ".join(f'"{n}"' for n in names)
        parts.append(f'"{t}": [{quoted}]')
    return "{" + ", ".join(parts) + "}"


def format_pokemon_entry(name: str, types: list[str], stats: dict,
                         abilities: list[str], move_tiers: dict) -> str:
    """Format a POKEMON_DB entry."""
    types_str = "[" + ", ".join(f'"{t}"' for t in types) + "]"
    stats_order = ["hp", "atk", "def", "spa", "spd", "spe"]
    stats_str = "{" + ", ".join(f'"{k}": {stats[k]}' for k in stats_order) + "}"
    abilities_str = "[" + ", ".join(f'"{a}"' for a in abilities) + "]"
    tiers_str = format_move_tiers(move_tiers)
    return (
        f'    "{name}": {{\n'
        f'        "types": {types_str},\n'
        f'        "stats": {stats_str},\n'
        f'        "abilities": {abilities_str},\n'
        f'        "move_tiers": {tiers_str},\n'
        f'    }},'
    )


def format_move_entry(name: str, move: dict) -> str:
    """Format a basic MOVES_DB entry for a new move."""
    cat = move["category"]
    mtype = move["type"]
    power = move["power"]
    acc = move["accuracy"]
    return f'    "{name}": {{"type": "{mtype}", "category": "{cat}", "power": {power}, "accuracy": {acc}}},'


def find_insertion_point_pokemon(content: str, name: str, types: list[str]) -> int:
    """Find where to insert a new Pokemon in POKEMON_DB.
    Tries to insert near Pokemon of the same primary type."""
    primary = types[0]
    # Find the type section comment
    pattern = rf'# [═]+ {primary} [═]+'
    m = re.search(pattern, content)
    if m:
        # Find the last entry in this type section (before next section comment or end of dict)
        section_start = m.end()
        next_section = re.search(r'# [═]+', content[section_start:])
        if next_section:
            section_end = section_start + next_section.start()
        else:
            # Find the closing brace of POKEMON_DB
            db_match = re.search(r"^POKEMON_DB\s*=\s*\{", content, re.MULTILINE)
            if db_match:
                brace_depth = 0
                for i in range(db_match.start(), len(content)):
                    if content[i] == "{":
                        brace_depth += 1
                    elif content[i] == "}":
                        brace_depth -= 1
                        if brace_depth == 0:
                            section_end = i
                            break
            else:
                section_end = len(content)
        # Find the last '},' in this section
        last_entry = content[:section_end].rfind("},")
        if last_entry > section_start:
            return last_entry + 2  # After '},'
    # Fallback: insert before the closing brace of POKEMON_DB
    db_match = re.search(r"^POKEMON_DB\s*=\s*\{", content, re.MULTILINE)
    if db_match:
        brace_depth = 0
        for i in range(db_match.start(), len(content)):
            if content[i] == "{":
                brace_depth += 1
            elif content[i] == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    return i
    raise ValueError("Could not find POKEMON_DB insertion point")


def insert_pokemon(content: str, name: str, entry: str, types: list[str]) -> str:
    """Insert a new Pokemon entry into POKEMON_DB."""
    pos = find_insertion_point_pokemon(content, name, types)
    return content[:pos] + "\n" + entry + "\n" + content[pos:]


def insert_move(content: str, name: str, move: dict) -> str:
    """Insert a new move entry into MOVES_DB."""
    entry = format_move_entry(name, move)
    # Find MOVES_DB closing brace
    m = re.search(r"^MOVES_DB\s*=\s*\{", content, re.MULTILINE)
    if not m:
        raise ValueError("Could not find MOVES_DB")
    brace_depth = 0
    closing = m.start()
    for i in range(m.start(), len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                closing = i
                break
    # Insert before the closing brace
    return content[:closing] + "    # ── Auto-added ──\n" + entry + "\n" + content[closing:]


def insert_evolves_from(content: str, species: str, pre_evo: str) -> str:
    """Add an EVOLVES_FROM entry."""
    m = re.search(r"^EVOLVES_FROM\s*=\s*\{", content, re.MULTILINE)
    if not m:
        return content
    brace_depth = 0
    closing = m.start()
    for i in range(m.start(), len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                closing = i
                break
    entry = f'    "{species}": "{pre_evo}",\n'
    return content[:closing] + entry + content[closing:]


def determine_tier_position(stats: dict, type_tiers_list: list[str],
                            all_pokemon_data: str) -> int:
    """Determine insertion position in TYPE_TIERS based on BST.
    Returns the index where this Pokemon should be inserted."""
    bst = sum(stats.values())
    # Extract BSTs for existing Pokemon in this tier
    positions = []
    for i, poke in enumerate(type_tiers_list):
        # Find this pokemon's stats in content
        m = re.search(rf'"{re.escape(poke)}":\s*\{{[^}}]*?"stats":\s*\{{([^}}]+)\}}', all_pokemon_data)
        if m:
            stat_vals = re.findall(r':\s*(\d+)', m.group(1))
            existing_bst = sum(int(v) for v in stat_vals)
            positions.append((i, existing_bst))
    # Find where to insert (sorted by BST ascending)
    insert_idx = len(type_tiers_list)
    for i, (idx, existing_bst) in enumerate(positions):
        if bst <= existing_bst:
            insert_idx = idx
            break
    return insert_idx


def update_type_tiers(content: str, name: str, types: list[str], stats: dict) -> str:
    """Add Pokemon to TYPE_TIERS under its primary (first) type only."""
    tiers = get_type_tiers(content)
    modified = False
    primary = types[0]
    for ptype in [primary]:
        if ptype in tiers and name not in tiers[ptype]:
            pos = determine_tier_position(stats, tiers[ptype], content)
            tiers[ptype].insert(pos, name)
            modified = True
    if not modified:
        return content
    # Rebuild the TYPE_TIERS block
    m = re.search(r"^TYPE_TIERS\s*=\s*\{", content, re.MULTILINE)
    if not m:
        return content
    start = m.start()
    brace_depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == "{":
            brace_depth += 1
        elif content[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                end = i + 1
                break
    # Build new TYPE_TIERS
    lines = ["TYPE_TIERS = {"]
    for type_name, pokemon_list in tiers.items():
        quoted = ", ".join(f'"{p}"' for p in pokemon_list)
        lines.append(f'    "{type_name}": [')
        # Wrap the list nicely
        items = [f'"{p}"' for p in pokemon_list]
        # Groups of 4
        for g in range(0, len(items), 4):
            chunk = ", ".join(items[g:g+4])
            if g + 4 < len(items):
                chunk += ","
            lines.append(f"        {chunk}")
        lines.append("    ],")
    lines.append("}")
    new_block = "\n".join(lines)
    return content[:start] + new_block + content[end:]


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

def process_pokemon(url: str):
    """Main processing pipeline for a Bulbapedia Pokemon URL."""
    print(f"\nFetching {url} ...")
    soup = fetch_page(url)
    content = read_data_file()
    existing_pokemon = get_existing_pokemon(content)
    existing_moves = get_existing_moves(content)
    known_abilities = get_known_abilities(content)

    # ── Parse page ──
    name = parse_name(soup)
    types = parse_types(soup)
    stats = parse_base_stats(soup)
    abilities = parse_abilities(soup, known_abilities)
    learnset = parse_learnset(soup)
    evo_chain = parse_evolution_chain(soup, name)
    # Build display-friendly chain names (deduplicated, ordered)
    evo_names = []
    for _, n in evo_chain:
        if n not in evo_names:
            evo_names.append(n)

    bst = sum(stats.values())
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"  Types:     {', '.join(types)}")
    print(f"  Stats:     {stats}  (BST: {bst})")
    print(f"  Abilities: {', '.join(abilities) if abilities else '(none matched game abilities)'}")
    print(f"  Learnset:  {len(learnset)} moves by leveling up")
    print(f"  Evo chain: {' → '.join(evo_names) if evo_names else '(none)'}")
    print(f"{'='*50}")

    # ── Ability fallback (needed before comparison) ──
    if not abilities:
        print("\n⚠  No matching abilities found in game. Using first type's generic ability.")
        type_defaults = {
            "Fire": "Blaze", "Water": "Torrent", "Grass": "Overgrow",
            "Electric": "Static", "Ice": "Ice Body", "Fighting": "Guts",
            "Poison": "Immunity", "Ground": "Sand Veil", "Flying": "Levitate",
            "Psychic": "Insomnia", "Bug": "Swarm", "Rock": "Sturdy",
            "Ghost": "Levitate", "Dragon": "Intimidate", "Dark": "Intimidate",
            "Steel": "Sturdy", "Fairy": "Natural Cure", "Normal": "Adaptability",
        }
        default = type_defaults.get(types[0])
        if default and default in known_abilities:
            abilities = [default]
            print(f"   Using default: {default}")
        else:
            abilities = [list(known_abilities)[0]]

    # ── Build move tiers ──
    move_tiers = build_move_tiers(learnset)
    if not move_tiers:
        print("\n⚠  No damaging moves found in learnset!")
    else:
        print(f"\nMove tiers (by type, sorted by power):")
        for t, names in move_tiers.items():
            print(f"  {t:10s}: {', '.join(names)}")

    # ── Duplicate check ──
    is_update = name in existing_pokemon
    if is_update:
        old_data = extract_existing_pokemon_data(content, name)
        new_data = {"types": types, "stats": stats, "abilities": abilities, "move_tiers": move_tiers}
        if old_data == new_data:
            print(f"\n✓  {name} already exists with identical values. No Pokemon update needed.")
        else:
            print(f"\n⚠  {name} already exists but with different values. Changes:")
            if old_data:
                for key in ("types", "stats", "abilities", "move_tiers"):
                    old_val = old_data.get(key)
                    new_val = new_data.get(key)
                    if old_val != new_val:
                        print(f"   {key}: {old_val} → {new_val}")
            print("   The entry will be updated with the new values.")

    # ── Check for missing moves ──
    new_moves = []
    for move in learnset:
        if move["name"] not in existing_moves and move["power"] > 0:
            new_moves.append(move)
    if new_moves:
        print(f"\nNew moves to add ({len(new_moves)}):")
        for m in new_moves:
            print(f"  {m['name']:20s} {m['type']:10s} {m['category']:10s} pwr={m['power']:3d} acc={m['accuracy']:3d}")

    # ── Confirm ──
    print()
    resp = input("Proceed with adding to data.py? [y/N] ").strip().lower()
    if resp != "y":
        print("Aborted.")
        return

    # ── Apply changes ──
    content = read_data_file()  # Re-read in case of external changes
    changes = []

    # 1. Add new moves
    for m in new_moves:
        if m["name"] not in get_existing_moves(content):
            content = insert_move(content, m["name"], m)
            changes.append(f"Added move: {m['name']}")

    # 2. Add or update Pokemon entry
    entry = format_pokemon_entry(name, types, stats, abilities, move_tiers)
    if is_update:
        old_data = extract_existing_pokemon_data(content, name)
        new_data = {"types": types, "stats": stats, "abilities": abilities, "move_tiers": move_tiers}
        if old_data != new_data:
            content = replace_pokemon_entry(content, name, entry)
            changes.append(f"Updated Pokemon: {name}")
    else:
        content = insert_pokemon(content, name, entry, types)
        changes.append(f"Added Pokemon: {name}")

    # 3. Add evolution entries (stage-aware: each Pokemon evolves from the nearest lower-stage Pokemon)
    if len(evo_chain) >= 2:
        # Group by stage
        by_stage: dict[int, list[str]] = {}
        for stage, evo_name in evo_chain:
            by_stage.setdefault(stage, []).append(evo_name)
        sorted_stages = sorted(by_stage.keys())
        for s_idx in range(1, len(sorted_stages)):
            current_stage = sorted_stages[s_idx]
            prev_stage = sorted_stages[s_idx - 1]
            # Each Pokemon at current_stage evolves from the first Pokemon at prev_stage
            pre_evo = by_stage[prev_stage][0]
            for evolved in by_stage[current_stage]:
                check = f'"{evolved}": "{pre_evo}"'
                if check not in content:
                    content = insert_evolves_from(content, evolved, pre_evo)
                    changes.append(f"Added evolution: {pre_evo} → {evolved}")

    # 4. Update TYPE_TIERS (primary type only)
    content = update_type_tiers(content, name, types, stats)
    # Check if it was actually added
    new_tiers = get_type_tiers(content)
    primary = types[0]
    for ptype in [primary]:
        if ptype in new_tiers and name in new_tiers[ptype]:
            pos = new_tiers[ptype].index(name)
            changes.append(f"Added to TYPE_TIERS[{ptype}] at position {pos}")

    # ── Write ──
    write_data_file(content)
    print(f"\n✓ Changes applied to {DATA_FILE}:")
    for c in changes:
        print(f"  • {c}")
    print()


def main():
    print("=" * 50)
    print("  Pokemon League Champion - Add Pokemon Tool")
    print("=" * 50)
    print()
    print("Paste a Bulbapedia Pokemon URL (e.g.:")
    print("  https://bulbapedia.bulbagarden.net/wiki/Pikachu_(Pokémon)")
    print()

    while True:
        url = input("URL (or 'quit'): ").strip()
        if url.lower() in ("quit", "q", "exit"):
            break
        if not url.startswith("https://bulbapedia.bulbagarden.net/wiki/"):
            print("Invalid URL. Must be a Bulbapedia Pokemon page URL.")
            continue
        try:
            process_pokemon(url)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
        print()


if __name__ == "__main__":
    main()
