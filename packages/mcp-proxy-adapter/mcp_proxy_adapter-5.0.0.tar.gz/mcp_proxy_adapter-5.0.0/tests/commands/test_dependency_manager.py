"""
Tests for dependency management system.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from mcp_proxy_adapter.commands.dependency_manager import DependencyManager


class TestDependencyManager:
    """Test DependencyManager class."""
    
    @pytest.fixture
    def dependency_manager(self):
        """Create DependencyManager instance."""
        return DependencyManager()
    
    def test_init(self, dependency_manager):
        """Test DependencyManager initialization."""
        assert dependency_manager._installed_packages is not None
        assert isinstance(dependency_manager._installed_packages, dict)
    
    def test_check_dependencies_no_deps(self, dependency_manager):
        """Test checking dependencies when no dependencies are specified."""
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies([])
        
        assert all_satisfied is True
        assert missing_deps == []
        assert installed_deps == []
    
    def test_check_dependencies_builtin_modules(self, dependency_manager):
        """Test checking dependencies for built-in modules."""
        deps = ["os", "sys", "json"]
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(deps)
        
        assert all_satisfied is True
        assert missing_deps == []
        assert len(installed_deps) == 3
    
    def test_check_dependencies_missing_modules(self, dependency_manager):
        """Test checking dependencies for missing modules."""
        deps = ["nonexistent_module", "another_missing_module"]
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(deps)
        
        assert all_satisfied is False
        assert len(missing_deps) == 2
        assert installed_deps == []
    
    def test_check_dependencies_mixed(self, dependency_manager):
        """Test checking dependencies with mixed available and missing modules."""
        deps = ["os", "nonexistent_module", "json"]
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(deps)
        
        assert all_satisfied is False
        assert len(missing_deps) == 1
        assert "nonexistent_module" in missing_deps
        assert len(installed_deps) == 2
        assert "os" in installed_deps
        assert "json" in installed_deps
    
    @patch('subprocess.run')
    def test_install_dependencies_success(self, mock_run, dependency_manager):
        """Test successful dependency installation."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        deps = ["test_package"]
        success, installed_deps, failed_deps = dependency_manager.install_dependencies(deps)
        
        assert success is True
        assert len(installed_deps) == 1
        assert "test_package" in installed_deps
        assert failed_deps == []
        
        # Verify pip command was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[1] == "-m"  # python -m
        assert call_args[2] == "pip"  # python -m pip
        assert call_args[3] == "install"  # python -m pip install
        assert "test_package" in call_args
    
    @patch('subprocess.run')
    def test_install_dependencies_failure(self, mock_run, dependency_manager):
        """Test failed dependency installation."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Package not found"
        mock_run.return_value = mock_result
        
        deps = ["nonexistent_package"]
        success, installed_deps, failed_deps = dependency_manager.install_dependencies(deps)
        
        assert success is False
        assert installed_deps == []
        assert len(failed_deps) == 1
        assert "nonexistent_package" in failed_deps
    
    @patch('subprocess.run')
    def test_install_dependencies_timeout(self, mock_run, dependency_manager):
        """Test dependency installation timeout."""
        mock_run.side_effect = TimeoutError("Installation timeout")
        
        deps = ["slow_package"]
        success, installed_deps, failed_deps = dependency_manager.install_dependencies(deps)
        
        assert success is False
        assert installed_deps == []
        assert len(failed_deps) == 1
        assert "slow_package" in failed_deps
    
    def test_verify_installation_all_verified(self, dependency_manager):
        """Test verification when all dependencies are satisfied."""
        deps = ["os", "sys"]
        all_verified, failed_verifications = dependency_manager.verify_installation(deps)
        
        assert all_verified is True
        assert failed_verifications == []
    
    def test_verify_installation_some_failed(self, dependency_manager):
        """Test verification when some dependencies are missing."""
        deps = ["os", "nonexistent_module"]
        all_verified, failed_verifications = dependency_manager.verify_installation(deps)
        
        assert all_verified is False
        assert len(failed_verifications) == 1
        assert "nonexistent_module" in failed_verifications
    
    def test_get_dependency_info_builtin(self, dependency_manager):
        """Test getting dependency info for built-in module."""
        info = dependency_manager.get_dependency_info("os")
        
        assert info["name"] == "os"
        assert info["importable"] is True
        # Built-in modules may not be in pkg_resources
        assert info["installed"] in [True, False]
    
    def test_get_dependency_info_missing(self, dependency_manager):
        """Test getting dependency info for missing module."""
        info = dependency_manager.get_dependency_info("nonexistent_module")
        
        assert info["name"] == "nonexistent_module"
        assert info["installed"] is False
        assert info["importable"] is False
        assert info["version"] is None
    
    def test_list_installed_dependencies(self, dependency_manager):
        """Test listing installed dependencies."""
        deps = dependency_manager.list_installed_dependencies()
        
        assert isinstance(deps, dict)
        # Should contain at least some basic packages
        assert len(deps) > 0


class TestDependencyManagerIntegration:
    """Integration tests for DependencyManager."""
    
    @pytest.fixture
    def dependency_manager(self):
        """Create DependencyManager instance."""
        return DependencyManager()
    
    def test_full_workflow_check_install_verify(self, dependency_manager):
        """Test full workflow: check -> install -> verify."""
        # This test would require actual package installation
        # For now, we'll test with built-in modules
        deps = ["os", "sys"]
        
        # Step 1: Check dependencies
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(deps)
        assert all_satisfied is True
        
        # Step 2: Verify installation
        all_verified, failed_verifications = dependency_manager.verify_installation(deps)
        assert all_verified is True
        
        # Step 3: Get info for each dependency
        for dep in deps:
            info = dependency_manager.get_dependency_info(dep)
            assert info["name"] == dep
            assert info["importable"] is True 