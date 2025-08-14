from setuptools import setup, find_packages
import os
def find_pyc_files(package_dir):
    pyc_files = []
    for root, _, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".pyc"):
                pyc_files.append(os.path.relpath(os.path.join(root, file), package_dir))
    return pyc_files

# 获取所有 .pyc 文件
package_dir = "subtitle_corrector"
pyc_files = find_pyc_files(package_dir)

# 递归排除所有 .py 文件
def exclude_py_files(package_dir):
    py_files = []
    for root, _, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.relpath(os.path.join(root, file), package_dir))
    return py_files

py_files = exclude_py_files(package_dir)
setup(
    name='lda_segmenter',
    version='0.1.1',
    description='基于LDA主题模型的文档分段工具',
    author="imuzhangy",
    author_email="imuzhangying@gmail.com",
    url='https://github.com/your_username/lda_segmenter',
    packages=find_packages(exclude=py_files),  # 排除 .py 文件
    install_requires=[
        'jieba',
        'python-docx',
        'nltk',
        'scikit-learn',
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)