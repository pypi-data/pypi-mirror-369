#!/usr/bin/env python3
"""
CUDA下载器模块
提供自动下载和安装CUDA的功能
"""

import os
import sys
import re
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

class CudaDownloader:
    """CUDA版本下载器"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.base_url = "https://developer.download.nvidia.com/compute/cuda"
        self.install_dir = "/usr/local"
        self.ubuntu_version = "2404"  # Ubuntu 24.04
        self.arch = "x86_64"
        
    def log(self, message: str):
        """调试日志输出"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def get_system_info(self) -> Tuple[str, str]:
        """获取系统信息"""
        try:
            # 获取操作系统
            result = subprocess.run(['uname', '-s'], capture_output=True, text=True)
            os_name = result.stdout.strip().lower()
            
            # 获取架构
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            arch = result.stdout.strip()
            
            # 标准化架构名称
            if arch == "arm64":
                arch = "aarch64"
            elif arch == "x86_64":
                arch = "x86_64"
            
            return os_name, arch
        except subprocess.SubprocessError:
            return "unknown", "unknown"
    
    def get_available_versions(self) -> List[str]:
        """获取可下载的CUDA版本列表 - 针对Ubuntu 24.04优化"""
        # 支持Ubuntu 24.04的CUDA版本（按发布时间倒序）
        # 注意：只包含NVIDIA官方已发布的版本
        versions = [
            # CUDA 12.6系列 (最新，完全支持Ubuntu 24.04)
            "12.8.0",
            "12.6.2", "12.6.1", "12.6.0",
            # CUDA 12.5系列 (推荐用于生产环境)
            "12.5.1", "12.5.0",
            # CUDA 12.4系列 (稳定版本)
            "12.4.1", "12.4.0", 
            # CUDA 12.3系列
            "12.3.2", "12.3.1", "12.3.0",
            # CUDA 12.2系列
            "12.2.2", "12.2.1", "12.2.0",
            # CUDA 12.1系列
            "12.1.1", "12.1.0",
            # CUDA 12.0系列
            "12.0.1", "12.0.0",
            # CUDA 11.8系列 (长期支持版本)
            "11.8.0",
            # 较旧版本 (兼容性考虑)
            "11.7.1", "11.6.2"
        ]
        return versions
    
    def find_matching_version(self, target_version: str) -> Optional[str]:
        """智能版本匹配 - 支持模糊匹配"""
        available_versions = self.get_available_versions()
        
        # 精确匹配
        if target_version in available_versions:
            return target_version
        
        # # 特殊处理：12.8 -> 12.6.2 (因为12.8.x系列还未发布)
        # if target_version == "12.8":
        #     return "12.6.2"
        
        # 模糊匹配 - 前缀匹配
        matches = []
        for version in available_versions:
            if version.startswith(target_version + "."):
                matches.append(version)
        
        if matches:
            # 返回最新版本（列表已按时间倒序排列）
            return matches[0]
        
        # 主版本匹配 (如 12 匹配 12.x.x)
        if "." not in target_version:
            for version in available_versions:
                if version.startswith(target_version + "."):
                    return version
        
        return None
    
    def build_download_url(self, version: str) -> Optional[str]:
        """构建下载URL - 针对Ubuntu 24.04优化"""
        os_name, arch = self.get_system_info()
        self.log(f"原始系统信息: {os_name} {arch}")
        
        # macOS系统特殊处理 - 提供Linux版本下载
        if os_name == "darwin":
            self.log("macOS系统，将提供Linux版本下载")
            os_name = "linux"
        
        # 只支持x86_64架构（Ubuntu 24.04主要架构）
        if arch not in ["x86_64"]:
            self.log(f"不支持的架构: {arch}，仅支持x86_64")
            return None
        
        # 检查版本格式
        if not (version.startswith("12.") or version.startswith("11.")):
            self.log(f"不支持的版本格式: {version}")
            return None
        
        # 构建正确的下载链接格式
        # NVIDIA官方格式: https://developer.download.nvidia.com/compute/cuda/{version}/local_installers/cuda_{version}_{build_id}_linux.run
        
        # 版本到构建ID的映射（基于NVIDIA官方发布）
        version_build_map = {
            # 12.8系列 - 已验证可用
            "12.8.0": "570.86.10",
            # 12.6系列 - 已验证可用
            "12.6.2": "560.35.03",
            "12.6.1": "555.42.06", 
            "12.6.0": "555.42.06",
            # 12.5系列
            "12.5.1": "555.42.06",
            "12.5.0": "555.42.06",
            # 12.4系列 - 已验证可用
            "12.4.1": "550.54.15",
            "12.4.0": "550.54.15",
            # 12.3系列
            "12.3.2": "545.23.08",
            "12.3.1": "545.23.08",
            "12.3.0": "545.23.06",
            # 12.2系列
            "12.2.2": "535.104.05",
            "12.2.1": "535.86.10",
            "12.2.0": "535.54.03",
            # 12.1系列
            "12.1.1": "530.30.02",
            "12.1.0": "530.30.02",
            # 12.0系列
            "12.0.1": "525.85.12",
            "12.0.0": "525.60.13",
            # 11.x系列
            "11.8.0": "520.61.05",
            "11.7.1": "515.65.01",
            "11.6.2": "510.47.03"
        }
        
        build_id = version_build_map.get(version)
        if not build_id:
            self.log(f"未找到版本 {version} 对应的构建ID，尝试多种URL格式")
            # 尝试多种可能的URL格式
            possible_urls = [
                # 标准格式
                f"{self.base_url}/{version}/local_installers/cuda_{version}_linux.run",
                # 常见的构建ID格式
                f"{self.base_url}/{version}/local_installers/cuda_{version}_535.154.05_linux.run",
                f"{self.base_url}/{version}/local_installers/cuda_{version}_550.54.15_linux.run",
                f"{self.base_url}/{version}/local_installers/cuda_{version}_555.42.06_linux.run",
                f"{self.base_url}/{version}/local_installers/cuda_{version}_560.35.03_linux.run",
                # 尝试不同的版本格式
                f"{self.base_url}/{version}/local_installers/cuda_{version}_570.09_linux.run"
            ]
            
            for test_url in possible_urls:
                self.log(f"测试URL: {test_url}")
                try:
                    if self.check_url_exists(test_url):
                        self.log(f"找到有效URL: {test_url}")
                        return test_url
                except Exception as e:
                    self.log(f"URL检查失败: {e}")
                    continue
            
            # 如果都不行，返回第一个作为默认
            filename = f"cuda_{version}_linux.run"
        else:
            filename = f"cuda_{version}_{build_id}_linux.run"
        
        url = f"{self.base_url}/{version}/local_installers/{filename}"
        
        self.log(f"构建的URL: {url}")
        self.log(f"文件名: {filename}")
        
        return url
    
    def check_url_exists(self, url: str) -> bool:
        """检查URL是否存在 - 支持重定向处理"""
        try:
            # 使用HEAD请求检查，允许重定向
            response = requests.head(url, timeout=10, allow_redirects=True)
            self.log(f"URL检查: {url} -> 状态码: {response.status_code}")
            
            # 如果有重定向，记录最终URL
            if response.history:
                final_url = response.url
                self.log(f"重定向到: {final_url}")
            
            # 200表示成功，302/301表示重定向但资源存在
            return response.status_code in [200, 302, 301]
            
        except requests.RequestException as e:
            self.log(f"URL检查失败: {e}")
            # 如果HEAD请求失败，尝试GET请求的前几个字节
            try:
                response = requests.get(url, timeout=10, allow_redirects=True, 
                                      headers={'Range': 'bytes=0-1023'})
                self.log(f"GET请求检查: {url} -> 状态码: {response.status_code}")
                return response.status_code in [200, 206, 302, 301]  # 206是部分内容
            except requests.RequestException as e2:
                self.log(f"GET请求也失败: {e2}")
                return False
    
    def download_file(self, url: str, filename: str, max_retries: int = 3) -> bool:
        """下载文件，支持重试和断点续传"""
        for attempt in range(max_retries):
            try:
                print(f"正在下载: {url}")
                print(f"保存到: {filename}")
                if attempt > 0:
                    print(f"重试第 {attempt} 次...")
                
                # 检查是否存在部分下载的文件
                resume_pos = 0
                if os.path.exists(filename):
                    resume_pos = os.path.getsize(filename)
                    print(f"检测到部分下载文件，从 {resume_pos} 字节处继续...")
                
                # 设置请求头支持断点续传
                headers = {}
                if resume_pos > 0:
                    headers['Range'] = f'bytes={resume_pos}-'
                
                response = requests.get(url, stream=True, timeout=60, headers=headers)
                response.raise_for_status()
                
                # 获取文件总大小
                if 'content-range' in response.headers:
                    # 断点续传情况
                    content_range = response.headers['content-range']
                    total_size = int(content_range.split('/')[-1])
                else:
                    # 全新下载情况
                    total_size = int(response.headers.get('content-length', 0)) + resume_pos
                
                downloaded = resume_pos
                
                # 选择文件打开模式
                mode = 'ab' if resume_pos > 0 else 'wb'
                
                with open(filename, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 显示进度
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                downloaded_mb = downloaded / (1024 * 1024)
                                total_mb = total_size / (1024 * 1024)
                                print(f"\r下载进度: {progress:.1f}% ({downloaded_mb:.1f}MB/{total_mb:.1f}MB)", 
                                      end='', flush=True)
                
                print("\n✅ 下载完成!")
                
                # 验证文件大小
                if total_size > 0 and os.path.getsize(filename) != total_size:
                    print(f"⚠️ 文件大小不匹配，期望: {total_size}, 实际: {os.path.getsize(filename)}")
                    if attempt < max_retries - 1:
                        continue
                    return False
                
                return True
                
            except requests.RequestException as e:
                print(f"\n❌下载失败: {e}")
                if attempt < max_retries - 1:
                    print(f"将在 3 秒后重试...")
                    import time
                    time.sleep(3)
                    continue
                else:
                    print(f"已达到最大重试次数 ({max_retries})，下载失败")
                    return False
            except IOError as e:
                print(f"\n❌文件写入失败: {e}")
                return False
            except Exception as e:
                print(f"\n❌未知错误: {e}")
                if attempt < max_retries - 1:
                    continue
                return False
        
        return False
    
    def install_cuda(self, installer_path: str, version: str) -> bool:
        """安装CUDA - 针对Ubuntu 24.04优化"""
        # 转换为绝对路径
        installer_path = os.path.abspath(installer_path)
        
        if not os.path.exists(installer_path):
            print(f"❌安装包不存在: {installer_path}")
            return False
        
        try:
            # 设置可执行权限
            os.chmod(installer_path, 0o755)
            
            # 构建安装路径
            install_path = f"{self.install_dir}/cuda-{version}"
            
            print(f"正在安装CUDA {version}到 {install_path}...")
            print("这可能需要几分钟时间，请耐心等待...")
            
            # 检查系统依赖
            print("检查系统依赖...")
            deps_check = subprocess.run(['which', 'gcc'], capture_output=True)
            if deps_check.returncode != 0:
                print("⚠️ 警告: 未检测到gcc编译器，建议先安装:")
                print("   sudo apt update && sudo apt install build-essential")
            
            # 静默安装命令 - 针对Ubuntu 24.04优化
            cmd = [
                "sudo", installer_path,
                "--silent",
                f"--installpath={install_path}",
                "--toolkit",
                "--no-opengl-libs",  # 避免与系统OpenGL库冲突
                "--override"         # 覆盖已存在的安装
            ]
            
            self.log(f"执行安装命令: {' '.join(cmd)}")
            
            # 执行安装
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30分钟超时
            
            if result.returncode == 0:
                print(f"✅ CUDA {version} 安装成功!")
                print(f"安装路径: {install_path}")
                
                # 验证安装
                nvcc_path = f"{install_path}/bin/nvcc"
                if os.path.exists(nvcc_path):
                    print("✅ nvcc编译器安装成功")
                    
                    # 测试nvcc版本
                    try:
                        nvcc_result = subprocess.run([nvcc_path, '--version'], 
                                                   capture_output=True, text=True, timeout=10)
                        if nvcc_result.returncode == 0:
                            print("✅ nvcc版本验证通过")
                            self.log(f"nvcc版本信息: {nvcc_result.stdout}")
                    except subprocess.TimeoutExpired:
                        print("⚠️ nvcc版本检查超时")
                else:
                    print("⚠️ 警告: nvcc编译器未找到")
                
                # 创建符号链接
                cuda_link = f"{self.install_dir}/cuda"
                try:
                    if os.path.islink(cuda_link):
                        os.unlink(cuda_link)
                    elif os.path.exists(cuda_link):
                        print(f"⚠️ 警告: {cuda_link} 已存在且不是符号链接")
                    
                    os.symlink(install_path, cuda_link)
                    print(f"✅ 创建符号链接: {cuda_link} -> {install_path}")
                except OSError as e:
                    print(f"⚠️ 创建符号链接失败: {e}")
                
                # 清理安装包
                try:
                    os.remove(installer_path)
                    print("✅ 已清理安装包")
                except OSError:
                    print("⚠️ 清理安装包失败")
                
                # 显示后续步骤
                print("\n📋 安装完成后的步骤:")
                print("1. 添加环境变量到 ~/.bashrc 或 ~/.zshrc:")
                print(f"   export PATH={install_path}/bin:$PATH")
                print(f"   export LD_LIBRARY_PATH={install_path}/lib64:$LD_LIBRARY_PATH")
                print("2. 重新加载shell配置:")
                print("   source ~/.bashrc  # 或 source ~/.zshrc")
                print("3. 验证安装:")
                print("   nvcc --version")
                
                return True
            else:
                print(f"❌安装失败 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"错误输出: {result.stderr}")
                if result.stdout:
                    print(f"标准输出: {result.stdout}")
                
                # 常见错误的解决建议
                if "Permission denied" in result.stderr:
                    print("\n💡 解决建议:")
                    print("- 确保有sudo权限")
                    print("- 检查安装包文件权限")
                elif "No space left" in result.stderr:
                    print("\n💡 解决建议:")
                    print("- 检查磁盘空间: df -h")
                    print("- 清理不必要的文件")
                elif "already exists" in result.stderr:
                    print("\n💡 解决建议:")
                    print(f"- 先卸载现有版本: sudo rm -rf {install_path}")
                    print("- 或使用 --override 参数强制覆盖")
                
                return False
                
        except subprocess.TimeoutExpired:
            print("❌安装超时 (30分钟)")
            print("可能的原因:")
            print("- 网络连接问题")
            print("- 系统资源不足")
            print("- 安装包损坏")
            return False
        except subprocess.SubprocessError as e:
            print(f"❌安装过程出错: {e}")
            return False
        except OSError as e:
            print(f"❌文件操作失败: {e}")
            return False
    
    def download_and_install(self, version: str) -> bool:
        """下载并安装指定版本的CUDA"""
        print(f"准备下载并安装 CUDA {version}")
        
        # 智能版本匹配
        matched_version = self.find_matching_version(version)
        if not matched_version:
            print(f"❌未找到匹配的版本: {version}")
            print("支持的版本:")
            available_versions = self.get_available_versions()
            for v in available_versions[:10]:  # 显示前10个版本
                print(f"  - {v}")
            return False
        
        if matched_version != version:
            print(f"💡 版本匹配: {version} -> {matched_version}")
        
        # 使用匹配到的版本
        version = matched_version
        
        # 检查系统兼容性
        os_name, arch = self.get_system_info()
        if os_name == "darwin":
            print("⚠️ 检测到macOS系统")
            print("CUDA官方不直接支持macOS，但您可以：")
            print("1. 使用Docker容器运行CUDA应用")
            print("2. 在Linux虚拟机中安装CUDA")
            print("3. 使用Metal Performance Shaders (MPS)作为替代")
            print("\n是否继续下载Linux版本用于虚拟机？")
            
            confirm = input("继续下载Linux版本？(输入 y 继续): ").strip().lower()
            if confirm != 'y':
                print("已取消下载")
                self.show_manual_download_guide(version)
                return False
            # 继续执行，将macOS当作Linux处理
        
        # 构建下载URL
        download_url = self.build_download_url(version)
        if not download_url:
            print("❌无法构建下载URL")
            self.show_manual_download_guide(version)
            return False
        
        # 检查URL是否有效
        if not self.check_url_exists(download_url):
            print(f"❌下载链接无效: {download_url}")
            print("可能的原因：")
            print("1. 版本号不正确")
            print("2. NVIDIA服务器暂时不可用")
            print("3. 网络连接问题")
            self.show_manual_download_guide(version)
            return False
        
        # 确认下载
        print(f"即将下载 CUDA {version}")
        print(f"下载地址: {download_url}")
        print("此操作可能需要较长时间（通常几GB大小）")
        
        if os_name != "darwin":  # 非macOS系统才询问安装
            confirm = input("确认下载并安装？(输入 y 继续): ").strip().lower()
        else:
            confirm = input("确认下载？(输入 y 继续): ").strip().lower()
            
        if confirm != 'y':
            print("已取消下载")
            return False
        
        # 下载文件
        filename = f"cuda_{version}_linux.run"
        if not self.download_file(download_url, filename):
            return False
        
        # 根据系统决定是否安装
        if os_name == "linux":
            # Linux系统直接安装
            success = self.install_cuda(filename, version)
            if success:
                print(f"\n✅ CUDA {version} 下载安装完成!")
                print("现在可以使用以下命令切换到新版本:")
                print(f"   cuda-switch {version}")
        else:
            # 其他系统只下载
            print(f"\n✅ CUDA {version} 下载完成!")
            print(f"文件保存为: {filename}")
            if os_name == "darwin":
                print("\n📖 macOS使用说明:")
                print("1. 将文件传输到Linux虚拟机或服务器")
                print("2. 在Linux系统中运行安装:")
                print(f"   chmod +x {filename}")
                print(f"   sudo ./{filename}")
            success = True
        
        return success
    
    def show_manual_download_guide(self, version: str):
        """显示手动下载指南 - 针对Ubuntu 24.04优化"""
        print(f"\n📖 CUDA {version} 手动下载指南:")
        print("="*60)
        
        # 构建NVIDIA官方下载页面URL
        version_parts = version.split('.')
        if len(version_parts) >= 2:
            major = version_parts[0]
            minor = version_parts[1]
            patch = version_parts[2] if len(version_parts) > 2 else "0"
            
            # NVIDIA官方下载页面格式
            if patch == "0":
                download_page = f"https://developer.nvidia.com/cuda-{major}-{minor}-download-archive"
            else:
                download_page = f"https://developer.nvidia.com/cuda-{major}-{minor}-{patch}-download-archive"
            
            print(f"🌐 1. 访问NVIDIA官方下载页面:")
            print(f"   {download_page}")
            print()
            print("⚙️ 2. 选择系统配置:")
            print("   - Operating System: Linux")
            print("   - Architecture: x86_64") 
            print("   - Distribution: Ubuntu")
            print("   - Version: 24.04 (推荐) 或 22.04")
            print("   - Installer Type: runfile (local)")
            print()
            print("📥 3. 下载文件:")
            print("   - 点击 'Download' 按钮下载 Base Installer")
            print("   - 文件名通常为: cuda_<version>_<driver_version>_linux.run")
            print("   - 文件大小约 3-4GB，请确保网络稳定")
            print()
            print("🔧 4. 安装前准备 (Ubuntu 24.04):")
            print("   sudo apt update")
            print("   sudo apt install build-essential")
            print("   sudo apt install linux-headers-$(uname -r)")
            print()
            print("📦 5. 安装命令:")
            print(f"   chmod +x cuda_{version}_*_linux.run")
            print(f"   sudo ./cuda_{version}_*_linux.run --silent --toolkit --no-opengl-libs")
            print()
            print("🔗 6. 配置环境变量 (添加到 ~/.bashrc 或 ~/.zshrc):")
            print(f"   export PATH=/usr/local/cuda-{version}/bin:$PATH")
            print(f"   export LD_LIBRARY_PATH=/usr/local/cuda-{version}/lib64:$LD_LIBRARY_PATH")
            print(f"   export CUDA_HOME=/usr/local/cuda-{version}")
            print()
            print("✅ 7. 验证安装:")
            print("   source ~/.bashrc  # 重新加载环境变量")
            print("   nvcc --version    # 检查CUDA编译器版本")
            print("   nvidia-smi        # 检查GPU驱动状态")
            print()
            print("🔄 8. 使用CUDA切换工具管理版本:")
            print(f"   python3 cuda_switch.py {version}")
            print()
            print("💡 故障排除:")
            print("   - 如果安装失败，检查是否有足够的磁盘空间 (至少5GB)")
            print("   - 确保NVIDIA驱动已正确安装")
            print("   - 如果遇到权限问题，确保使用sudo运行安装程序")
            print("   - Ubuntu 24.04可能需要禁用Secure Boot")

def main():
    """测试函数"""
    downloader = CudaDownloader(debug=True)
    
    if len(sys.argv) > 1:
        version = sys.argv[1]
        success = downloader.download_and_install(version)
        if not success:
            downloader.show_manual_download_guide(version)
    else:
        print("用法: python3 cuda_downloader.py <版本号>")
        print("例如: python3 cuda_downloader.py 12.4.1")

if __name__ == "__main__":
    main()