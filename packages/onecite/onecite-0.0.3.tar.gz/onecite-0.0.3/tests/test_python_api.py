"""
测试Python API
验证process_references函数和相关API
"""
import pytest
from unittest.mock import Mock

class TestPythonAPI:
    """Python API测试"""

    def test_api_import(self):
        """测试API导入"""
        try:
            from onecite import process_references
            assert callable(process_references), "process_references should be callable"
        except ImportError as e:
            pytest.fail(f"Failed to import API: {e}")

    def test_api_basic_functionality(self, sample_references):
        """测试API基本功能"""
        try:
            from onecite import process_references
            
            def mock_callback(candidates):
                return 0  # 总是选择第一个候选
            
            result = process_references(
                input_content=sample_references["doi_only"],
                input_type="txt",
                template_name="journal_article_full",
                output_format="bibtex",
                interactive_callback=mock_callback
            )
            
            # 验证返回结构
            assert isinstance(result, dict), "Result should be a dictionary"
            assert "results" in result, "Result should contain 'results' key"
            assert "report" in result, "Result should contain 'report' key"
            
            # 验证报告结构
            report = result["report"]
            assert "total" in report, "Report should contain 'total'"
            assert "succeeded" in report, "Report should contain 'succeeded'"
            assert "failed_entries" in report, "Report should contain 'failed_entries'"
            
            # 验证结果类型
            assert isinstance(result["results"], list), "Results should be a list"
            assert isinstance(report["total"], int), "Total should be an integer"
            assert isinstance(report["succeeded"], int), "Succeeded should be an integer"
            assert isinstance(report["failed_entries"], list), "Failed entries should be a list"
            
        except ImportError:
            pytest.skip("API not available for testing")

    def test_api_with_bibtex_input(self, sample_references):
        """测试API处理BibTeX输入"""
        try:
            from onecite import process_references
            
            def mock_callback(candidates):
                return 0
            
            result = process_references(
                input_content=sample_references["bibtex_entry"],
                input_type="bib",
                template_name="journal_article_full",
                output_format="bibtex",
                interactive_callback=mock_callback
            )
            
            assert result["report"]["total"] >= 1, "Should process at least one entry"
            
        except ImportError:
            pytest.skip("API not available for testing")

    def test_api_different_output_formats(self, sample_references):
        """测试API不同输出格式"""
        try:
            from onecite import process_references
            
            def mock_callback(candidates):
                return 0
            
            formats = ["bibtex", "apa", "mla"]
            
            for fmt in formats:
                result = process_references(
                    input_content=sample_references["doi_only"],
                    input_type="txt",
                    template_name="journal_article_full",
                    output_format=fmt,
                    interactive_callback=mock_callback
                )
                
                assert isinstance(result["results"], list), f"Results should be list for {fmt}"
                # 至少应该尝试处理条目（即使失败）
                assert result["report"]["total"] >= 1, f"Should process entry for {fmt}"
                
        except ImportError:
            pytest.skip("API not available for testing")

    def test_api_interactive_callback(self, sample_references):
        """测试交互回调功能"""
        try:
            from onecite import process_references
            
            callback_called = []
            
            def test_callback(candidates):
                callback_called.append(len(candidates))
                return 0  # 选择第一个
            
            result = process_references(
                input_content="Some ambiguous reference that might trigger callback",
                input_type="txt",
                template_name="journal_article_full",
                output_format="bibtex",
                interactive_callback=test_callback
            )
            
            # 回调可能被调用，也可能不被调用，取决于是否有歧义
            # 但函数应该成功执行
            assert isinstance(result, dict), "Should return result dictionary"
            
        except ImportError:
            pytest.skip("API not available for testing")

    def test_api_error_handling(self):
        """测试API错误处理"""
        try:
            from onecite import process_references
            
            def mock_callback(candidates):
                return 0
            
            # 测试无效输入类型
            with pytest.raises(Exception):  # 应该抛出某种异常
                process_references(
                    input_content="test",
                    input_type="invalid_type",
                    template_name="journal_article_full",
                    output_format="bibtex",
                    interactive_callback=mock_callback
                )
                
        except ImportError:
            pytest.skip("API not available for testing")

    def test_api_empty_input(self):
        """测试空输入处理"""
        try:
            from onecite import process_references
            
            def mock_callback(candidates):
                return 0
            
            result = process_references(
                input_content="",
                input_type="txt",
                template_name="journal_article_full",
                output_format="bibtex",
                interactive_callback=mock_callback
            )
            
            # 空输入应该返回空结果但不崩溃
            assert result["report"]["total"] == 0, "Empty input should result in 0 total"
            assert len(result["results"]) == 0, "Empty input should result in empty results"
            
        except ImportError:
            pytest.skip("API not available for testing")

    def test_api_multiple_entries(self, sample_references):
        """测试多条目处理"""
        try:
            from onecite import process_references
            
            def mock_callback(candidates):
                return 0
            
            # 组合多个引用
            multi_content = f"{sample_references['doi_only']}\n\n{sample_references['arxiv_id']}"
            
            result = process_references(
                input_content=multi_content,
                input_type="txt",
                template_name="journal_article_full",
                output_format="bibtex",
                interactive_callback=mock_callback
            )
            
            # 应该处理多个条目
            assert result["report"]["total"] >= 2, "Should process multiple entries"
            
        except ImportError:
            pytest.skip("API not available for testing")
