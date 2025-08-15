# CUDA下载功能使用指南

## 功能概述

CUDA切换工具现在支持自动下载和安装CUDA版本，当您尝试切换到未安装的版本时，工具会提示您下载。

## 使用方法

### 1. 基本切换（如果版本不存在会提示下载）

```bash
python3 cuda_switch.py 12.4.1
```

如果版本12.4.1未安装，会显示：
```
❌错误: 版本 12.4.1 不在可用版本列表中
可用版本:
  - [当前] 12.2
  - [系统] 12.2.20230823

💡提示: 版本 12.4.1 未安装
您可以使用以下命令下载并安装:
   python3 cuda_switch.py download 12.4.1
或者:
   python3 cuda_switch.py --download 12.4.1
```

### 2. 直接下载安装

#### 方法一：使用download命令
```bash
python3 cuda_switch.py download 12.4.1
```

#### 方法二：使用--download参数
```bash
python3 cuda_switch.py --download 12.4.1
```

### 3. 列出可用版本
```bash
python3 cuda_switch.py --list
```

### 4. 启用调试模式
```bash
python3 cuda_switch.py --debug download 12.4.1
```

## 支持的版本

当前支持自动下载的CUDA版本：

- **12.x系列**: 12.6.2, 12.6.1, 12.6.0, 12.5.1, 12.5.0, 12.4.1, 12.4.0, 12.3.2, 12.3.1, 12.3.0, 12.2.2, 12.2.1, 12.2.0, 12.1.1, 12.1.0, 12.0.1, 12.0.0
- **11.x系列**: 11.8.0, 11.7.1, 11.6.2

## 下载过程

1. **版本验证**: 检查请求的版本是否支持
2. **URL构建**: 自动构建NVIDIA官方下载链接
3. **链接验证**: 检查下载链接是否有效
4. **用户确认**: 提示用户确认下载（文件通常几GB大小）
5. **文件下载**: 显示下载进度
6. **自动安装**: 使用sudo权限静默安装到`/usr/local/cuda-{version}`
7. **清理文件**: 安装完成后自动删除安装包

## 安装要求

- **操作系统**: Linux x86_64
- **权限**: 需要sudo权限进行安装
- **网络**: 稳定的网络连接（下载文件较大）
- **磁盘空间**: 至少5GB可用空间
- **Python依赖**: requests库（用于下载）

安装requests库：
```bash
pip3 install requests
```

## 故障排除

### 1. 下载失败
如果自动下载失败，工具会显示手动下载指南：

```
📖 CUDA 12.4.1 手动下载指南:
==================================================
1. 访问NVIDIA官方下载页面:
   https://developer.nvidia.com/cuda-12-4-1-download-archive

2. 选择系统配置:
   - Operating System: Linux
   - Architecture: x86_64
   - Distribution: Ubuntu (推荐选择最新版本)
   - Version: 20.04 或 22.04
   - Installer Type: runfile (local)

3. 下载Base Installer

4. 安装命令:
   chmod +x cuda_12.4.1_*_linux.run
   sudo ./cuda_12.4.1_*_linux.run

5. 安装完成后，使用以下命令切换版本:
   python3 cuda_switch.py 12.4.1
```

### 2. 权限问题
确保您有sudo权限：
```bash
sudo -v
```

### 3. 网络问题
如果下载速度慢或中断，可以：
- 使用稳定的网络连接
- 手动下载后使用本地安装包

### 4. 磁盘空间不足
检查可用空间：
```bash
df -h /usr/local
```

## 测试功能

运行测试脚本验证下载功能：
```bash
python3 test_download.py
```

## 安全说明

- 所有下载均来自NVIDIA官方服务器
- 安装过程使用NVIDIA官方安装包
- 工具会在安装前请求用户确认
- 安装完成后自动清理临时文件

## 完整工作流程示例

```bash
# 1. 查看当前可用版本
python3 cuda_switch.py --list

# 2. 尝试切换到新版本（如果不存在会提示下载）
python3 cuda_switch.py 12.4.1

# 3. 根据提示下载安装
python3 cuda_switch.py download 12.4.1

# 4. 下载完成后切换版本
python3 cuda_switch.py 12.4.1

# 5. 验证版本
nvcc --version
```

这样您就可以轻松管理和下载不同版本的CUDA了！