#!/bin/bash

# Live Agent SDK 构建和安装脚本

set -e

echo "🚀 开始构建 Live Agent SDK..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "📋 Python版本: $python_version"

# 清理之前的构建
echo "🧹 清理之前的构建..."
rm -rf build/ dist/ *.egg-info/

# 安装构建依赖
echo "📦 安装构建依赖..."
pip install --upgrade pip setuptools wheel

# 构建包
echo "🔨 构建SDK包..."
python3 setup.py sdist bdist_wheel

# 检查构建结果
echo "📋 构建结果:"
ls -la dist/

# 安装到本地环境（可选）
if [ "$1" = "--install" ]; then
    echo "📥 安装到本地环境..."
    pip install dist/*.whl
    echo "✅ 安装完成!"
fi

echo "🎉 构建完成!"
echo ""
echo "📦 可用的包文件:"
ls -la dist/
echo ""
echo "💡 要安装到本地环境，请运行:"
echo "   pip install dist/*.whl"
echo ""
echo "💡 要上传到PyPI，请运行:"
echo "   twine upload dist/*" 