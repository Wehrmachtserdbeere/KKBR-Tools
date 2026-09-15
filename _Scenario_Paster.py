import json
from pathlib import Path
import pyperclip


# ----------------------------------------
# Configuration
# ----------------------------------------

SCENARIOS_FOLDER = Path("Scenarios")


# ----------------------------------------
# Windows clipboard functions
# ----------------------------------------


def copy_to_clipboard(text):

    import pyperclip

    pyperclip.copy(text)


# ----------------------------------------
# Find JSON files
# ----------------------------------------

if not SCENARIOS_FOLDER.exists():

    print()
    print("The Scenarios folder does not exist.")
    print(f"Expected folder: {SCENARIOS_FOLDER}")
    print()

    raise SystemExit


json_files = sorted(
    SCENARIOS_FOLDER.glob("*.json")
)


if not json_files:

    print()
    print("No Scenario JSON files were found.")
    print(f"Expected folder: {SCENARIOS_FOLDER}")
    print()

    raise SystemExit


# ----------------------------------------
# Choose Scenario
# ----------------------------------------

print()
print("KKBR Clipboard Assistant")
print("========================")
print()

for i, json_file in enumerate(json_files, start=1):

    print(
        f"{i}. {json_file.stem}"
    )


print()

while True:

    choice = input(
        "Select a Scenario: "
    ).strip()

    try:
        choice = int(choice)

    except ValueError:
        print("Please enter a number.")
        continue

    if 1 <= choice <= len(json_files):
        break

    print("That number is not in the list.")


selected_file = json_files[choice - 1]


# ----------------------------------------
# Load Scenario
# ----------------------------------------

with selected_file.open(
    "r",
    encoding="utf-8"
) as file:

    scenario = json.load(file)


scenario_name = scenario.get(
    "name",
    selected_file.stem
)


print()
print(f"Loaded: {scenario_name}")
print()


# ----------------------------------------
# Build paste queue
# ----------------------------------------

paste_queue = []

# --------------------------------------------------
# SCENARIO
# --------------------------------------------------

scenario_fields = [
    ("Name", scenario.get("name")),
    ("Tagline", scenario.get("tagline")),
    ("Description", scenario.get("description")),
]

for field_name, content in scenario_fields:
    if content is None:
        continue

    paste_queue.append({
        "category": "SCENARIO",
        "field": field_name,
        "html": content
    })


# --------------------------------------------------
# ACTOR
# --------------------------------------------------

actor = scenario.get("actor", {})

actor_fields = [
    ("Name", actor.get("name")),
    ("Persona", actor.get("Persona")),
    ("Somatics", actor.get("Somatics")),
    ("Emotions", actor.get("Emotions")),
    ("Physical", actor.get("Physical")),
]

for field_name, content in actor_fields:
    if content is None:
        continue

    paste_queue.append({
        "category": "ACTOR",
        "field": field_name,
        "html": content
    })


# --------------------------------------------------
# INTERACTIONS
# --------------------------------------------------

interactions = scenario.get("interactions", [])

for interaction in interactions:
    number = interaction.get("number")
    properties = interaction.get("properties", {})

    # "subtitle" in the JSON corresponds to "Title" on KKBR.
    subtitle = interaction.get("subtitle")

    if subtitle:
        paste_queue.append({
            "category": "INTERACTION",
            "number": number,
            "field": "Title",
            "html": subtitle
        })

    interaction_fields = [
        ("Message", "message"),
        ("Clothing", "clothing"),
        ("Environment", "environment"),
        ("Emotion", "emotion"),
        ("Plan", "plan"),
    ]

    for display_name, json_name in interaction_fields:
        content = properties.get(json_name)

        if content is None:
            continue

        paste_queue.append({
            "category": "INTERACTION",
            "number": number,
            "field": display_name,
            "html": content
        })


# --------------------------------------------------
# PASTE LOOP
# --------------------------------------------------

print()
print("=" * 70)
print("READY TO PASTE")
print("=" * 70)
print()

for item in paste_queue:

    category = item["category"]
    field = item["field"]
    html = item["html"]

    if category == "SCENARIO":

        print(
            f'Field "{field}" copied, please paste it into '
            f'the "{field}" field.'
        )

    elif category == "ACTOR":

        print(
            f'ACTOR Field "{field}" copied, please '
            f'create a new Actor or edit an existing actor '
            f'and paste it into the "{field}" field.'
        )

    elif category == "INTERACTION":

        number = item["number"]

        print(
            f'INTERACTION - {number} - Field "{field}" copied, '
            f'please paste it into the "{field}" field.'
        )

    copy_to_clipboard(html)

    print()
    print('Press "Enter" to continue to the next property.')
    print('Press "Q" to quit early.')
    print()

    command = input("> ").strip().lower()

    if command == "q":
        print()
        print("Pasting stopped.")
        break

else:
    print()
    print("=" * 70)
    print("All properties have been copied.")
    print("=" * 70)