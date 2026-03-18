"""
Pokemon League Champion - Rebuild TYPE_TIERS
Reads POKEMON_DB from data.py and rebuilds TYPE_TIERS to include
all 18 types, with Pokemon sorted by ascending total base stats.

Usage:
    python rebuild_type_tiers.py
"""
import re

DATA_FILE = "data.py"
ALL_TYPES = [
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic",
    "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy",
]


def read_data_file() -> str:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return f.read()


def write_data_file(content: str):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def parse_pokemon_db(content: str) -> dict[str, dict]:
    """Extract all Pokemon entries from POKEMON_DB."""
    m = re.search(r"^POKEMON_DB\s*=\s*\{", content, re.MULTILINE)
    if not m:
        raise ValueError("Could not find POKEMON_DB")
    # Find the closing brace
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
    # Parse each Pokemon entry
    pokemon = {}
    # Match each top-level entry: "Name": { ... },
    pattern = r'"([^"]+)":\s*\{\s*"types":\s*\[([^\]]+)\][^}]*"stats":\s*\{([^}]+)\}'
    for pm in re.finditer(pattern, section):
        name = pm.group(1)
        types = re.findall(r'"([^"]+)"', pm.group(2))
        stats = {}
        for k, v in re.findall(r'"(\w+)":\s*(\d+)', pm.group(3)):
            stats[k] = int(v)
        bst = sum(stats.values())
        pokemon[name] = {"types": types, "bst": bst}
    return pokemon


def build_type_tiers(pokemon_db: dict[str, dict]) -> dict[str, list[str]]:
    """Build TYPE_TIERS: for each type, list all Pokemon whose primary type matches, sorted by BST."""
    tiers = {}
    for ptype in ALL_TYPES:
        members = []
        for name, data in pokemon_db.items():
            if data["types"][0] == ptype:
                members.append((data["bst"], name))
        members.sort(key=lambda x: (x[0], x[1]))
        if members:
            tiers[ptype] = [name for _, name in members]
    return tiers


def format_type_tiers(tiers: dict[str, list[str]]) -> str:
    """Format TYPE_TIERS as a Python block."""
    lines = ["TYPE_TIERS = {"]
    for ptype in ALL_TYPES:
        if ptype not in tiers:
            continue
        pokemon_list = tiers[ptype]
        items = [f'"{p}"' for p in pokemon_list]
        lines.append(f'    "{ptype}": [')
        for g in range(0, len(items), 4):
            chunk = ", ".join(items[g:g + 4])
            if g + 4 < len(items):
                chunk += ","
            lines.append(f"        {chunk}")
        lines.append("    ],")
    lines.append("}")
    return "\n".join(lines)


def replace_type_tiers(content: str, new_block: str) -> str:
    """Replace the TYPE_TIERS block in data.py."""
    m = re.search(r"^TYPE_TIERS\s*=\s*\{", content, re.MULTILINE)
    if not m:
        raise ValueError("Could not find TYPE_TIERS")
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
    return content[:start] + new_block + content[end:]


def main():
    print("=" * 50)
    print("  Rebuild TYPE_TIERS")
    print("=" * 50)
    print()

    content = read_data_file()
    pokemon_db = parse_pokemon_db(content)
    print(f"Found {len(pokemon_db)} Pokemon in POKEMON_DB.\n")

    tiers = build_type_tiers(pokemon_db)
    print(f"Built tiers for {len(tiers)}/{len(ALL_TYPES)} types:\n")
    for ptype in ALL_TYPES:
        if ptype in tiers:
            names = tiers[ptype]
            bsts = []
            for n in names:
                bsts.append(f"{n}({pokemon_db[n]['bst']})")
            print(f"  {ptype:10s} ({len(names):2d}): {', '.join(bsts)}")
        else:
            print(f"  {ptype:10s} ( 0): (empty)")

    print()
    resp = input("Apply changes to data.py? [y/N] ").strip().lower()
    if resp != "y":
        print("Aborted.")
        return

    new_block = format_type_tiers(tiers)
    content = read_data_file()  # Re-read
    content = replace_type_tiers(content, new_block)
    write_data_file(content)
    print(f"\n✓ TYPE_TIERS updated in {DATA_FILE} with {len(tiers)} types.")


if __name__ == "__main__":
    main()
