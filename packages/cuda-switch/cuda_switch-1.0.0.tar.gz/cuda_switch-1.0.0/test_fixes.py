#!/usr/bin/env python3
"""
测试修复后的功能
"""

from cuda_downloader import CudaDownloader

def test_version_matching():
    """测试版本匹配功能"""
    print("🧪 测试版本匹配功能...")
    downloader = CudaDownloader(debug=True)
    
    test_cases = [
        ("12.8", "12.8.0"),
        ("12.6", "12.6.2"),
        ("12.4", "12.4.1"),
        ("12", "12.8.0"),
        ("11", "11.8.0"),
        ("12.6.2", "12.6.2"),  # 精确匹配
        ("99.9", None)  # 不存在的版本
    ]
    
    for input_version, expected in test_cases:
        result = downloader.find_matching_version(input_version)
        status = "✅" if result == expected else "❌"
        print(f"{status} {input_version} -> {result} (期望: {expected})")

def test_url_building():
    """测试URL构建功能"""
    print("\n🧪 测试URL构建功能...")
    downloader = CudaDownloader(debug=True)
    
    test_versions = ["12.8.0", "12.6.2", "12.4.1"]
    
    for version in test_versions:
        print(f"\n测试版本: {version}")
        url = downloader.build_download_url(version)
        if url:
            print(f"✅ URL: {url}")
        else:
            print(f"❌ URL构建失败")

def test_available_versions():
    """测试可用版本列表"""
    print("\n🧪 测试可用版本列表...")
    downloader = CudaDownloader()
    
    versions = downloader.get_available_versions()
    print(f"✅ 支持的版本数量: {len(versions)}")
    print("前5个版本:")
    for i, version in enumerate(versions[:5]):
        print(f"  {i+1}. {version}")
    
    # 检查是否包含12.8.0
    if "12.8.0" in versions:
        print("✅ 包含12.8.0版本")
    else:
        print("❌ 缺少12.8.0版本")

def main():
    """主测试函数"""
    print("🚀 CUDA下载器修复测试")
    print("=" * 50)
    
    try:
        test_available_versions()
        test_version_matching()
        test_url_building()
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())