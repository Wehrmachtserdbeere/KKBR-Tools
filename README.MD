# KKBR Tools

A collection of Python tools for the [KKBR](https://kkbr.ai) Service.

The project currently contains two utilities:

* `_Scenario_Extractor.py` — extracts Scenario data from KKBR Scenario pages and saves it as JSON.
* `_Scenario_Paster.py` — loads an extracted JSON file and sequentially copies each property to the clipboard for manual pasting back into KKBR.

The tools are designed to avoid API-based automation. The Paster in particular acts as a guided clipboard assistant: you paste each copied field into the appropriate KKBR field yourself.

## Requirements

* Python 3.14.2 (The Extractor and Paster were created on this version)
* Internet access for the Scenario Extractor
* A Chromium-based browser installed by Playwright (can be done automatically by running `Setup.bat`)
* Access to KKBR Scenario pages

Python packages:

* `playwright`
* `pyperclip`

## Installation

Clone or download this repository and open a terminal in the project folder.

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

Then install the Chromium browser used by Playwright:

```powershell
playwright install chromium
```

After that, the tools should be ready to use.

### Optional: One-click setup

If `Setup.bat` is included in your download, you can simply run it instead:

```text
setup.bat
```

It installs the Python requirements and Playwright's Chromium browser automatically.

## Project Structure

```text
Strawbs-KKBR-Tools/
│
├── _Scenario_Extractor.py
├── _Scenario_Paster.py
├── _Links.txt
├── requirements.txt
├── README.md
│
└── Scenarios/
    ├── Scenario_Name.json
    ├── Another_Scenario.json
    └── ...
```

`Scenarios/` is created automatically by the Extractor if it does not already exist.

## Scenario Extractor

`_Scenario_Extractor.py` extracts the following information from a KKBR Scenario:

* Scenario Name
* Scenario URL
* Scenario Tagline
* Scenario Description
* Actor Name
* Actor Persona
* Actor Somatics
* Actor Emotions
* Actor Physical
* Interaction Titles
* Interaction Messages
* Interaction Clothing
* Interaction Environment
* Interaction Emotions
* Interaction Plans

HTML content is preserved where appropriate. This is intentional, as some Scenarios use HTML and CSS inside their messages and descriptions.

### 1. Add Scenario URLs

Put the Scenario URLs you want to extract into:

```text
_Links.txt
```

For example:

```text
https://kkbr.ai/scenario/::S::example1
https://kkbr.ai/scenario/::S::example2
https://kkbr.ai/scenario/::S::example3
```

You can put multiple URLs in the file, one per line.

Blank lines are ignored.

Lines beginning with `#` are treated as comments and skipped:

```text
# My scenarios

https://kkbr.ai/scenario/::S::example1
https://kkbr.ai/scenario/::S::example2
```

The Extractor only processes URLs on the main `kkbr.ai` domain.

It will identify other KKBR subdomains separately rather than silently processing them.

### 2. Run the Extractor

Run:

```powershell
python _Scenario_Extractor.py
```

The Extractor will process each valid URL in `_Links.txt` sequentially.

If an age gate appears, the Extractor will automatically attempt to press `I Agree`.

After extraction, the Scenario is saved as a JSON file inside:

```text
Scenarios/
```

For example:

```text
Scenarios/
└── Natsuki.json
```

## Extraction Modes

When starting the Extractor, you can choose between two modes:

- Loud — opens a visible Chromium browser window while extracting.
- Quiet — runs Chromium in headless mode without displaying a browser window.

Quiet mode is useful when extracting many Scenarios or when you don't need to watch the browser.

### Extracted JSON

A simplified Scenario looks like this:

```json
{
  "name": "Example Scenario",
  "url": "https://kkbr.ai/scenario/::S::example",
  "tagline": "An example Scenario.",
  "description": "<p>Scenario description...</p>",
  "actor": {
    "name": "Example Character",
    "Persona": "<p>...</p>",
    "Somatics": "<p>...</p>",
    "Emotions": "<p>...</p>",
    "Physical": "<p>...</p>"
  },
  "interactions": [
    {
      "number": 1,
      "subtitle": "The beginning.",
      "properties": {
        "message": "<p>...</p>",
        "clothing": "<p>...</p>",
        "environment": "<p>...</p>",
        "emotion": "<p>...</p>",
        "plan": "<p>...</p>"
      }
    }
  ]
}
```

The `subtitle` property represents the Interaction's **Title** in the KKBR interface.

## Scenario Paster

`_Scenario_Paster.py` is a manual clipboard assistant for rebuilding a Scenario from an extracted JSON file.

It does **not** automatically fill out the KKBR website.

Instead, it copies one property to your clipboard at a time and tells you where to paste it.

For example:

```text
Field "Name" copied, please paste it into the "Name" field.

Press "Enter" to continue to the next property.
Press "Q" to quit early.
```

After pressing Enter:

```text
Field "Tagline" copied, please paste it into the "Tagline" field.

Press "Enter" to continue to the next property.
Press "Q" to quit early.
```

Actor fields are explicitly identified:

```text
ACTOR Field "Persona" copied, please create a new Actor or edit an existing actor and paste it into the "Persona" field.

Press "Enter" to continue to the next property.
Press "Q" to quit early.
```

Interactions are identified by number:

```text
INTERACTION - 1 - Field "Message" copied, please paste it into the "Message" field.

Press "Enter" to continue to the next property.
Press "Q" to quit early.
```

### Running the Paster

Run:

```powershell
python _Scenario_Paster.py
```

The program will let you select one of the JSON files in the `Scenarios/` folder.

After selecting a Scenario:

1. The first property is copied to the clipboard.
2. Paste it into the appropriate KKBR field.
3. Return to the command prompt.
4. Press `Enter`.
5. The next property is copied.
6. Repeat until the Scenario is reconstructed.

At any point, press:

```text
Q
```

to stop the process early.

## Important Notes

### The Extractor opens a real browser

The Extractor uses Playwright with a visible Chromium window:

```python
browser = p.chromium.launch(headless=False)
```

This is intentional. It allows the page to load normally and allows the age gate to be handled when necessary.

### HTML is preserved

The Extractor uses HTML rather than plain text for fields such as descriptions and messages.

For example:

```html
<p>Hello.</p>
<p><strong>This is important.</strong></p>
```

is stored as HTML instead of being reduced to:

```text
Hello.
This is important.
```

This is necessary for Scenarios that rely on formatting, HTML, or embedded CSS.

### The Paster uses the clipboard

The Paster requires `pyperclip` to copy extracted content to the system clipboard.

It does not attempt to control your browser or automatically interact with KKBR's fields.

You remain responsible for navigating the KKBR interface and pasting each property.

### Scenario structure may change

The Extractor relies on KKBR's current HTML structure and CSS classes.

If KKBR changes its website structure, selectors used by the Extractor may stop working.

If that happens, the relevant selectors in `_Scenario_Extractor.py` may need to be updated.

## Troubleshooting

### `ModuleNotFoundError`

If Python reports something such as:

```text
ModuleNotFoundError: No module named 'playwright'
```

or:

```text
ModuleNotFoundError: No module named 'pyperclip'
```

run:

```powershell
pip install -r requirements.txt
```

### Playwright browser error

If Playwright reports that Chromium is missing, run:

```powershell
playwright install chromium
```

### The Scenario does not load

The Extractor checks whether the Scenario content appears after loading the page.

If it cannot find the expected Scenario content, the website may be inaccessible from your current connection, the Scenario may no longer exist, or KKBR's page structure may have changed.

### Clipboard problems

If the Paster cannot copy text to the clipboard, make sure `pyperclip` is installed:

```powershell
pip install pyperclip
```

On Windows, `pyperclip` normally works without additional clipboard software.

## Disclaimer

This project is an independent utility and is not affiliated with or endorsed by KKBR.

Use it responsibly, you could get IP banned if you try to use it maliciously.

## License

PolyForm Noncommercial 1.0.0. See LICENSE.md. Additional project-specific attribution and endorsement requirements are described in NOTICE.md.