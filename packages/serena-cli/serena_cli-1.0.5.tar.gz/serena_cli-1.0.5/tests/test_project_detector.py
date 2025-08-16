"""
Tests for ProjectDetector class.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from panda_index_helper.project_detector import ProjectDetector


class TestProjectDetector:
    """Test cases for ProjectDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ProjectDetector()
        self.test_project_path = Path("/tmp/test-project")

    def test_init(self):
        """Test ProjectDetector initialization."""
        assert self.detector is not None
        assert len(self.detector.project_indicators) > 0
        assert ".git" in self.detector.project_indicators
        assert "README.md" in self.detector.project_indicators

    @patch('pathlib.Path.cwd')
    def test_detect_current_project_success(self, mock_cwd):
        """Test successful current project detection."""
        mock_cwd.return_value = self.test_project_path
        
        with patch.object(self.detector, '_find_project_root') as mock_find:
            mock_find.return_value = str(self.test_project_path)
            
            result = self.detector.detect_current_project()
            assert result == str(self.test_project_path)

    @patch('pathlib.Path.cwd')
    def test_detect_current_project_failure(self, mock_cwd):
        """Test failed current project detection."""
        mock_cwd.return_value = self.test_project_path
        
        with patch.object(self.detector, '_find_project_root') as mock_find:
            mock_find.return_value = None
            
            result = self.detector.detect_current_project()
            assert result is None

    def test_detect_project_from_path_success(self):
        """Test successful project detection from path."""
        with patch.object(self.detector, '_find_project_root') as mock_find:
            mock_find.return_value = str(self.test_project_path)
            
            result = self.detector.detect_project_from_path(str(self.test_project_path))
            assert result == str(self.test_project_path)

    def test_detect_project_from_path_failure(self):
        """Test failed project detection from path."""
        with patch.object(self.detector, '_find_project_root') as mock_find:
            mock_find.return_value = None
            
            result = self.detector.detect_project_from_path(str(self.test_project_path))
            assert result is None

    def test_validate_project_success(self):
        """Test successful project validation."""
        with patch.object(self.detector, '_has_project_indicators') as mock_has:
            mock_has.return_value = True
            
            result = self.detector.validate_project(str(self.test_project_path))
            assert result is True

    def test_validate_project_failure(self):
        """Test failed project validation."""
        with patch.object(self.detector, '_has_project_indicators') as mock_has:
            mock_has.return_value = False
            
            result = self.detector.validate_project(str(self.test_project_path))
            assert result is False

    def test_has_project_indicators_success(self):
        """Test successful project indicators check."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        
        with patch.object(mock_path, 'iterdir') as mock_iter:
            mock_iter.return_value = [mock_path]
            
            result = self.detector._has_project_indicators(mock_path)
            assert result is True

    def test_has_project_indicators_failure(self):
        """Test failed project indicators check."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        
        result = self.detector._has_project_indicators(mock_path)
        assert result is False

    def test_detect_project_type_python(self):
        """Test Python project type detection."""
        mock_path = MagicMock()
        mock_path.__truediv__.return_value.exists.return_value = True
        
        result = self.detector._detect_project_type(mock_path)
        assert result == "python"

    def test_detect_project_type_nodejs(self):
        """Test Node.js project type detection."""
        mock_path = MagicMock()
        mock_path.__truediv__.return_value.exists.return_value = True
        
        result = self.detector._detect_project_type(mock_path)
        assert result == "nodejs"

    def test_detect_project_type_generic(self):
        """Test generic project type detection."""
        mock_path = MagicMock()
        mock_path.__truediv__.return_value.exists.return_value = False
        
        result = self.detector._detect_project_type(mock_path)
        assert result == "generic"

    def test_get_project_size(self):
        """Test project size calculation."""
        mock_path = MagicMock()
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.stat.return_value.st_size = 1024
        
        with patch.object(mock_path, 'rglob') as mock_rglob:
            mock_rglob.return_value = [mock_file]
            
            result = self.detector._get_project_size(mock_path)
            assert result["total_files"] == 1
            assert result["total_size_bytes"] == 1024
            assert result["total_size_mb"] == 0.0

    def test_detect_languages(self):
        """Test programming language detection."""
        mock_path = MagicMock()
        mock_py_file = MagicMock()
        mock_py_file.suffix = ".py"
        mock_js_file = MagicMock()
        mock_js_file.suffix = ".js"
        
        with patch.object(mock_path, 'rglob') as mock_rglob:
            mock_rglob.return_value = [mock_py_file, mock_js_file]
            
            result = self.detector._detect_languages(mock_path)
            assert "Python" in result
            assert "JavaScript" in result
            assert len(result) == 2

    def test_has_serena_config(self):
        """Test Serena configuration check."""
        mock_path = MagicMock()
        mock_serena_dir = MagicMock()
        mock_serena_dir.exists.return_value = True
        
        with patch.object(mock_path, '__truediv__') as mock_div:
            mock_div.return_value.__truediv__.return_value = mock_serena_dir
            
            result = self.detector._has_serena_config(mock_path)
            assert result is True

    def test_has_panda_config(self):
        """Test Panda configuration check."""
        mock_path = MagicMock()
        mock_panda_dir = MagicMock()
        mock_panda_dir.exists.return_value = True
        
        with patch.object(mock_path, '__truediv__') as mock_div:
            mock_div.return_value.__truediv__.return_value = mock_panda_dir
            
            result = self.detector._has_panda_config(mock_path)
            assert result is True
