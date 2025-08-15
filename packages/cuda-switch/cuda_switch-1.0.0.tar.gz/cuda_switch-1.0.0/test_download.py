#!/usr/bin/env python3
"""
测试CUDA下载功能
"""

from cuda_downloader import CudaDownloader

def test_downloader():
    """测试下载器功能"""
    downloader = CudaDownloader(debug=True)
    
    print("=== 测试系统信息获取 ===")
    os_name, arch = downloader.get_system_info()
    print(f"操作系统: {os_name}")
    print(f"架构: {arch}")
    
    print("\n=== 测试可用版本列表 ===")
    versions = downloader.get_available_versions()
    print("支持的版本:")
    for version in versions[:10]:  # 显示前10个
        print(f"  - {version}")
    
    print("\n=== 测试URL构建 ===")
    test_version = "12.4.1"
    url = downloader.build_download_url(test_version)
    if url:
        print(f"CUDA {test_version} 下载URL: {url}")
        
        print("\n=== 测试URL有效性 ===")
        exists = downloader.check_url_exists(url)
        print(f"URL是否有效: {exists}")
    else:
        print(f"无法为版本 {test_version} 构建URL")
    
    print("\n=== 显示手动下载指南 ===")
    downloader.show_manual_download_guide(test_version)

if __name__ == "__main__":
    test_downloader()