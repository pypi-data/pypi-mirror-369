from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import shutil
import sys
import pybind11  # 引入 pybind11 库

def clean_old_files():
    """清理旧的构建文件，避免缓存干扰"""
    clean_targets = ["build", "sliding_median.egg-info", "dist", "*.egg-info"]
    for file in os.listdir(os.getcwd()):
        # 清理旧的 .pyd 扩展文件
        if file.startswith("sliding_median.") and file.endswith(".pyd"):
            clean_targets.append(file)
    for target in clean_targets:
        if os.path.isfile(target):
            os.remove(target)
            print(f"已删除旧文件: {target}")
        elif os.path.isdir(target):
            shutil.rmtree(target, ignore_errors=True)
            print(f"已删除旧目录: {target}")

class BuildExt(build_ext):
    """自定义编译逻辑，适配不同编译器"""
    def build_extensions(self):
        # 针对 MSVC 编译器的配置
        if self.compiler.compiler_type == 'msvc':
            for ext in self.extensions:
                # 启用 C++14 标准，确保异常处理，关闭宽松模式
                ext.extra_compile_args = ['/std:c++14', '/EHsc', '/permissive-']
        # 针对 GCC/Clang 等编译器的配置（可选，方便跨平台）
        else:
            for ext in self.extensions:
                ext.extra_compile_args = ['-std=c++14', '-O3']  # 添加优化参数
        super().build_extensions()

# 定义 C++ 扩展模块
ext_modules = [
    Extension(
        'sliding_median',  # 模块名（必须与 PYBIND11_MODULE 定义的一致）
        sources=['median_sliding_window.cpp'],  # C++ 源文件路径（确保正确）
        language='c++',
        include_dirs=[pybind11.get_include()],  # 引入 pybind11 头文件目录
    )
]

if __name__ == "__main__":
    # 仅在手动运行 setup.py 时清理旧文件（避免构建过程中重复清理）
    if 'clean' in sys.argv or 'build_ext' in sys.argv:
        clean_old_files()
    
    # 移除硬编码的 sys.argv，让 build 命令自动处理参数
    setup(
        name='sliding_median',  # 包名称（pip install 时使用）
        version='0.1.0',  # 版本号（建议遵循语义化版本）
        author='Meng Gang',  # 作者信息（必填，用于 PyPI 展示）
        author_email='981214502@qq.com',  # 联系方式（必填）
        description='滑动窗口中位数的高效 C++ 实现（Python 绑定）',  # 简短描述
        long_description=open('README.md').read() if os.path.exists('README.md') else '',  # 详细描述
        long_description_content_type='text/markdown',  # 详细描述格式
        ext_modules=ext_modules,  # 关联扩展模块
        cmdclass={'build_ext': BuildExt},  # 注册自定义编译类
        install_requires=['pybind11>=2.12.0'],  # 运行时依赖（确保用户安装时自动拉取）
        python_requires='>=3.8',  # 支持的 Python 版本（根据实际情况调整）
        classifiers=[  # 分类信息（帮助 PyPI 索引，可选但推荐）
            'Programming Language :: Python :: 3',
            'Programming Language :: C++',
            'License :: OSI Approved :: MIT License',  # 开源协议（根据实际情况选择）
            'Operating System :: Microsoft :: Windows',
        ],
    )