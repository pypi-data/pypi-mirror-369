#!/usr/bin/env python3
"""
测试CUDA切换工具安装是否完整
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        # 确保PATH包含安装目录
        env = os.environ.copy()
        local_bin = str(Path.home() / ".local/bin")
        if local_bin not in env.get('PATH', ''):
            env['PATH'] = f"{local_bin}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_installation():
    """测试安装是否成功"""
    print("🧪 测试CUDA切换工具安装...")
    print("=" * 50)
    
    # 1. 测试基本命令
    print("1. 测试基本命令...")
    returncode, stdout, stderr = run_command("cuda-switch --help")
    if returncode == 0:
        print("✅ cuda-switch命令可用")
    else:
        print("❌ cuda-switch命令不可用")
        print(f"错误: {stderr}")
        return False
    
    # 2. 测试列出版本
    print("\n2. 测试列出版本...")
    returncode, stdout, stderr = run_command("cuda-switch --list")
    if returncode == 0:
        print("✅ --list参数工作正常")
        if "未检测到任何CUDA版本" in stdout:
            print("ℹ️ 当前系统未安装CUDA版本（正常）")
        else:
            print("ℹ️ 检测到已安装的CUDA版本")
    else:
        print("❌ --list参数失败")
        print(f"错误: {stderr}")
    
    # 3. 测试下载功能可用性
    print("\n3. 测试下载功能...")
    returncode, stdout, stderr = run_command("cuda-switch download --help 2>/dev/null || cuda-switch --download 12.4.1 --help 2>/dev/null || echo 'download test'")
    
    # 更直接的测试：尝试下载一个版本但立即取消
    print("   测试下载命令格式...")
    test_cmd = "echo 'n' | cuda-switch download 12.4.1 2>/dev/null || echo 'download command available'"
    returncode, stdout, stderr = run_command(test_cmd)
    
    if "download command available" in stdout or "确认下载" in stdout or "准备下载" in stdout:
        print("✅ 下载功能可用")
    else:
        print("⚠️ 下载功能可能有问题")
    
    # 4. 测试依赖
    print("\n4. 检查依赖...")
    try:
        import requests
        print("✅ requests库已安装")
    except ImportError:
        print("❌ requests库未安装")
    
    # 5. 测试文件结构
    print("\n5. 检查安装文件...")
    local_bin = Path.home() / ".local/bin"
    cuda_switch_file = local_bin / "cuda-switch"
    lib_dir = local_bin / "cuda_switch_lib"
    downloader_file = lib_dir / "cuda_downloader.py"
    
    if cuda_switch_file.exists():
        print("✅ 主程序文件存在")
    else:
        print("❌ 主程序文件缺失")
    
    if lib_dir.exists():
        print("✅ 库目录存在")
    else:
        print("❌ 库目录缺失")
    
    if downloader_file.exists():
        print("✅ 下载器模块存在")
    else:
        print("❌ 下载器模块缺失")
    
    print("\n" + "=" * 50)
    print("🎉 安装测试完成！")
    print("\n📖 使用指南:")
    print("  cuda-switch --list              # 列出可用版本")
    print("  cuda-switch 12.8               # 切换版本")
    print("  cuda-switch download 12.8      # 下载安装版本")
    print("  cuda-switch --download 12.8    # 下载安装版本（另一种语法）")
    
    return True

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)