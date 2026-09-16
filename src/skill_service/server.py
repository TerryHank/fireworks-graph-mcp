import json
import subprocess
import sys
import xml.etree.ElementTree as ET

import resvg_py
from .common import FastMCP, VENDOR, attach, launch, uploaded

mcp = FastMCP("fireworks-graph-mcp")
attach(mcp)


@mcp.tool()
def start_render(upload_id: str, mode: str = "architecture") -> dict:
    """Render uploaded Fireworks JSON to SVG/PNG/HTML. Host LLM creates graph JSON."""
    source = uploaded(upload_id)
    if source.suffix != ".json" or source.stat().st_size > 1048576:
        raise ValueError("Supply graph JSON <=1 MiB.")
    if mode not in {"architecture", "flowchart", "sequence", "class", "er", "state", "network", "mindmap", "timeline", "comparison"}:
        raise ValueError("Unsupported diagram mode.")
    graph = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(graph, dict) or not 1 <= len(graph.get("nodes", [])) <= 100:
        raise ValueError("Supply 1-100 graph nodes.")
    for size in ("width", "height"):
        if not 1 <= float(graph.get(size, 960)) <= 4096:
            raise ValueError("Canvas outside allowed bounds.")
    def process(folder):
        cli = str(VENDOR / "scripts/fireworks.py")
        svg = folder / "diagram.svg"
        def run(args):
            p = subprocess.run([sys.executable, cli, *args], capture_output=True, timeout=90)
            if p.returncode:
                raise RuntimeError("Diagram validation/render failed.")
        run(["render", mode, str(source), str(svg), "--report", str(folder / "layout.json")])
        # No active/external content before rasterization.
        tree = ET.parse(svg)
        for node in tree.iter():
            if node.tag.rsplit("}", 1)[-1] in {"script", "foreignObject", "image"}:
                raise ValueError("Active/external SVG content forbidden.")
            for k, v in node.attrib.items():
                if k.lower().startswith("on") or (k.endswith("href") and not v.startswith("#")):
                    raise ValueError("External reference forbidden.")
        png = resvg_py.svg_to_bytes(svg_string=svg.read_text(encoding="utf-8"), width=1920)
        if png[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Invalid PNG.")
        (folder / "diagram.png").write_bytes(png)
        run(["export-html", str(svg), str(folder / "diagram.html"), "--title", str(graph.get("title", "Diagram"))])
        return {"formats": ["svg", "png", "html"], "visual_review": "requires host image inspection"}
    return launch(process)


def main():
    mcp.run(transport="stdio")

