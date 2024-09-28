from pathlib import Path

# TODO: make the config customizable by user.
TEMPLATES_DIR = Path.home() / '.templates'
TEMPLATES_DIR.mkdir(exist_ok=True)
