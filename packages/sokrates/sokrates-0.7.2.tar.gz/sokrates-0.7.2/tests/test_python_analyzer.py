import pytest
from pathlib import Path
from sokrates.coding.python_analyzer import PythonAnalyzer

import shutil

@pytest.fixture
def tmp_path(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)

class TestPythonAnalyzer:

    def test_create_markdown_documentation_for_directory(self, tmp_path):
        test_file = tmp_path / "analysis.md"
        assert not test_file.exists()
        
        source_path = f"{Path(__file__).parent.parent.resolve()}/src"
        PythonAnalyzer.create_markdown_documentation_for_directory(source_path, test_file, verbose=True)
        assert test_file.exists()
    
    # TODO: implement full testsuite