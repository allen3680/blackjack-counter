#!/usr/bin/env python3
"""
Build script for creating Windows executable of Blackjack Counter.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def clean_build_dirs():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"Cleaning {dir_name}/...")
            shutil.rmtree(dir_name)
    
    # Clean .spec file if exists
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        if spec_file.name != 'blackjack-counter.spec':
            print(f"Removing {spec_file}...")
            spec_file.unlink()


def build_executable():
    """Build the Windows executable using PyInstaller."""
    print("Building Blackjack Counter executable...")
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build using the spec file
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        'blackjack-counter.spec',
        '--clean',
        '--noconfirm'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("Build completed successfully!")
    
    # Check if executable was created
    exe_path = Path('dist/BlackjackCounter.exe')
    if exe_path.exists():
        print(f"\n✓ Executable created: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print("\n✗ Executable not found!")
        return False


def create_distribution():
    """Create a distribution folder with the executable and any additional files."""
    dist_dir = Path('dist/BlackjackCounter_Windows')
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir(parents=True)
    
    # Copy executable
    exe_src = Path('dist/BlackjackCounter.exe')
    if exe_src.exists():
        shutil.copy2(exe_src, dist_dir / 'BlackjackCounter.exe')
    
    # Create a simple README
    readme_content = """# Blackjack Counter

21點計牌器 - 使用 Wong Halves 系統與基本策略

## 使用方法

直接執行 BlackjackCounter.exe 即可開始使用。

## 功能特色

- Wong Halves 計牌系統
- 8副牌基本策略
- 深色主題介面
- 實時計牌建議

## 系統需求

- Windows 7 或更新版本
- 無需安裝 Python
"""
    
    with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n✓ Distribution created: {dist_dir}")
    return dist_dir


def main():
    """Main build process."""
    print("=== Blackjack Counter Windows Build ===\n")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found. Please install it:")
        print("  pip install pyinstaller")
        sys.exit(1)
    
    # Build executable
    if build_executable():
        # Create distribution
        dist_dir = create_distribution()
        
        print("\n=== Build Complete ===")
        print(f"Executable location: {dist_dir}/BlackjackCounter.exe")
        print("\nYou can now distribute the contents of the 'dist/BlackjackCounter_Windows' folder.")
    else:
        print("\n=== Build Failed ===")
        sys.exit(1)


if __name__ == "__main__":
    main()