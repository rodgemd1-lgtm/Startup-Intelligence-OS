#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path
from statistics import mean

import yaml
from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/mikerodgers/Startup-Intelligence-OS")
APP_ROOT = ROOT / "apps"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from decision_os.maturity_surfaces import load_simulated_maturity_state  # noqa: E402

DEFAULT_MATRIX = ROOT / ".startup-os/artifacts/department-ten-state-verification-matrix-2026-03-12.yaml"
DEFAULT_HTML = ROOT / ".startup-os/artifacts/department-maturity-dashboard-2026-03-12.html"
DEFAULT_MD = ROOT / ".startup-os/artifacts/department-maturity-dashboard-2026-03-12.md"
DEFAULT_PNG = ROOT / ".startup-os/artifacts/department-maturity-dashboard-2026-03-12.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a visual maturity dashboard from the department verification matrix.")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--html-out", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--png-out", type=Path, default=DEFAULT_PNG)
    return parser.parse_args()


def score(current: list[str], required: list[str]) -> float:
    if not required:
        return 10.0
    return round((len(set(current) & set(required)) / len(required)) * 10, 1)


def bar(value: float) -> str:
    full = int(round(value))
    return "█" * full + "░" * (10 - full)


def enrich(entries: list[dict], simulated_scores: dict[str, dict] | None = None) -> list[dict]:
    enriched = []
    simulated_scores = simulated_scores or {}
    for entry in entries:
        required_data = entry.get("required_data_sources", [])
        current_data = entry.get("current_data_sources", [])
        required_capabilities = entry.get("required_capabilities", [])
        current_capabilities = entry.get("current_capabilities", [])
        data_score = score(current_data, required_data)
        capability_score = score(current_capabilities, required_capabilities)
        simulated_entry = simulated_scores.get(entry["id"], {})
        simulated_score = simulated_entry.get("score")
        enriched.append(
            {
                **entry,
                "data_score": data_score,
                "capability_score": capability_score,
                "overall_score": round(mean([entry.get("current_maturity", 0.0), data_score, capability_score]), 1),
                "missing_data_sources": [item for item in required_data if item not in current_data],
                "missing_capabilities": [item for item in required_capabilities if item not in current_capabilities],
                "simulated_maturity": simulated_score,
                "simulated_review_path": simulated_entry.get("review_path", ""),
            }
        )
    return enriched


def render_table_rows(entries: list[dict], include_simulated: bool = False) -> str:
    rows = []
    for entry in entries:
        next_lifts = "".join(f"<li>{html.escape(item)}</li>" for item in entry.get("next_lifts", []))
        proofs = "".join(f"<li><code>{html.escape(path)}</code></li>" for path in entry.get("proof_paths", []))
        missing_data = ", ".join(entry["missing_data_sources"]) or "none"
        missing_caps = ", ".join(entry["missing_capabilities"]) or "none"
        simulated_cell = ""
        if include_simulated:
            simulated_value = entry.get("simulated_maturity")
            simulated_label = f"{simulated_value:.1f}" if isinstance(simulated_value, (float, int)) else "n/a"
            simulated_meta = ""
            if entry.get("simulated_review_path"):
                simulated_meta = f'<div class="sub"><code>{html.escape(entry["simulated_review_path"])}</code></div>'
            simulated_cell = f'<td class="score">{simulated_label}{simulated_meta}</td>'
        rows.append(
            f"""
            <tr>
              <td>
                <div class="name">{html.escape(entry['name'])}</div>
                <div class="sub">{html.escape(entry['id'])}</div>
              </td>
              <td class="score">{entry['current_maturity']:.1f}</td>
              <td class="score">
                <div class="bar"><span style="width:{entry['data_score']*10:.0f}%"></span></div>
                <div class="sub">{entry['data_score']:.1f}/10</div>
              </td>
              <td class="score">
                <div class="bar"><span style="width:{entry['capability_score']*10:.0f}%"></span></div>
                <div class="sub">{entry['capability_score']:.1f}/10</div>
              </td>
              {simulated_cell}
              <td class="score">{entry['overall_score']:.1f}</td>
              <td>
                <div class="sub"><strong>Missing data:</strong> {html.escape(missing_data)}</div>
                <div class="sub"><strong>Missing capabilities:</strong> {html.escape(missing_caps)}</div>
                <ul>{next_lifts}</ul>
              </td>
              <td><ul>{proofs}</ul></td>
            </tr>
            """
        )
    return "\n".join(rows)


