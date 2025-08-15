#!/usr/bin/env python3
"""
CUDA版本切换工具 - Python实现
提供智能的CUDA版本检测、匹配和切换功能
"""

import os
import sys
import re
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 导入下载器
try:
    from cuda_downloader import CudaDownloader
except ImportError:
    CudaDownloader = None

@dataclass
class CudaVersion:
    """CUDA版本信息数据类"""
    source: str  # 来源：系统、当前、conda等
    version: str  # 版本号：如12.8.1
    path: str    # 安装路径
    
    def __str__(self):
        return f"[{self.source}] {self.version}"
    
    def display(self):
        return f"[{self.source}] {self.version}"

class CudaDetector:
    """CUDA版本检测器"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.script_root = Path(__file__).parent.parent
        
    def log(self, message: str):
        """调试日志输出"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def run_command(self, cmd: str, capture_output=True) -> Tuple[bool, str]:
        """安全执行命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=capture_output, 
                text=True, timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            self.log(f"命令执行失败: {cmd}, 错误: {e}")
            return False, ""
    
    def detect_system_versions(self) -> List[CudaVersion]:
        """检测系统安装的CUDA版本"""
        versions = []
        
        # 检查标准安装路径
        search_paths = [
            "/usr/local/cuda-*",
            "/opt/cuda-*", 
            str(self.script_root / "test_cuda/cuda-*")
        ]
        
        for pattern in search_paths:
            success, output = self.run_command(f"ls -d {pattern} 2>/dev/null")
            if success and output:
                for path in output.split('\n'):
                    if os.path.isdir(path):
                        version = self._extract_version_from_path(path)
                        if version:
                            versions.append(CudaVersion("系统", version, path))
        
        return versions
    
    def detect_current_version(self) -> Optional[CudaVersion]:
        """检测当前活跃的CUDA版本"""
        success, output = self.run_command("nvcc --version")
        if success and output:
            match = re.search(r'release (\d+\.\d+)', output)
            if match:
                version = match.group(1)
                success, nvcc_path = self.run_command("which nvcc")
                if success:
                    cuda_path = str(Path(nvcc_path).parent.parent)
                    return CudaVersion("当前", version, cuda_path)
        return None
    
    def detect_conda_versions(self) -> List[CudaVersion]:
        """检测Conda环境中的CUDA版本"""
        versions = []
        
        # 检查是否有conda环境
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if not conda_prefix:
            return versions
        
        # 检查conda中的CUDA安装
        cuda_paths = [
            f"{conda_prefix}/lib/cuda",
            f"{conda_prefix}/pkgs/cuda-toolkit"
        ]
        
        for path in cuda_paths:
            if os.path.isdir(path):
                version = self._extract_conda_version(path)
                if version:
                    versions.append(CudaVersion("conda", version, path))
        
        return versions
    
    def _extract_version_from_path(self, path: str) -> Optional[str]:
        """从路径中提取版本号"""
        basename = os.path.basename(path)
        
        # 首先尝试从version.json获取
        version_file = os.path.join(path, "version.json")
        if os.path.isfile(version_file):
            try:
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    version = data.get('cuda', {}).get('version')
                    if version:
                        return version
            except (json.JSONDecodeError, IOError):
                pass
        
        # 从目录名提取版本号
        match = re.search(r'cuda-(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)', basename)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_conda_version(self, path: str) -> Optional[str]:
        """从conda安装中提取版本号"""
        # 尝试从conda元数据获取版本
        meta_pattern = f"{path}/conda-meta/cuda-*.json"
        success, output = self.run_command(f"ls {meta_pattern} 2>/dev/null")
        if success and output:
            try:
                with open(output.split('\n')[0], 'r') as f:
                    data = json.load(f)
                    return data.get('version')
            except (json.JSONDecodeError, IOError):
                pass
        
        return self._extract_version_from_path(path)
    
    def detect_all_versions(self) -> List[CudaVersion]:
        """检测所有可用的CUDA版本"""
        self.log("开始检测CUDA版本...")
        
        all_versions = []
        
        # 检测系统版本
        system_versions = self.detect_system_versions()
        all_versions.extend(system_versions)
        self.log(f"检测到系统版本: {len(system_versions)}个")
        
        # 检测当前版本
        current_version = self.detect_current_version()
        if current_version:
            all_versions.append(current_version)
            self.log(f"检测到当前版本: {current_version.version}")
        
        # 检测conda版本
        conda_versions = self.detect_conda_versions()
        all_versions.extend(conda_versions)
        self.log(f"检测到conda版本: {len(conda_versions)}个")
        
        # 去重并排序
        unique_versions = self._deduplicate_versions(all_versions)
        self.log(f"去重后版本数量: {len(unique_versions)}")
        
        return unique_versions
    
    def _deduplicate_versions(self, versions: List[CudaVersion]) -> List[CudaVersion]:
        """去重版本列表"""
        seen = set()
        unique = []
        
        for version in versions:
            key = f"{version.source}:{version.version}"
            if key not in seen:
                seen.add(key)
                unique.append(version)
        
        # 按版本号排序
        return sorted(unique, key=lambda v: self._version_key(v.version))
    
    def _version_key(self, version: str) -> Tuple[int, ...]:
        """生成版本排序键"""
        try:
            parts = version.split('.')
            return tuple(int(part) for part in parts)
        except ValueError:
            return (0,)

class CudaMatcher:
    """CUDA版本匹配器"""
    
    def __init__(self, debug=False):
        self.debug = debug
    
    def log(self, message: str):
        """调试日志输出"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def fuzzy_match(self, target: str, versions: List[CudaVersion]) -> List[CudaVersion]:
        """模糊匹配CUDA版本"""
        self.log(f"开始匹配目标版本: {target}")
        
        matches = []
        
        for version in versions:
            if self._is_match(target, version.version):
                matches.append(version)
        
        self.log(f"找到匹配版本: {len(matches)}个")
        return matches
    
    def _is_match(self, target: str, version: str) -> bool:
        """判断版本是否匹配"""
        # 移除日期后缀进行比较
        normalized_version = re.sub(r'\.20\d{6}$', '', version)
        
        # 1. 完全匹配
        if target == version or target == normalized_version:
            return True
        
        # 2. 前缀匹配 (12.8 匹配 12.8.1)
        if normalized_version.startswith(target + '.'):
            return True
        
        # 3. 主次版本匹配 (12.8 匹配 12.8.x)
        if '.' in target:
            version_major_minor = '.'.join(normalized_version.split('.')[:2])
            if version_major_minor == target:
                return True
        
        # 4. 主版本匹配 (12 匹配 12.x.x)
        if target.isdigit():
            version_major = normalized_version.split('.')[0]
            if version_major == target:
                return True
        
        return False

