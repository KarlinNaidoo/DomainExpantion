from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR = REPO_ROOT / "vendor" / "bot-crossing"
OVERLAY = Path(__file__).resolve().parent / "bot_crossing"


def bot_crossing_available() -> bool:
    return (VENDOR / "package.json").is_file()


def install_overlay() -> None:
    dest = VENDOR / "server" / "harnesses"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OVERLAY / "domain-expantion.mjs", dest / "domain-expantion.mjs")
    shutil.copyfile(OVERLAY / "index.mjs", dest / "index.mjs")


def launch_bot_crossing(*, open_browser: bool = True, port: int = 5274) -> int:
    if not bot_crossing_available():
        print("Bot Crossing is not vendored at vendor/bot-crossing.", file=sys.stderr)
        return 1
    install_overlay()
    env = os.environ.copy()
    env["DOMAIN_EXPANTION_ROOT"] = str(REPO_ROOT)
    env["PORT"] = str(port)
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        print("npm is not on PATH. Install Node 22+ to run Bot Crossing.", file=sys.stderr)
        return 1
    if not (VENDOR / "node_modules").is_dir():
        print("Installing Bot Crossing npm dependencies (first run)…")
        subprocess.run([npm, "install"], cwd=VENDOR, check=True, env=env)
    url = f"http://127.0.0.1:{port}/"
    print(f"Bot Crossing colony at {url}")
    print("Family snapshot: .data/planet-family.json")
    print("Keep domain-expantion chat running in another window to see workers hammer.")
    if open_browser:
        webbrowser.open(url)
    return subprocess.call([npm, "run", "dev"], cwd=VENDOR, env=env)
