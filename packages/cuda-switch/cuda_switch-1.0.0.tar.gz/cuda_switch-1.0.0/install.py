#!/usr/bin/env python3
"""
CUDA切换工具完整安装脚本
"""

import os
import sys
import shutil
from pathlib import Path

def install_cuda_switch():
    """安装完整的CUDA切换工具套件"""
    
    # 获取脚本路径
    script_dir = Path(__file__).parent
    
    # 检查必需文件
    required_files = {
        "cuda_switch.py": "主程序",
        "cuda_downloader.py": "下载器模块"
    }
    
    for filename, description in required_files.items():
        if not (script_dir / filename).exists():
            print(f"❌错误: 找不到{description}文件: {filename}")
            return False
    
    # 目标安装路径
    install_paths = [
        Path.home() / ".local/bin",  # 用户本地路径
        Path("/usr/local/bin"),      # 系统路径
    ]
    
    # 选择可写的安装路径
    install_path = None
    for path in install_paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
            if os.access(path, os.W_OK):
                install_path = path
                break
        except PermissionError:
            continue
    
    if not install_path:
        print("❌错误: 没有找到可写的安装路径")
        print("请尝试使用sudo运行此脚本")
        return False
    
    # 创建支持库目录
    lib_path = install_path / "cuda_switch_lib"
    lib_path.mkdir(exist_ok=True)
    
    try:
        # 1. 安装下载器模块到库目录
        downloader_src = script_dir / "cuda_downloader.py"
        downloader_dst = lib_path / "cuda_downloader.py"
        shutil.copy2(downloader_src, downloader_dst)
        print(f"✅ 下载器模块已安装到: {downloader_dst}")
        
        # 2. 创建统一的可执行脚本
        cuda_switch_script = install_path / "cuda-switch"
        create_unified_script(cuda_switch_script, script_dir, lib_path)
        cuda_switch_script.chmod(0o755)
        
        print(f"✅ CUDA切换工具已安装到: {cuda_switch_script}")
        print("\n🎉 安装完成！现在支持以下功能:")
        print("  cuda-switch                    # 列出所有可用版本")
        print("  cuda-switch 12.8              # 切换到CUDA 12.8")
        print("  cuda-switch download 12.8     # 下载并安装CUDA 12.8")
        print("  cuda-switch --download 12.8   # 下载并安装CUDA 12.8")
        print("  cuda-switch --debug 12.8      # 启用调试模式")
        print("  cuda-switch --list            # 仅列出版本")
        
        # 检查PATH
        path_env = os.environ.get('PATH', '')
        if str(install_path) not in path_env:
            print(f"\n⚠️ 注意: {install_path} 不在PATH中")
            print("请将以下行添加到你的shell配置文件中:")
            print(f'export PATH="{install_path}:$PATH"')
            print("然后运行: source ~/.zshrc")
        
        # 检查依赖
        check_dependencies()
        
        return True
        
    except (IOError, OSError) as e:
        print(f"❌错误: 安装失败: {e}")
        return False

def create_unified_script(script_path: Path, source_dir: Path, lib_path: Path):
    """创建统一的可执行脚本"""
    script_content = f'''#!/usr/bin/env python3
"""
CUDA切换工具 - 统一入口
自动集成下载功能
"""

import sys
import os
from pathlib import Path

# 添加库路径到Python路径
lib_path = Path(__file__).parent / "cuda_switch_lib"
if lib_path.exists():
    sys.path.insert(0, str(lib_path))

# 导入主程序代码
{read_main_program_code(source_dir / "cuda_switch.py")}

if __name__ == "__main__":
    main()
'''
    
    script_path.write_text(script_content)

def read_main_program_code(cuda_switch_path: Path) -> str:
    """读取主程序代码并处理导入"""
    content = cuda_switch_path.read_text()
    
    # 修复导入语句，确保能找到下载器
    content = content.replace(
        "# 导入下载器\ntry:\n    from cuda_downloader import CudaDownloader\nexcept ImportError:\n    CudaDownloader = None",
        """# 导入下载器
try:
    from cuda_downloader import CudaDownloader
except ImportError:
    try:
        # 尝试从当前目录导入
        import sys
        from pathlib import Path
        current_dir = Path(__file__).parent
        lib_dir = current_dir / "cuda_switch_lib"
        if lib_dir.exists():
            sys.path.insert(0, str(lib_dir))
        from cuda_downloader import CudaDownloader
    except ImportError:
        CudaDownloader = None"""
    )
    
    return content

def check_dependencies():
    """检查依赖项"""
    print("\n🔍 检查依赖项...")
    
    # 检查requests库
    try:
        import requests
        print("✅ requests库已安装")
    except ImportError:
        print("⚠️ 缺少requests库，下载功能可能不可用")
        print("安装命令: pip3 install requests")
    
    # 检查系统工具
    required_tools = ["wget", "curl", "sudo"]
    for tool in required_tools:
        if shutil.which(tool):
            print(f"✅ {tool}已安装")
        else:
            print(f"⚠️ {tool}未找到，可能影响某些功能")

if __name__ == "__main__":
    success = install_cuda_switch()
    sys.exit(0 if success else 1)
