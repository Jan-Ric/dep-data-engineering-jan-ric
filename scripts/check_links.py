from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
DOCS_DIR = PROJECT_ROOT / "docs"
MAX_TRACKED_FILE_BYTES = 50 * 1024 * 1024
MARKDOWN_LINK_PATTERN = re.compile(
    r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))"
)
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"(?i)(?<![\w])[a-z]:[\\/][^\s\"'<>)]*")
UNC_ABSOLUTE_PATH_PATTERN = re.compile(r"(?<!\w)\\\\[^\\/\s]+[\\/][^\s\"'<>)]*")
UNIX_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(?<![\w:])/(?:Users|home|tmp|private|var/tmp|mnt|workspace)/[^\s\"'<>)]*"
)
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sql",
    ".txt",
    ".toml",
    ".xml",
    ".yaml",
    ".yml",
}


class HTMLLinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.targets.append(value)


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return [
        PROJECT_ROOT / Path(path.decode("utf-8"))
        for path in result.stdout.split(b"\0")
        if path
    ]


def document_targets(path):
    text = path.read_text(encoding="utf-8")
    targets = []
    for match in MARKDOWN_LINK_PATTERN.finditer(text):
        targets.append(match.group(1) or match.group(2))

    if path.suffix.lower() == ".html":
        parser = HTMLLinkCollector()
        parser.feed(text)
        targets.extend(parser.targets)
    return targets


def check_target(source_path, target):
    if target.startswith("#"):
        return None

    parts = urlsplit(target)
    if parts.scheme.lower() in ("http", "https", "mailto"):
        return None

    target_path = unquote(parts.path)
    if not target_path:
        return None

    resolved_target = (source_path.parent / target_path).resolve()
    if not resolved_target.exists():
        relative_source = source_path.relative_to(PROJECT_ROOT)
        return ("broken link", str(relative_source), target)
    return None


def check_local_paths(path):
    patterns = (
        WINDOWS_ABSOLUTE_PATH_PATTERN,
        UNC_ABSOLUTE_PATH_PATTERN,
        UNIX_ABSOLUTE_PATH_PATTERN,
    )
    matches = []
    overlap = ""
    with path.open("r", encoding="utf-8", errors="ignore") as input_file:
        while chunk := input_file.read(1024 * 1024):
            text = overlap + chunk
            for pattern in patterns:
                matches.extend(match.group(0) for match in pattern.finditer(text))
            overlap = text[-4096:]
    return matches


def main() -> int:
    problems = []
    files = tracked_files()
    documents = [README_PATH, *sorted(DOCS_DIR.rglob("*.md")), DOCS_DIR / "index.html"]

    for source_path in documents:
        for target in document_targets(source_path):
            problem = check_target(source_path, target)
            if problem:
                problems.append(problem)

    for path in files:
        if not path.is_file():
            continue
        relative_path = path.relative_to(PROJECT_ROOT).as_posix()
        if path.stat().st_size > MAX_TRACKED_FILE_BYTES:
            problems.append(
                ("tracked file over 50 MB", relative_path, f"{path.stat().st_size:,} bytes")
            )
        if path.suffix.lower() == ".ipynb":
            problems.append(("tracked notebook", relative_path, ""))
        if path.suffix.lower() in TEXT_SUFFIXES:
            for local_path in check_local_paths(path):
                problems.append(("absolute local path", relative_path, local_path))

    if problems:
        print(f"{'Problem':30} {'File':45} Details")
        print("-" * 110)
        for kind, source, detail in problems:
            print(f"{kind:30} {source:45} {detail}")
        return 1

    print("No broken relative links, oversized tracked files, local paths, or tracked notebooks found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())