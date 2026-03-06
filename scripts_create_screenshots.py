import textwrap
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SCREEN = ROOT / "screenshots"
OUTPUTS = ROOT / "outputs"
SCREEN.mkdir(parents=True, exist_ok=True)


def save_text_image(text: str, path: Path, title: str) -> None:
    fig = plt.figure(figsize=(13, 7), dpi=140)
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    ax.text(
        0.01,
        0.98,
        title,
        fontsize=18,
        fontweight="bold",
        va="top",
        family="DejaVu Sans",
    )
    ax.text(
        0.01,
        0.90,
        text,
        fontsize=10,
        va="top",
        family="DejaVu Sans Mono",
        wrap=True,
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


terminal_text = (OUTPUTS / "terminal_output.txt").read_text(encoding="utf-8", errors="ignore")
save_text_image(terminal_text[:3500], SCREEN / "terminal_run.png", "Terminal Run (Captured Output)")

md_text = (OUTPUTS / "sample_report.md").read_text(encoding="utf-8", errors="ignore")
wrapped_md = "\n".join(textwrap.wrap(md_text[:4200], width=120, replace_whitespace=False))
save_text_image(wrapped_md, SCREEN / "report_preview.png", "Report Preview (Rendered From Markdown Output)")


def build_tree(path: Path, prefix: str = "") -> list[str]:
    lines = []
    items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for idx, item in enumerate(items):
        connector = "`-- " if idx == len(items) - 1 else "|-- "
        lines.append(f"{prefix}{connector}{item.name}")
        if item.is_dir() and item.name not in {".git", "__pycache__"}:
            extension = "    " if idx == len(items) - 1 else "|   "
            lines.extend(build_tree(item, prefix + extension))
    return lines

repo_tree = ".\n" + "\n".join(build_tree(ROOT))
save_text_image(repo_tree[:4200], SCREEN / "repo_structure.png", "Repository Structure Snapshot")

print("Screenshots generated:")
for p in [
    SCREEN / "terminal_run.png",
    SCREEN / "report_preview.png",
    SCREEN / "repo_structure.png",
]:
    print(p)
