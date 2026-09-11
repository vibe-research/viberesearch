"""Safety and workflow tests; run with python3 -m unittest discover -s tests."""

import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / ".agents/skills/vibe-research/scripts/research.py"
SPEC = importlib.util.spec_from_file_location("research", SCRIPT)
research = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research)


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "project"
        self.source = self.base / "source-skill"
        self.write(self.source / "SKILL.md", "# Test skill\n")
        self.write(self.source / "assets/AGENTS.md", "Read agent-research/STATE.md.\n")
        for relative in research.REQUIRED:
            self.write(self.source / "assets/workspace" / relative, f"# {relative}\nProject: {{{{PROJECT_NAME}}}}\nDate: {{{{DATE}}}}\n")
        self.write(self.source / "assets/experiment.md", "# {{ID}}: {{TITLE}}\nDate: {{DATE}}\nParent: {{PARENT}}\nProtocol: {{METHODOLOGY}}\nStatus: planned\n")
        self.write(self.source / "assets/methodology.md", "# {{ID}}: {{TITLE}}\nDate: {{DATE}}\nStatus: draft\n")
        patcher = patch.object(research, "SKILL_DIR", self.source)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def command(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = research.main(list(args))
        return code, output.getvalue(), error.getvalue()

    def init(self):
        code, _, error = self.command("init", str(self.root), "--name", "Test project")
        self.assertEqual(code, 0, error)
        return self.root / "agent-research"

    def tree(self, root):
        return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}

    def test_init_preserves_existing_content_and_is_idempotent(self):
        self.write(self.root / "AGENTS.md", "User instructions without final newline")
        self.write(self.root / ".gitignore", "build/\n!important\n")
        self.write(self.root / "agent-research/ideas/INBOX.md", "An idea the user already wrote.\n")
        workspace = self.init()
        self.assertTrue((self.root / "AGENTS.md").read_text().startswith("User instructions without final newline\n"))
        self.assertEqual((workspace / "ideas/INBOX.md").read_text(), "An idea the user already wrote.\n")
        self.assertEqual((self.root / ".gitignore").read_text(), "build/\n!important\n/agent-research/\n")
        self.assertIn("Project: Test project", (workspace / "STATE.md").read_text())
        before = self.tree(self.root)
        self.init()
        self.assertEqual(self.tree(self.root), before)

    def test_changed_skill_collision_is_preflighted_before_any_write(self):
        self.write(self.root / ".agents/skills/vibe-research/SKILL.md", "User customization\n")
        self.write(self.root / "AGENTS.md", "Keep me.\n")
        before = self.tree(self.root)
        code, _, error = self.command("init", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("Existing file differs", error)
        self.assertEqual(self.tree(self.root), before)

    def test_ignore_rule_follows_existing_negation(self):
        self.write(self.root / ".gitignore", "/agent-research/\n!/agent-research/\n")
        self.init()
        self.assertEqual((self.root / ".gitignore").read_text(), "/agent-research/\n!/agent-research/\n/agent-research/\n")
        before = self.tree(self.root)
        self.init()
        self.assertEqual(self.tree(self.root), before)

    def test_changed_bootstrap_collision_is_preflighted(self):
        self.write(self.root / "AGENTS.md", f"{research.START}\nCustom instructions\n{research.END}\n")
        before = self.tree(self.root)
        code, _, error = self.command("init", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("block differs", error)
        self.assertEqual(self.tree(self.root), before)

    def test_symlink_target_cannot_write_outside_project(self):
        outside = self.base / "outside"
        outside.mkdir()
        self.root.mkdir()
        (self.root / "agent-research").symlink_to(outside, target_is_directory=True)
        code, _, error = self.command("init", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("symlink", error)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_context_is_bounded_and_does_not_load_private_inbox(self):
        workspace = self.init()
        self.write(workspace / "ideas/INBOX.md", "UNREQUESTED_IDEA_DETAIL " * 900)
        code, output, error = self.command("context", "--root", str(self.root))
        self.assertEqual(code, 0, error)
        self.assertNotIn("UNREQUESTED_IDEA_DETAIL", output)
        self.assertIn("heuristic", output)
        self.write(workspace / "STATE.md", "word " * 351)
        code, output, error = self.command("context", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("351 words exceeds the 350-word cap", error)
        self.assertIn("No text was truncated", error)

    def test_methodology_is_draft_then_experiment_pins_selected_protocol(self):
        workspace = self.init()
        before = (workspace / "methodology/current.md").read_bytes()
        code, _, error = self.command("new-methodology", "baseline", "--root", str(self.root))
        self.assertEqual(code, 0, error)
        self.assertEqual((workspace / "methodology/current.md").read_bytes(), before)
        protocol = workspace / "methodology/m-001-baseline.md"
        self.assertTrue(protocol.exists())
        self.write(workspace / "methodology/current.md", "Active: [m-001](m-001-baseline.md)\n")
        code, _, error = self.command("new-experiment", "bce", "--root", str(self.root), "--title", "Try BCE")
        self.assertEqual(code, 0, error)
        content = (workspace / "experiments/exp-001-bce.md").read_text()
        self.assertIn("../methodology/m-001-baseline.md", content)
        self.assertIn("Try BCE", content)
        self.assertIn("| [1](exp-001-bce.md) | Try BCE | — | proposed | No observations yet. |", (workspace / "experiments/INDEX.md").read_text())

    def test_experiment_lineage_allocates_siblings_and_major_changes(self):
        workspace = self.init()
        for slug, parent in (("bce", None), ("ce", "exp-001"), ("weighted-ce", "exp-001"), ("temperature", "exp-001.001"), ("contrastive", None)):
            args = ["new-experiment", slug, "--root", str(self.root)]
            if parent:
                args.extend(["--parent", parent])
            code, _, error = self.command(*args)
            self.assertEqual(code, 0, error)
        names = {path.name for path in (workspace / "experiments").glob("exp-*.md")}
        self.assertEqual(names, {"exp-001-bce.md", "exp-001.001-ce.md", "exp-001.002-weighted-ce.md", "exp-001.001.001-temperature.md", "exp-002-contrastive.md"})
        self.assertIn("Unassigned", (workspace / "experiments/exp-001-bce.md").read_text())

    def test_numeric_parent_aliases_and_display_ids(self):
        workspace = self.init()
        for slug, parent in (("bce", None), ("ce", "1"), ("weighted", "1.1")):
            args = ["new-experiment", slug, "--root", str(self.root)]
            if parent:
                args.extend(["--parent", parent])
            code, _, error = self.command(*args)
            self.assertEqual(code, 0, error)
        content = (workspace / "experiments/exp-001.001.001-weighted.md").read_text()
        self.assertIn("# 1.1.1: Weighted", content)
        self.assertIn("[Exp 1.1](exp-001.001-ce.md)", content)

    def test_invalid_parent_and_slug_make_no_records(self):
        workspace = self.init()
        before = self.tree(workspace)
        for args in (("new-experiment", "ce", "--parent", "exp-999"), ("new-experiment", "../escape"), ("new-methodology", "../../escape")):
            code, _, _ = self.command(*args, "--root", str(self.root))
            self.assertEqual(code, 1)
            self.assertEqual(self.tree(workspace), before)

    def test_duplicate_ids_block_check_and_allocation(self):
        workspace = self.init()
        self.write(workspace / "experiments/exp-001-first.md", "# First\n")
        self.write(workspace / "experiments/exp-001-second.md", "# Second\n")
        code, output, _ = self.command("check", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("Duplicate experiment ID exp-001", output)
        before = self.tree(workspace)
        code, _, error = self.command("new-experiment", "third", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("Duplicate experiment ID", error)
        self.assertEqual(self.tree(workspace), before)

    def test_check_reports_links_pointer_and_budget_but_skips_external_artifacts(self):
        workspace = self.init()
        self.write(workspace / "docs/project.md", "[site](https://example.com) [anchor](#plan) [artifact](../../results/model.bin)\n[local](missing.md)\n")
        self.write(workspace / "methodology/current.md", "Active: [m-001](m-001-missing.md)\n")
        self.write(workspace / "STATE.md", "word " * 351)
        code, output, error = self.command("check", "--root", str(self.root))
        self.assertEqual(code, 1, error)
        self.assertIn("Broken local link in docs/project.md: missing.md", output)
        self.assertIn("Active methodology pointer is broken", output)
        self.assertIn("Context budget", output)
        self.assertNotIn("model.bin", output)
        self.assertIn("not scientific validation", output)
        code, _, error = self.command("new-experiment", "blocked", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("Active methodology pointer is broken", error)

    def test_check_handles_reference_links_and_encoded_spaces(self):
        workspace = self.init()
        self.write(workspace / "docs/with space.md", "# Existing file\n")
        self.write(workspace / "docs/project.md", "[good](with%20space.md#anchor)\n[also good](<with space.md>)\n[missing]: missing.md\n")
        code, output, _ = self.command("check", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("missing.md", output)
        self.assertNotIn("Broken local link in docs/project.md: with", output)

    def test_code_examples_are_not_treated_as_live_links(self):
        workspace = self.init()
        self.write(workspace / "docs/project.md", "Example: `[example](inline-missing.md)`\n```markdown\n[fenced](fenced-missing.md)\n```\n~~~\n[tilde](tilde-missing.md)\n~~~\n")
        code, output, error = self.command("check", "--root", str(self.root))
        self.assertEqual(code, 0, error + output)

    def test_active_methodology_requires_link_or_explicit_unassigned(self):
        workspace = self.init()
        for assignment in ("baseline", "`m-001-baseline.md`", ""):
            self.write(workspace / "methodology/current.md", f"Active protocol: {assignment}\n")
            code, output, _ = self.command("check", "--root", str(self.root))
            self.assertEqual(code, 1)
            self.assertIn("Active protocol needs one local Markdown link", output)

    def test_unassigned_protocol_does_not_activate_a_linked_draft(self):
        workspace = self.init()
        self.write(workspace / "methodology/m-001-draft.md", "# Draft\n")
        self.write(workspace / "methodology/current.md", "Active protocol: none\nDraft to review: [M-001](m-001-draft.md)\n")
        code, _, error = self.command("new-experiment", "bce", "--root", str(self.root))
        self.assertEqual(code, 0, error)
        content = (workspace / "experiments/exp-001-bce.md").read_text()
        self.assertIn("Unassigned", content)
        self.assertNotIn("m-001-draft.md", content)

    def test_active_protocol_ignores_predecessor_link_in_rationale(self):
        workspace = self.init()
        self.write(workspace / "methodology/m-001-previous.md", "# Previous\n")
        self.write(workspace / "methodology/m-002-active.md", "# Active\n")
        self.write(workspace / "methodology/current.md", "Active protocol: [M-002](m-002-active.md)\nRationale: supersedes [M-001](m-001-previous.md).\n")
        code, _, error = self.command("new-experiment", "bce", "--root", str(self.root))
        self.assertEqual(code, 0, error)
        content = (workspace / "experiments/exp-001-bce.md").read_text()
        self.assertIn("../methodology/m-002-active.md", content)
        self.assertNotIn("m-001-previous.md", content)

    def test_init_does_not_copy_python_or_editor_runtime_residue(self):
        self.write(self.source / "scripts/__pycache__/research.cpython-312.pyc", "cache")
        self.write(self.source / "scripts/research.py.swp", "editor temporary")
        self.write(self.source / "scripts/research.py.tmp", "temporary")
        self.init()
        installed = self.root / ".agents/skills/vibe-research"
        self.assertFalse((installed / "scripts/__pycache__").exists())
        self.assertFalse((installed / "scripts/research.py.swp").exists())
        self.assertFalse((installed / "scripts/research.py.tmp").exists())

    def test_snapshot_excludes_prior_archives_and_temporary_files(self):
        workspace = self.init()
        self.write(workspace / "docs/notes.md", "Evidence to preserve.\n")
        self.write(workspace / "docs/scratch.tmp", "Not durable.\n")
        for _ in range(2):
            code, _, error = self.command("snapshot", "--root", str(self.root))
            self.assertEqual(code, 0, error)
        archives = sorted((workspace / "handoffs/snapshots").glob("*.zip"))
        self.assertEqual(len(archives), 2)
        for archive in archives:
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertIn("STATE.md", names)
                self.assertEqual(bundle.read("docs/notes.md"), b"Evidence to preserve.\n")
                self.assertNotIn("docs/scratch.tmp", names)
                self.assertNotIn(".research.lock", names)
                self.assertFalse(any(name.endswith(".zip") or name.startswith("/") or ".." in Path(name).parts for name in names))

    def test_snapshot_refuses_symlinks_without_copying_external_content(self):
        workspace = self.init()
        outside = self.base / "secret.txt"
        self.write(outside, "External content\n")
        (workspace / "docs/link.txt").symlink_to(outside)
        code, _, error = self.command("snapshot", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("symlink", error)
        self.assertFalse((workspace / "handoffs/snapshots").exists())
        self.assertFalse((workspace / ".research.lock").exists())

    def test_failed_snapshot_does_not_leave_an_incomplete_archive(self):
        workspace = self.init()
        with patch.object(zipfile.ZipFile, "write", side_effect=OSError("simulated read failure")):
            code, _, error = self.command("snapshot", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("simulated read failure", error)
        self.assertEqual(list((workspace / "handoffs/snapshots").iterdir()), [])
        self.assertFalse((workspace / ".research.lock").exists())

    def test_existing_lock_prevents_mutation(self):
        workspace = self.init()
        self.write(workspace / ".research.lock", "pid=another-command\n")
        before = self.tree(workspace)
        code, _, error = self.command("new-experiment", "concurrent", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("Workspace is locked", error)
        self.assertEqual(self.tree(workspace), before)

    def test_index_update_failure_rolls_back_only_just_created_record(self):
        workspace = self.init()
        before = self.tree(workspace)
        with patch.object(research, "replace_checked", side_effect=OSError("simulated disk failure")):
            code, _, error = self.command("new-experiment", "bce", "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("simulated disk failure", error)
        self.assertEqual(self.tree(workspace), before)

    def test_root_option_works_before_command(self):
        self.init()
        code, output, error = self.command("--root", str(self.root), "check")
        self.assertEqual(code, 0, error)
        self.assertIn("Structural check passed", output)

    def test_root_with_parent_components_still_audits_links(self):
        workspace = self.init()
        self.write(workspace / "docs/project.md", "[missing](missing.md)\n")
        root = self.root / "agent-research/.."
        code, output, error = self.command("check", "--root", str(root))
        self.assertEqual(code, 1, error)
        self.assertIn("Broken local link", output)


if __name__ == "__main__":
    unittest.main()
