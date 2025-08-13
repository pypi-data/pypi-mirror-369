import pytest
from pathlib import Path
from sokrates import FileHelper

import shutil

@pytest.fixture
def tmp_path(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)

class TestFileHelperBasicFunctionality:

    def test_create_new_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        assert not test_file.exists()
        FileHelper.create_new_file(test_file)
        assert test_file.exists()
        
    def test_write_to_file(self, tmp_path):
        content = "Hello, world!"
        test_file = tmp_path / "content.txt"
        FileHelper.write_to_file(file_path=test_file, content=content)
        assert test_file.read_text() == content
        
    def test_read_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        FileHelper.create_new_file(test_file)
        expected_content = "Sample content."
        FileHelper.write_to_file(file_path=test_file, content=expected_content)
        actual_content = FileHelper.read_file(test_file)
        assert actual_content == expected_content

class TestFileHelperEdgeCases:
    def test_write_to_existing_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        initial_content = "First line."
        FileHelper.write_to_file(file_path=test_file, content=initial_content)
        new_content = "Second line."
        FileHelper.write_to_file(file_path=test_file, content=new_content)
        assert test_file.read_text() == new_content
