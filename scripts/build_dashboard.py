import html
import json
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_PATH = DOCS_DIR / "data" / "dashboard_data.json"
FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
ASSETS_DIR = DOCS_DIR / "assets"
INDEX_PATH = DOCS_DIR / "index.html"
PAGE_LIMIT_BYTES = 1_000_000
REPOSITORY_URL = "https://github.com/Jan-Ric/dep-data-engineering-jan-ric"
GITHUB_DOCS_URL = REPOSITORY_URL + "/blob/main/docs/"


def escape(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def find_kpi(kpis, name):
    matches = [item for item in kpis if item["KPI"] == name]
    assert len(matches) == 1, f"Expected one KPI named {name}"
    return matches[0]["Value"]


def kpi_card(label, value):
    return "\n".join(
        [
            '<div class="kpi">',
            f'  <span class="kpi-label">{escape(label)}</span>',
            f'  <span class="kpi-value">{escape(value)}</span>',
            "</div>",
        ]
    )


def table(headers, rows, caption):
    parts = [
        '<div class="table-scroll">',
        "<table>",
        f"<caption class=\"visually-hidden\">{escape(caption)}</caption>",
        "<thead><tr>",
    ]
    parts.extend(f"<th scope=\"col\">{escape(header)}</th>" for header in headers)
    parts.extend(["</tr></thead>", "<tbody>"])
    parts.extend(f"<tr>{row}</tr>" for row in rows)
    parts.extend(["</tbody>", "</table>", "</div>"])
    return "\n".join(parts)


def tier_label(value):
    tier = str(value)
    css_name = tier.lower() if tier in ("Watch", "Alert", "Critical") else ""
    if not css_name:
        return escape(tier)
    return f'<span class="tier tier-{css_name}">{escape(tier)}</span>'


def format_flagged_window(item):
    start_time = str(item.get("start_time", ""))[:5]
    end_time = str(item.get("end_time", ""))[:5]
    if not start_time or not end_time:
        return escape(item.get("date", "Time unavailable"))
    return f"{escape(item.get('date', ''))} {escape(start_time)} to {escape(end_time)}"


def build_page(data):
    kpis = data["kpis"]
    kpi_values = [
        (
            "Flagged 3-hour blocks",
            find_kpi(kpis, "Flagged 3-hour block count"),
        ),
        (
            "Flagged inverter share",
            find_kpi(kpis, "Flagged inverter share"),
        ),
        (
            "Fault detection rate",
            find_kpi(kpis, "Fault detection rate"),
        ),
        (
            "Pooled mean hourly PR",
            find_kpi(kpis, "Performance Ratio (hourly, per inverter)"),
        ),
    ]
    kpi_cards = "\n".join(kpi_card(label, value) for label, value in kpi_values)

    severity_cards = []
    severity_order = ["Watch", "Alert", "Critical"]
    severity_total = sum(int(data["severity_counts"].get(tier, 0)) for tier in severity_order)
    for tier in severity_order:
        count = int(data["severity_counts"].get(tier, 0))
        share = count / severity_total * 100 if severity_total else 0
        severity_cards.append(
            "\n".join(
                [
                    f'<div class="severity-item tier-{tier.lower()}">',
                    f'  <span class="severity-label">{tier_label(tier)} blocks</span>',
                    f'  <span class="severity-value">{count}</span>',
                    f'  <span>{share:.2f}% of saved blocks</span>',
                    "</div>",
                ]
            )
        )
    severity_cards_html = "\n".join(severity_cards)

    if data["flagged_blocks"]:
        flagged_rows = []
        for item in data["flagged_blocks"]:
            cells = [
                escape(item.get("inverter_id", "")),
                format_flagged_window(item),
                escape(item.get("mean_gap", "")),
                tier_label(item.get("severity_tier", "")),
            ]
            flagged_rows.append("".join(f"<td>{cell}</td>" for cell in cells))
        flagged_content = table(
            ["Inverter", "Date and time", "Mean PR gap", "Tier"],
            flagged_rows,
            "Flagged inverter blocks",
        ) + '<p class="panel-intro">Overlapping rolling blocks count separately.</p>'
    else:
        flagged_content = (
            '<div class="empty-state"><strong>No flagged blocks</strong>'
            "<p>No dated block details are available in the saved dashboard data. "
            "The available aggregate does not include event dates or hours.</p></div>"
        )

    ranking_rows = []
    for item in data["ranking"]:
        cells = [
            escape(item.get("rank", "")),
            escape(item.get("INVERTER_ID", "")),
            escape(item.get("mean_performance_ratio", "")),
            tier_label(item.get("max_severity", "")),
            escape(item.get("absolute_flagged_hours", "")),
            escape(item.get("baseline_relative_flagged_hours", "")),
        ]
        ranking_rows.append("".join(f"<td>{cell}</td>" for cell in cells))
    ranking_table = table(
        ["Rank", "Inverter", "Mean PR", "Maximum tier", "Absolute flagged hours", "Baseline-relative flagged hours"],
        ranking_rows,
        "Inverter ranking by mean performance ratio",
    )

    figure_name = "fault_day_pr_101_202_303.png"
    investigation_rows = []
    for inverter_id in data["inverter_detail"]:
        for observation in data["inverter_detail"][inverter_id]:
            pr_value = observation.get("performance_ratio")
            display_value = "No daytime reading" if pr_value is None else escape(pr_value)
            investigation_rows.append(
                "".join(
                    [
                        f"<td>{escape(inverter_id)}</td>",
                        f"<td>{escape(observation.get('date_time', ''))}</td>",
                        f"<td>{display_value}</td>",
                    ]
                )
            )
    investigation_table = table(
        ["Inverter", "Date and hour", "Performance ratio"],
        investigation_rows,
        "Hourly performance ratio on validation fault days",
    )

    detection_rows = []
    for item in data["detection_validation"]:
        detected = str(item.get("detected", "")).lower() == "true"
        cells = [
            escape(item.get("inverter_id", "")),
            escape(item.get("window", "")),
            escape(item.get("mean_pr_gap", "")),
            "Yes" if detected else "No",
            tier_label(item.get("severity_tier", "")),
        ]
        detection_rows.append("".join(f"<td>{cell}</td>" for cell in cells))
    detection_table = table(
        ["Inverter", "Injected test window", "Mean PR gap", "Detected", "Tier"],
        detection_rows,
        "Fault-window detection validation",
    )

    actions = [
        ("Watch", "Remote checking only; log and monitor for the next 24 hours."),
        ("Alert", "Attempt a remote reset and schedule a site visit within 72 hours."),
        ("Critical", "Likely a hardware fault that requires immediate dispatch."),
    ]
    action_rows = [
        f"<td>{tier_label(tier)}</td><td>{escape(action)}</td>"
        for tier, action in actions
    ]
    action_table = table(
        ["Tier", "Suggested O&M action"], action_rows, "Suggested follow-up by severity tier"
    )

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            '  <meta name="description" content="Solar inverter performance ratio monitoring and fault-window validation results.">',
            "  <title>Solar Inverter PR Monitoring</title>",
            '  <link rel="stylesheet" href="style.css">',
            "</head>",
            "<body>",
            '  <header class="page-header">',
            '    <p class="eyebrow">Solar inverter PR monitoring</p>',
            "    <h1>When and where are inverters showing negative performance ratio gaps?</h1>",
            '    <p class="question">A fleet-level view for reviewing underperformance signals and deciding which records need O&amp;M follow-up.</p>',
            "  </header>",
            "  <main>",
            '    <section class="panel" aria-labelledby="overview-title">',
            '      <h2 id="overview-title">Fleet overview</h2>',
            f'      <div class="kpi-grid">{kpi_cards}</div>',
            "    </section>",
            '    <section class="panel" aria-labelledby="severity-title">',
            '      <h2 id="severity-title">Fleet status by severity</h2>',
            '      <p class="panel-intro">Saved rolling blocks by tier; each tier is labeled as well as color-coded.</p>',
            f'      <div class="severity-grid">{severity_cards_html}</div>',
            "    </section>",
            '    <section class="panel" aria-labelledby="blocks-title">',
            '      <h2 id="blocks-title">When and where</h2>',
            '      <p class="panel-intro">The saved SQL result contains per-inverter aggregates; dates and times are matched from detected validation windows.</p>',
            f"      {flagged_content}",
            "    </section>",
            '    <section class="panel" aria-labelledby="ranking-title">',
            '      <h2 id="ranking-title">Inverter ranking</h2>',
            '      <p class="panel-intro">Lowest mean PR first, using the saved top-ten ranking.</p>',
            f"      {ranking_table}",
            "    </section>",
            '    <section class="panel" aria-labelledby="investigation-title">',
            '      <h2 id="investigation-title">Investigation: validation fault days</h2>',
            '      <p class="panel-intro">Hourly PR series for validation inverters 101, 202, and 303.</p>',
            '      <figure class="investigation-figure">',
            f'        <img src="assets/{escape(figure_name)}" alt="Line chart comparing hourly performance ratio on the validation fault days for inverters 101, 202, and 303.">',
            '        <figcaption>Chart from the saved fault-day analysis; the table below provides the underlying hourly values.</figcaption>',
            "      </figure>",
            f"      {investigation_table}",
            "    </section>",
            '    <section class="panel" aria-labelledby="detection-title">',
            '      <h2 id="detection-title">Detection check</h2>',
            '      <p class="panel-intro">Detected status is written as Yes or No for each planted validation window.</p>',
            f"      {detection_table}",
            "    </section>",
            '    <section class="panel" aria-labelledby="actions-title">',
            '      <h2 id="actions-title">What to do</h2>',
            f"      {action_table}",
            "    </section>",
            '    <section class="panel" aria-labelledby="limits-title">',
            '      <h2 id="limits-title">Limits and documentation</h2>',
            '      <div class="limits">',
            '        <p>These are demonstration results, not live plant telemetry or fault diagnoses. The validation faults are simulated, the weather inputs are modeled, and the detector thresholds are demonstration settings.</p>',
            '        <ul>',
            f'          <li><a href="{GITHUB_DOCS_URL}kpi_definitions.md">KPI definitions</a></li>',
            f'          <li><a href="{GITHUB_DOCS_URL}segmentation.md">Segmentation method</a></li>',
            f'          <li><a href="{GITHUB_DOCS_URL}stakeholder_brief.md">Stakeholder brief</a></li>',
            "        </ul>",
            "      </div>",
            "    </section>",
            "  </main>",
            "  <footer>",
            '    <p>Solar inverter PR analysis</p>',
            "    <ul>",
            f'      <li><a href="{REPOSITORY_URL}">Project repository</a></li>',
            f'      <li><a href="{GITHUB_DOCS_URL}dashboard_layout.md">Dashboard layout</a></li>',
            f'      <li><a href="{GITHUB_DOCS_URL}kpi_definitions.md">KPI definitions</a></li>',
            f'      <li><a href="{GITHUB_DOCS_URL}segmentation.md">Segmentation</a></li>',
            f'      <li><a href="{GITHUB_DOCS_URL}stakeholder_brief.md">Stakeholder brief</a></li>',
            "    </ul>",
            "  </footer>",
            "</body>",
            "</html>",
            "",
        ]
    )


