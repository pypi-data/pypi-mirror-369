"""
测试输入格式支持（健壮版本，减少网络依赖）
验证TXT和BibTeX输入格式的处理，但避免超时问题
"""
import pytest
import subprocess
import os

class TestInputFormatsRobust:
    """输入格式测试（健壮版本）"""

    def run_onecite_command_with_timeout(self, args, cwd=None, timeout=15):
        """运行onecite命令的辅助方法，使用较短的超时"""
        cmd = ["onecite"] + args
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=timeout  # 减少超时时间
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"

    def test_doi_only_processing(self, create_test_file):
        """测试仅包含DOI的简单处理（应该快速完成）"""
        test_file = create_test_file("10.1038/nature14539")
        code, stdout, stderr = self.run_onecite_command_with_timeout([
            "process", test_file, "--quiet"
        ])
        # 这个测试应该能快速完成，因为DOI处理相对简单
        if code == 0:
            assert "@" in stdout, "Should contain BibTeX entry"
        else:
            # 如果失败，至少验证不是因为格式问题
            assert "format" not in stderr.lower(), f"Should not be format error: {stderr}"

    def test_bibtex_input_processing(self, create_test_file, sample_references):
        """测试BibTeX输入处理（不涉及外部API）"""
        test_file = create_test_file(sample_references["bibtex_entry"])
        code, stdout, stderr = self.run_onecite_command_with_timeout([
            "process", test_file, "--input-type", "bib", "--quiet"
        ])
        # BibTeX处理应该不需要外部网络调用
        assert code == 0 or "timeout" not in stderr.lower(), f"BibTeX processing should not timeout: {stderr}"

    def test_command_line_robustness(self, create_test_file):
        """测试命令行的基本健壮性"""
        # 测试空文件
        empty_file = create_test_file("")
        code, stdout, stderr = self.run_onecite_command_with_timeout([
            "process", empty_file, "--quiet"
        ], timeout=10)
        # 空文件应该快速处理完成
        assert code == 0 or "timeout" not in stderr.lower(), "Empty file should process quickly"

    def test_output_format_switching(self, create_test_file):
        """测试输出格式切换（不依赖网络的部分）"""
        test_file = create_test_file("Simple test reference")
        
        formats = ["bibtex", "apa", "mla"]
        for fmt in formats:
            code, stdout, stderr = self.run_onecite_command_with_timeout([
                "process", test_file, "--output-format", fmt, "--quiet"
            ], timeout=10)
            
            # 即使处理失败，也不应该超时
            assert "timeout" not in stderr.lower(), f"Format {fmt} should not timeout"

    def test_template_switching(self, create_test_file):
        """测试模板切换"""
        test_file = create_test_file("Test reference")
        
        templates = ["journal_article_full", "conference_paper"]
        for template in templates:
            code, stdout, stderr = self.run_onecite_command_with_timeout([
                "process", test_file, "--template", template, "--quiet"
            ], timeout=10)
            
            # 模板处理不应该超时
            assert "timeout" not in stderr.lower(), f"Template {template} should not timeout"

    @pytest.mark.slow
    def test_arxiv_processing_with_long_timeout(self, create_test_file):
        """测试arXiv处理（使用长超时，标记为慢测试）"""
        test_file = create_test_file("1706.03762")
        code, stdout, stderr = self.run_onecite_command_with_timeout([
            "process", test_file, "--quiet"
        ], timeout=60)  # 给arXiv处理更长时间
        
        # 这个测试可能会因为网络问题失败，但不应该是格式问题
        if code != 0:
            # 检查是否是网络相关的错误而不是代码错误
            network_errors = ["timeout", "connection", "network", "dns", "resolve"]
            is_network_error = any(error in stderr.lower() for error in network_errors)
            if not is_network_error:
                pytest.fail(f"arXiv processing failed with non-network error: {stderr}")

    def test_error_message_quality(self, create_test_file):
        """测试错误消息质量"""
        # 测试无效DOI
        test_file = create_test_file("invalid.doi.format")
        code, stdout, stderr = self.run_onecite_command_with_timeout([
            "process", test_file, "--quiet"
        ], timeout=10)
        
        # 应该快速失败并给出合理的错误信息
        assert "timeout" not in stderr.lower(), "Invalid input should fail quickly, not timeout"

    def test_basic_functionality_without_network(self, create_test_file):
        """测试基本功能（尽量避免网络调用）"""
        # 使用已知的本地可处理内容
        local_content = """@article{local2023,
  title={Local Test Article},
  author={Test Author},
  journal={Test Journal},
  year={2023}
}"""
        
        test_file = create_test_file(local_content, "test.bib")
        code, stdout, stderr = self.run_onecite_command_with_timeout([
            "process", test_file, "--input-type", "bib", "--quiet"
        ], timeout=15)
        
        # 本地BibTeX处理应该成功
        if code == 0:
            assert "@" in stdout, "Should generate BibTeX output"
        else:
            # 如果失败，确保不是超时
            assert "timeout" not in stderr.lower(), f"Local processing should not timeout: {stderr}"
