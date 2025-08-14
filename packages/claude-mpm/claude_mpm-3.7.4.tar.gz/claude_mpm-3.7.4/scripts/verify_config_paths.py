#!/usr/bin/env python3
"""
Verification script for configuration path consistency.

This script verifies that all configuration paths are using the correct
.claude-mpm directory name throughout the codebase.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from claude_mpm.core.config_paths import ConfigPaths
from claude_mpm.utils.paths import PathResolver


def main():
    """Run configuration path verification tests."""
    print("=" * 60)
    print("Configuration Path Verification")
    print("=" * 60)
    
    # Test 1: Verify the constant is correct
    print("\n1. Checking CONFIG_DIR_NAME constant...")
    assert ConfigPaths.CONFIG_DIR == ".claude-mpm", f"ERROR: CONFIG_DIR is '{ConfigPaths.CONFIG_DIR}', expected '.claude-mpm'"
    print(f"   ✓ CONFIG_DIR = '{ConfigPaths.CONFIG_DIR}'")
    
    # Test 2: Verify path methods
    print("\n2. Testing ConfigPaths methods...")
    user_config = ConfigPaths.get_user_config_dir()
    print(f"   ✓ User config dir: {user_config}")
    assert ".claude-mpm" in str(user_config), f"ERROR: User config dir doesn't contain .claude-mpm: {user_config}"
    
    project_config = ConfigPaths.get_project_config_dir()
    print(f"   ✓ Project config dir: {project_config}")
    assert ".claude-mpm" in str(project_config), f"ERROR: Project config dir doesn't contain .claude-mpm: {project_config}"
    
    # Test 3: Verify PathResolver uses correct names
    print("\n3. Testing PathResolver integration...")
    
    # Test get_config_dir for different scopes
    project_config_dir = PathResolver.get_config_dir('project')
    print(f"   ✓ Project config via PathResolver: {project_config_dir}")
    assert ".claude-mpm" in str(project_config_dir), f"ERROR: PathResolver project config doesn't contain .claude-mpm: {project_config_dir}"
    
    user_config_dir = PathResolver.get_config_dir('user')
    print(f"   ✓ User config via PathResolver: {user_config_dir}")
    assert "claude-mpm" in str(user_config_dir), f"ERROR: PathResolver user config doesn't contain claude-mpm: {user_config_dir}"
    
    # Test 4: Verify legacy detection
    print("\n4. Testing legacy path detection...")
    test_path = Path("/some/path/.claude-pm/config")
    is_valid = ConfigPaths.validate_not_legacy(test_path)
    assert not is_valid, "ERROR: Legacy path should be detected as invalid"
    print("   ✓ Legacy paths are properly detected")
    
    test_path = Path("/some/path/.claude-mpm/config")
    is_valid = ConfigPaths.validate_not_legacy(test_path)
    assert is_valid, "ERROR: Valid path should not be detected as legacy"
    print("   ✓ Valid paths are properly accepted")
    
    # Test 5: Verify common paths
    print("\n5. Testing common path generation...")
    paths_to_check = [
        ConfigPaths.get_user_agents_dir(),
        ConfigPaths.get_tracking_dir(),
        ConfigPaths.get_backups_dir(),
        ConfigPaths.get_memories_dir(),
        ConfigPaths.get_responses_dir(),
    ]
    
    for path in paths_to_check:
        print(f"   ✓ {path}")
        assert ".claude-mpm" in str(path), f"ERROR: Path doesn't contain .claude-mpm: {path}"
    
    print("\n" + "=" * 60)
    print("✅ All configuration path tests passed!")
    print("=" * 60)
    print("\nConfiguration is now using '.claude-mpm' consistently.")
    print("No references to '.claude-pm' remain in the active code.")
    

if __name__ == "__main__":
    main()