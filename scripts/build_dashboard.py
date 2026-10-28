import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_PATH = DOCS_DIR / "data" / "dashboard_data.json"
FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
ASSETS_DIR = DOCS_DIR / "assets"
INDEX_PATH = DOCS_DIR / "index.html"
PAGE_LIMIT_BYTES = 1_000_000
GAP_THRESHOLD = 0.05


def escape(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def find_kpi(kpis, name):
    matches = [item for item in kpis if item["KPI"] == name]
    assert len(matches) == 1, f"Expected one KPI named {name}"
    return matches[0]["Value"]


def format_ratio(value):
    return f"{float(value):.3f}"


def tier_label(value):
    tier = str(value)
    css_name = tier.lower() if tier in ("Watch", "Alert", "Critical") else "other"
    return f'<span class="tier tier-{css_name}">{escape(tier)}</span>'


def table(headers, rows, caption):
    parts = [
        '<div class="table-scroll" tabindex="0" role="region" aria-label="' + escape(caption) + '">',
        "<table>",
        f'<caption class="visually-hidden">{escape(caption)}</caption>',
        "<thead><tr>",
    ]
    parts.extend(f'<th scope="col">{escape(header)}</th>' for header in headers)
    parts.extend(["</tr></thead>", "<tbody>"])
    parts.extend(f"<tr>{row}</tr>" for row in rows)
    parts.extend(["</tbody>", "</table>", "</div>"])
    return "\n".join(parts)


def cells(values):
    return "".join(f"<td>{value}</td>" for value in values)


def date_time(value):
    return escape(str(value).replace("T", " ")[:16])


def build_page(data):
    headline = data["headline"]
    tier_counts = data["inverters_by_tier"]
    fleet_size = int(headline["fleet_size"])
    flagged_count = int(headline["flagged_inverters"])
    kpis = data["kpis"]

    cards = [
        ("Inverters flagged", f'{flagged_count} of {fleet_size}', "At least one qualifying rolling block."),
        ("Designed faults caught", headline["designed_faults_caught"], "Designed tier tests detected in their own windows."),
        ("Expected misses confirmed", headline["expected_misses_confirmed"], "Hard cases remain outside the rule's intended detection."),
        (
            "False alarm blocks",
            f'{headline["false_alarm_blocks"]} across {headline["non_faulted_inverters"]}',
            "Non-faulted inverters checked against the same simulated inputs.",
        ),
    ]
    card_html = "\n".join(
        '<article class="kpi"><h3>' + escape(label) + '</h3><p class="kpi-value">' + escape(value)
        + '</p><p class="kpi-note">' + escape(note) + "</p></article>"
        for label, value, note in cards
    )

    tier_actions = {
        "Watch": "Remote check, log, and monitor for 24 hours.",
        "Alert": "Attempt a remote reset and schedule a site visit within 72 hours.",
        "Critical": "Likely hardware fault; dispatch immediately.",
    }
    total_flagged = sum(int(tier_counts.get(tier, 0)) for tier in tier_actions)
    bars = []
    for tier, action in tier_actions.items():
        count = int(tier_counts.get(tier, 0))
        width = count / total_flagged * 100 if total_flagged else 0
        bars.append(
            f'<div class="tier-row"><div class="tier-row-heading">{tier_label(tier)}'
            f'<strong>{count}</strong></div><div class="bar-track" role="img" '
            f'aria-label="{tier}: {count} inverters"><span class="bar-fill tier-{tier.lower()}" '
            f'style="width: {width:.2f}%"></span></div><p>{escape(action)}</p></div>'
        )

    inverter_rows = []
    for item in data["flagged_inverters"]:
        inverter_rows.append(cells([
            escape(item["inverter_id"]),
            date_time(item["first_block_start"]),
            date_time(item["last_block_end"]),
            escape(item["rolling_block_count"]),
            format_ratio(item["peak_mean_gap"]),
            tier_label(item["highest_tier"]),
            escape(item["test_target"]),
        ]))
    inverter_table = table(
        ["Inverter", "First flag", "Last flag", "Rolling blocks", "Peak gap", "Highest tier", "Test target"],
        inverter_rows,
        "Flagged inverter summary",
    )

    block_rows = []
    for item in data["flagged_blocks"]:
        block_rows.append(cells([
            escape(item["inverter_id"]),
            date_time(item["block_start"]),
            date_time(item["block_end"]),
            format_ratio(item["mean_gap"]),
            tier_label(item["severity_tier"]),
        ]))
    block_table = table(
        ["Inverter", "Block start", "Block end", "Mean gap", "Tier"],
        block_rows,
        "All saved rolling blocks",
    )

    hourly_rows = []
    for inverter_id, observations in data["inverter_detail"].items():
        for observation in observations:
            pr_value = observation.get("performance_ratio")
            if pr_value is None:
                continue
            hourly_rows.append(cells([
                escape(inverter_id),
                date_time(observation["date_time"]),
                format_ratio(pr_value),
            ]))
    hourly_table = table(
        ["Inverter", "Date and hour", "Performance ratio"],
        hourly_rows,
        "Daytime performance ratio readings for validation fault days",
    )

    validation = data["detection_validation"]
    detection_rows = []
    designed_detected = 0
    hard_below_threshold = 0
    short_faults = 0
    hard_case_count = 0
    for item in validation:
        target = str(item["target_tier"])
        detected = str(item["detected"]).lower() == "true"
        start_text, end_text = item["window"].split(" to ")
        start = datetime.fromisoformat(start_text)
        end = datetime.fromisoformat(end_text)
        if start.date() == end.date():
            display_window = f"{start:%Y-%m-%d %H:%M} to {end:%H:%M}"
        else:
            display_window = f"{start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M}"
        if target in ("Watch", "Alert", "Critical") and detected:
            designed_detected += 1
        if "expected miss" in target.lower() or "too short" in target.lower():
            hard_case_count += 1
            if "too short" in target.lower():
                duration = (end - start).total_seconds() / 3600 + 1
                if duration < 3:
                    short_faults += 1
            elif float(item["mean_pr_gap"]) < GAP_THRESHOLD:
                hard_below_threshold += 1
        note = escape(item.get("note", ""))
        detection_rows.append(cells([
            escape(item["inverter_id"]),
        ]) + f'<td class="detection-window">{escape(display_window)}</td>' + cells([
            escape(target),
            format_ratio(item["mean_pr_gap"]),
            "Yes" if detected else "No",
            note,
        ]))
    detection_table = table(
        ["Inverter", "Window", "Target", "Gap", "Flagged by own window", "Note"],
        detection_rows,
        "Designed fault-window detection check",
    )
    detection_summary = (
        f"The {designed_detected} designed faults were detected in their own windows. "
        f"The {hard_case_count} hard cases show the rule's limits: {hard_below_threshold} gaps "
        f"were below {GAP_THRESHOLD:.2f}, and {short_faults} fault lasted fewer than 3 hours."
    )

    false_alarm = data["false_alarm_check"][0]
    false_alarm_sentence = (
        f'{false_alarm["flagged_blocks_on_non_faulted"]} false alarm blocks across '
        f'{false_alarm["non_faulted_inverters"]} non-faulted inverters.'
    )

    action_rows = [cells([tier_label(tier), escape(action)]) for tier, action in tier_actions.items()]
    action_table = table(["Tier", "Suggested action"], action_rows, "Suggested follow-up by tier")

    severity = data["rolling_blocks_by_tier"]
    severity_summary = "; ".join(f"{tier}: {severity[tier]}" for tier in tier_actions)
    extra_metrics = [
        ("Pooled mean hourly PR", format_ratio(find_kpi(kpis, "Performance Ratio (hourly, per inverter)"))),
        ("Shortfall from PR 1.0", format_ratio(find_kpi(kpis, "fleet_mean_pr_shortfall_from_1"))),
        ("Clipping share, sample estimate", find_kpi(kpis, "Clipping hours share (sample estimate)")),
        ("Rolling blocks by severity", severity_summary),
    ]
    metric_rows = [cells([escape(label), escape(value)]) for label, value in extra_metrics]
    metric_table = table(["Metric", "Value"], metric_rows, "Additional fleet metrics")

    links = [
        ("Project repository", "../"),
        ("KPI definitions", "kpi_definitions.md"),
        ("Segmentation", "segmentation.md"),
        ("Stakeholder brief", "stakeholder_brief.md"),
        ("Dashboard layout", "dashboard_layout.md"),
    ]

    return "\n".join([
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
        '  <div class="sticky-top"><div class="demo-banner">Simulated demonstration. Faults in this data are planted to test the detector. Results show how the rule behaves, not the condition of a real plant.</div>',
        '  <nav class="site-nav" aria-label="Dashboard sections"><a href="#fleet-status">Fleet status</a><a href="#when-where">When and where</a><a href="#investigation">Investigation</a><a href="#detection">Detection check</a><a href="#false-alarms">False alarms</a><a href="#actions">What to do</a></nav></div>',
        '  <header class="hero">',
        '    <p class="eyebrow">Solar inverter PR monitoring</p>',
        '    <h1>When and where are inverters underperforming against the fleet?</h1>',
        f'    <p class="answer">{flagged_count} of {fleet_size} inverters were flagged: {headline["critical_inverters"]} Critical, {headline["alert_inverters"]} Alert, {headline["watch_inverters"]} Watch.</p>',
        '    <p class="gap-explainer">A gap is how far an inverter\'s performance ratio (PR) sits below the fleet median at the same hour. The rule flags 3 hours in a row averaging 0.05 or more.</p>',
        "  </header>",
        '  <main id="main-content">',
        f'    <section class="kpi-grid" aria-label="Key results">{card_html}</section>',
        '    <section class="section" id="fleet-status" aria-labelledby="fleet-title">',
        '      <div class="section-heading"><p class="eyebrow">Fleet</p><h2 id="fleet-title">Fleet status</h2></div>',
        f'      <div class="tier-bars">{"".join(bars)}</div>',
        "    </section>",
        '    <section class="section" id="when-where" aria-labelledby="when-title">',
        '      <div class="section-heading"><p class="eyebrow">Signals</p><h2 id="when-title">When and where</h2></div>',
        f"      {inverter_table}",
        f'      <details class="disclosure"><summary>All {len(data["flagged_blocks"])} rolling blocks</summary>{block_table}<p class="fine-print">Overlapping rolling blocks count separately.</p></details>',
        "    </section>",
        '    <section class="section" id="investigation" aria-labelledby="investigation-title">',
        '      <div class="section-heading"><p class="eyebrow">Investigation</p><h2 id="investigation-title">What the planted fault hours look like</h2></div>',
        f'      <figure class="investigation-figure"><img src="assets/fault_day_pr_by_tier.png" alt="Line chart comparing hourly performance ratio across Watch, Alert, and Critical planted-fault days."></figure>',
        '      <p class="takeaway">PR drops during the planted fault hours, and the drop grows from Watch to Critical.</p>',
        f'      <details class="disclosure"><summary>Hourly values</summary>{hourly_table}</details>',
        "    </section>",
        '    <section class="section" id="detection" aria-labelledby="detection-title">',
        '      <div class="section-heading"><p class="eyebrow">Validation</p><h2 id="detection-title">Detection check</h2></div>',
        f'      <p class="section-intro">{escape(detection_summary)}</p>',
        f"      {detection_table}",
        "    </section>",
        '    <section class="section" id="false-alarms" aria-labelledby="false-title">',
        '      <div class="section-heading"><p class="eyebrow">Validation</p><h2 id="false-title">False alarms</h2></div>',
        f'      <p class="false-alarm-result">{escape(false_alarm_sentence)}</p>',
        '      <p class="section-intro">Non-faulted inverters share the same weather and simulated PR, so this does not test noisy real data.</p>',
        "    </section>",
        '    <section class="section" id="actions" aria-labelledby="actions-title">',
        '      <div class="section-heading"><p class="eyebrow">Response</p><h2 id="actions-title">What to do</h2></div>',
        f"      {action_table}",
        '      <details class="disclosure"><summary>More metrics</summary>' + metric_table + "</details>",
        "    </section>",
        "  </main>",
        '  <footer><p>Solar inverter PR analysis</p><ul>',
        *[f'<li><a href="{escape(path)}">{escape(label)}</a></li>' for label, path in links],
        "  </ul></footer>",
        "</body>",
        "</html>",
        "",
    ])


def validate_page(page):
    paths = re.findall(r'\b(?:href|src)="([^"]+)"', page)
    for value in paths:
        assert not value.startswith("/"), f"Absolute-root path is not allowed: {value}"
        parsed = urlsplit(value)
        assert not parsed.scheme and not parsed.netloc, f"Only relative paths are allowed: {value}"
        relative_path = unquote(parsed.path)
        target = (DOCS_DIR / relative_path).resolve() if relative_path else DOCS_DIR.resolve()
        assert target.is_relative_to(PROJECT_ROOT.resolve()), f"Path escapes the project: {value}"
        assert target.exists(), f"Broken relative href/src: {value}"
    image_tags = re.findall(r"<img\b[^>]*>", page, flags=re.IGNORECASE)
    assert all(re.search(r'\balt="[^"]*"', tag) for tag in image_tags), "Every image needs an alt attribute"
    page_size = len(page.encode("utf-8"))
    assert page_size < PAGE_LIMIT_BYTES, f"Generated page is {page_size} bytes"
    print(f"Validated {len(paths)} relative href/src paths and {len(image_tags)} image alt attributes; page is {page_size} bytes.")


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
