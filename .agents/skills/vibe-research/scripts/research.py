#!/usr/bin/env python3
"""Small, offline helpers for a private, Markdown-based research workspace."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile


SKILL_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = "agent-research"
START = "<!-- vibe-research:start -->"
END = "<!-- vibe-research:end -->"
CONTEXT_CAPS = {
    "STATE.md": 350,
    "docs/project.md": 500,
    "methodology/current.md": 200,
    "handoffs/LATEST.md": 350,
}
REQUIRED = (*CONTEXT_CAPS, "ideas/INBOX.md", "reviews/OPEN.md", "experiments/INDEX.md")
EXP_FILE = re.compile(r"^(exp-\d{3,}(?:\.\d{3,})*)(?:-[a-z0-9-]+)?\.md$")
EXP_ID = re.compile(r"^exp-\d{3,}(?:\.\d{3,})*$")
METHOD_FILE = re.compile(r"^(m-\d{3,})(?:-[a-z0-9-]+)?\.md$")
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[^)]+)?\)")
REFERENCE_LINK = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", re.MULTILINE)


class ResearchError(Exception):
    """A problem the researcher can resolve without a Python traceback."""


def safe_path(path: Path) -> Path:
    """Refuse symlinks in managed paths, including their existing parents."""
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ResearchError(f"Refusing symlink in managed path: {part}")
    return Path(os.path.abspath(path))


def read_text(path: Path) -> str:
    safe_path(path)
    return path.read_text(encoding="utf-8")


def files_below(root: Path):
    """Walk deterministically without following symlinks."""
    safe_path(root)
    for child in sorted(root.iterdir()):
        if child.is_symlink():
            raise ResearchError(f"Refusing symlink in workspace/package: {child}")
        if child.is_dir():
            if child.name != "__pycache__":
                yield from files_below(child)
        elif child.is_file() and child.suffix != ".pyc":
            yield child
        else:
            raise ResearchError(f"Unsupported filesystem entry: {child}")


def render(text: str, **values: str) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def clean_text(value: str, label: str) -> str:
    if not value.strip() or any(ord(char) < 32 for char in value):
        raise ResearchError(f"{label} must be nonempty and fit on one line.")
    return value.strip()


def slug_text(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ResearchError("Use a lowercase slug with letters, digits, and single hyphens.")
    return value


def canonical_experiment_id(value: str) -> str:
    if not re.fullmatch(r"(?:exp-)?\d+(?:\.\d+)*", value):
        raise ResearchError(f"Invalid experiment ID: {value}. Use 1, 1.1, or exp-001.001.")
    numbers = [int(part) for part in value.removeprefix("exp-").split(".")]
    if any(number < 1 for number in numbers):
        raise ResearchError("Experiment ID components must be positive integers.")
    return "exp-" + ".".join(f"{number:03d}" for number in numbers)


def display_experiment_id(value: str) -> str:
    return ".".join(str(int(part)) for part in value.removeprefix("exp-").split("."))


def exclusive_write(path: Path, data: bytes) -> None:
    safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def replace_checked(path: Path, before: bytes, after: bytes) -> None:
    """Replace one known file atomically; detect intervening edits before replacement."""
    safe_path(path)
    if path.read_bytes() != before:
        raise ResearchError(f"File changed during this command; retry after reviewing: {path}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".research-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(after)
        temporary.chmod(path.stat().st_mode & 0o777)
        if path.read_bytes() != before:
            raise ResearchError(f"File changed during this command; retry after reviewing: {path}")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def append_text(existing: bytes, addition: str) -> bytes:
    separator = b"" if not existing or existing.endswith(b"\n") else b"\n"
    return existing + separator + addition.encode("utf-8")


def init_workspace(root: Path, name: str | None) -> None:
    root = safe_path(root)
    project_name = clean_text(name or root.name, "Project name")
    assets = SKILL_DIR / "assets"
    template_root = assets / "workspace"
    if not template_root.is_dir():
        raise ResearchError(f"Workspace templates are missing: {template_root}")
    for relative in ("SKILL.md", "assets/AGENTS.md", "assets/experiment.md", "assets/methodology.md"):
        if not (SKILL_DIR / relative).is_file():
            raise ResearchError(f"Required skill file is missing: {relative}")
    for relative in REQUIRED:
        if not (template_root / relative).is_file():
            raise ResearchError(f"Required workspace template is missing: {relative}")

    # Build the complete plan first. A changed installed skill causes no writes.
    planned: dict[Path, tuple[bytes | None, bytes]] = {}

    def plan(path: Path, data: bytes, preserve: bool = False) -> None:
        safe_path(path)
        for ancestor in path.parents:
            if ancestor.exists() and not ancestor.is_dir():
                raise ResearchError(f"Expected a directory: {ancestor}")
        if path.exists():
            if not path.is_file():
                raise ResearchError(f"Expected a file: {path}")
            if preserve:
                return
            if path.read_bytes() != data:
                raise ResearchError(f"Existing file differs; no files were changed: {path}")
        else:
            planned[path] = (None, data)

    for source in files_below(SKILL_DIR):
        if source.name.endswith((".lock", ".tmp", ".temp", ".swp", "~")):
            continue
        plan(root / ".agents/skills/vibe-research" / source.relative_to(SKILL_DIR), source.read_bytes())
    for source in files_below(template_root):
        content = render(read_text(source), PROJECT_NAME=project_name, DATE=date.today().isoformat())
        plan(root / WORKSPACE / source.relative_to(template_root), content.encode("utf-8"), preserve=True)

    bootstrap = render(read_text(assets / "AGENTS.md"), PROJECT_NAME=project_name, DATE=date.today().isoformat()).strip()
    block = f"{START}\n{bootstrap}\n{END}\n"
    agents = safe_path(root / "AGENTS.md")
    before = agents.read_bytes() if agents.exists() else None
    old_text = before.decode("utf-8") if before is not None else ""
    if START in old_text or END in old_text:
        if old_text.count(START) != 1 or old_text.count(END) != 1:
            raise ResearchError("AGENTS.md has malformed or repeated vibe-research markers; review them before init.")
        start, end = old_text.index(START), old_text.index(END)
        if end < start or old_text[start:end + len(END)] != block.rstrip("\n"):
            raise ResearchError("The existing vibe-research block differs; review it manually before updating. No files were changed.")
    else:
        planned[agents] = (before, append_text(before or b"", ("\n" if before else "") + block))

    ignore = safe_path(root / ".gitignore")
    before = ignore.read_bytes() if ignore.exists() else None
    rules = [line.strip() for line in (before or b"").splitlines() if line.strip() and not line.lstrip().startswith(b"#")]
    if not rules or rules[-1] != b"/agent-research/":
        planned[ignore] = (before, append_text(before or b"", "/agent-research/\n"))

    for path, (before, after) in planned.items():
        if before is None:
            exclusive_write(path, after)
        else:
            replace_checked(path, before, after)
    print(f"Research workspace ready: {root / WORKSPACE}")
    print(f"Created or updated {len(planned)} files; existing research notes were preserved.")
    print("The workspace is gitignored. This does not untrack files already committed to Git.")


def workspace_for(root: Path) -> Path:
    workspace = safe_path(root / WORKSPACE)
    if not workspace.is_dir():
        raise ResearchError(f"No research workspace at {workspace}. Run init first.")
    return workspace


def word_count(text: str) -> int:
    return len(text.split())


def context(root: Path) -> None:
    workspace = workspace_for(root)
    sections = []
    problems = []
    for relative, cap in CONTEXT_CAPS.items():
        path = workspace / relative
        if not path.is_file():
            problems.append(f"Missing {relative}")
            continue
        content = read_text(path)
        count = word_count(content)
        if count > cap:
            problems.append(f"{relative}: {count} words exceeds the {cap}-word cap")
        sections.append((relative, content, count))
    if problems:
        raise ResearchError("Cannot emit bounded context:\n  " + "\n  ".join(problems) + "\nMove durable detail to linked records, then condense these summaries. No text was truncated.")
    characters = sum(len(content) for _, content, _ in sections)
    print(f"Startup context: {sum(count for _, _, count in sections)} words; approximately {math.ceil(characters / 4)} tokens (characters / 4 heuristic, not a tokenizer or guarantee).")
    for relative, content, count in sections:
        print(f"\n--- {relative} ({count}/{CONTEXT_CAPS[relative]} words) ---\n{content.rstrip()}")


def prose_only(text: str) -> str:
    """Ignore common fenced and inline code examples during the Markdown audit."""
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence is None and marker:
            fence = marker.group(1)
        elif fence is not None:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
        else:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "".join(lines), flags=re.DOTALL)


def markdown_links(text: str):
    text = prose_only(text)
    for pattern in (INLINE_LINK, REFERENCE_LINK):
        for match in pattern.finditer(text):
            yield match.group(1).strip("<>")


def local_target(source: Path, link: str, workspace: Path) -> Path | None:
    if link.startswith("#"):
        return None
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = Path(unquote(parsed.path))
    if path.is_absolute():
        return None  # Explicit artifact paths are outside the managed link audit.
    target = Path(os.path.abspath(source.parent / path))
    if not target.is_relative_to(workspace.absolute()):
        return None  # Explicit external artifact references are allowed.
    safe_path(target)
    return target


def active_methodology(workspace: Path) -> Path | None:
    pointer = workspace / "methodology/current.md"
    if not pointer.is_file():
        raise ResearchError("Missing methodology/current.md; restore the pointer before creating records.")
    content = read_text(pointer)
    assignment = re.search(r"^[ \t]*Active protocol:[ \t]*(.*)$", prose_only(content), re.MULTILINE | re.IGNORECASE)
    if assignment and re.match(r"(?:none|unassigned)\b", assignment.group(1), re.IGNORECASE):
        return None
    # An explicit assignment is authoritative; rationale may link earlier or draft protocols.
    selection = assignment.group(1) if assignment else content
    candidates = set()
    for link in markdown_links(selection):
        target = local_target(pointer, link, workspace)
        if target is not None and target.parent == workspace / "methodology" and METHOD_FILE.fullmatch(target.name):
            if not target.is_file():
                raise ResearchError(f"Active methodology pointer is broken: {link}")
            candidates.add(target)
    if len(candidates) > 1:
        raise ResearchError("The active methodology selection links multiple versioned protocols. Put one protocol link on the 'Active protocol:' line.")
    if not candidates and assignment:
        raise ResearchError("Active protocol needs one local Markdown link to an existing methodology/m-NNN-slug.md, or an explicit 'none'/'unassigned'.")
    return next(iter(candidates), None)


def experiment_records(workspace: Path) -> dict[str, Path]:
    records = {}
    directory = workspace / "experiments"
    if not directory.is_dir():
        raise ResearchError("Missing experiments directory. Run init to restore missing templates.")
    for path in files_below(directory):
        match = EXP_FILE.fullmatch(path.name)
        if match:
            identifier = canonical_experiment_id(match.group(1))
            if identifier in records:
                raise ResearchError(f"Duplicate experiment ID {identifier}: {records[identifier].name} and {path.name}")
            records[identifier] = path
    return records


def check(root: Path) -> bool:
    workspace = workspace_for(root)
    problems = []
    for relative in REQUIRED:
        if not (workspace / relative).is_file():
            problems.append(f"Missing required file: {relative}")
    for relative, cap in CONTEXT_CAPS.items():
        path = workspace / relative
        if path.is_file():
            count = word_count(read_text(path))
            if count > cap:
                problems.append(f"Context budget: {relative} has {count} words (cap {cap}); condense and link detail.")
    paths = list(files_below(workspace))
    for path in paths:
        if path.suffix.lower() != ".md":
            continue
        for link in markdown_links(read_text(path)):
            target = local_target(path, link, workspace)
            if target is not None and not target.exists():
                problems.append(f"Broken local link in {path.relative_to(workspace)}: {link}")
    for validator in (experiment_records, active_methodology):
        try:
            validator(workspace)
        except ResearchError as error:
            problems.append(str(error))
    if problems:
        print("Structural check failed:")
        for problem in problems:
            print(f"- {problem}")
    else:
        print("Structural check passed: required files, context word caps, local file links, experiment IDs, and active protocol pointer.")
    print("This is not scientific validation. Claims, provenance, statistics, Markdown anchor targets, and external artifacts still require review.")
    return not problems


@contextmanager
def workspace_lock(workspace: Path):
    lock = workspace / ".research.lock"
    try:
        exclusive_write(lock, f"pid={os.getpid()}\n".encode("utf-8"))
    except FileExistsError:
        raise ResearchError(f"Workspace is locked: {lock}. If no command is running, inspect and remove the stale lock manually.") from None
    try:
        yield
    finally:
        lock.unlink()


def new_experiment(root: Path, slug: str, parent: str | None, title: str | None) -> None:
    workspace = workspace_for(root)
    slug = slug_text(slug)
    title = clean_text(title or slug.replace("-", " ").capitalize(), "Title")
    if parent is not None:
        parent = canonical_experiment_id(parent)
    with workspace_lock(workspace):
        records = experiment_records(workspace)
        if parent is not None and (not EXP_ID.fullmatch(parent) or parent not in records):
            raise ResearchError(f"Unknown or invalid parent experiment: {parent}. Use an existing ID such as exp-001.")
        prefix = parent + "." if parent else "exp-"
        siblings = [int(identifier[len(prefix):]) for identifier in records if identifier.startswith(prefix) and "." not in identifier[len(prefix):]]
        identifier = prefix + f"{max(siblings, default=0) + 1:03d}"
        path = workspace / "experiments" / f"{identifier}-{slug}.md"
        protocol = active_methodology(workspace)
        methodology = f"[{protocol.stem}](../methodology/{protocol.name})" if protocol else "Unassigned — choose a versioned protocol before running."
        parent_link = f"[Exp {display_experiment_id(parent)}]({os.path.relpath(records[parent], path.parent)})" if parent else "None (major experiment)"
        template = read_text(SKILL_DIR / "assets/experiment.md")
        display_id = display_experiment_id(identifier)
        content = render(template, ID=display_id, TITLE=title, DATE=date.today().isoformat(), PARENT=parent_link, METHODOLOGY=methodology)
        index = safe_path(workspace / "experiments/INDEX.md")
        before = index.read_bytes()
        row_title = title.replace("|", "\\|")
        row = f"| [{display_id}]({path.name}) | {row_title} | {display_experiment_id(parent) if parent else '—'} | proposed | No observations yet. |\n"
        exclusive_write(path, content.encode("utf-8"))
        try:
            replace_checked(index, before, append_text(before, row))
        except Exception:
            # Remove only the exact, just-created file if the index update failed.
            if path.read_bytes() == content.encode("utf-8"):
                path.unlink()
            raise
    print(f"Created {path}")
    print("Complete the plan and review the pinned protocol before execution; no experiment was run.")


def new_methodology(root: Path, slug: str, title: str | None) -> None:
    workspace = workspace_for(root)
    slug = slug_text(slug)
    title = clean_text(title or slug.replace("-", " ").capitalize(), "Title")
    with workspace_lock(workspace):
        directory = workspace / "methodology"
        existing = []
        for path in files_below(directory):
            match = METHOD_FILE.fullmatch(path.name)
            if match:
                existing.append(int(match.group(1)[2:]))
        identifier = f"m-{max(existing, default=0) + 1:03d}"
        path = directory / f"{identifier}-{slug}.md"
        template = read_text(SKILL_DIR / "assets/methodology.md")
        content = render(template, ID=identifier, TITLE=title, DATE=date.today().isoformat())
        exclusive_write(path, content.encode("utf-8"))
    print(f"Created draft protocol {path}")
    print("It is not active. After discussion, update methodology/current.md to link this protocol and record why it changed.")


def snapshot(root: Path) -> None:
    workspace = workspace_for(root)
    with workspace_lock(workspace):
        destination = workspace / "handoffs/snapshots"
        members = []
        for path in files_below(workspace):
            if path.parent == destination and path.suffix == ".zip":
                continue
            if path.name == ".research.lock" or path.name.endswith((".lock", ".tmp", ".temp", ".swp", "~")):
                continue
            members.append(path)
        safe_path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        archive = destination / f"research-{stamp}.zip"
        created = False
        try:
            with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
                created = True
                for path in members:
                    safe_path(path)
                    bundle.write(path, arcname=path.relative_to(workspace).as_posix())
        except BaseException:
            if created:
                archive.unlink()  # Do not leave a failed snapshot looking complete.
            raise
    print(f"Created snapshot {archive} ({len(members)} files).")
    print("Existing snapshots are never overwritten. This local, gitignored archive is not an off-device backup; copy it to a durable location yourself.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
    commands = result.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init", help="Install the skill and initialize a private workspace without replacing notes")
    initialize.add_argument("path", type=Path, help="Target project directory")
    initialize.add_argument("--name", help="Human-readable project name")
    for name, description in (("context", "Print the four bounded startup summaries"), ("check", "Check structure and local file links, not scientific correctness"), ("new-experiment", "Create a planned experiment and append its index row"), ("new-methodology", "Create a draft protocol without activating it"), ("snapshot", "Create a new local ZIP without overwriting earlier snapshots")):
        command = commands.add_parser(name, help=description)
        command.add_argument("--root", type=Path, default=argparse.SUPPRESS, help="Project root (default: current directory)")
        if name in {"new-experiment", "new-methodology"}:
            command.add_argument("slug", help="Lowercase hyphenated filename suffix")
            command.add_argument("--title", help="Human-readable title")
        if name == "new-experiment":
            command.add_argument("--parent", help="Existing parent ID, for example 1, 1.1, or exp-001.001")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            init_workspace(args.path, args.name)
        elif args.command == "context":
            context(args.root)
        elif args.command == "check":
            return 0 if check(args.root) else 1
        elif args.command == "new-experiment":
            new_experiment(args.root, args.slug, args.parent, args.title)
        elif args.command == "new-methodology":
            new_methodology(args.root, args.slug, args.title)
        elif args.command == "snapshot":
            snapshot(args.root)
        return 0
    except (ResearchError, OSError, UnicodeError, ValueError) as error:
        print(f"research: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