class CudaSwitcher:
    """CUDA版本切换器"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.shell_config = self._detect_shell_config()
    
    def log(self, message: str):
        """调试日志输出"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def run_command(self, cmd: str, require_sudo=False) -> Tuple[bool, str]:
        """执行系统命令"""
        if require_sudo and os.geteuid() != 0:
            cmd = f"sudo {cmd}"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        except subprocess.SubprocessError as e:
            self.log(f"命令执行失败: {cmd}, 错误: {e}")
            return False, ""
    
    def _detect_shell_config(self) -> str:
        """检测shell配置文件"""
        home = Path.home()
        
        # 按优先级检查配置文件
        config_files = ['.zshrc', '.bashrc', '.bash_profile', '.profile']
        
        for config in config_files:
            config_path = home / config
            if config_path.exists():
                return str(config_path)
        
        # 默认创建.zshrc
        return str(home / '.zshrc')
    
    def switch_version(self, target_version: CudaVersion) -> bool:
        """切换到指定CUDA版本"""
        self.log(f"开始切换到版本: {target_version}")
        
        # 检查目标路径是否存在
        if not os.path.isdir(target_version.path):
            print(f"❌错误: CUDA安装路径不存在: {target_version.path}")
            return False
        
        # 检查是否已经是当前版本
        if self._is_current_version(target_version):
            print(f"当前CUDA版本已经是 {target_version.version}")
            return True
        
        try:
            # 1. 备份配置文件
            self._backup_config()
            
            # 2. 清理旧配置
            self._clean_old_config()
            
            # 3. 更新环境变量
            self._update_environment(target_version)
            
            # 4. 创建符号链接
            self._create_symlink(target_version)
            
            # 5. 持久化配置
            self._persist_config(target_version)
            
            print(f"✅ CUDA {target_version.version} 已成功配置")
            print(f"当前路径: {target_version.path}")
            print("请运行以下命令使更改生效：")
            print(f"   source {self.shell_config}")
            print("请使用以下命令检查CUDA版本:")
            print("   nvcc --version")
            
            return True
            
        except Exception as e:
            print(f"❌错误: 切换版本失败: {e}")
            return False
    
    def _is_current_version(self, target: CudaVersion) -> bool:
        """检查是否已经是当前版本"""
        try:
            # 使用which命令获取nvcc的路径
            which_result = subprocess.run(
                ["which", "nvcc"], 
                capture_output=True, text=True
            )
            
            if which_result.returncode != 0:
                return False
                
            # 获取nvcc的真实路径，避免符号链接问题
            nvcc_path = which_result.stdout.strip()
            real_path = subprocess.run(
                ["readlink", "-f", nvcc_path],
                capture_output=True, text=True
            ).stdout.strip()
            
            # 使用完整路径执行nvcc命令
            if real_path:
                result = subprocess.run(
                    [real_path, "--version"], 
                    capture_output=True, text=True
                )
            else:
                # 如果无法获取真实路径，尝试直接使用环境变量中的CUDA_HOME
                cuda_home = os.environ.get('CUDA_HOME')
                if cuda_home:
                    nvcc_bin = os.path.join(cuda_home, 'bin', 'nvcc')
                    if os.path.exists(nvcc_bin):
                        result = subprocess.run(
                            [nvcc_bin, "--version"], 
                            capture_output=True, text=True
                        )
                    else:
                        return False
                else:
                    return False
                    
            if result.returncode == 0:
                match = re.search(r'release (\d+\.\d+)', result.stdout)
                if match:
                    current_version = match.group(1)
                    return self._version_matches(current_version, target.version)
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            self.log(f"检查当前版本失败: {e}")
            pass
        return False
    
    def _version_matches(self, current: str, target: str) -> bool:
        """检查版本是否匹配"""
        # 精确匹配
        if current == target:
            return True
        
        # 主次版本匹配
        if '.' in target:
            current_major_minor = '.'.join(current.split('.')[:2])
            target_major_minor = '.'.join(target.split('.')[:2])
            return current_major_minor == target_major_minor
        
        return False
    
    def _backup_config(self):
        """备份配置文件"""
        config_path = Path(self.shell_config)
        backup_path = config_path.with_suffix(config_path.suffix + '.cuda_backup')
        
        if config_path.exists() and not backup_path.exists():
            try:
                backup_path.write_text(config_path.read_text())
                self.log(f"已备份配置文件到: {backup_path}")
            except IOError as e:
                self.log(f"备份配置文件失败: {e}")
    
    def _clean_old_config(self):
        """安全清理旧的CUDA配置 - 修复版本"""
        self.log("安全清理旧的CUDA配置...")
        
        config_path = Path(self.shell_config)
        if not config_path.exists():
            return
        
        try:
            lines = config_path.read_text().splitlines()
            new_lines = []
            skip_cuda_block = False
            
            for line in lines:
                # 检测CUDA配置块的开始（由此工具生成的）
                if "# CUDA" in line and "配置" in line and "由cuda-switch工具生成" in line:
                    skip_cuda_block = True
                    continue
                
                # 如果在CUDA配置块中，跳过相关行
                if skip_cuda_block:
                    # 检查是否是CUDA相关的export语句
                    if (line.strip().startswith('export') and 
                        any(cuda_var in line for cuda_var in ['CUDA_HOME', 'PATH', 'LD_LIBRARY_PATH']) and
                        '/cuda' in line):
                        continue
                    # 如果是空行或注释，继续跳过
                    elif line.strip() == '' or line.strip().startswith('#'):
                        continue
                    else:
                        # 遇到非CUDA配置行，结束跳过
                        skip_cuda_block = False
                        new_lines.append(line)
                else:
                    # 只删除明确由此工具添加的CUDA配置行
                    # 更精确的匹配，避免误删用户自定义配置
                    if (line.strip().startswith('export') and 
                        any(pattern in line for pattern in [
                            'export PATH="/usr/local/cuda-',
                            'export LD_LIBRARY_PATH="/usr/local/cuda-',
                            'export CUDA_HOME="/usr/local/cuda-'
                        ]) and 
                        line.startswith('export ') and 
                        '=' in line and 
                        '"' in line):
                        # 这些是工具生成的标准格式，可以安全删除
                        continue
                    else:
                        new_lines.append(line)
            
            # 只有在内容确实发生变化时才写入文件
            new_content = '\n'.join(new_lines)
            original_content = config_path.read_text().rstrip()
            if new_content.rstrip() != original_content:
                config_path.write_text(new_content + '\n')
                self.log("旧配置安全清理完成")
            else:
                self.log("无需清理配置")
            
        except IOError as e:
            self.log(f"清理配置失败: {e}")
    
    def _update_environment(self, version: CudaVersion):
        """更新当前环境变量"""
        self.log("更新环境变量...")
        
        cuda_bin = os.path.join(version.path, 'bin')
        cuda_lib = os.path.join(version.path, 'lib64')
        
        # 清理PATH中的旧CUDA路径
        current_path = os.environ.get('PATH', '')
        path_parts = [p for p in current_path.split(':') 
                     if p and '/cuda' not in p]
        
        # 添加新的CUDA路径
        path_parts.insert(0, cuda_bin)
        os.environ['PATH'] = ':'.join(path_parts)
        
        # 更新LD_LIBRARY_PATH
        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        ld_path_parts = [p for p in current_ld_path.split(':') 
                        if p and '/cuda' not in p]
        ld_path_parts.insert(0, cuda_lib)
        os.environ['LD_LIBRARY_PATH'] = ':'.join(ld_path_parts)
        
        # 设置CUDA_HOME
        os.environ['CUDA_HOME'] = version.path
    
    def _create_symlink(self, version: CudaVersion):
        """创建CUDA符号链接"""
        self.log("创建符号链接...")
        
        symlink_path = "/usr/local/cuda"
        
        # 避免自引用和循环引用
        if version.path == symlink_path:
            self.log("避免创建自引用符号链接")
            return
            
        # 检查目标路径是否已经是符号链接
        try:
            real_target_path = os.path.realpath(version.path)
            if os.path.islink(version.path) and real_target_path == symlink_path:
                self.log(f"检测到循环引用: {version.path} -> {symlink_path}")
                print(f"⚠️警告: 检测到符号链接循环引用，跳过创建符号链接")
                return
        except OSError:
            self.log("检查符号链接时出错")
        
        try:
            # 尝试直接创建
            if os.access("/usr/local", os.W_OK):
                # 如果目标存在且是符号链接，先获取它的真实路径
                if os.path.exists(symlink_path):
                    try:
                        # 检查是否存在循环引用
                        real_symlink_path = os.path.realpath(symlink_path)
                        if real_symlink_path == version.path:
                            self.log(f"检测到循环引用: {symlink_path} -> {version.path}")
                            print(f"⚠️警告: 检测到符号链接循环引用，跳过创建符号链接")
                            return
                        # 安全删除
                        os.remove(symlink_path)
                    except OSError as e:
                        self.log(f"删除旧符号链接失败: {e}")
                        return
                
                # 创建新的符号链接
                os.symlink(version.path, symlink_path)
                self.log(f"已创建符号链接: {symlink_path} -> {version.path}")
            else:
                # 使用sudo
                # 先检查是否存在循环引用
                check_cmd = f"readlink -f {symlink_path}"
                success, output = self.run_command(check_cmd)
                if success and output == version.path:
                    self.log(f"检测到循环引用: {symlink_path} -> {version.path}")
                    print(f"⚠️警告: 检测到符号链接循环引用，跳过创建符号链接")
                    return
                
                success, _ = self.run_command(f"rm -f {symlink_path}", require_sudo=True)
                if success:
                    success, _ = self.run_command(
                        f"ln -sf {version.path} {symlink_path}", 
                        require_sudo=True
                    )
                    if success:
                        self.log(f"已创建符号链接: {symlink_path} -> {version.path}")
        
        except (OSError, subprocess.SubprocessError) as e:
            self.log(f"创建符号链接失败: {e}")
            print(f"❌错误: 创建符号链接失败: {e}")
    
    def _persist_config(self, version: CudaVersion):
        """持久化配置到shell配置文件"""
        self.log("持久化配置...")
        
        config_lines = [
            "",
            f"# CUDA {version.version} 配置 - 由cuda-switch工具生成",
            f'export PATH="{version.path}/bin:$PATH"',
            f'export LD_LIBRARY_PATH="{version.path}/lib64:$LD_LIBRARY_PATH"',
            f'export CUDA_HOME="{version.path}"'
        ]
        
        try:
            with open(self.shell_config, 'a') as f:
                f.write('\n'.join(config_lines) + '\n')
            self.log(f"配置已写入: {self.shell_config}")
        except IOError as e:
            self.log(f"写入配置失败: {e}")

