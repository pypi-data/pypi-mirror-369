# CUDA切换工具 Makefile

.PHONY: install test clean help

# 默认目标
help:
	@echo "CUDA切换工具 - 可用命令:"
	@echo "  make install    - 安装工具到系统"
	@echo "  make test       - 运行测试"
	@echo "  make clean      - 清理临时文件"
	@echo "  make help       - 显示此帮助信息"

# 安装工具
install:
	@echo "正在安装CUDA切换工具..."
	python3 install.py

# 运行测试
test:
	@echo "正在运行测试..."
	python3 test_cuda_switch.py

# 清理临时文件
clean:
	@echo "正在清理临时文件..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "清理完成"

# 检查Python环境
check:
	@echo "检查Python环境..."
	@python3 --version
	@echo "检查依赖..."
	@python3 -c "import json, subprocess, re, os, sys; print('所有依赖都可用')"

# 快速测试（仅检测版本）
quick-test:
	@echo "快速测试 - 检测CUDA版本..."
	@python3 cuda_switch.py --list

# 调试模式测试
debug-test:
	@echo "调试模式测试..."
	@python3 cuda_switch.py --debug --list