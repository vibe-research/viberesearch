"""Check the actual shipped package, not just isolated helper fixtures."""

import html.parser
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/vibe-research/scripts/research.py"
SPEC = importlib.util.spec_from_file_location("distribution_research", SCRIPT)
research = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research)


class HtmlLinks(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


class DistributionTests(unittest.TestCase):
    def test_archived_records_reserve_their_ids(self):
        with tempfile.TemporaryDirectory(prefix="vibe-research-archive-") as directory:
            project = Path(directory) / "study"

            def run(*args):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), *args],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            run("init", str(project))
            workspace = project / "agent-research"
            for relative in (
                "experiments/archive/exp-007-previous-question.md",
                "methodology/archive/m-004-previous-method.md",
            ):
                record = workspace / relative
                record.parent.mkdir(parents=True, exist_ok=True)
                record.write_text("# Fictional archived record\n", encoding="utf-8")
            run("new-experiment", "next-question", "--root", str(project))
            run("new-experiment", "variation", "--parent", "7", "--root", str(project))
            run("new-methodology", "next-method", "--root", str(project))
            self.assertTrue((workspace / "experiments/exp-008-next-question.md").is_file())
            child = workspace / "experiments/exp-007.001-variation.md"
            self.assertIn("archive/exp-007-previous-question.md", child.read_text())
            self.assertTrue((workspace / "methodology/m-005-next-method.md").is_file())
            run("check", "--root", str(project))

    def test_shipped_assets_complete_round_trip(self):
        with tempfile.TemporaryDirectory(prefix="vibe-research-distribution-") as directory:
            project = Path(directory) / "study"

            def run(script, *args):
                result = subprocess.run(
                    [sys.executable, str(script), *args],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            run(SCRIPT, "init", str(project), "--name", "An actual template smoke test")
            installed = project / SCRIPT.relative_to(ROOT)
            workspace = project / "agent-research"
            initial_files = sorted(workspace.rglob("*.md"))
            self.assertEqual(len(initial_files), 7)
            for path in initial_files:
                self.assertNotIn("{{", path.read_text(), str(path))
            run(installed, "check", "--root", str(project))
            context = run(installed, "context", "--root", str(project))
            self.assertIn("An actual template smoke test", context)
            run(installed, "new-methodology", "baseline", "--root", str(project))
            pointer = workspace / "methodology/current.md"
            pointer.write_text("# Current methodology\n\nActive protocol: [M-001](m-001-baseline.md).\n", encoding="utf-8")
            run(installed, "new-experiment", "bce", "--root", str(project))
            run(installed, "new-experiment", "ce", "--parent", "1", "--root", str(project))
            baseline = workspace / "experiments/exp-001-bce.md"
            variant = workspace / "experiments/exp-001.001-ce.md"
            original = baseline.read_bytes()
            self.assertIn("# Exp 1.1", variant.read_text())
            self.assertIn("../methodology/m-001-baseline.md", variant.read_text())
            run(installed, "new-methodology", "revised", "--root", str(project))
            pointer.write_text("# Current methodology\n\nActive protocol: [M-002](m-002-revised.md).\n", encoding="utf-8")
            run(installed, "new-experiment", "representation", "--root", str(project))
            self.assertEqual(baseline.read_bytes(), original)
            self.assertIn("../methodology/m-002-revised.md", (workspace / "experiments/exp-002-representation.md").read_text())
            run(installed, "check", "--root", str(project))
            run(installed, "snapshot", "--root", str(project))
            archive = next((workspace / "handoffs/snapshots").glob("*.zip"))
            with zipfile.ZipFile(archive) as saved:
                self.assertEqual(saved.read("experiments/exp-001-bce.md"), original)
            run(SCRIPT, "init", str(project))
            self.assertEqual(baseline.read_bytes(), original)
            self.assertIn("m-002-revised.md", pointer.read_text())
            self.assertEqual((project / "AGENTS.md").read_text().count(research.START), 1)

    def test_shipped_document_links_resolve(self):
        documents = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "CONTRIBUTING.md"]
        documents += list((ROOT / "docs").rglob("*.md"))
        skill = ROOT / ".agents/skills/vibe-research"
        documents += [skill / "SKILL.md", *list((skill / "references").glob("*.md"))]
        missing = []
        for document in documents:
            content = document.read_text(encoding="utf-8")
            html_links = HtmlLinks()
            html_links.feed(content)
            for link in [*research.markdown_links(content), *html_links.links]:
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = document.parent / unquote(parsed.path)
                if not target.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {link}")
        self.assertEqual(missing, [], "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