def validate_page(page):
    from html.parser import HTMLParser

    class LinkCollector(HTMLParser):
        def __init__(self):
            super().__init__()
            self.paths = []

        def handle_starttag(self, tag, attrs):
            for name, value in attrs:
                if name in ("href", "src") and value is not None:
                    self.paths.append(value)

    collector = LinkCollector()
    collector.feed(page)
    for value in collector.paths:
        assert not value.startswith("/"), f"Absolute-root path is not allowed: {value}"
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme == "https", f"Unexpected external URL: {value}"
            continue
        relative_path = unquote(parsed.path)
        target = (DOCS_DIR / relative_path).resolve() if relative_path else DOCS_DIR.resolve()
        assert target.is_relative_to(DOCS_DIR.resolve()), f"Path escapes docs/: {value}"
        assert target.exists(), f"Broken relative href/src: {value}"
    page_size = len(page.encode("utf-8"))
    assert page_size < PAGE_LIMIT_BYTES, f"Generated page is {page_size} bytes"
    print(f"Validated {len(collector.paths)} href/src paths; page is {page_size} bytes.")


def main():
    with DATA_PATH.open("r", encoding="utf-8") as data_file:
        data = json.load(data_file)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    figure_paths = sorted(FIGURES_DIR.glob("*.png"))
    assert figure_paths, f"No PNG figures found in {FIGURES_DIR}"
    for figure_path in figure_paths:
        shutil.copy2(figure_path, ASSETS_DIR / figure_path.name)

    page = build_page(data)
    validate_page(page)
    INDEX_PATH.write_text(page, encoding="utf-8")
    assert INDEX_PATH.stat().st_size < PAGE_LIMIT_BYTES
    print(f"Wrote {INDEX_PATH.relative_to(PROJECT_ROOT)} ({INDEX_PATH.stat().st_size} bytes).")
    print(f"Copied {len(figure_paths)} PNG figures into {ASSETS_DIR.relative_to(PROJECT_ROOT)}.")


if __name__ == "__main__":
    main()