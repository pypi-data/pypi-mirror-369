#!/usr/bin/env python3
"""
CUDA切换工具测试脚本
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from cuda_switch import CudaDetector, CudaMatcher, CudaSwitcher, CudaManager, CudaVersion

def test_cuda_detector():
    """测试CUDA检测器"""
    print("=== 测试CUDA检测器 ===")
    
    detector = CudaDetector(debug=True)
    versions = detector.detect_all_versions()
    
    print(f"检测到 {len(versions)} 个CUDA版本:")
    for version in versions:
        print(f"  - {version.display()} (路径: {version.path})")
    
    return versions

def test_cuda_matcher():
    """测试CUDA匹配器"""
    print("\n=== 测试CUDA匹配器 ===")
    
    # 创建测试版本
    test_versions = [
        CudaVersion("系统", "12.2.20230823", "/usr/local/cuda-12.2"),
        CudaVersion("系统", "12.4.1", "/usr/local/cuda-12.4"),
        CudaVersion("系统", "12.8.1", "/usr/local/cuda-12.8"),
        CudaVersion("当前", "12.4", "/usr/local/cuda"),
    ]
    
    matcher = CudaMatcher(debug=True)
    
    # 测试不同的匹配模式
    test_cases = ["12.8", "12.8.1", "12.4", "12", "11.8"]
    
    for target in test_cases:
        print(f"\n测试匹配目标: {target}")
        matches = matcher.fuzzy_match(target, test_versions)
        if matches:
            print(f"  找到匹配:")
            for match in matches:
                print(f"    - {match.display()}")
        else:
            print(f"  未找到匹配")

def test_version_detection():
    """测试版本检测功能"""
    print("\n=== 测试版本检测功能 ===")
    
    manager = CudaManager(debug=True)
    versions = manager.list_versions()
    
    if versions:
        print("检测结果:")
        for version in versions:
            print(f"  - {version.display()}")
            print(f"    路径: {version.path}")
            print(f"    存在: {os.path.exists(version.path)}")
    else:
        print("未检测到任何CUDA版本")

def test_interactive_mode():
    """测试交互模式"""
    print("\n=== 测试交互模式 ===")
    
    # 模拟多个匹配的情况
    test_versions = [
        CudaVersion("系统", "12.4.1", "/usr/local/cuda-12.4.1"),
        CudaVersion("系统", "12.4.2", "/usr/local/cuda-12.4.2"),
        CudaVersion("当前", "12.4", "/usr/local/cuda"),
    ]
    
    print("模拟多版本匹配情况:")
    for i, version in enumerate(test_versions, 1):
        print(f"  {i}. {version.display()}")
    
    print("在实际使用中，用户可以选择具体版本")

def main():
    """主测试函数"""
    print("CUDA切换工具测试")
    print("=" * 50)
    
    try:
        # 测试检测器
        versions = test_cuda_detector()
        
        # 测试匹配器
        test_cuda_matcher()
        
        # 测试版本检测
        test_version_detection()
        
        # 测试交互模式
        test_interactive_mode()
        
        print("\n" + "=" * 50)
        print("测试完成！")
        
        if versions:
            print(f"\n发现 {len(versions)} 个可用的CUDA版本")
            print("可以使用以下命令进行切换:")
            for version in versions[:3]:  # 只显示前3个
                print(f"  python3 cuda_switch.py {version.version}")
        else:
            print("\n未发现可用的CUDA版本")
            print("请确保系统已安装CUDA")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()