class CudaManager:
    """CUDA管理器主类"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.detector = CudaDetector(debug)
        self.matcher = CudaMatcher(debug)
        self.switcher = CudaSwitcher(debug)
        self.downloader = CudaDownloader(debug) if CudaDownloader else None
    
    def list_versions(self) -> List[CudaVersion]:
        """列出所有可用版本"""
        return self.detector.detect_all_versions()
    
    def download_version(self, target: str) -> bool:
        """下载指定版本的CUDA"""
        if not self.downloader:
            print("❌错误: 下载功能不可用，请检查cuda_downloader.py文件")
            return False
        
        return self.downloader.download_and_install(target)
    
    def switch_to_version(self, target: str) -> bool:
        """切换到指定版本"""
        versions = self.list_versions()
        
        if not versions:
            print("❌错误: 未检测到任何CUDA版本")
            self._suggest_download(target)
            return False
        
        matches = self.matcher.fuzzy_match(target, versions)
        
        if not matches:
            print(f"❌错误: 版本 {target} 不在可用版本列表中")
            print("可用版本:")
            for version in versions:
                print(f"  - {version.display()}")
            self._suggest_download(target)
            return False
        
        if len(matches) == 1:
            return self.switcher.switch_version(matches[0])
        else:
            print(f"⚠️警告: 找到多个匹配版本:")
            for i, version in enumerate(matches, 1):
                print(f"  {i}. {version.display()}")
            
            try:
                choice = input("请选择版本号 (1-{}): ".format(len(matches)))
                index = int(choice) - 1
                if 0 <= index < len(matches):
                    return self.switcher.switch_version(matches[index])
                else:
                    print("❌错误: 无效的选择")
                    return False
            except (ValueError, KeyboardInterrupt):
                print("❌错误: 操作已取消")
                return False
    
    def _suggest_download(self, target: str):
        """建议下载版本"""
        print(f"\n💡提示: 版本 {target} 未安装")
        if self.downloader:
            print(f"您可以使用以下命令下载并安装:")
            print(f"   cuda-switch download {target}")
            print("或者:")
            print(f"   cuda-switch --download {target}")
        else:
            print("请手动下载并安装CUDA，或检查cuda_downloader.py文件")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="CUDA版本切换工具 - 增强版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                    # 列出所有可用版本
  %(prog)s 12.8              # 切换到CUDA 12.8
  %(prog)s 12.8.1            # 切换到CUDA 12.8.1
  %(prog)s download 12.4     # 下载并安装CUDA 12.4
  %(prog)s --download 12.4   # 下载并安装CUDA 12.4
  %(prog)s --debug 12.8      # 启用调试模式切换版本
        """
    )
    
    parser.add_argument(
        'action_or_version', 
        nargs='?', 
        help='操作(download)或要切换的CUDA版本号'
    )
    parser.add_argument(
        'version', 
        nargs='?', 
        help='当第一个参数是download时，这里是版本号'
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='启用调试模式'
    )
    parser.add_argument(
        '--list', 
        action='store_true', 
        help='仅列出可用版本'
    )
    parser.add_argument(
        '--download', 
        metavar='VERSION',
        help='下载并安装指定版本的CUDA'
    )
    
    args = parser.parse_args()
    
    manager = CudaManager(debug=args.debug)
    
    # 处理下载请求
    if args.download:
        success = manager.download_version(args.download)
        sys.exit(0 if success else 1)
    
    # 处理download命令
    if args.action_or_version == 'download':
        if not args.version:
            print("❌错误: 请指定要下载的版本号")
            print("用法: cuda-switch download <版本号>")
            print("例如: cuda-switch download 12.4.1")
            sys.exit(1)
        success = manager.download_version(args.version)
        sys.exit(0 if success else 1)
    
    # 列出版本
    if args.list or not args.action_or_version:
        versions = manager.list_versions()
        if versions:
            print("可用CUDA版本:")
            for version in versions:
                print(f"  - {version.display()}")
        else:
            print("未检测到任何CUDA版本")
            if manager.downloader:
                print("\n💡提示: 您可以使用以下命令下载CUDA:")
                print("   cuda-switch download <版本号>")
                print("例如: cuda-switch download 12.4.1")
        return
    
    # 切换版本
    success = manager.switch_to_version(args.action_or_version)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()