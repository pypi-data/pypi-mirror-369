import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from boilersync.commands.pull import (
    get_parent_template,
    get_template_inheritance_chain,
)


class TestTemplateInheritance(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.boilerplate_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_template_dir(self, name: str, parent: str | None = None) -> Path:
        """Create a template directory with optional parent reference.

        Args:
            name: Template name
            parent: Parent template name if any

        Returns:
            Path to the created template directory
        """
        template_dir = self.boilerplate_dir / name
        template_dir.mkdir(parents=True)

        if parent:
            template_json = template_dir / "template.json"
            with open(template_json, "w") as f:
                json.dump({"parent": parent}, f)

        # Create a dummy file to make it a valid template
        (template_dir / "README.md").write_text("# {{name_pretty}}\n")

        return template_dir

    def test_get_parent_template_with_parent(self):
        """Test getting parent template when template.json exists with parent."""
        template_dir = self.create_template_dir("child", "parent")

        parent = get_parent_template(template_dir)
        self.assertEqual(parent, "parent")

    def test_get_parent_template_without_parent(self):
        """Test getting parent template when template.json doesn't exist."""
        template_dir = self.create_template_dir("standalone")

        parent = get_parent_template(template_dir)
        self.assertIsNone(parent)

    def test_get_parent_template_empty_json(self):
        """Test getting parent template when template.json exists but has no parent."""
        template_dir = self.create_template_dir("child")
        template_json = template_dir / "template.json"
        with open(template_json, "w") as f:
            json.dump({"other_key": "value"}, f)

        parent = get_parent_template(template_dir)
        self.assertIsNone(parent)

    def test_get_parent_template_invalid_json(self):
        """Test getting parent template when template.json has invalid JSON."""
        template_dir = self.create_template_dir("child")
        template_json = template_dir / "template.json"
        template_json.write_text("invalid json")

        parent = get_parent_template(template_dir)
        self.assertIsNone(parent)

    @patch("boilersync.commands.pull.paths")
    def test_inheritance_chain_single_template(self, mock_paths):
        """Test inheritance chain for a template with no parent."""
        mock_paths.boilerplate_dir = self.boilerplate_dir
        self.create_template_dir("standalone")

        chain = get_template_inheritance_chain("standalone")
        self.assertEqual(chain, ["standalone"])

    @patch("boilersync.commands.pull.paths")
    def test_inheritance_chain_two_levels(self, mock_paths):
        """Test inheritance chain for parent -> child."""
        mock_paths.boilerplate_dir = self.boilerplate_dir
        self.create_template_dir("parent")
        self.create_template_dir("child", "parent")

        chain = get_template_inheritance_chain("child")
        self.assertEqual(chain, ["parent", "child"])

    @patch("boilersync.commands.pull.paths")
    def test_inheritance_chain_three_levels(self, mock_paths):
        """Test inheritance chain for grandparent -> parent -> child."""
        mock_paths.boilerplate_dir = self.boilerplate_dir
        self.create_template_dir("grandparent")
        self.create_template_dir("parent", "grandparent")
        self.create_template_dir("child", "parent")

        chain = get_template_inheritance_chain("child")
        self.assertEqual(chain, ["grandparent", "parent", "child"])

    @patch("boilersync.commands.pull.paths")
    def test_inheritance_chain_circular_dependency(self, mock_paths):
        """Test that circular dependencies are detected."""
        mock_paths.boilerplate_dir = self.boilerplate_dir
        self.create_template_dir("template_a", "template_b")
        self.create_template_dir("template_b", "template_a")

        with self.assertRaises(ValueError) as cm:
            get_template_inheritance_chain("template_a")

        self.assertIn("Circular dependency", str(cm.exception))

    @patch("boilersync.commands.pull.paths")
    def test_inheritance_chain_missing_parent(self, mock_paths):
        """Test handling of missing parent template."""
        mock_paths.boilerplate_dir = self.boilerplate_dir
        self.create_template_dir("child", "nonexistent_parent")

        with self.assertRaises(FileNotFoundError) as cm:
            get_template_inheritance_chain("child")

        self.assertIn("nonexistent_parent", str(cm.exception))

    @patch("boilersync.commands.pull.paths")
    def test_inheritance_chain_missing_child(self, mock_paths):
        """Test handling of missing child template."""
        mock_paths.boilerplate_dir = self.boilerplate_dir

        with self.assertRaises(FileNotFoundError) as cm:
            get_template_inheritance_chain("nonexistent_child")

        self.assertIn("nonexistent_child", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
