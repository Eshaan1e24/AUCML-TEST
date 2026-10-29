"""Screenshot of the executed notebook (tuning times and test results) for the slides and the report.

Usage:  python make_exec_evidence.py <run folder>      (the folder holds executed_v3.ipynb and outputs/)
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

run = Path(sys.argv[1])
notebook = run / "executed_v3.ipynb"
if not notebook.exists():
    notebook = run / "IHDS_poverty_escape_v3.ipynb"      # the executed notebook that is shipped in the project folder
html = run / "executed_notebook.html"
subprocess.run([sys.executable, "-m", "nbconvert", "--to", "html", str(notebook), "--output", html.name], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
out_dir = run / "outputs" / "figures_ppt"
out_dir.mkdir(parents=True, exist_ok=True)
pieces = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1250, "height": 1000}, device_scale_factor=2)
    page.goto(html.as_uri())
    page.evaluate("document.body.style.zoom = 2.0")      # larger text so that the picture is readable on a slide
    page.wait_for_timeout(1500)
    for marker in ["clf__min_child_weight"]:
        cell = page.locator("div.jp-CodeCell", has_text=marker).first
        target = cell.locator(".jp-OutputArea").first
        target.scroll_into_view_if_needed()
        piece = out_dir / f"_piece_{len(pieces)}.png"
        target.screenshot(path=str(piece))
        pieces.append(piece)
    browser.close()
images = [Image.open(p).convert("RGB") for p in pieces]
width = max(i.width for i in images)
height = sum(i.height for i in images) + 30 * (len(images) - 1)
canvas = Image.new("RGB", (width, height), "white")
y = 0
for image in images:
    canvas.paste(image, (0, y))
    y += image.height + 30
canvas.save(out_dir / "exec_evidence.png")
for p in pieces:
    p.unlink()
print("saved", out_dir / "exec_evidence.png", canvas.size)
