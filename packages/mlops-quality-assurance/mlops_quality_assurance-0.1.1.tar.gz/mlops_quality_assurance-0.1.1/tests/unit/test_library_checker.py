import pytest
import nbformat
from unittest.mock import patch, mock_open
from achs_mlops_quality.models.library_checker import LibraryChecker

class DummyCell:
    def __init__(self, cell_type, source):
        self.cell_type = cell_type
        self.source = source
    def __getitem__(self, key):
        if key == "cell_type":
            return self.cell_type
        if key == "source":
            return self.source
        raise KeyError(key)

def make_notebook(cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = cells
    return nb

def test_get_files_called_on_init(monkeypatch):
    called = {}
    def fake_get_files(self):
        called['yes'] = True
    monkeypatch.setattr(LibraryChecker, "_get_files", fake_get_files)
    checker = LibraryChecker(src_path="foo")
    assert called['yes']
    assert checker.source_path == "foo"

def test_analize_notebooks_reads_cells(monkeypatch):
    checker = LibraryChecker()
    checker.notebooks = ["notebook1.ipynb", "notebook2.ipynb"]
    called = []
    def fake_read_notebook_cells(self, path):
        called.append(path)
    monkeypatch.setattr(LibraryChecker, "read_notebook_cells", fake_read_notebook_cells)
    checker.analized_files = 0
    checker.analize_notebooks()
    assert called == ["notebook1.ipynb", "notebook2.ipynb"]
    assert checker.analized_files == 2

def test_read_notebook_cells_detects_issues(monkeypatch):
    # Prepare a notebook with one code cell with pip install violation
    code = "!pip install pandas\n!pip install numpy==1.24.0"
    nb = make_notebook([
        nbformat.v4.new_code_cell(source=code),
        nbformat.v4.new_markdown_cell(source="# just text")
    ])
    m = mock_open(read_data=nbformat.writes(nb))
    checker = LibraryChecker()
    checker.issues_detected = 0
    checker.issues_files = []
    with patch("builtins.open", m):
        checker.read_notebook_cells("dummy.ipynb")
    assert checker.issues_detected == 1
    assert "dummy.ipynb" in checker.issues_files

def test_check_pip_installs_from_lines():
    checker = LibraryChecker()
    # No violation
    code = "!pip install numpy==1.24.0 pandas==2.0.0"
    result, issues = checker.check_pip_installs_from_lines(code)
    assert result is True
    assert issues == []
    # Violation: missing version
    code = "!pip install numpy pandas==2.0.0"
    result, issues = checker.check_pip_installs_from_lines(code)
    assert result is False
    assert any("numpy" in str(issue) for issue in issues)
    # Ignore comments
    code = "# !pip install numpy\n!pip install pandas==2.0.0"
    result, issues = checker.check_pip_installs_from_lines(code)
    assert result is True
    assert issues == []
    # Handles options
    code = "!pip install -r requirements.txt"
    result, issues = checker.check_pip_installs_from_lines(code)
    assert result is True
    assert issues == []
