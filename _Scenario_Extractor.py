from playwright.sync_api import sync_playwright, TimeoutError
import json
import re
from pathlib import Path
from urllib.parse import urlparse


LINKS_FILE = Path("_Links.txt")


# ----------------------------------------
# Create _Links.txt if it doesn't exist
# ----------------------------------------

if not LINKS_FILE.exists():

    LINKS_FILE.touch()

    print()
    print("_Links.txt did not exist, so it has been created.")
    print("Put your KKBR Scenario links into the file,")
    print("one link per line, then run the extractor again.")
    print()

    raise SystemExit


# ----------------------------------------
# Read links
# ----------------------------------------

valid_urls = []
prelinked_urls = []
unrecognized_urls = []
skipped_lines = []


with LINKS_FILE.open(
    "r",
    encoding="utf-8"
) as file:

    for line_number, line in enumerate(file, start=1):

        URL = line.strip()


        # Empty lines
        if not URL:
            continue


        # Comments
        if URL.startswith("#"):
            skipped_lines.append(URL)
            continue


        # ------------------------------------
        # Check URL format
        # ------------------------------------

        try:
            parsed = urlparse(URL)

        except ValueError:
            unrecognized_urls.append(URL)
            continue


        # ------------------------------------
        # Check protocol
        # ------------------------------------

        if parsed.scheme != "https":
            unrecognized_urls.append(URL)
            continue


        # ------------------------------------
        # Check hostname
        # ------------------------------------

        hostname = parsed.hostname

        if hostname == "kkbr.ai":

            # Regular KKBR URL
            valid_urls.append(URL)

        elif hostname and hostname.endswith(".kkbr.ai"):

            # Alternate / development KKBR host
            prelinked_urls.append(URL)

        else:

            # Not a recognized KKBR host
            unrecognized_urls.append(URL)


# ----------------------------------------
# Show link summary
# ----------------------------------------

print(
    f"Found {len(valid_urls)} valid KKBR link(s)."
)

if skipped_lines:
    print(
        f"Skipped {len(skipped_lines)} comment line(s)."
    )

if prelinked_urls:
    print(
        f"Found {len(prelinked_urls)} "
        f"alternate/development KKBR link(s)."
    )

if unrecognized_urls:
    print(
        f"Found {len(unrecognized_urls)} "
        f"unrecognized link(s)."
    )


# ----------------------------------------
# Show skipped comments
# ----------------------------------------

for URL in skipped_lines:

    print(
        f"Skipped: {URL}"
    )


# ----------------------------------------
# Show alternate/development URLs
# ----------------------------------------

for URL in prelinked_urls:

    print(
        f"Alternate/development link: {URL}"
    )


# ----------------------------------------
# Show unrecognized URLs
# ----------------------------------------

for URL in unrecognized_urls:

    print(
        f"Unrecognized link: {URL}"
    )


# ----------------------------------------
# Stop if there are no valid URLs
# ----------------------------------------

if not valid_urls:

    print()
    print("No valid KKBR links to process.")
    raise SystemExit


# ----------------------------------------
# Loud or Quiet mode?
# ----------------------------------------

print("Select extraction mode:")
print()
print("L - Loud  (show browser window)")
print("Q - Quiet (run browser in background)")
print("")

while True:
    mode = input("> ").strip().lower()

    if mode == "l":
        headless = False
        break

    if mode == "q":
        headless = True
        break

    print('Please enter "L" or "Q".')


