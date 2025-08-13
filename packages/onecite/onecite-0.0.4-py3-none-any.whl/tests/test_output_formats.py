"""
测试输出格式支持
验证BibTeX, APA, MLA输出格式
"""
import pytest
import subprocess
import re

class TestOutputFormats:
    """输出格式测试"""

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

    def test_bibtex_output_default(self, create_test_file, sample_references):
        """测试BibTeX输出（默认格式）"""
        test_file = create_test_file(sample_references["doi_only"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        assert code == 0, f"BibTeX output failed: {stderr}"
        
        # 验证BibTeX格式特征
        assert "@article" in stdout or "@inproceedings" in stdout, "Missing BibTeX entry type"
        assert "title" in stdout.lower(), "Missing title field"
        assert "author" in stdout.lower(), "Missing author field"
        assert "{" in stdout and "}" in stdout, "Missing BibTeX braces"

    def test_bibtex_output_explicit(self, create_test_file, sample_references):
        """测试显式指定BibTeX输出"""
        test_file = create_test_file(sample_references["doi_only"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--output-format", "bibtex", "--quiet"
        ])
        assert code == 0, f"Explicit BibTeX output failed: {stderr}"
        assert "@" in stdout, "Missing BibTeX entry marker"

    def test_apa_output_format(self, create_test_file, sample_references):
        """测试APA格式输出"""
        test_file = create_test_file(sample_references["doi_only"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--output-format", "apa", "--quiet"
        ])
        assert code == 0, f"APA output failed: {stderr}"
        
        # APA格式特征：年份在括号中，有句点分隔
        # 注意：这些是基本的APA格式特征，实际格式可能更复杂
        output_lower = stdout.lower()
        # 至少应该包含一些标点和结构
        assert len(stdout.strip()) > 0, "APA output should not be empty"

    def test_mla_output_format(self, create_test_file, sample_references):
        """测试MLA格式输出"""
        test_file = create_test_file(sample_references["doi_only"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--output-format", "mla", "--quiet"
        ])
        assert code == 0, f"MLA output failed: {stderr}"
        
        # MLA格式基本验证
        assert len(stdout.strip()) > 0, "MLA output should not be empty"

    def test_output_format_consistency(self, create_test_file, sample_references):
        """测试不同输出格式的一致性"""
        test_file = create_test_file(sample_references["doi_only"])
        
        formats = ["bibtex", "apa", "mla"]
        outputs = {}
        
        for fmt in formats:
            code, stdout, stderr = self.run_onecite_command([
                "process", test_file, "--output-format", fmt, "--quiet"
            ])
            assert code == 0, f"{fmt} format failed: {stderr}"
            outputs[fmt] = stdout
            assert len(stdout.strip()) > 0, f"{fmt} output should not be empty"

        # 所有格式都应该成功生成输出
        assert len(outputs) == 3, "All formats should produce output"

    def test_output_file_generation(self, create_test_file, sample_references, temp_dir):
        """测试输出到文件"""
        test_file = create_test_file(sample_references["doi_only"])
        output_file = f"{temp_dir}/output.bib"
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--output", output_file, "--quiet"
        ])
        assert code == 0, f"Output to file failed: {stderr}"
        
        # 验证文件是否生成
        import os
        assert os.path.exists(output_file), "Output file was not created"
        
        # 验证文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content.strip()) > 0, "Output file should not be empty"
        assert "@" in content, "Output file should contain BibTeX content"

    def test_complex_entry_formatting(self, create_test_file):
        """测试复杂条目的格式化"""
        # 使用一个已知的复杂DOI
        complex_doi = "10.1021/acs.jcim.8b00542"  # 这是我们之前修复的DOI
        test_file = create_test_file(complex_doi)
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        assert code == 0, f"Complex entry formatting failed: {stderr}"
        
        # 验证包含基本字段
        output_lower = stdout.lower()
        expected_fields = ["title", "author", "journal", "year"]
        
        for field in expected_fields:
            assert field in output_lower, f"Missing field: {field}"
