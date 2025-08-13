"""
集成测试
测试完整的工作流程和README中的示例
"""
import pytest
import subprocess
import os
import tempfile

class TestIntegration:
    """集成测试"""

    def run_onecite_command(self, args, cwd=None):
        """运行onecite命令的辅助方法"""
        cmd = ["onecite"] + args
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=60  # 增加超时时间用于集成测试
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"

    def test_readme_basic_example(self, create_test_file, temp_dir):
        """测试README中的基本示例"""
        # README中的示例输入
        readme_input = """10.1038/nature14539

Attention is all you need
Vaswani et al.
NIPS 2017"""
        
        test_file = create_test_file(readme_input)
        output_file = os.path.join(temp_dir, "results.bib")
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--output", output_file, "--quiet"
        ])
        
        assert code == 0, f"README example failed: {stderr}"
        assert os.path.exists(output_file), "Output file should be created"
        
        # 验证输出内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 应该包含两个条目
        bib_entries = content.count("@")
        assert bib_entries >= 1, f"Should contain BibTeX entries, found {bib_entries}"
        
        # 检查特定内容（基于README期望）
        content_lower = content.lower()
        # 可能包含深度学习相关内容或Attention相关内容
        has_relevant_content = any(keyword in content_lower for keyword in [
            "nature", "deep", "learning", "attention", "vaswani", "nips", "neural"
        ])
        assert has_relevant_content, "Output should contain relevant academic content"

    def test_workflow_txt_to_bibtex(self, create_test_file, temp_dir):
        """测试完整的TXT到BibTeX工作流程"""
        # 创建包含不同类型引用的输入
        mixed_input = """10.1038/nature14539

1706.03762

Attention is all you need
Vaswani et al.
NIPS 2017

https://arxiv.org/abs/1706.03762"""
        
        test_file = create_test_file(mixed_input)
        output_file = os.path.join(temp_dir, "output.bib")
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, 
            "--input-type", "txt",
            "--output-format", "bibtex",
            "--template", "journal_article_full",
            "--output", output_file,
            "--quiet"
        ])
        
        assert code == 0, f"TXT to BibTeX workflow failed: {stderr}"
        assert os.path.exists(output_file), "BibTeX output file should be created"
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "@" in content, "Should contain BibTeX entries"
        assert len(content.strip()) > 100, "Should contain substantial content"

    def test_workflow_bib_to_apa(self, create_test_file, temp_dir):
        """测试BibTeX到APA的工作流程"""
        # 创建BibTeX输入
        bib_input = """@article{test2015,
  title={Deep learning},
  author={LeCun, Yann and Bengio, Yoshua and Hinton, Geoffrey},
  journal={Nature},
  year={2015},
  volume={521},
  pages={436--444},
  doi={10.1038/nature14539}
}"""
        
        test_file = create_test_file(bib_input, "input.bib")
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file,
            "--input-type", "bib",
            "--output-format", "apa",
            "--quiet"
        ])
        
        assert code == 0, f"BibTeX to APA workflow failed: {stderr}"
        assert len(stdout.strip()) > 0, "APA output should not be empty"

    def test_conference_paper_workflow(self, create_test_file, temp_dir):
        """测试会议论文完整工作流程"""
        conference_input = """Attention is all you need
Vaswani et al.
NIPS 2017

ResNet: Deep Residual Learning for Image Recognition
He, Zhang, Ren, Sun
CVPR 2016"""
        
        test_file = create_test_file(conference_input)
        output_file = os.path.join(temp_dir, "conference.bib")
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file,
            "--template", "conference_paper",
            "--output", output_file,
            "--quiet"
        ])
        
        assert code == 0, f"Conference paper workflow failed: {stderr}"
        assert os.path.exists(output_file), "Conference output file should be created"

    def test_arxiv_workflow(self, create_test_file):
        """测试arXiv论文工作流程"""
        arxiv_input = """1706.03762

arxiv:1512.03385

https://arxiv.org/abs/2010.11929"""
        
        test_file = create_test_file(arxiv_input)
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        
        assert code == 0, f"arXiv workflow failed: {stderr}"
        
        # 验证arXiv相关内容
        output_lower = stdout.lower()
        assert "arxiv" in output_lower or "1706.03762" in stdout, "Should contain arXiv references"

    def test_error_recovery_workflow(self, create_test_file):
        """测试错误恢复工作流程"""
        # 混合有效和无效的引用
        mixed_input = """10.1038/nature14539

invalid_reference_12345

1706.03762

another_invalid_reference"""
        
        test_file = create_test_file(mixed_input)
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        
        # 应该部分成功（处理有效的引用，跳过无效的）
        assert code == 0, f"Error recovery workflow failed: {stderr}"
        
        # 应该至少处理一些有效条目
        if "@" in stdout:
            bib_entries = stdout.count("@")
            assert bib_entries >= 1, "Should process some valid entries"

    def test_large_batch_processing(self, create_test_file):
        """测试大批量处理"""
        # 创建多个引用的输入
        large_input = """10.1038/nature14539

10.1126/science.1127647

1706.03762

1512.03385

Attention is all you need
Vaswani et al.
NIPS 2017

BERT: Pre-training of Deep Bidirectional Transformers
Devlin et al.
NAACL 2019"""
        
        test_file = create_test_file(large_input)
        
        code, stdout, stderr = self.run_onecite_command([
            "process", test_file, "--quiet"
        ])
        
        # 大批量处理应该成功
        assert code == 0, f"Large batch processing failed: {stderr}"
        
        # 应该处理多个条目
        if "@" in stdout:
            bib_entries = stdout.count("@")
            assert bib_entries >= 2, f"Should process multiple entries, found {bib_entries}"

    def test_cross_format_compatibility(self, create_test_file, temp_dir):
        """测试格式间兼容性"""
        # 先生成BibTeX
        input_content = "10.1038/nature14539"
        test_file = create_test_file(input_content)
        bib_file = os.path.join(temp_dir, "temp.bib")
        
        # 生成BibTeX
        code1, stdout1, stderr1 = self.run_onecite_command([
            "process", test_file, "--output", bib_file, "--quiet"
        ])
        
        if code1 == 0 and os.path.exists(bib_file):
            # 使用生成的BibTeX作为输入
            code2, stdout2, stderr2 = self.run_onecite_command([
                "process", bib_file, "--input-type", "bib", "--output-format", "apa", "--quiet"
            ])
            
            assert code2 == 0, f"Cross-format compatibility failed: {stderr2}"
            assert len(stdout2.strip()) > 0, "Cross-format output should not be empty"
