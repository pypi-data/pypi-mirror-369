#!/usr/bin/env python3
"""
测试修复后的CUDA下载器功能
"""

import sys
import os
from cuda_downloader import CudaDownloader

def test_url_building():
    """测试URL构建功能"""
    print("🧪 测试URL构建功能...")
    downloader = CudaDownloader(debug=True)
    
    test_versions = ["12.6.2", "12.4.1", "11.8.0"]
    
    for version in test_versions:
        print(f"\n测试版本: {version}")
        url = downloader.build_download_url(version)
        if url:
            print(f"✅ URL构建成功: {url}")
            # 测试URL是否可访问
            if downloader.check_url_exists(url):
                print(f"✅ URL可访问")
            else:
                print(f"❌ URL不可访问")
        else:
            print(f"❌ URL构建失败")

def test_version_list():
    """测试版本列表功能"""
    print("\n🧪 测试版本列表功能...")
    downloader = CudaDownloader()
    
    versions = downloader.get_available_versions()
    print(f"✅ 支持的版本数量: {len(versions)}")
    print("前10个版本:")
    for i, version in enumerate(versions[:10]):
        print(f"  {i+1}. {version}")

def test_system_info():
    """测试系统信息检测"""
    print("\n🧪 测试系统信息检测...")
    downloader = CudaDownloader(debug=True)
    
    os_name, arch = downloader.get_system_info()
    print(f"✅ 检测到系统: {os_name} {arch}")

def test_manual_guide():
    """测试手动下载指南"""
    print("\n🧪 测试手动下载指南...")
    downloader = CudaDownloader()
    
    downloader.show_manual_download_guide("12.4.1")

def main():
    """主测试函数"""
    print("🚀 CUDA下载器修复测试")
    print("=" * 50)
    
    try:
        test_system_info()
        test_version_list()
        test_url_building()
        test_manual_guide()
        
        print("\n✅ 所有测试完成!")
        print("\n💡 使用建议:")
        print("1. 在Ubuntu 24.04环境中测试实际下载功能")
        print("2. 确保网络连接稳定")
        print("3. 确保有足够的磁盘空间 (至少5GB)")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())