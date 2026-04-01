from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent import SkillReferenceError, build_system_prompt, load_skill_reference
from config import Settings


class SkillReferenceLoadingTests(unittest.TestCase):
    def _make_settings(self, root: Path) -> Settings:
        backend_root = root / "backend"
        web_root = root / "web"
        backend_root.mkdir()
        web_root.mkdir()
        return Settings(
            app_root=root,
            backend_root=backend_root,
            web_root=web_root,
            idabus_root=root / "idabus-go",
            openai_api_key="test-key",
            openai_model="gpt-4.1-mini",
            chat_max_tool_rounds=8,
            session_ttl_seconds=3600,
        )

    def _write_skill_fixture(self, root: Path) -> None:
        idabus_root = root / "idabus-go"
        references_root = idabus_root / "references"
        references_root.mkdir(parents=True)
        (references_root / "api_spec.json").write_text(
            json.dumps(
                {
                    "endpoints": [
                        {
                            "name": "get-resource-by-id",
                            "method": "GET",
                            "path": "/resources/{id}",
                            "description": "Fetch one resource.",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (idabus_root / "SKILL.md").write_text(
            "\n".join(
                [
                    "# Idabus",
                    "Use `references/object_types_and_attributes.md` when object details are needed.",
                    "Use `references/idabus_xpath_dialect.md` for XPath syntax.",
                ]
            ),
            encoding="utf-8",
        )
        (references_root / "object_types_and_attributes.md").write_text(
            "object reference content",
            encoding="utf-8",
        )
        (references_root / "idabus_xpath_dialect.md").write_text(
            "xpath reference content",
            encoding="utf-8",
        )
        (references_root / "not_mentioned.md").write_text(
            "should not load",
            encoding="utf-8",
        )

    def test_load_skill_reference_succeeds_for_referenced_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)

            path, content = load_skill_reference(
                root / "idabus-go",
                "references/object_types_and_attributes.md",
            )

            self.assertEqual(path, "references/object_types_and_attributes.md")
            self.assertEqual(content, "object reference content")

    def test_load_skill_reference_rejects_unmentioned_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)

            with self.assertRaises(SkillReferenceError):
                load_skill_reference(root / "idabus-go", "references/not_mentioned.md")

    def test_load_skill_reference_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)

            with self.assertRaises(SkillReferenceError):
                load_skill_reference(root / "idabus-go", "../backend/config.py")

    def test_build_system_prompt_includes_loaded_references_once_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_skill_fixture(root)
            settings = self._make_settings(root)

            prompt = build_system_prompt(
                settings,
                {"references/object_types_and_attributes.md": "object reference content"},
            )

            self.assertIn("Local skill instructions:", prompt)
            self.assertIn("Loaded local references:", prompt)
            self.assertIn("references/object_types_and_attributes.md", prompt)
            self.assertIn("object reference content", prompt)


if __name__ == "__main__":
    unittest.main()