with sync_playwright() as p:

    # ----------------------------------------
    # Start browser
    # ----------------------------------------

    browser = p.chromium.launch(
        headless=headless
    )
    page = browser.new_page()


    # ----------------------------------------
    # Process each valid URL
    # ----------------------------------------

    for URL in valid_urls:

        print()
        print("----------------------------------------")
        print(f"Processing: {URL}")
        print("----------------------------------------")

        response = page.goto(
            URL,
            wait_until="domcontentloaded"
        )

        page.wait_for_load_state("networkidle")

        # ------------------------------------
        # Access check
        # ------------------------------------

        # 404 = Scenario/link does not exist
        if response and response.status == 404:

            print(
                f"ERROR: Scenario not found (404): {URL}"
            )

            continue

        # ----------------------------------------
        # Access check
        # ----------------------------------------

        age_gate = page.locator(".age-gate-overlay")

        try:
            # Give the normal age gate a few seconds to appear.
            age_gate.wait_for(
                state="visible",
                timeout=3000
            )

            print("Age gate detected.")

            agree_button = page.get_by_role(
                "button",
                name="I Agree"
            )

            if agree_button.count() == 0:
                print("ERROR: Age gate detected, but I Agree was not found.")
                browser.close()
                raise SystemExit

            print("Clicking I Agree...")
            agree_button.click()

            # Make sure the gate actually disappeared.
            age_gate.wait_for(
                state="hidden",
                timeout=5000
            )

            print("Age gate accepted.")

        except TimeoutError:
            # No age gate appeared.
            pass


        # ----------------------------------------
        # Check that the actual scenario loaded
        # ----------------------------------------

        scenario_content = page.locator(
            ".scenarios-section"
        )

        try:
            scenario_content.wait_for(
                state="attached",
                timeout=5000
            )

        except TimeoutError:
            print()
            print("ERROR: The scenario page did not load.")
            print(
                "The site may be blocking access from your "
                "current jurisdiction, or the page structure "
                "may have changed. Check the site status and "
                "check if you need to run this program with "
                "a VPN. If you can access it, create an issue "
                "on the GitHub repository (check README.MD)."
            )

            browser.close()
            raise SystemExit

        # ----------------------------------------
        # Scenario name
        # ----------------------------------------

        scenario_name = page.locator(
            'script[type="application/ld+json"]'
        ).first.evaluate(
            "element => JSON.parse(element.textContent).name"
        )

        print(f"Scenario: {scenario_name}")


        # ----------------------------------------
        # Scenario Tagline
        # ----------------------------------------

        scenario_tagline = page.locator(
            "p.card-tagline"
        ).first.inner_text().strip()

        # ----------------------------------------
        # Description
        # ----------------------------------------

        description = page.locator(
            ".description-card .markdown-content"
        ).first.inner_html()


        # ----------------------------------------
        # Actor information
        # ----------------------------------------

        # ----------------------------------------
        # Actor Name
        # ----------------------------------------

        actor_name_locator = page.locator(
            ".actor-selector .actor-name"
        )

        if actor_name_locator.count() > 0:
        
            actor_name = (
                actor_name_locator.first
                .inner_text()
                .strip()
            )

        else:
        
            actor_name = ""


        # ----------------------------------------
        # Actor Tabs
        # ----------------------------------------

        tabs = page.locator(
            ".actor-description-container .tab-btn"
        )

        actor_tabs = {}

        for i in range(tabs.count()):
        
            tab = tabs.nth(i)

            name = tab.locator(
                ".tab-label"
            ).inner_text().strip()

            tab.click()

            page.wait_for_timeout(1000)

            content = page.locator(
                ".actor-description-container "
                ".tab-content .markdown-content"
            ).inner_html()

            actor_tabs[name] = content


        # ----------------------------------------
        # Combine Actor information
        # ----------------------------------------

        actor = {
            "name": actor_name,
            **actor_tabs
        }


        # ----------------------------------------
        # Interactions
        # ----------------------------------------

        interactions = []

        counter = page.locator(
            ".interaction-counter"
        ).inner_text().strip()

        # Example:
        # "of 1"
        # "of 5"

        total_interactions = int(
            counter.replace("of", "").strip()
        )

        print(
            f"Found {total_interactions} interaction(s)."
        )


        for i in range(total_interactions):

            # ------------------------------------
            # Interaction subtitle
            # ------------------------------------

            subtitle_locator = page.locator(
                ".interaction-subtitle"
            )

            if subtitle_locator.count() > 0:
                subtitle = subtitle_locator.inner_text().strip()
            else:
                subtitle = ""


            # ------------------------------------
            # Interaction properties
            # ------------------------------------

            properties = {}

            property_classes = [
                "message",
                "clothing",
                "environment",
                "emotion",
                "plan"
            ]


            for property_name in property_classes:

                section = page.locator(
                    f".message-section.{property_name}"
                )

                # Some interactions may not have
                # every possible property.
                if section.count() == 0:
                    continue


                content = section.locator(
                    ".markdown-content"
                ).inner_html()


                properties[property_name] = content


            # ------------------------------------
            # Save interaction
            # ------------------------------------

            interaction = {
                "number": i + 1,
                "subtitle": subtitle,
                "properties": properties
            }

            interactions.append(interaction)


            print(
                f"Extracted interaction "
                f"{i + 1}/{total_interactions}"
            )


            # ------------------------------------
            # Go to next interaction
            # ------------------------------------

            if i < total_interactions - 1:

                next_button = page.locator(
                    ".interaction-navigation "
                    ".nav-button.next"
                )

                next_button.click()

                page.wait_for_timeout(500)


        # ----------------------------------------
        # Combine everything
        # ----------------------------------------

        result = {
            "name": scenario_name,
            "url": URL,
            "tagline": scenario_tagline,
            "description": description,
            "actor": actor,
            "interactions": interactions
        }


        # ----------------------------------------
        # Save JSON
        # ----------------------------------------

        SCENARIOS_FOLDER = Path("Scenarios")

        SCENARIOS_FOLDER.mkdir(
            exist_ok=True
        )


        file_name = re.sub(r'[<>:"/\\|?*]', "", scenario_name)
        file_name = re.sub(r"\s+", "_", file_name).strip("_")


        output_path = SCENARIOS_FOLDER / f"{file_name}.json"


        with output_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                ensure_ascii=False,
                indent=2
            )


        print()
        print("Extraction complete.")
        print(f"Saved to {output_path}")


    # ----------------------------------------
    # Close browser
    # ----------------------------------------

    browser.close()