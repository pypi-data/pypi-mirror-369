#!/usr/bin/env python3
"""
CUDA下载器使用示例
"""

from cuda_downloader import CudaDownloader

def example_download_cuda():
    """示例：下载CUDA 12.4.1"""
    print("📦 CUDA下载器使用示例")
    print("=" * 40)
    
    # 创建下载器实例
    downloader = CudaDownloader(debug=True)
    
    # 显示可用版本
    print("可用的CUDA版本:")
    versions = downloader.get_available_versions()
    for i, version in enumerate(versions[:5]):  # 显示前5个版本
        print(f"  {i+1}. {version}")
    
    # 选择要下载的版本
    target_version = "12.4.1"
    print(f"\n准备下载 CUDA {target_version}")
    
    # 构建下载URL
    url = downloader.build_download_url(target_version)
    if url:
        print(f"下载URL: {url}")
        
        # 检查URL是否有效
        if downloader.check_url_exists(url):
            print("✅ 下载链接有效")
            
            # 注意：实际下载需要在Linux环境中进行
            print("\n⚠️ 注意：实际下载需要在Ubuntu 24.04环境中进行")
            print("在开发机上只能测试URL构建和验证功能")
            
        else:
            print("❌ 下载链接无效")
            downloader.show_manual_download_guide(target_version)
    else:
        print("❌ 无法构建下载URL")

if __name__ == "__main__":
    example_download_cuda()