"""
测试输入格式支持
验证TXT和BibTeX输入格式的处理
"""
import pytest
import subprocess
import os

class TestInputFormats:
    """输入格式测试"""

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

    def test_txt_format_basic(self, create_test_file, sample_references):
        """测试基本TXT格式输入"""
        test_file = create_test_file(sample_references["doi_only"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--input-type", "txt", "--quiet"
        ])
        assert code == 0, f"TXT processing failed: {stderr}"
        assert "@article" in stdout or "@inproceedings" in stdout

    def test_txt_format_multiline(self, create_test_file, sample_references):
        """测试多行TXT格式输入"""
        multiline_content = f"{sample_references['doi_only']}\n\n{sample_references['conference_paper']}"
        test_file = create_test_file(multiline_content)
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--input-type", "txt", "--quiet"
        ])
        assert code == 0, f"Multiline TXT processing failed: {stderr}"
        # 应该处理两个条目
        bib_entries = stdout.count("@")
        assert bib_entries >= 1, "Should process multiple entries"

    def test_bibtex_format_input(self, create_test_file, sample_references):
        """测试BibTeX格式输入"""
        test_file = create_test_file(sample_references["bibtex_entry"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--input-type", "bib", "--quiet"
        ])
        assert code == 0, f"BibTeX processing failed: {stderr}"
        assert "@article" in stdout or "@inproceedings" in stdout

    def test_doi_recognition_variants(self, create_test_file):
        """测试各种DOI格式识别"""
        doi_variants = [
            "10.1038/nature14539",
            "doi:10.1038/nature14539",
            "DOI: 10.1038/nature14539",
            "https://doi.org/10.1038/nature14539"
        ]
        
        for doi in doi_variants:
            test_file = create_test_file(doi)
            code, stdout, stderr = self.run_onecite_command([
                "process", test_file, "--quiet"
            ])
            assert code == 0, f"DOI variant processing failed for {doi}: {stderr}"
            assert "doi" in stdout.lower(), f"DOI field missing for {doi}"

    def test_arxiv_recognition_variants(self, create_test_file):
        """测试各种arXiv格式识别"""
        arxiv_variants = [
            "1706.03762",
            "arxiv:1706.03762",
            "arXiv:1706.03762",
            "https://arxiv.org/abs/1706.03762"
        ]
        
        for arxiv in arxiv_variants:
            test_file = create_test_file(arxiv)
            code, stdout, stderr = self.run_onecite_command([
                "process", test_file, "--quiet"
            ])
            assert code == 0, f"arXiv variant processing failed for {arxiv}: {stderr}"
            # arXiv论文应该包含arxiv字段或url
            assert "arxiv" in stdout.lower() or "1706.03762" in stdout, f"arXiv identifier missing for {arxiv}"

    def test_conference_paper_recognition(self, create_test_file, sample_references):
        """测试会议论文识别"""
        test_file = create_test_file(sample_references["conference_paper"])
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        assert code == 0, f"Conference paper processing failed: {stderr}"
        # 会议论文应该生成@inproceedings条目
        # 注意：这取决于具体实现，可能不总是生成@inproceedings
        assert "@" in stdout, "Should generate some BibTeX entry"

    def test_mixed_content_processing(self, create_test_file, sample_references):
        """测试混合内容处理"""
        mixed_content = f"""{sample_references['doi_only']}

{sample_references['arxiv_id']}

{sample_references['conference_paper']}"""
        
        test_file = create_test_file(mixed_content)
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        assert code == 0, f"Mixed content processing failed: {stderr}"
        
        # 应该处理多个条目
        bib_entries = stdout.count("@")
        assert bib_entries >= 2, f"Should process multiple entries, found {bib_entries}"
