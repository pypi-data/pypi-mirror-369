# CUDA版本切换工具 - Python版本

一个功能完善的CUDA版本管理和切换工具，使用Python实现，提供更好的跨平台兼容性和更稳定的性能。

## 特性

### 🔍 智能版本检测
- **多源检测**: 支持系统安装、当前环境、Conda环境等多种CUDA安装源
- **精确识别**: 自动识别版本号和安装路径
- **去重排序**: 智能去重并按版本号排序

### 🎯 模糊版本匹配
- **精确匹配**: 完全相同版本号优先匹配
- **前缀匹配**: 12.8匹配12.8.1等子版本
- **主次版本匹配**: 12.3匹配12.3.x系列
- **主版本匹配**: 12匹配12.x.x系列

### ⚙️ 自动环境配置
- **PATH管理**: 智能清理旧路径，添加新CUDA路径
- **环境变量**: 自动配置CUDA_HOME、LD_LIBRARY_PATH
- **符号链接**: 创建/更新/usr/local/cuda软链接
- **配置持久化**: 自动写入shell配置文件

## 安装

### 方法1: 使用安装脚本
```bash
cd cuda_switch_python
python3 install.py
```

### 方法2: 手动安装
```bash
# 复制到系统路径
sudo cp cuda_switch.py /usr/local/bin/cuda-switch
sudo chmod +x /usr/local/bin/cuda-switch

# 或复制到用户路径
mkdir -p ~/.local/bin
cp cuda_switch.py ~/.local/bin/cuda-switch
chmod +x ~/.local/bin/cuda-switch
export PATH="$HOME/.local/bin:$PATH"
```

## 使用方法

### 基本用法
```bash
# 列出所有可用版本
cuda-switch

# 切换到指定版本
cuda-switch 12.8

# 切换到具体子版本
cuda-switch 12.8.1

# 启用调试模式
cuda-switch --debug 12.8
```

### 高级用法
```bash
# 仅列出版本（不进行切换）
cuda-switch --list

# 主版本匹配（切换到最新的12.x版本）
cuda-switch 12

# 主次版本匹配（切换到最新的12.8.x版本）
cuda-switch 12.8
```

## 项目架构

### 核心类设计

#### CudaVersion
```python
@dataclass
class CudaVersion:
    source: str  # 来源：系统、当前、conda等
    version: str # 版本号：如12.8.1
    path: str   # 安装路径
```

#### CudaDetector
- 负责检测系统中所有可用的CUDA版本
- 支持多种安装源：系统路径、conda环境等
- 智能解析版本号和路径信息

#### CudaMatcher
- 实现智能的版本匹配算法
- 支持精确匹配、前缀匹配、主次版本匹配等
- 处理版本号标准化和比较

#### CudaSwitcher
- 负责实际的版本切换操作
- 管理环境变量和PATH配置
- 创建符号链接和持久化配置

#### CudaManager
- 主控制器，协调各个组件
- 提供统一的用户接口
- 处理用户交互和错误处理

## 相比Shell版本的优势

### 🚀 更好的性能
- **无shell兼容性问题**: 不再受bash/zsh差异影响
- **更快的执行速度**: Python解释器比shell脚本更高效
- **内存管理优化**: 避免了shell脚本的内存泄漏问题

### 🛡️ 更高的稳定性
- **异常处理机制**: 完善的try-catch错误处理
- **类型安全**: 使用dataclass和类型提示
- **测试友好**: 模块化设计便于单元测试

### 👥 更好的用户体验
- **清晰的输出格式**: 结构化的信息显示
- **交互式选择**: 多版本匹配时的用户选择界面
- **详细的帮助信息**: 完整的命令行参数说明

### 🔧 更强的可维护性
- **面向对象设计**: 清晰的类结构和职责分离
- **模块化架构**: 各组件独立，便于扩展
- **代码可读性**: Python语法更清晰易懂

## 技术特点

### 数据结构优化
- 使用`CudaVersion`数据类统一管理版本信息
- 避免了shell脚本中的字符串解析问题
- 支持结构化的版本比较和排序

### 错误处理
- 完善的异常捕获和处理机制
- 用户友好的错误提示信息
- 优雅的降级处理策略

### 跨平台兼容
- 纯Python实现，支持Linux、macOS等系统
- 自动检测shell类型和配置文件
- 智能的权限处理和sudo降级

## 使用示例

### 场景1: 开发环境切换
```bash
# 当前使用CUDA 12.4，需要切换到12.8进行新项目开发
$ cuda-switch 12.8
✅ CUDA 12.8.1 已成功配置
当前路径: /usr/local/cuda-12.8
请运行以下命令使更改生效：
   source ~/.zshrc
```

### 场景2: 多版本管理
```bash
# 查看所有可用版本
$ cuda-switch
可用CUDA版本:
  - [系统] 12.2.20230823
  - [系统] 12.4.1
  - [系统] 12.8.1
  - [当前] 12.4
  - [conda] 11.8
```

### 场景3: 调试模式
```bash
# 启用调试模式查看详细过程
$ cuda-switch --debug 12.8
[DEBUG] 开始检测CUDA版本...
[DEBUG] 检测到系统版本: 3个
[DEBUG] 检测到当前版本: 12.4
[DEBUG] 去重后版本数量: 4
[DEBUG] 开始匹配目标版本: 12.8
[DEBUG] 找到匹配版本: 1个
[DEBUG] 开始切换到版本: [系统] 12.8.1
```

## 故障排除

### 常见问题

1. **权限不足**
   ```bash
   # 使用sudo运行安装脚本
   sudo python3 install.py
   ```

2. **PATH未更新**
   ```bash
   # 手动添加到PATH
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **版本检测失败**
   ```bash
   # 使用调试模式查看详细信息
   cuda-switch --debug --list
   ```

## 开发计划

- [ ] 支持CUDA版本下载和安装
- [ ] 添加配置文件支持
- [ ] 实现版本锁定功能
- [ ] 添加更多的安装源支持
- [ ] 提供Web界面管理

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 许可证

MIT License