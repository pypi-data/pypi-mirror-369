"""
pytest配置和共享fixtures
"""
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_dir():
    """创建临时目录fixture"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def sample_references():
    """示例引用数据"""
    return {
        "doi_only": "10.1038/nature14539",
        "arxiv_id": "1706.03762",
        "arxiv_url": "https://arxiv.org/abs/1706.03762",
        "conference_paper": """Attention is all you need
Vaswani et al.
NIPS 2017""",
        "journal_paper": """Deep learning
LeCun, Bengio, Hinton
Nature 2015""",
        "bibtex_entry": """@article{test2015,
  title={Test Article},
  author={Test Author},
  journal={Test Journal},
  year={2015},
  doi={10.1038/nature14539}
}"""
    }

@pytest.fixture
def create_test_file(temp_dir):
    """创建测试文件的helper函数"""
    def _create_file(content, filename="test_input.txt"):
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    return _create_file
