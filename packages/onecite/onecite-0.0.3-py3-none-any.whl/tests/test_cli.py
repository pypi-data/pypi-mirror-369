"""
测试命令行界面功能
基于README声明的CLI功能进行测试
"""
import pytest
import subprocess
import os
import tempfile
from pathlib import Path

class TestCLI:
    """命令行界面测试"""

    def run_onecite_command(self, args, cwd=None):
        """运行onecite命令的辅助方法"""
        cmd = ["onecite"] + args
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "onecite command not found"

    def test_help_command(self):
        """测试--help命令"""
        code, stdout, stderr = self.run_onecite_command(["--help"])
        assert code == 0, f"Help command failed: {stderr}"
        assert "Universal citation management" in stdout
        assert "process" in stdout

    def test_version_command(self):
        """测试--version命令"""
        code, stdout, stderr = self.run_onecite_command(["--version"])
        assert code == 0, f"Version command failed: {stderr}"
        assert "onecite" in stdout.lower()

    def test_process_help(self):
        """测试process子命令的帮助"""
        code, stdout, stderr = self.run_onecite_command(["process", "--help"])
        assert code == 0, f"Process help failed: {stderr}"
        
        # 检查所有README中提到的选项
        expected_options = [
            "--input-type", "--output-format", "--template", 
            "--interactive", "--quiet", "--output"
        ]
        for option in expected_options:
            assert option in stdout, f"Missing CLI option: {option}"

    def test_input_type_choices(self):
        """测试输入类型选择"""
        code, stdout, stderr = self.run_onecite_command(["process", "--help"])
        assert "{txt,bib}" in stdout, "Input type choices not found"

    def test_output_format_choices(self):
        """测试输出格式选择"""
        code, stdout, stderr = self.run_onecite_command(["process", "--help"])
        assert "{bibtex,apa,mla}" in stdout, "Output format choices not found"

    def test_invalid_file_error(self):
        """测试无效文件错误处理"""
        code, stdout, stderr = self.run_onecite_command(["process", "nonexistent_file.txt"])
        assert code != 0, "Should return error for nonexistent file"

    def test_invalid_output_format_error(self, create_test_file, sample_references):
        """测试无效输出格式错误处理"""
        test_file = create_test_file(sample_references["doi_only"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--output-format", "invalid"
        ])
        assert code != 0, "Should return error for invalid output format"
