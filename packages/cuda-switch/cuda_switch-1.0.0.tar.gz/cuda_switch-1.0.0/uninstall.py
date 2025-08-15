#!/usr/bin/env python3
"""
CUDA切换工具卸载脚本
"""

import os
import sys
import shutil
from pathlib import Path

def uninstall_cuda_switch():
    """卸载CUDA切换工具"""
    
    # 可能的安装路径
    install_paths = [
        Path.home() / ".local/bin",
        Path("/usr/local/bin"),
    ]
    
    removed_files = []
    
    for install_path in install_paths:
        # 主程序
        cuda_switch_file = install_path / "cuda-switch"
        if cuda_switch_file.exists():
            try:
                cuda_switch_file.unlink()
                removed_files.append(str(cuda_switch_file))
                print(f"✅ 已删除: {cuda_switch_file}")
            except OSError as e:
                print(f"❌错误: 无法删除 {cuda_switch_file}: {e}")
        
        # 库目录
        lib_path = install_path / "cuda_switch_lib"
        if lib_path.exists():
            try:
                shutil.rmtree(lib_path)
                removed_files.append(str(lib_path))
                print(f"✅ 已删除库目录: {lib_path}")
            except OSError as e:
                print(f"❌错误: 无法删除库目录 {lib_path}: {e}")
    
    if removed_files:
        print(f"\n🎉 卸载完成！已删除 {len(removed_files)} 个文件/目录")
        print("\n注意: 配置文件备份(.zshrc.cuda_backup)未删除，如需要请手动删除")
    else:
        print("ℹ️ 未找到已安装的CUDA切换工具")
    
    return len(removed_files) > 0

if __name__ == "__main__":
    success = uninstall_cuda_switch()
    sys.exit(0 if success else 1)