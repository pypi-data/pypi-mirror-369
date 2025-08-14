# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description:
"""
import unittest
import tempfile
import os
import sys

sys.path.append('..')
from run_python_code.code import RunPythonCode


class TestRunPythonCodeMCPServer(unittest.TestCase):
    """Test cases for RunPythonCode MCP Server tools."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = RunPythonCode(base_dir=self.temp_dir)

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_run_python_code_success(self):
        """Test that run_python_code executes code correctly."""
        code = "x = 10\ny = 20\nz = x + y"
        result = self.runner.run_python_code(code, "z")
        self.assertEqual(result, "30")

    def test_run_python_code_no_return_variable(self):
        """Test that run_python_code works without return variable."""
        code = "print('Hello, World!')"
        result = self.runner.run_python_code(code)
        self.assertEqual(result, "successfully ran python code")

    def test_run_python_code_variable_not_found(self):
        """Test that run_python_code handles missing variables."""
        code = "x = 10"
        result = self.runner.run_python_code(code, "y")
        self.assertEqual(result, "Variable y not found")

    def test_run_python_code_syntax_error(self):
        """Test that run_python_code handles syntax errors."""
        code = "x = 10\ny ="  # Incomplete syntax
        result = self.runner.run_python_code(code, "x")
        self.assertIn("Error running python code:", result)

    def test_save_to_file_and_run_success(self):
        """Test that save_to_file_and_run works correctly."""
        code = "a = 5\nb = 15\nc = a * b"
        result = self.runner.save_to_file_and_run("test.py", code, "c")
        self.assertEqual(result, "75")

    def test_save_to_file_and_run_file_exists(self):
        """Test overwrite behavior."""
        code = "x = 100"
        # First save
        self.runner.save_to_file_and_run("test.py", code, overwrite=True)
        # Second save with overwrite=False
        result = self.runner.save_to_file_and_run("test.py", code, overwrite=False)
        self.assertEqual(result, "File test.py already exists")

    def test_run_python_file_return_variable_success(self):
        """Test running an existing Python file."""
        # First create a file
        code = "result = 42\nprint('File executed')"
        self.runner.save_to_file_and_run("calc.py", code)

        # Then run it
        result = self.runner.run_python_file_return_variable("calc.py", "result")
        self.assertEqual(result, "42")

    def test_run_python_file_not_found(self):
        """Test running a non-existent file."""
        result = self.runner.run_python_file_return_variable("nonexistent.py", "x")
        self.assertIn("Error running file:", result)

    def test_pip_install_package_success(self):
        """Test pip package installation (mock test)."""
        # This is a real test that installs a lightweight package
        # You might want to mock this in actual test environments
        result = self.runner.pip_install_package("pip")  # pip installs itself
        self.assertIn("successfully installed package", result)


if __name__ == "__main__":
    unittest.main()