def render_html(data: dict, sections: list[dict], departments: list[dict]) -> str:
    section_avg = round(mean([entry["overall_score"] for entry in sections]), 1)
    department_avg = round(mean([entry["overall_score"] for entry in departments]), 1)
    simulated_departments = [entry for entry in departments if isinstance(entry.get("simulated_maturity"), (float, int))]
    simulated_avg = round(mean([entry["simulated_maturity"] for entry in simulated_departments]), 1) if simulated_departments else 0.0
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(data.get('title', 'Department Maturity Dashboard'))}</title>
  <style>
    :root {{
      --navy: #1A2B4A;
      --red: #C74634;
      --cream: #F6F2EC;
      --white: #FFFFFF;
      --charcoal: #222222;
      --slate: #5B667A;
      --stone: #D9CEC2;
      --mint: #6B8E7A;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: var(--cream);
      color: var(--charcoal);
    }}
    .topbar {{
      background: var(--navy);
      color: var(--white);
      padding: 18px 28px 16px;
      letter-spacing: 0.08em;
      font-size: 12px;
      font-weight: 700;
    }}
    .wrap {{
      padding: 28px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      color: var(--navy);
    }}
    .lede {{
      margin: 0 0 20px;
      font-size: 14px;
      color: var(--slate);
      max-width: 1100px;
      line-height: 1.5;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .card {{
      background: var(--white);
      border: 1px solid var(--stone);
      border-radius: 14px;
      padding: 16px 18px;
    }}
    .card .label {{
      color: var(--slate);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}
    .card .value {{
      font-size: 28px;
      font-weight: 700;
      color: var(--navy);
    }}
    .card .meta {{
      margin-top: 8px;
      font-size: 13px;
      color: var(--slate);
    }}
    h2 {{
      margin: 28px 0 12px;
      color: var(--navy);
      font-size: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--white);
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid var(--stone);
      margin-bottom: 24px;
    }}
    th {{
      background: var(--navy);
      color: var(--white);
      text-align: left;
      font-size: 11px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      padding: 12px;
    }}
    td {{
      vertical-align: top;
      padding: 12px;
      border-top: 1px solid #eee5db;
      font-size: 13px;
      line-height: 1.45;
    }}
    .name {{
      font-weight: 700;
      color: var(--navy);
      margin-bottom: 4px;
    }}
    .sub {{
      color: var(--slate);
      font-size: 12px;
    }}
    .score {{
      min-width: 110px;
      text-align: center;
      white-space: nowrap;
    }}
    .bar {{
      width: 100%;
      height: 10px;
      background: #efe6db;
      border-radius: 999px;
      overflow: hidden;
      margin-bottom: 6px;
    }}
    .bar span {{
      display: block;
      height: 10px;
      background: linear-gradient(90deg, var(--red), var(--mint));
      border-radius: 999px;
    }}
    ul {{
      margin: 8px 0 0 18px;
      padding: 0;
    }}
    li {{
      margin: 0 0 4px;
    }}
    .footer {{
      margin-top: 12px;
      color: var(--slate);
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="topbar">STARTUP INTELLIGENCE OS · DEPARTMENT TEN-STATE VERIFICATION</div>
  <div class="wrap">
    <h1>{html.escape(data.get('title', 'Department Maturity Dashboard'))}</h1>
    <p class="lede">This dashboard is generated from the file-backed verification matrix and the simulated-maturity harness summary. It shows current operational maturity, benchmark-backed simulated maturity where available, current data-source coverage, current capability coverage, and the proof paths currently present in the repo for each core section and department.</p>
    <div class="cards">
      <div class="card"><div class="label">Core Sections</div><div class="value">{len(sections)}</div><div class="meta">Average verified score: {section_avg}/10</div></div>
      <div class="card"><div class="label">Departments</div><div class="value">{len(departments)}</div><div class="meta">Average verified score: {department_avg}/10</div></div>
      <div class="card"><div class="label">Simulated Reviews</div><div class="value">{len(simulated_departments)}</div><div class="meta">Average simulated score: {simulated_avg}/10</div></div>
      <div class="card"><div class="label">Data Categories</div><div class="value">{len(data.get('data_source_categories', {}))}</div><div class="meta">Shared source model used across the OS</div></div>
      <div class="card"><div class="label">Capability Categories</div><div class="value">{len(data.get('capability_categories', {}))}</div><div class="meta">Shared capability model used across the OS</div></div>
    </div>

    <h2>Core Sections</h2>
    <table>
      <thead>
        <tr>
          <th>Section</th>
          <th>Current Maturity</th>
          <th>Data Coverage</th>
          <th>Capability Coverage</th>
          <th>Verified Score</th>
          <th>Next Lifts</th>
          <th>Proof Paths</th>
        </tr>
      </thead>
      <tbody>
        {render_table_rows(sections)}
      </tbody>
    </table>

    <h2>Departments</h2>
    <table>
      <thead>
        <tr>
          <th>Department</th>
          <th>Current Maturity</th>
          <th>Data Coverage</th>
          <th>Capability Coverage</th>
          <th>Simulated Maturity</th>
          <th>Verified Score</th>
          <th>Next Lifts</th>
          <th>Proof Paths</th>
        </tr>
      </thead>
      <tbody>
        {render_table_rows(departments, include_simulated=True)}
      </tbody>
    </table>

    <div class="footer">Generated from <code>{html.escape(str(DEFAULT_MATRIX.relative_to(ROOT)))}</code></div>
  </div>
</body>
</html>
"""


def render_md(data: dict, sections: list[dict], departments: list[dict]) -> str:
    simulated_departments = [entry for entry in departments if isinstance(entry.get("simulated_maturity"), (float, int))]
    lines = [
        f"# {data.get('title', 'Department Maturity Dashboard')}",
        "",
        "## Summary",
        "",
        f"- core_sections: `{len(sections)}`",
        f"- departments: `{len(departments)}`",
        f"- simulated_departments: `{len(simulated_departments)}`",
        "",
        "## Core Sections",
        "",
        "| Section | Current maturity | Data coverage | Capability coverage | Verified score |",
        "|---|---:|---:|---:|---:|",
    ]
    for entry in sections:
        lines.append(
            f"| {entry['name']} | {entry['current_maturity']:.1f} | {entry['data_score']:.1f} | {entry['capability_score']:.1f} | {entry['overall_score']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Departments",
            "",
            "| Department | Current maturity | Simulated maturity | Data coverage | Capability coverage | Verified score |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for entry in departments:
        simulated_value = entry.get("simulated_maturity")
        simulated_label = f"{simulated_value:.1f}" if isinstance(simulated_value, (float, int)) else "n/a"
        lines.append(
            f"| {entry['name']} | {entry['current_maturity']:.1f} | {simulated_label} | {entry['data_score']:.1f} | {entry['capability_score']:.1f} | {entry['overall_score']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Build Rule",
            "",
            "No section or department can claim `10/10` operational maturity until both data coverage and capability coverage reach `10.0`, the proof paths are operating, and the live run history supports the claim.",
            "",
        ]
    )
    return "\n".join(lines)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",
                "DejaVuSans-Bold.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",
                "DejaVuSans.ttf",
            ]
        )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_bar(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, value: float) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill="#efe6db")
    fill_w = max(1, int(w * (value / 10.0)))
    draw.rounded_rectangle((x, y, x + fill_w, y + h), radius=h // 2, fill="#C74634")


def render_png(data: dict, sections: list[dict], departments: list[dict], out_path: Path) -> None:
    width = 1680
    row_h = 88
    top_h = 180
    section_h = 64
    margin = 40
    height = top_h + section_h + row_h * (len(sections) + len(departments) + 4)

    img = Image.new("RGB", (width, height), "#F6F2EC")
    draw = ImageDraw.Draw(img)
    title_font = load_font(34, bold=True)
    h2_font = load_font(22, bold=True)
    label_font = load_font(14, bold=True)
    body_font = load_font(15, bold=False)
    small_font = load_font(12, bold=False)

    draw.rectangle((0, 0, width, 52), fill="#1A2B4A")
    draw.text((margin, 16), "STARTUP INTELLIGENCE OS · TEN-STATE VERIFICATION", fill="#FFFFFF", font=label_font)
    draw.text((margin, 76), data.get("title", "Department Maturity Dashboard"), fill="#1A2B4A", font=title_font)
    draw.text(
        (margin, 118),
        "Rendered from the file-backed verification matrix. Scores combine current maturity, current data-source coverage, and current capability coverage.",
        fill="#5B667A",
        font=body_font,
    )

    def draw_table(title: str, entries: list[dict], start_y: int, include_simulated: bool = False) -> int:
        draw.text((margin, start_y), title, fill="#1A2B4A", font=h2_font)
        y = start_y + 36
        headers = [
            ("Name", 360),
            ("Maturity", 120),
            ("Data", 220),
            ("Capability", 220),
        ]
        if include_simulated:
            headers.append(("Simulated", 150))
        headers.extend(
            [
                ("Verified", 110),
                ("Top gaps", 530 if include_simulated else 680),
            ]
        )
        x = margin
        for label, col_w in headers:
            draw.rectangle((x, y, x + col_w, y + 36), fill="#1A2B4A")
            draw.text((x + 12, y + 10), label.upper(), fill="#FFFFFF", font=small_font)
            x += col_w
        y += 36

        for entry in entries:
            x = margin
            draw.rectangle((margin, y, width - margin, y + row_h), fill="#FFFFFF", outline="#D9CEC2", width=1)
            draw.text((x + 12, y + 14), entry["name"], fill="#1A2B4A", font=label_font)
            draw.text((x + 12, y + 40), entry["id"], fill="#5B667A", font=small_font)
            x += headers[0][1]

            draw.text((x + 16, y + 28), f"{entry['current_maturity']:.1f}", fill="#222222", font=body_font)
            x += headers[1][1]

            draw_bar(draw, x + 14, y + 18, 160, 12, entry["data_score"])
            draw.text((x + 182, y + 14), f"{entry['data_score']:.1f}/10", fill="#222222", font=small_font)
            x += headers[2][1]

            draw_bar(draw, x + 14, y + 18, 160, 12, entry["capability_score"])
            draw.text((x + 182, y + 14), f"{entry['capability_score']:.1f}/10", fill="#222222", font=small_font)
            x += headers[3][1]

            if include_simulated:
                simulated_value = entry.get("simulated_maturity")
                simulated_label = f"{simulated_value:.1f}" if isinstance(simulated_value, (float, int)) else "n/a"
                draw.text((x + 16, y + 28), simulated_label, fill="#222222", font=body_font)
                x += headers[4][1]

            draw.text((x + 16, y + 28), f"{entry['overall_score']:.1f}", fill="#222222", font=body_font)
            x += headers[5 if include_simulated else 4][1]

            missing = []
            if entry["missing_data_sources"]:
                missing.append("data: " + ", ".join(entry["missing_data_sources"][:3]))
            if entry["missing_capabilities"]:
                missing.append("cap: " + ", ".join(entry["missing_capabilities"][:3]))
            if include_simulated and entry.get("simulated_review_path"):
                missing.append("sim: " + Path(entry["simulated_review_path"]).name)
            if entry.get("next_lifts"):
                missing.append("next: " + entry["next_lifts"][0])
            draw.text((x + 12, y + 14), " | ".join(missing)[:110], fill="#5B667A", font=small_font)
            y += row_h
        return y + 20

    y = 170
    y = draw_table("Core Sections", sections, y)
    y = draw_table("Departments", departments, y, include_simulated=True)

    draw.text((margin, y + 10), "Build rule: no section or department can claim 10/10 operational maturity until data and capability coverage reach 10.0 and the proof paths are operating with live run history.", fill="#5B667A", font=body_font)

    img.save(out_path)


def main() -> int:
    args = parse_args()
    data = yaml.safe_load(args.matrix.read_text(encoding="utf-8")) or {}
    sections = enrich(data.get("sections", []))
    simulated_state = load_simulated_maturity_state(ROOT)
    departments = enrich(data.get("departments", []), simulated_state.get("departments", {}))

    args.html_out.write_text(render_html(data, sections, departments), encoding="utf-8")
    args.md_out.write_text(render_md(data, sections, departments), encoding="utf-8")
    render_png(data, sections, departments, args.png_out)
    print(f"Wrote {args.html_out}")
    print(f"Wrote {args.md_out}")
    print(f"Wrote {args.png_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
