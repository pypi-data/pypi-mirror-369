# CUDA切换工具使用示例

## 安装完成后的功能验证

### 1. 基本功能测试

```bash
# 查看帮助
cuda-switch --help

# 列出当前可用版本
cuda-switch --list

# 尝试切换到某个版本（如果不存在会提示下载）
cuda-switch 12.4.1
```

### 2. 下载功能测试

```bash
# 方法一：使用download命令
cuda-switch download 12.4.1

# 方法二：使用--download参数
cuda-switch --download 12.4.1
```

### 3. 完整工作流程

```bash
# 步骤1: 查看当前状态
cuda-switch --list

# 步骤2: 下载需要的版本
cuda-switch download 12.4.1

# 步骤3: 切换到新版本（Linux系统）
cuda-switch 12.4.1

# 步骤4: 验证版本
nvcc --version
```

## macOS用户特别说明

由于CUDA官方不支持macOS，工具会：

1. **检测系统**：自动识别macOS环境
2. **提供选择**：询问是否下载Linux版本用于虚拟机
3. **下载文件**：下载Linux安装包到本地
4. **使用指导**：提供在虚拟机中安装的说明

### macOS使用流程

```bash
# 1. 下载Linux版本
cuda-switch download 12.4.1
# 系统会提示：检测到macOS系统，是否继续下载Linux版本？

# 2. 确认下载
# 输入 y 继续

# 3. 下载完成后，文件保存为 cuda_12.4.1_550.54.15_linux.run

# 4. 在Linux虚拟机中使用：
# chmod +x cuda_12.4.1_550.54.15_linux.run
# sudo ./cuda_12.4.1_550.54.15_linux.run
```

## 故障排除

### 问题1: 命令不存在
```bash
# 检查安装路径是否在PATH中
echo $PATH | grep -o '/Users/[^:]*/.local/bin'

# 如果没有，添加到PATH
export PATH="$HOME/.local/bin:$PATH"

# 永久添加到shell配置
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 问题2: 下载失败
```bash
# 检查网络连接
curl -I https://developer.download.nvidia.com

# 检查requests库
python3 -c "import requests; print('requests库正常')"

# 如果缺少requests库
pip3 install requests
```

### 问题3: 权限问题
```bash
# 检查安装目录权限
ls -la ~/.local/bin/cuda-switch

# 如果权限不正确
chmod +x ~/.local/bin/cuda-switch
```

## 高级用法

### 调试模式
```bash
# 启用详细日志
cuda-switch --debug download 12.4.1
cuda-switch --debug 12.4.1
```

### 批量操作
```bash
# 下载多个版本
for version in 12.4.1 12.5.0 12.6.0; do
    cuda-switch download $version
done
```

### 脚本集成
```bash
#!/bin/bash
# 自动设置CUDA环境的脚本

# 检查并下载CUDA版本
if ! cuda-switch --list | grep -q "12.4.1"; then
    echo "下载CUDA 12.4.1..."
    cuda-switch download 12.4.1
fi

# 切换到指定版本
cuda-switch 12.4.1

# 验证安装
if command -v nvcc &> /dev/null; then
    echo "CUDA版本: $(nvcc --version | grep release)"
else
    echo "CUDA未正确安装"
fi
```

## 卸载

如果需要卸载工具：

```bash
# 运行卸载脚本
python3 uninstall.py

# 或手动删除
rm -f ~/.local/bin/cuda-switch
rm -rf ~/.local/bin/cuda_switch_lib
```

## 总结

现在的CUDA切换工具提供了：

✅ **统一入口** - 单一的`cuda-switch`命令  
✅ **完整功能** - 列出、切换、下载版本  
✅ **跨平台支持** - Linux直接安装，macOS下载用于虚拟机  
✅ **安全设计** - 不会破坏现有配置  
✅ **智能提示** - 版本不存在时自动提示下载  
✅ **错误处理** - 详细的错误信息和解决方案  

这是一个完整的、生产就绪的CUDA版本管理解决方案！